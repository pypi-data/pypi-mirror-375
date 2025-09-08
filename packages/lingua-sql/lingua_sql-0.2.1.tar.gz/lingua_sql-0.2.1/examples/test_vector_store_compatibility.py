#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
向量库通用性测试脚本
测试不同向量库目录是否可以互相访问和共享数据
"""

import os
import sys
import json
import shutil
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_vector_store_compatibility():
    """测试向量库的通用性"""
    
    print("=== 向量库通用性测试 ===\n")
    
    # 获取当前目录
    current_dir = Path(__file__).parent
    print(f"当前目录: {current_dir}")
    
    # 检查向量库目录
    vector_dirs = [
        "27fb8419-3b63-4973-a72b-6be68a1166b9",
        "ae102e87-e644-4fee-899c-97d9d654fab2", 
        "d4f94d14-543b-42c0-80fb-e5ee4260efc6"
    ]
    
    print("发现的向量库目录:")
    for dir_name in vector_dirs:
        dir_path = current_dir / dir_name
        if dir_path.exists():
            print(f"  ✓ {dir_name}")
            # 检查目录内容
            for file_name in ["data_level0.bin", "header.bin", "length.bin", "link_lists.bin"]:
                file_path = dir_path / file_name
                if file_path.exists():
                    size = file_path.stat().st_size
                    print(f"    - {file_name}: {size} bytes")
                else:
                    print(f"    - {file_name}: 缺失")
        else:
            print(f"  ✗ {dir_name} (不存在)")
    
    print("\n" + "="*50)
    
    # 测试1: 使用不同路径初始化 LinguaSQL
    print("\n--- 测试1: 不同路径初始化测试 ---")
    
    test_paths = [
        str(current_dir),  # 当前目录
        str(current_dir / "27fb8419-3b63-4973-a72b-6be68a1166b9"),  # 向量库目录1
        str(current_dir / "ae102e87-e644-4fee-899c-97d9d654fab2"),  # 向量库目录2
        str(current_dir / "d4f94d14-543b-42c0-80fb-e5ee4260efc6"),  # 向量库目录3
    ]
    
    for i, test_path in enumerate(test_paths, 1):
        print(f"\n测试路径 {i}: {test_path}")
        try:
            from lingua_sql import LinguaSQL
            from lingua_sql.config import LinguaSQLConfig, DatabaseConfig, APIConfig
            
            # 创建测试配置
            config = LinguaSQLConfig(
                api=APIConfig(
                    api_key="test_key",
                    model="deepseek-chat",
                    client="persistent",
                    path=test_path,
                ),
                database=DatabaseConfig(
                    type="mysql",
                    host="localhost",
                    port=3306,
                    user="test",
                    password="test",
                    database="test",
                    auto_connect=False,  # 不连接数据库
                    auto_import_ddl=False,
                ),
                debug=False
            )
            
            # 尝试初始化
            nl = LinguaSQL(config=config)
            print(f"  ✓ 初始化成功")
            
            # 检查向量存储是否可用
            if hasattr(nl, 'ddl_collection') and nl.ddl_collection:
                print(f"  ✓ 向量存储可用")
                
                # 尝试获取集合信息
                try:
                    ddl_info = nl.ddl_collection.get()
                    if ddl_info and 'ids' in ddl_info:
                        print(f"  ✓ DDL集合包含 {len(ddl_info['ids'])} 条记录")
                    else:
                        print(f"  ⚠ DDL集合为空或无法访问")
                except Exception as e:
                    print(f"  ✗ 访问DDL集合失败: {e}")
            else:
                print(f"  ✗ 向量存储不可用")
                
        except Exception as e:
            print(f"  ✗ 初始化失败: {e}")
    
    print("\n" + "="*50)
    
    # 测试2: 数据迁移测试
    print("\n--- 测试2: 数据迁移测试 ---")
    
    try:
        # 创建临时测试目录
        temp_dir = current_dir / "temp_test_vector_store"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir()
        
        print(f"创建临时测试目录: {temp_dir}")
        
        # 复制一个向量库目录到临时目录
        source_dir = current_dir / "27fb8419-3b63-4973-a72b-6be68a1166b9"
        if source_dir.exists():
            # 复制文件
            for file_name in ["data_level0.bin", "header.bin", "length.bin", "link_lists.bin"]:
                source_file = source_dir / file_name
                target_file = temp_dir / file_name
                if source_file.exists():
                    shutil.copy2(source_file, target_file)
                    print(f"  ✓ 复制 {file_name}")
                else:
                    print(f"  ✗ 源文件 {file_name} 不存在")
            
            # 测试使用临时目录初始化
            print(f"\n测试使用临时目录初始化...")
            try:
                config = LinguaSQLConfig(
                    api=APIConfig(
                        api_key="test_key",
                        model="deepseek-chat",
                        client="persistent",
                        path=str(temp_dir),
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
                
                nl_temp = LinguaSQL(config=config)
                print(f"  ✓ 临时目录初始化成功")
                
                # 检查数据是否可访问
                if hasattr(nl_temp, 'ddl_collection') and nl_temp.ddl_collection:
                    ddl_info = nl_temp.ddl_collection.get()
                    if ddl_info and 'ids' in ddl_info:
                        print(f"  ✓ 临时目录数据可访问，包含 {len(ddl_info['ids'])} 条记录")
                    else:
                        print(f"  ⚠ 临时目录数据为空")
                else:
                    print(f"  ✗ 临时目录向量存储不可用")
                    
            except Exception as e:
                print(f"  ✗ 临时目录初始化失败: {e}")
        
        # 清理临时目录
        shutil.rmtree(temp_dir)
        print(f"\n清理临时测试目录: {temp_dir}")
        
    except Exception as e:
        print(f"数据迁移测试失败: {e}")
    
    print("\n" + "="*50)
    
    # 测试3: 跨目录数据访问测试
    print("\n--- 测试3: 跨目录数据访问测试 ---")
    
    try:
        # 尝试使用一个目录初始化，然后访问另一个目录的数据
        print("测试跨目录数据访问...")
        
        # 使用第一个目录初始化
        config1 = LinguaSQLConfig(
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
        
        nl1 = LinguaSQL(config=config1)
        print(f"  ✓ 使用目录1初始化成功")
        
        # 检查目录1的数据
        if hasattr(nl1, 'ddl_collection') and nl1.ddl_collection:
            ddl_info1 = nl1.ddl_collection.get()
            if ddl_info1 and 'ids' in ddl_info1:
                print(f"  ✓ 目录1包含 {len(ddl_info1['ids'])} 条DDL记录")
            else:
                print(f"  ⚠ 目录1数据为空")
        
        # 使用第二个目录初始化
        config2 = LinguaSQLConfig(
            api=APIConfig(
                api_key="test_key",
                model="deepseek-chat",
                client="persistent",
                path=str(current_dir / "ae102e87-e644-4fee-899c-97d9d654fab2"),
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
        print(f"  ✓ 使用目录2初始化成功")
        
        # 检查目录2的数据
        if hasattr(nl2, 'ddl_collection') and nl2.ddl_collection:
            ddl_info2 = nl2.ddl_collection.get()
            if ddl_info2 and 'ids' in ddl_info2:
                print(f"  ✓ 目录2包含 {len(ddl_info2['ids'])} 条DDL记录")
            else:
                print(f"  ⚠ 目录2数据为空")
        
        # 比较两个目录的数据
        if 'ddl_info1' in locals() and 'ddl_info2' in locals():
            if ddl_info1 and ddl_info2:
                if len(ddl_info1.get('ids', [])) == len(ddl_info2.get('ids', [])):
                    print(f"  ✓ 两个目录包含相同数量的记录")
                else:
                    print(f"  ⚠ 两个目录记录数量不同: 目录1={len(ddl_info1.get('ids', []))}, 目录2={len(ddl_info2.get('ids', []))}")
            else:
                print(f"  ⚠ 无法比较数据")
        
    except Exception as e:
        print(f"跨目录数据访问测试失败: {e}")
    
    print("\n" + "="*50)
    
    # 测试4: 数据完整性测试
    print("\n--- 测试4: 数据完整性测试 ---")
    
    try:
        # 检查 ChromaDB 数据库文件
        chroma_db_file = current_dir / "chroma.sqlite3"
        if chroma_db_file.exists():
            size = chroma_db_file.stat().st_size
            print(f"ChromaDB 数据库文件: {chroma_db_file}")
            print(f"  大小: {size} bytes ({size/1024/1024:.2f} MB)")
            
            if size > 0:
                print(f"  ✓ 数据库文件正常")
            else:
                print(f"  ⚠ 数据库文件为空")
        else:
            print(f"  ✗ ChromaDB 数据库文件不存在")
        
        # 检查向量库目录的完整性
        for dir_name in vector_dirs:
            dir_path = current_dir / dir_name
            if dir_path.exists():
                print(f"\n检查目录: {dir_name}")
                
                # 检查必要文件
                required_files = ["data_level0.bin", "header.bin", "length.bin"]
                missing_files = []
                
                for file_name in required_files:
                    file_path = dir_path / file_name
                    if file_path.exists():
                        size = file_path.stat().st_size
                        print(f"  ✓ {file_name}: {size} bytes")
                        if size == 0:
                            print(f"    ⚠ 文件大小为0")
                    else:
                        print(f"  ✗ {file_name}: 缺失")
                        missing_files.append(file_name)
                
                if not missing_files:
                    print(f"  ✓ 目录 {dir_name} 完整")
                else:
                    print(f"  ✗ 目录 {dir_name} 缺少文件: {missing_files}")
        
    except Exception as e:
        print(f"数据完整性测试失败: {e}")
    
    print("\n" + "="*50)
    
    # 总结
    print("\n--- 测试总结 ---")
    print("✓ 向量库目录结构检查完成")
    print("✓ 不同路径初始化测试完成")
    print("✓ 数据迁移测试完成")
    print("✓ 跨目录数据访问测试完成")
    print("✓ 数据完整性测试完成")
    print("\n🎯 测试完成！请查看上述结果了解向量库的通用性。")

if __name__ == "__main__":
    test_vector_store_compatibility()
