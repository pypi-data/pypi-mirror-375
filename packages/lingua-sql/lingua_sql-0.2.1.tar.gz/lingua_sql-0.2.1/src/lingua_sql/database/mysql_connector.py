import mysql.connector
from mysql.connector import Error
from typing import Optional, List, Dict, Any
import pandas as pd
import re
from ..base.base import Lingua_sqlBase
import logging

logger = logging.getLogger(__name__)

class MySQLConnector(Lingua_sqlBase):
    def __init__(self, host, user, password, database, port=3306, config=None):
        # Initialize the base class first
        super().__init__(config=config)

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    def connect(self) -> bool:
        """连接到 MySQL 数据库"""
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
                if self.connection.is_connected():
                    print("数据库连接成功")
                    self.cursor = self.connection.cursor(dictionary=True)
                    return True
            return True
        except Error as e:
            print(f"连接数据库时发生错误: {e}")
            return False

    def disconnect(self) -> None:
        """关闭数据库连接"""
        try:
            if hasattr(self, 'cursor') and self.cursor:
                try:
                    self.cursor.close()
                except Exception:
                    pass
                self.cursor = None
            if hasattr(self, 'connection') and self.connection and self.connection.is_connected():
                self.connection.close()
                self.connection = None
                print("数据库连接已关闭")
        except Error as e:
            print(f"关闭数据库连接时发生错误: {e}")

    def run_sql(self, sql: str, params: Optional[tuple] = None) -> Optional[List[Dict[str, Any]]]:
        """执行 SQL 查询并返回结果"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return None
            self.cursor.execute(sql, params or ())
            return self.cursor.fetchall()
        except Error as e:
            print(f"执行查询时发生错误: {e}")
            return None

    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """执行更新操作（INSERT, UPDATE, DELETE）"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()

            self.cursor.execute(query, params or ())
            self.connection.commit()
            return self.cursor.rowcount
        except Error as err:
            self.connection.rollback()
            print(f"更新执行失败: {err}")
            raise

    def get_tables(self) -> List[str]:
        """获取数据库中的所有表名"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return []
            self.cursor.execute("SHOW TABLES")
            tables = self.cursor.fetchall()
            return [list(table.values())[0] for table in tables]
        except Error as e:
            print(f"获取表名时发生错误: {e}")
            return []

    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """获取指定表的结构信息"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return []
            self.cursor.execute(f"""
                SELECT 
                    COLUMN_NAME,
                    DATA_TYPE,
                    CHARACTER_MAXIMUM_LENGTH,
                    IS_NULLABLE,
                    COLUMN_KEY,
                    COLUMN_COMMENT
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = '{self.database}'
                AND TABLE_NAME = '{table_name}'
                ORDER BY ORDINAL_POSITION
            """)
            return self.cursor.fetchall()
        except Error as e:
            print(f"获取表 {table_name} 结构时发生错误: {e}")
            return []

    def get_all_tables(self) -> List[str]:
        """获取所有表名"""
        query = """
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = %s
        """
        results = self.run_sql(query, (self.database,))
        return [row['TABLE_NAME'] for row in results] if results else []

    def get_table_comment(self, table_name: str) -> str:
        """获取表的注释"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return ""
            query = """
            SELECT TABLE_COMMENT 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            """
            self.cursor.execute(query, (self.database, table_name))
            result = self.cursor.fetchone()
            return result['TABLE_COMMENT'] if result else ""
        except Error as e:
            print(f"获取表 {table_name} 注释时发生错误: {e}")
            return ""

    def get_tables_with_comments(self) -> List[Dict[str, str]]:
        """获取所有表名及其注释"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return []
            query = """
            SELECT TABLE_NAME, TABLE_COMMENT 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = %s
            ORDER BY TABLE_NAME
            """
            self.cursor.execute(query, (self.database,))
            results = self.cursor.fetchall()
            return [{"name": row['TABLE_NAME'], "comment": row['TABLE_COMMENT']} for row in results]
        except Error as e:
            print(f"获取表名和注释时发生错误: {e}")
            return []

    def generate_ddl_from_schema(self, table_name: str) -> str:
        """根据表结构生成DDL语句"""
        schema = self.get_table_schema(table_name)
        if not schema:
            return ""

        # 获取表注释
        table_comment = self.get_table_comment(table_name)

        ddl = f"CREATE TABLE {table_name} (\n"
        columns = []
        for column in schema:
            col_def = f"    {column['COLUMN_NAME']} {column['DATA_TYPE']}"
            if column['CHARACTER_MAXIMUM_LENGTH']:
                col_def += f"({column['CHARACTER_MAXIMUM_LENGTH']})"
            if column['IS_NULLABLE'] == 'NO':
                col_def += " NOT NULL"
            if column['COLUMN_KEY'] == 'PRI':
                col_def += " PRIMARY KEY"
            # 添加列注释
            if column['COLUMN_COMMENT']:
                col_def += f" COMMENT '{column['COLUMN_COMMENT']}'"
            columns.append(col_def)
        ddl += ",\n".join(columns)
        ddl += "\n)"
        
        # 添加表注释
        if table_comment:
            ddl += f" COMMENT '{table_comment}'"
        
        ddl += ";"

        return ddl

    def import_database_schema(self, ddl_collection=None, train_method=None):
        """导入数据库结构（使用通用DDL提取器）
        与 Lingua_sql 对齐：优先通过 train(ddl=...) 写入，避免直接对集合 add 造成误放。
        """
        if not self.is_connected():
            logger.error("数据库未连接")
            return False
        
        try:
            logger.info("开始导入数据库结构...")
            
            # 使用通用DDL提取器
            from .ddl_extractor import extract_ddl_from_connection
            ddl_statements = extract_ddl_from_connection(
                self.connection, 
                database_type='mysql'
            )
            
            if not ddl_statements:
                logger.warning("未提取到DDL语句")
                return False
            
            logger.info(f"提取到 {len(ddl_statements)} 条DDL语句")

            # 优先通过 train 写入，避免集合错放
            if train_method is not None:
                added = 0
                skipped = 0
                for ddl in ddl_statements:
                    try:
                        res = train_method(ddl=ddl)
                        if res == "duplicate":
                            skipped += 1
                        else:
                            added += 1
                    except Exception as e:
                        logger.warning(f"train 导入DDL失败: {e}")
                        continue
                logger.info(f"DDL 导入完成：新增 {added}，跳过 {skipped}")
            # 退化：在无 train_method 场景下，才直接写集合（不建议）
            elif ddl_collection and hasattr(ddl_collection, 'add'):
                for i, ddl in enumerate(ddl_statements):
                    try:
                        ddl_collection.add(
                            documents=[ddl],
                            metadatas=[{"type": "ddl", "database": "mysql", "index": i}],
                            ids=[f"mysql_ddl_{i}"]
                        )
                        logger.info(f"已添加DDL {i+1}")
                    except Exception as e:
                        logger.warning(f"添加DDL {i+1} 失败: {e}")
                        continue
            
            # 添加导入标记
            if ddl_collection and hasattr(ddl_collection, 'add'):
                try:
                    ddl_collection.add(
                        documents=["MySQL schema imported successfully"],
                        metadatas=[{"type": "import_marker", "database": "mysql"}],
                        ids=["mysql_import_marker"]
                    )
                except Exception as e:
                    logger.warning(f"添加导入标记失败: {e}")
            
            logger.info("数据库结构导入完成")
            return True

        except Exception as e:
            logger.error(f"导入数据库结构失败: {e}")
            return False

    def get_database_statistics(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        try:
            tables_with_comments = self.get_tables_with_comments()
            
            # 统计有注释的表
            tables_with_table_comments = [t for t in tables_with_comments if t['comment']]
            
            # 统计有列注释的列数
            total_columns = 0
            columns_with_comments = 0
            tables_without_comments = []
            
            for table_info in tables_with_comments:
                schema = self.get_table_schema(table_info['name'])
                total_columns += len(schema)
                columns_with_comments += sum(1 for col in schema if col['COLUMN_COMMENT'])
                
                if not table_info['comment']:
                    tables_without_comments.append(table_info['name'])
            
            return {
                "total_tables": len(tables_with_comments),
                "tables_with_comments": len(tables_with_table_comments),
                "table_comment_coverage": len(tables_with_table_comments) / len(tables_with_comments) * 100 if tables_with_comments else 0,
                "total_columns": total_columns,
                "columns_with_comments": columns_with_comments,
                "column_comment_coverage": columns_with_comments / total_columns * 100 if total_columns > 0 else 0,
                "tables_without_comments": tables_without_comments
            }
        except Exception as e:
            print(f"获取数据库统计信息时发生错误: {e}")
            return {}

    def print_database_info(self):
        """打印数据库信息"""
        try:
            tables_with_comments = self.get_tables_with_comments()
            
            print("\n=== 数据库表信息 ===")
            for table_info in tables_with_comments:
                comment = table_info['comment'] if table_info['comment'] else '无注释'
                print(f"- {table_info['name']}: {comment}")

            # 获取每个表的结构
            for table_info in tables_with_comments:
                table_name = table_info['name']
                table_comment = table_info['comment']
                
                print(f"\n表 {table_name} 的结构:")
                if table_comment:
                    print(f"表注释: {table_comment}")
                
                schema = self.get_table_schema(table_name)
                for column in schema:
                    comment = column['COLUMN_COMMENT'] if column['COLUMN_COMMENT'] else '无注释'
                    print(f"- {column['COLUMN_NAME']}: {column['DATA_TYPE']} "
                          f"({'NULL' if column['IS_NULLABLE'] == 'YES' else 'NOT NULL'}) "
                          f"({comment})")

            # 显示统计信息
            stats = self.get_database_statistics()
            if stats:
                print(f"\n=== 数据库统计信息 ===")
                print(f"总表数: {stats['total_tables']}")
                print(f"有表注释的表数: {stats['tables_with_comments']}")
                print(f"表注释覆盖率: {stats['table_comment_coverage']:.1f}%")
                print(f"总列数: {stats['total_columns']}")
                print(f"有列注释的列数: {stats['columns_with_comments']}")
                print(f"列注释覆盖率: {stats['column_comment_coverage']:.1f}%")

                # 显示缺少注释的表
                if stats['tables_without_comments']:
                    print(f"\n=== 缺少表注释的表 ===")
                    for table_name in stats['tables_without_comments']:
                        print(f"- {table_name}")
                    print(f"\n建议为这些表添加注释以提高数据库文档质量。")

        except Exception as e:
            print(f"打印数据库信息时发生错误: {e}")

    def get_table_relationships(self) -> List[Dict[str, str]]:
        """获取表之间的关联关系"""
        try:
            relationships = []
            
            # 获取所有表的外键信息
            for table_info in self.get_tables_with_comments():
                table_name = table_info['name']
                schema = self.get_table_schema(table_name)
                
                for column in schema:
                    if column['COLUMN_KEY'] == 'MUL':  # 外键
                        # 尝试获取外键约束信息
                        fk_info = self._get_foreign_key_info(table_name, column['COLUMN_NAME'])
                        if fk_info:
                            relationships.append({
                                'from_table': table_name,
                                'from_column': column['COLUMN_NAME'],
                                'to_table': fk_info['referenced_table'],
                                'to_column': fk_info['referenced_column'],
                                'constraint_name': fk_info['constraint_name']
                            })
            
            return relationships
        except Exception as e:
            print(f"获取表关联关系时发生错误: {e}")
            return []

    def _get_foreign_key_info(self, table_name: str, column_name: str) -> Optional[Dict[str, str]]:
        """获取外键约束信息"""
        try:
            query = """
            SELECT 
                CONSTRAINT_NAME,
                REFERENCED_TABLE_NAME,
                REFERENCED_COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = %s 
            AND COLUMN_NAME = %s
            AND REFERENCED_TABLE_NAME IS NOT NULL
            """
            result = self.run_sql(query, (self.database, table_name, column_name))
            if result:
                return {
                    'constraint_name': result[0]['CONSTRAINT_NAME'],
                    'referenced_table': result[0]['REFERENCED_TABLE_NAME'],
                    'referenced_column': result[0]['REFERENCED_COLUMN_NAME']
                }
            return None
        except Exception as e:
            print(f"获取外键信息时发生错误: {e}")
            return None

    def generate_table_documentation(self, table_name: str) -> str:
        """生成表的文档说明"""
        try:
            table_comment = self.get_table_comment(table_name)
            schema = self.get_table_schema(table_name)
            
            doc = f"表名: {table_name}\n"
            if table_comment:
                doc += f"表说明: {table_comment}\n"
            doc += f"字段数量: {len(schema)}\n\n"
            
            doc += "字段列表:\n"
            for column in schema:
                comment = column['COLUMN_COMMENT'] if column['COLUMN_COMMENT'] else '无说明'
                key_info = ""
                if column['COLUMN_KEY'] == 'PRI':
                    key_info = " (主键)"
                elif column['COLUMN_KEY'] == 'MUL':
                    key_info = " (外键)"
                elif column['COLUMN_KEY'] == 'UNI':
                    key_info = " (唯一键)"
                
                nullable = "可空" if column['IS_NULLABLE'] == 'YES' else "非空"
                doc += f"- {column['COLUMN_NAME']}: {column['DATA_TYPE']} {nullable}{key_info} - {comment}\n"
            
            return doc
        except Exception as e:
            print(f"生成表文档时发生错误: {e}")
            return f"表 {table_name} 的文档生成失败: {str(e)}"

    def generate_database_documentation(self) -> str:
        """生成完整的数据库文档"""
        try:
            tables_with_comments = self.get_tables_with_comments()
            stats = self.get_database_statistics()
            relationships = self.get_table_relationships()
            
            doc = f"# 数据库 {self.database} 文档\n\n"
            
            # 数据库概览
            doc += "## 数据库概览\n\n"
            doc += f"- 数据库名: {self.database}\n"
            doc += f"- 总表数: {stats.get('total_tables', 0)}\n"
            doc += f"- 表注释覆盖率: {stats.get('table_comment_coverage', 0):.1f}%\n"
            doc += f"- 列注释覆盖率: {stats.get('column_comment_coverage', 0):.1f}%\n\n"
            
            # 表关联关系
            if relationships:
                doc += "## 表关联关系\n\n"
                for rel in relationships:
                    doc += f"- {rel['from_table']}.{rel['from_column']} → {rel['to_table']}.{rel['to_column']}\n"
                doc += "\n"
            
            # 表详细信息
            doc += "## 表详细信息\n\n"
            for table_info in tables_with_comments:
                table_name = table_info['name']
                table_comment = table_info['comment']
                
                doc += f"### {table_name}\n\n"
                if table_comment:
                    doc += f"**表说明**: {table_comment}\n\n"
                
                # 添加表文档
                table_doc = self.generate_table_documentation(table_name)
                doc += table_doc + "\n\n"
            
            return doc
        except Exception as e:
            print(f"生成数据库文档时发生错误: {e}")
            return f"数据库 {self.database} 的文档生成失败: {str(e)}"

    def export_database_documentation(self, file_path: str = None) -> bool:
        """导出数据库文档到文件"""
        try:
            if file_path is None:
                file_path = f"{self.database}_documentation.md"
            
            doc = self.generate_database_documentation()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(doc)
            
            print(f"数据库文档已导出到: {file_path}")
            return True
        except Exception as e:
            print(f"导出数据库文档时发生错误: {e}")
            return False

    def get_table_suggestions(self):
        """获取表建议"""
        try:
            tables_with_comments = self.get_tables_with_comments()
            suggestions = []
            
            for table_info in tables_with_comments:
                table_name = table_info['name']
                comment = table_info['comment'] or '无注释'
                
                # 获取表结构
                schema = self.get_table_schema(table_name)
                if schema:
                    # 生成表描述
                    description = f"表 {table_name}: {comment}\n"
                    description += "字段信息:\n"
                    
                    for col in schema:
                        col_name = col['COLUMN_NAME']
                        col_type = col['DATA_TYPE']
                        col_comment = col['COLUMN_COMMENT'] or '无注释'
                        col_nullable = 'NOT NULL' if col['IS_NULLABLE'] == 'NO' else 'NULL'
                        col_key = f" ({col['COLUMN_KEY']})" if col['COLUMN_KEY'] else ''
                        
                        description += f"  - {col_name}: {col_type} {col_nullable}{col_key} - {col_comment}\n"
                    
                    suggestions.append({
                        'table_name': table_name,
                        'description': description,
                        'column_count': len(schema)
                    })
            
            return suggestions
        except Exception as e:
            print(f"获取表建议时发生错误: {e}")
            return []

    def generate_training_plan(self) -> dict:
        """
        生成自动训练计划
        
        Returns:
            dict: 包含训练计划的字典
        """
        try:
            print("正在生成自动训练计划...")
            
            # 获取所有表信息
            tables_with_comments = self.get_tables_with_comments()
            training_plan = {
                'ddl_items': [],
                'documentation_items': [],
                'suggested_questions': []
            }
            
            for table_info in tables_with_comments:
                table_name = table_info['name']
                table_comment = table_info['comment'] or '无注释'
                
                # 1. 生成 DDL
                ddl = self.generate_ddl_from_schema(table_name)
                if ddl:
                    training_plan['ddl_items'].append({
                        'table': table_name,
                        'ddl': ddl,
                        'comment': table_comment
                    })
                
                # 2. 生成结构化文档
                schema = self.get_table_schema(table_name)
                if schema:
                    doc = f"表 {table_name} 的详细说明:\n"
                    doc += f"表注释: {table_comment}\n\n"
                    doc += "字段结构:\n"
                    
                    for col in schema:
                        col_name = col['COLUMN_NAME']
                        col_type = col['DATA_TYPE']
                        col_comment = col['COLUMN_COMMENT'] or '无注释'
                        col_nullable = 'NOT NULL' if col['IS_NULLABLE'] == 'NO' else 'NULL'
                        col_key = f" ({col['COLUMN_KEY']})" if col['COLUMN_KEY'] else ''
                        
                        doc += f"  - {col_name}: {col_type} {col_nullable}{col_key} - {col_comment}\n"
                    
                    training_plan['documentation_items'].append({
                        'table': table_name,
                        'documentation': doc
                    })
                
                # 3. 生成建议问题
                if schema:
                    # 基于字段类型生成建议问题
                    numeric_fields = [col['COLUMN_NAME'] for col in schema if 'int' in col['DATA_TYPE'].lower() or 'decimal' in col['DATA_TYPE'].lower()]
                    text_fields = [col['COLUMN_NAME'] for col in schema if 'char' in col['DATA_TYPE'].lower() or 'text' in col['DATA_TYPE'].lower()]
                    date_fields = [col['COLUMN_NAME'] for col in schema if 'date' in col['DATA_TYPE'].lower() or 'time' in col['DATA_TYPE'].lower()]
                    
                    if numeric_fields:
                        training_plan['suggested_questions'].append({
                            'table': table_name,
                            'question': f"统计表 {table_name} 中 {numeric_fields[0]} 字段的总和",
                            'type': 'aggregation'
                        })
                    
                    if text_fields:
                        training_plan['suggested_questions'].append({
                            'table': table_name,
                            'question': f"查询表 {table_name} 中 {text_fields[0]} 字段的所有不同值",
                            'type': 'distinct'
                        })
                    
                    if date_fields:
                        training_plan['suggested_questions'].append({
                            'table': table_name,
                            'question': f"查询表 {table_name} 中 {date_fields[0]} 字段在最近30天的记录",
                            'type': 'date_range'
                        })
            
            print(f"训练计划生成完成:")
            print(f"  - DDL项目: {len(training_plan['ddl_items'])} 个")
            print(f"  - 文档项目: {len(training_plan['documentation_items'])} 个")
            print(f"  - 建议问题: {len(training_plan['suggested_questions'])} 个")
            
            return training_plan
            
        except Exception as e:
            print(f"生成训练计划时发生错误: {e}")
            return {}

    def auto_import_schema_with_plan(self, ddl_collection=None, train_method=None) -> bool:
        """
        使用训练计划自动导入数据库结构
        
        Args:
            ddl_collection: DDL集合
            train_method: 训练方法
            
        Returns:
            bool: 是否成功
        """
        try:
            print("=== 开始自动导入数据库结构 ===")
            
            # 生成训练计划
            training_plan = self.generate_training_plan()
            
            if not training_plan:
                print("无法生成训练计划")
                return False
            
            # 1. 导入 DDL
            print("\n--- 导入 DDL 语句 ---")
            for item in training_plan['ddl_items']:
                if train_method:
                    result = train_method(ddl=item['ddl'])
                    if result == "duplicate":
                        print(f"跳过重复DDL: {item['table']}")
                    else:
                        print(f"添加DDL: {item['table']} - {item['comment']}")
            
            # 2. 导入文档
            print("\n--- 导入表文档 ---")
            for item in training_plan['documentation_items']:
                if train_method:
                    result = train_method(documentation=item['documentation'])
                    if result == "duplicate":
                        print(f"跳过重复文档: {item['table']}")
                    else:
                        print(f"添加文档: {item['table']}")
            
            # 3. 显示建议问题
            print("\n--- 建议的训练问题 ---")
            for item in training_plan['suggested_questions']:
                print(f"表 {item['table']}: {item['question']} (类型: {item['type']})")
            
            # 4. 添加导入标记
            if ddl_collection and hasattr(ddl_collection, 'add'):
                try:
                    ddl_collection.add(
                        documents=["Auto schema imported"],
                        metadatas=[{"type": "auto_schema_imported", "timestamp": str(pd.Timestamp.now())}],
                        ids=["auto_schema_imported_marker"]
                    )
                    print("\n已添加自动导入标记")
                except Exception as e:
                    print(f"添加导入标记时发生错误: {e}")
            
            print("\n=== 自动导入完成 ===")
            return True
            
        except Exception as e:
            print(f"自动导入数据库结构时发生错误: {e}")
            return False

    def execute_sql_with_error_handling(self, sql: str, params: Optional[tuple] = None):
        """执行SQL并处理错误"""
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                print("数据库连接不可用，无法执行SQL")
                return None

        try:
            results = self.run_sql(sql, params)
            return results
        except Exception as e:
            print(f"执行 SQL 时发生错误: {e}")
            return None

    # Implementation of abstract methods from Lingua_sqlBase
    def generate_embedding(self, data: str, **kwargs) -> List[float]:
        """生成文本的嵌入向量 - 简单实现，实际应该使用embedding模型"""
        # 这是一个简单的占位符实现
        # 在实际使用中，应该使用真正的embedding模型
        return [0.0] * 384  # 返回384维的零向量作为占位符

    def get_similar_question_sql(self, question: str, **kwargs) -> list:
        """获取相似问题的 SQL - 简单实现"""
        # 这是一个占位符实现，实际应该从向量数据库中检索
        return []

    def get_related_ddl(self, question: str, **kwargs) -> list:
        """获取相关的 DDL - 简单实现"""
        # 这是一个占位符实现，实际应该从向量数据库中检索
        return []

    def get_related_documentation(self, question: str, **kwargs) -> list:
        """获取相关的文档 - 简单实现"""
        # 这是一个占位符实现，实际应该从向量数据库中检索
        return []

    def add_question_sql(self, question: str, sql: str, **kwargs) -> str:
        """添加问题和 SQL 对 - 简单实现"""
        # 这是一个占位符实现，实际应该添加到向量数据库
        return "mock_id"

    def add_ddl(self, ddl: str, **kwargs) -> str:
        """添加 DDL - 简单实现"""
        # 这是一个占位符实现，实际应该添加到向量数据库
        return "mock_id"

    def add_documentation(self, documentation: str, **kwargs) -> str:
        """添加文档 - 简单实现"""
        # 这是一个占位符实现，实际应该添加到向量数据库
        return "mock_id"

    def get_training_data(self, **kwargs) -> pd.DataFrame:
        """获取训练数据 - 简单实现"""
        # 返回空的DataFrame作为占位符
        return pd.DataFrame()

    def remove_training_data(self, id: str, **kwargs) -> bool:
        """删除训练数据 - 简单实现"""
        # 这是一个占位符实现
        return True

    def system_message(self, message: str) -> any:
        """系统消息 - 简单实现"""
        return {"role": "system", "content": message}

    def user_message(self, message: str) -> any:
        """用户消息 - 简单实现"""
        return {"role": "user", "content": message}

    def assistant_message(self, message: str) -> any:
        """助手消息 - 简单实现"""
        return {"role": "assistant", "content": message}

    def submit_prompt(self, prompt, **kwargs) -> str:
        """提交提示到 LLM - 简单实现"""
        # 这是一个占位符实现，实际应该调用LLM API
        if isinstance(prompt, list):
            # 如果是消息列表，提取最后一条用户消息
            for msg in reversed(prompt):
                if msg.get("role") == "user":
                    return f"Mock response for: {msg.get('content', '')}"
        elif isinstance(prompt, str):
            return f"Mock response for: {prompt}"
        return "Mock response"

    def get_sql_prompt(self, question: str, question_sql_list: list, ddl_list: list, doc_list: list, **kwargs) -> str:
        """生成SQL提示 - 简单实现"""
        prompt = f"Question: {question}\n\n"
        if question_sql_list:
            prompt += "Similar questions and SQL:\n"
            for item in question_sql_list:
                prompt += f"Q: {item.get('question', '')}\n"
                prompt += f"SQL: {item.get('sql', '')}\n\n"
        if ddl_list:
            prompt += "Related DDL:\n"
            for ddl in ddl_list:
                prompt += f"{ddl}\n\n"
        if doc_list:
            prompt += "Related documentation:\n"
            for doc in doc_list:
                prompt += f"{doc}\n\n"
        prompt += "Generate SQL for the question above."
        return prompt

    def __del__(self):
        """析构函数，确保关闭数据库连接"""
        self.disconnect() 