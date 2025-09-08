#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
向量库深度分析脚本
深入分析不同向量库目录的内容、结构和数据
"""

import os
import sys
import json
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def analyze_chroma_database():
    """分析 ChromaDB 数据库文件"""
    print("=== ChromaDB 数据库深度分析 ===\n")
    
    current_dir = Path(__file__).parent
    chroma_db_file = current_dir / "chroma.sqlite3"
    
    if not chroma_db_file.exists():
        print("❌ ChromaDB 数据库文件不存在")
        return
    
    try:
        # 连接数据库
        conn = sqlite3.connect(chroma_db_file)
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"数据库中的表:")
        for table in tables:
            table_name = table[0]
            print(f"  ✓ {table_name}")
            
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            print(f"    列结构:")
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                print(f"      - {col_name}: {col_type} {'(PK)' if pk else ''}")
            
            # 获取记录数量
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"    记录数: {count}")
            
            # 获取样本数据
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                sample_data = cursor.fetchall()
                print(f"    样本数据:")
                for i, row in enumerate(sample_data, 1):
                    print(f"      {i}. {row[:3]}...")  # 只显示前3个字段
            
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 分析 ChromaDB 数据库失败: {e}")

def analyze_vector_directories():
    """分析向量库目录"""
    print("=== 向量库目录深度分析 ===\n")
    
    current_dir = Path(__file__)
    vector_dirs = [
        "27fb8419-3b63-4973-a72b-6be68a1166b9",
        "ae102e87-e644-4fee-899c-97d9d654fab2", 
        "d4f94d14-543b-42c0-80fb-e5ee4260efc6"
    ]
    
    for dir_name in vector_dirs:
        dir_path = current_dir.parent / dir_name
        if not dir_path.exists():
            continue
            
        print(f"分析目录: {dir_name}")
        print(f"路径: {dir_path}")
        
        # 分析每个文件
        for file_name in ["data_level0.bin", "header.bin", "length.bin", "link_lists.bin"]:
            file_path = dir_path / file_name
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"  {file_name}:")
                print(f"    大小: {size} bytes ({size/1024/1024:.2f} MB)")
                
                # 分析文件内容（如果是文本文件）
                if file_name in ["header.bin", "length.bin"] and size < 10000:  # 小文件才尝试读取
                    try:
                        with open(file_path, 'rb') as f:
                            content = f.read()
                            # 尝试解码为文本
                            try:
                                text_content = content.decode('utf-8')
                                print(f"    内容预览: {text_content[:100]}...")
                            except UnicodeDecodeError:
                                # 如果是二进制，显示十六进制
                                hex_content = content[:50].hex()
                                print(f"    二进制内容预览: {hex_content}...")
                    except Exception as e:
                        print(f"    读取失败: {e}")
            else:
                print(f"  {file_name}: 缺失")
        
        print()
    
    print("="*60)

def test_vector_store_operations():
    """测试向量存储操作"""
    print("=== 向量存储操作测试 ===\n")
    
    try:
        from lingua_sql import LinguaSQL
        from lingua_sql.config import LinguaSQLConfig, DatabaseConfig, APIConfig
        
        current_dir = Path(__file__).parent
        
        # 测试1: 使用主目录
        print("测试1: 使用主目录")
        config1 = LinguaSQLConfig(
            api=APIConfig(
                api_key="test_key",
                model="deepseek-chat",
                client="persistent",
                path=str(current_dir),
            ),
            database=DatabaseConfig(
                type="mysql",
                host="localhost",
                port=3306,
                user="test",
                password="test",
                database="test",
                auto_connect=False,
                auto_import_ddl=False,
            ),
            debug=False
        )
        
        nl1 = LinguaSQL(config=config1)
        
        # 测试各种操作
        print("  测试 DDL 集合...")
        if hasattr(nl1, 'ddl_collection') and nl1.ddl_collection:
            ddl_info = nl1.ddl_collection.get()
            if ddl_info and 'ids' in ddl_info:
                print(f"    ✓ DDL集合包含 {len(ddl_info['ids'])} 条记录")
                if ddl_info['ids']:
                    print(f"    样本ID: {ddl_info['ids'][:3]}")
            else:
                print(f"    ⚠ DDL集合为空")
        
        print("  测试 SQL 集合...")
        if hasattr(nl1, 'sql_collection') and nl1.sql_collection:
            sql_info = nl1.sql_collection.get()
            if sql_info and 'ids' in sql_info:
                print(f"    ✓ SQL集合包含 {len(sql_info['ids'])} 条记录")
                if sql_info['ids']:
                    print(f"    样本ID: {sql_info['ids'][:3]}")
            else:
                print(f"    ⚠ SQL集合为空")
        
        print("  测试文档集合...")
        if hasattr(nl1, 'documentation_collection') and nl1.documentation_collection:
            doc_info = nl1.documentation_collection.get()
            if doc_info and 'ids' in doc_info:
                print(f"    ✓ 文档集合包含 {len(doc_info['ids'])} 条记录")
                if doc_info['ids']:
                    print(f"    样本ID: {doc_info['ids'][:3]}")
            else:
                print(f"    ⚠ 文档集合为空")
        
        print()
        
        # 测试2: 使用子目录
        print("测试2: 使用子目录")
        config2 = LinguaSQLConfig(
            api=APIConfig(
                api_key="test_key",
                model="deepseek-chat",
                client="persistent",
                path=str(current_dir / "27fb8419-3b63-4973-a72b-6be68a1166b9"),
            ),
            database=DatabaseConfig(
                type="mysql",
                host="localhost",
                port=3306,
                user="test",
                password="test",
                database="test",
                auto_connect=False,
                auto_import_ddl=False,
            ),
            debug=False
        )
        
        nl2 = LinguaSQL(config=config2)
        
        # 测试各种操作
        print("  测试 DDL 集合...")
        if hasattr(nl2, 'ddl_collection') and nl2.ddl_collection:
            ddl_info = nl2.ddl_collection.get()
            if ddl_info and 'ids' in ddl_info:
                print(f"    ✓ DDL集合包含 {len(ddl_info['ids'])} 条记录")
            else:
                print(f"    ⚠ DDL集合为空")
        
        print("  测试 SQL 集合...")
        if hasattr(nl2, 'sql_collection') and nl2.sql_collection:
            sql_info = nl2.sql_collection.get()
            if sql_info and 'ids' in sql_info:
                print(f"    ✓ SQL集合包含 {len(sql_info['ids'])} 条记录")
            else:
                print(f"    ⚠ SQL集合为空")
        
        print("  测试文档集合...")
        if hasattr(nl2, 'documentation_collection') and nl2.documentation_collection:
            doc_info = nl2.documentation_collection.get()
            if doc_info and 'ids' in doc_info:
                print(f"    ✓ 文档集合包含 {len(doc_info['ids'])} 条记录")
            else:
                print(f"    ⚠ 文档集合为空")
        
    except Exception as e:
        print(f"❌ 向量存储操作测试失败: {e}")

def analyze_data_relationships():
    """分析数据关系"""
    print("\n=== 数据关系分析 ===\n")
    
    try:
        from lingua_sql import LinguaSQL
        from lingua_sql.config import LinguaSQLConfig, DatabaseConfig, APIConfig
        
        current_dir = Path(__file__).parent
        
        # 使用主目录初始化
        config = LinguaSQLConfig(
            api=APIConfig(
                api_key="test_key",
                model="deepseek-chat",
                client="persistent",
                path=str(current_dir),
            ),
            database=DatabaseConfig(
                type="mysql",
                host="localhost",
                port=3306,
                user="test",
                password="test",
                database="test",
                auto_connect=False,
                auto_import_ddl=False,
            ),
            debug=False
        )
        
        nl = LinguaSQL(config=config)
        
        print("分析向量存储中的数据关系...")
        
        # 检查是否有训练数据
        if hasattr(nl, 'get_training_data'):
            try:
                training_data = nl.get_training_data()
                if training_data is not None and hasattr(training_data, 'shape'):
                    print(f"✓ 训练数据可用，形状: {training_data.shape}")
                    if len(training_data) > 0:
                        print(f"  样本数据:")
                        print(f"    {training_data.head(3).to_string()}")
                else:
                    print("⚠ 训练数据为空或不可用")
            except Exception as e:
                print(f"✗ 获取训练数据失败: {e}")
        
        # 检查是否有相似问题查询功能
        if hasattr(nl, 'get_similar_question_sql'):
            try:
                similar_questions = nl.get_similar_question_sql("测试问题")
                if similar_questions:
                    print(f"✓ 相似问题查询功能正常，返回 {len(similar_questions)} 条结果")
                else:
                    print("⚠ 相似问题查询返回空结果")
            except Exception as e:
                print(f"✗ 相似问题查询失败: {e}")
        
        # 检查是否有相关DDL查询功能
        if hasattr(nl, 'get_related_ddl'):
            try:
                related_ddl = nl.get_related_ddl("测试查询")
                if related_ddl:
                    print(f"✓ 相关DDL查询功能正常，返回 {len(related_ddl)} 条结果")
                else:
                    print("⚠ 相关DDL查询返回空结果")
            except Exception as e:
                print(f"✗ 相关DDL查询失败: {e}")
        
    except Exception as e:
        print(f"❌ 数据关系分析失败: {e}")

def main():
    """主函数"""
    print("🔍 向量库深度分析工具")
    print("=" * 60)
    
    # 1. 分析 ChromaDB 数据库
    analyze_chroma_database()
    
    # 2. 分析向量库目录
    analyze_vector_directories()
    
    # 3. 测试向量存储操作
    test_vector_store_operations()
    
    # 4. 分析数据关系
    analyze_data_relationships()
    
    print("\n" + "=" * 60)
    print("🎯 深度分析完成！")
    print("\n📋 分析结果总结:")
    print("1. ChromaDB 数据库结构分析")
    print("2. 向量库目录文件分析")
    print("3. 向量存储操作测试")
    print("4. 数据关系分析")
    print("\n💡 这些分析结果可以帮助你了解:")
    print("   - 向量库的数据存储结构")
    print("   - 不同目录的兼容性")
    print("   - 数据访问和查询能力")
    print("   - 向量库的通用性程度")

if __name__ == "__main__":
    main()
