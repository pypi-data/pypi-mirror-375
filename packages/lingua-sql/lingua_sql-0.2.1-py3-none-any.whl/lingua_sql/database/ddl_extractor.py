#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通用DDL提取器
支持多种数据库类型，具有泛化能力
"""

import re
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


class DDLStrategy(ABC):
    """DDL提取策略抽象基类"""
    
    @abstractmethod
    def can_handle(self, database_type: str) -> bool:
        """判断是否能处理指定数据库类型"""
        pass
    
    @abstractmethod
    def extract_ddl(self, connection, **kwargs) -> List[str]:
        """提取DDL语句"""
        pass
    
    @abstractmethod
    def get_database_type(self) -> str:
        """获取数据库类型"""
        pass


class MySQLDDLStrategy(DDLStrategy):
    """MySQL DDL提取策略"""
    
    def can_handle(self, database_type: str) -> bool:
        return database_type.lower() in ['mysql', 'mariadb']
    
    def get_database_type(self) -> str:
        return 'mysql'
    
    def extract_ddl(self, connection, **kwargs) -> List[str]:
        """从MySQL数据库提取DDL"""
        try:
            cursor = connection.cursor()
            ddl_statements = []
            
            # 获取所有数据库
            cursor.execute("SHOW DATABASES")
            databases = [row[0] for row in cursor.fetchall() if row[0] not in ['information_schema', 'performance_schema', 'sys', 'mysql']]
            
            for database in databases:
                try:
                    cursor.execute(f"USE `{database}`")
                    
                    # 获取所有表
                    cursor.execute("SHOW TABLES")
                    tables = [row[0] for row in cursor.fetchall()]
                    
                    for table in tables:
                        # 获取CREATE TABLE语句
                        cursor.execute(f"SHOW CREATE TABLE `{table}`")
                        create_statement = cursor.fetchone()[1]
                        ddl_statements.append(create_statement)
                        
                        # 获取视图
                        cursor.execute(f"SHOW CREATE VIEW `{table}`")
                        view_statements = cursor.fetchall()
                        for view in view_statements:
                            ddl_statements.append(view[1])
                            
                except Exception as e:
                    logger.warning(f"处理数据库 {database} 时出错: {e}")
                    continue
            
            cursor.close()
            return ddl_statements
            
        except Exception as e:
            logger.error(f"MySQL DDL提取失败: {e}")
            return []


class PostgreSQLDDLStrategy(DDLStrategy):
    """PostgreSQL DDL提取策略"""
    
    def can_handle(self, database_type: str) -> bool:
        return database_type.lower() in ['postgresql', 'postgres']
    
    def get_database_type(self) -> str:
        return 'postgresql'
    
    def extract_ddl(self, connection, **kwargs) -> List[str]:
        """从PostgreSQL数据库提取DDL"""
        try:
            cursor = connection.cursor()
            ddl_statements = []
            
            # 获取所有表的DDL
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    'CREATE TABLE ' || schemaname || '.' || tablename || ' (' ||
                    string_agg(
                        column_name || ' ' || data_type || 
                        CASE 
                            WHEN character_maximum_length IS NOT NULL 
                            THEN '(' || character_maximum_length || ')'
                            ELSE ''
                        END ||
                        CASE WHEN is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END ||
                        CASE WHEN column_default IS NOT NULL 
                             THEN ' DEFAULT ' || column_default 
                             ELSE '' 
                        END,
                        ', '
                        ORDER BY ordinal_position
                    ) || ');'
                FROM information_schema.columns 
                WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
                GROUP BY schemaname, tablename
            """)
            
            tables = cursor.fetchall()
            for table in tables:
                ddl_statements.append(table[0])
            
            cursor.close()
            return ddl_statements
            
        except Exception as e:
            logger.error(f"PostgreSQL DDL提取失败: {e}")
            return []


class SQLiteDDLStrategy(DDLStrategy):
    """SQLite DDL提取策略"""
    
    def can_handle(self, database_type: str) -> bool:
        return database_type.lower() in ['sqlite', 'sqlite3']
    
    def get_database_type(self) -> str:
        return 'sqlite'
    
    def extract_ddl(self, connection, **kwargs) -> List[str]:
        """从SQLite数据库提取DDL"""
        try:
            cursor = connection.cursor()
            ddl_statements = []
            
            # 获取所有表的DDL
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL")
            tables = cursor.fetchall()
            
            for table in tables:
                ddl_statements.append(table[0])
            
            cursor.close()
            return ddl_statements
            
        except Exception as e:
            logger.error(f"SQLite DDL提取失败: {e}")
            return []


class SnowflakeDDLStrategy(DDLStrategy):
    """Snowflake DDL提取策略"""
    
    def can_handle(self, database_type: str) -> bool:
        return database_type.lower() in ['snowflake']
    
    def get_database_type(self) -> str:
        return 'snowflake'
    
    def extract_ddl(self, connection, **kwargs) -> List[str]:
        """从Snowflake数据库提取DDL"""
        try:
            cursor = connection.cursor()
            ddl_statements = []
            
            # 获取当前数据库和schema
            cursor.execute("SELECT CURRENT_DATABASE(), CURRENT_SCHEMA()")
            current_db, current_schema = cursor.fetchone()
            
            # 获取所有表的DDL
            cursor.execute(f"""
                SELECT 
                    'CREATE TABLE ' || table_catalog || '.' || table_schema || '.' || table_name || ' (' ||
                    LISTAGG(
                        column_name || ' ' || data_type || 
                        CASE 
                            WHEN character_maximum_length IS NOT NULL 
                            THEN '(' || character_maximum_length || ')'
                            ELSE ''
                        END ||
                        CASE WHEN is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END,
                        ', '
                    ) WITHIN GROUP (ORDER BY ordinal_position) || ');'
                FROM information_schema.columns 
                WHERE table_catalog = '{current_db}' 
                AND table_schema = '{current_schema}'
                GROUP BY table_catalog, table_schema, table_name
            """)
            
            tables = cursor.fetchall()
            for table in tables:
                ddl_statements.append(table[0])
            
            cursor.close()
            return ddl_statements
            
        except Exception as e:
            logger.error(f"Snowflake DDL提取失败: {e}")
            return []


