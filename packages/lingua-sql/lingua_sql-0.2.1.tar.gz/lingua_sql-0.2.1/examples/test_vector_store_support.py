#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试 LinguaSQL 向量数据库支持
"""

import os
import time
from lingua_sql import LinguaSQL
from lingua_sql.config import LinguaSQLConfig, APIConfig, VectorStoreConfig, DatabaseConfig

def test_vector_store_support():
    """测试各种向量数据库的支持"""
    
    # 测试配置
    test_configs = [
        {
            "name": "ChromaDB",
            "type": "chromadb",
            "path": "./test_chromadb"
        },
        {
            "name": "FAISS",
            "type": "faiss",
            "path": "./test_faiss"
        }
    ]
    
    print("=== LinguaSQL 向量数据库支持测试 ===\n")
    
    for config_info in test_configs:
        print(f"测试 {config_info['name']} ({config_info['type']})...")
        
        try:
            # 创建配置
            config = LinguaSQLConfig(
                api=APIConfig(
                    api_key="dummy_key",  # 使用虚拟密钥进行测试
                    model="deepseek-chat"
                ),
                vector_store=VectorStoreConfig(
                    type=config_info['type'],
                    path=config_info['path'],
                    n_results_sql=5,
                    n_results_ddl=3,
                    n_results_documentation=3
                ),
                database=DatabaseConfig(
                    type="mysql",
                    host="localhost",
                    port=3306,
                    user="root",
                    password="",
                    database="test",
                    auto_connect=False  # 不自动连接数据库
                )
            )
            
            # 初始化 LinguaSQL
            nl = LinguaSQL(config=config)
            
            # 测试基本功能
            print(f"  ✅ {config_info['name']} 初始化成功")
            print(f"  📋 向量数据库类型: {config_info['type']}")
            print(f"  🔧 客户端类型: {type(nl.vector_store).__name__}")
            
            # 测试添加数据
            test_question = "查询所有用户的姓名和年龄"
            test_sql = "SELECT name, age FROM users"
            
            # 添加问题和SQL
            result_id = nl.train(question=test_question, sql=test_sql)
            print(f"  ✅ 添加训练数据成功: {result_id}")
            
            # 添加DDL
            test_ddl = "CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100), age INT)"
            ddl_id = nl.train(ddl=test_ddl)
            print(f"  ✅ 添加DDL成功: {ddl_id}")
            
            # 添加文档
            test_doc = "用户表包含用户的基本信息，包括ID、姓名和年龄"
            doc_id = nl.train(documentation=test_doc)
            print(f"  ✅ 添加文档成功: {doc_id}")
            
            # 测试相似性搜索
            similar_sql = nl.get_similar_question_sql("查询用户信息")
            print(f"  ✅ 相似SQL搜索成功: 找到 {len(similar_sql)} 个结果")
            
            # 测试DDL搜索
            related_ddl = nl.get_related_ddl("用户表结构")
            print(f"  ✅ 相关DDL搜索成功: 找到 {len(related_ddl)} 个结果")
            
            # 测试文档搜索
            related_docs = nl.get_related_documentation("用户信息")
            print(f"  ✅ 相关文档搜索成功: 找到 {len(related_docs)} 个结果")
            
            # 测试获取训练数据
            training_data = nl.get_training_data()
            print(f"  ✅ 获取训练数据成功: {len(training_data)} 条记录")
            
            # 测试清理重复数据
            cleaned = nl.clean_duplicates()
            print(f"  ✅ 清理重复数据成功: {cleaned}")
            
            # FAISS 特定功能测试
            if config_info['type'] == 'faiss' and hasattr(nl.vector_store, 'get_stats'):
                stats = nl.vector_store.get_stats()
                print(f"  ✅ 获取统计信息成功: {stats}")
            
            print(f"  🎉 {config_info['name']} 所有测试通过\n")
            
        except Exception as e:
            print(f"  ❌ {config_info['name']} 测试失败: {e}\n")
            import traceback
            traceback.print_exc()

def test_performance_comparison():
    """性能对比测试"""
    print("\n=== 性能对比测试 ===")
    
    # 准备测试数据
    test_data = [
        (f"查询用户{i}的信息", f"SELECT * FROM users WHERE id = {i}")
        for i in range(50)  # 减少数据量以加快测试
    ]
    
    vector_stores = ["chromadb", "faiss"]
    results = {}
    
    for vs_type in vector_stores:
        print(f"\n测试 {vs_type.upper()} 性能...")
        
        try:
            config = LinguaSQLConfig(
                vector_store=VectorStoreConfig(
                    type=vs_type,
                    path=f"./perf_test_{vs_type}"
                )
            )
            
            nl = LinguaSQL(config=config)
            
            # 测试添加数据性能
            start_time = time.time()
            for question, sql in test_data:
                nl.train(question=question, sql=sql)
            add_time = time.time() - start_time
            
            # 测试查询性能
            start_time = time.time()
            for question, _ in test_data[:10]:  # 只测试前10个
                nl.get_similar_question_sql(question)
            query_time = time.time() - start_time
            
            results[vs_type] = {
                'add_time': add_time,
                'query_time': query_time,
                'total_data': len(test_data)
            }
            
            print(f"  ✅ {vs_type.upper()} 性能测试完成")
            print(f"     添加 {len(test_data)} 条数据耗时: {add_time:.3f}秒")
            print(f"     查询 10 次耗时: {query_time:.3f}秒")
            
        except Exception as e:
            print(f"  ❌ {vs_type.upper()} 性能测试失败: {e}")
    
    # 输出性能对比结果
    if len(results) > 1:
        print(f"\n=== 性能对比结果 ===")
        for vs_type, result in results.items():
            print(f"{vs_type.upper()}:")
            print(f"  添加速度: {result['total_data']/result['add_time']:.1f} 条/秒")
            print(f"  查询速度: {10/result['query_time']:.1f} 次/秒")

def test_auto_detection():
    """测试自动检测功能"""
    print("\n=== 测试自动检测功能 ===")
    
    # 设置环境变量
    test_configs = [
        ("LINGUA_SQL_VECTOR_STORE", "chromadb"),
        ("LINGUA_SQL_VECTOR_STORE", "faiss")
    ]
    
    for env_key, expected_type in test_configs:
        print(f"测试环境变量 {env_key}={expected_type}")
        
        # 临时设置环境变量
        original_value = os.environ.get(env_key)
        os.environ[env_key] = expected_type
        
        try:
            # 使用环境变量自动配置
            nl = LinguaSQL()
            actual_type = nl._get_cfg('vector_store.type')
            print(f"  预期类型: {expected_type}")
            print(f"  实际类型: {actual_type}")
            print(f"  客户端类型: {type(nl.vector_store).__name__}")
            print(f"  ✅ 自动检测成功\n")
        except Exception as e:
            print(f"  ❌ 自动检测失败: {e}\n")
        finally:
            # 恢复原始环境变量
            if original_value is not None:
                os.environ[env_key] = original_value
            else:
                os.environ.pop(env_key, None)

def cleanup_test_data():
    """清理测试数据"""
    print("\n=== 清理测试数据 ===")
    
    import shutil
    
    test_dirs = [
        "./test_chromadb",
        "./test_faiss", 
        "./perf_test_chromadb",
        "./perf_test_faiss"
    ]
    
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            try:
                shutil.rmtree(test_dir)
                print(f"  ✅ 清理 {test_dir}")
            except Exception as e:
                print(f"  ❌ 清理 {test_dir} 失败: {e}")

if __name__ == "__main__":
    test_vector_store_support()
    test_performance_comparison()
    test_auto_detection()
    cleanup_test_data()
    
    print("=== 测试完成 ===")