class GenericDDLStrategy(DDLStrategy):
    """通用DDL提取策略，尝试自动识别数据库类型"""
    
    def can_handle(self, database_type: str) -> bool:
        return True  # 通用策略可以处理任何类型
    
    def get_database_type(self) -> str:
        return 'generic'
    
    def extract_ddl(self, connection, **kwargs) -> List[str]:
        """通用DDL提取方法"""
        try:
            # 尝试获取数据库类型
            db_type = self._detect_database_type(connection)
            logger.info(f"检测到数据库类型: {db_type}")
            
            # 根据数据库类型选择相应的策略
            if db_type == 'mysql':
                strategy = MySQLDDLStrategy()
            elif db_type == 'postgresql':
                strategy = PostgreSQLDDLStrategy()
            elif db_type == 'sqlite':
                strategy = SQLiteDDLStrategy()
            elif db_type == 'snowflake':
                strategy = SnowflakeDDLStrategy()
            else:
                # 使用通用方法
                return self._extract_generic_ddl(connection)
            
            return strategy.extract_ddl(connection, **kwargs)
            
        except Exception as e:
            logger.error(f"通用DDL提取失败: {e}")
            return self._extract_generic_ddl(connection)
    
    def _detect_database_type(self, connection) -> str:
        """自动检测数据库类型"""
        try:
            cursor = connection.cursor()
            
            # 尝试MySQL特定查询
            try:
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()[0]
                if 'mysql' in version.lower() or 'mariadb' in version.lower():
                    return 'mysql'
            except:
                pass
            
            # 尝试PostgreSQL特定查询
            try:
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                if 'postgresql' in version.lower():
                    return 'postgresql'
            except:
                pass
            
            # 尝试SQLite特定查询
            try:
                cursor.execute("SELECT sqlite_version()")
                return 'sqlite'
            except:
                pass
            
            # 尝试Snowflake特定查询
            try:
                cursor.execute("SELECT CURRENT_VERSION()")
                return 'snowflake'
            except:
                pass
            
            cursor.close()
            return 'unknown'
            
        except Exception as e:
            logger.warning(f"数据库类型检测失败: {e}")
            return 'unknown'
    
    def _extract_generic_ddl(self, connection) -> List[str]:
        """通用DDL提取方法"""
        try:
            cursor = connection.cursor()
            ddl_statements = []
            
            # 尝试获取表信息
            try:
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema NOT IN ('information_schema', 'pg_catalog')")
                tables = cursor.fetchall()
                
                for table in tables:
                    table_name = table[0]
                    try:
                        # 尝试获取表结构
                        cursor.execute(f"DESCRIBE {table_name}")
                        columns = cursor.fetchall()
                        
                        # 构建简单的DDL
                        ddl = f"CREATE TABLE {table_name} (\n"
                        column_defs = []
                        for col in columns:
                            col_name = col[0]
                            col_type = col[1]
                            col_null = " NOT NULL" if col[2] == "NO" else ""
                            column_defs.append(f"    {col_name} {col_type}{col_null}")
                        
                        ddl += ",\n".join(column_defs) + "\n);"
                        ddl_statements.append(ddl)
                        
                    except Exception as e:
                        logger.warning(f"提取表 {table_name} 的DDL失败: {e}")
                        continue
                        
            except Exception as e:
                logger.warning(f"获取表列表失败: {e}")
            
            cursor.close()
            return ddl_statements
            
        except Exception as e:
            logger.error(f"通用DDL提取失败: {e}")
            return []


class DDLManager:
    """DDL管理器，协调不同策略"""
    
    def __init__(self):
        self.strategies = [
            MySQLDDLStrategy(),
            PostgreSQLDDLStrategy(),
            SQLiteDDLStrategy(),
            SnowflakeDDLStrategy(),
            GenericDDLStrategy()
        ]
    
    def get_strategy(self, database_type: str = None) -> DDLStrategy:
        """获取适合的DDL策略"""
        if database_type:
            for strategy in self.strategies:
                if strategy.can_handle(database_type):
                    return strategy
        
        # 如果没有指定类型或找不到匹配的策略，返回通用策略
        return GenericDDLStrategy()
    
    def extract_ddl(self, connection, database_type: str = None, **kwargs) -> List[str]:
        """提取DDL语句"""
        strategy = self.get_strategy(database_type)
        logger.info(f"使用DDL策略: {strategy.get_database_type()}")
        return strategy.extract_ddl(connection, **kwargs)
    
    def get_supported_databases(self) -> List[str]:
        """获取支持的数据库类型列表"""
        return [strategy.get_database_type() for strategy in self.strategies[:-1]]  # 排除通用策略
    
    def add_custom_strategy(self, strategy: DDLStrategy):
        """添加自定义DDL策略"""
        self.strategies.insert(0, strategy)  # 插入到最前面，优先使用
        logger.info(f"添加自定义DDL策略: {strategy.get_database_type()}")


# 工厂函数
def create_ddl_manager() -> DDLManager:
    """创建DDL管理器实例"""
    return DDLManager()


def extract_ddl_from_connection(connection, database_type: str = None, **kwargs) -> List[str]:
    """从数据库连接提取DDL的便捷函数"""
    manager = create_ddl_manager()
    return manager.extract_ddl(connection, database_type, **kwargs)


