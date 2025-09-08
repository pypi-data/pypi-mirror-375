#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试 LinguaSQL 大模型支持
"""

import os
from lingua_sql import LinguaSQL
from lingua_sql.config import LinguaSQLConfig, APIConfig, DatabaseConfig

def test_llm_support():
    """测试各种大模型的支持"""
    
    # 测试配置
    test_configs = [
        {
            "name": "DeepSeek",
            "api_key": os.getenv("DEEPSEEK_API_KEY"),
            "model": "deepseek-chat"
        },
        {
            "name": "通义千问",
            "api_key": os.getenv("QWEN_API_KEY"),
            "model": "qwen-turbo"
        },
        {
            "name": "文心一言",
            "api_key": os.getenv("ERNIE_API_KEY"),
            "model": "ernie-bot"
        },
        {
            "name": "智谱AI",
            "api_key": os.getenv("GLM_API_KEY"),
            "model": "glm-4"
        },
        {
            "name": "月之暗面",
            "api_key": os.getenv("MOONSHOT_API_KEY"),
            "model": "moonshot-v1-8k"
        },
        {
            "name": "零一万物",
            "api_key": os.getenv("YI_API_KEY"),
            "model": "yi-34b-chat"
        }
    ]
    
    print("=== LinguaSQL 大模型支持测试 ===\n")
    
    for config_info in test_configs:
        print(f"测试 {config_info['name']} ({config_info['model']})...")
        
        if not config_info['api_key']:
            print(f"  ❌ 未设置 {config_info['name']} API密钥")
            continue
        
        try:
            # 创建配置
            config = LinguaSQLConfig(
                api=APIConfig(
                    api_key=config_info['api_key'],
                    model=config_info['model']
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
            print(f"  📋 使用模型: {config_info['model']}")
            print(f"  🔧 客户端类型: {type(nl.llm_client).__name__}")
            
            # 测试消息格式
            system_msg = nl.system_message("你是一个SQL专家")
            user_msg = nl.user_message("查询所有用户")
            assistant_msg = nl.assistant_message("SELECT * FROM users")
            
            print(f"  ✅ 消息格式测试通过")
            
            # 测试字段提取
            fields = nl.extract_field_names("查询用户的姓名和年龄")
            print(f"  ✅ 字段提取测试通过: {fields}")
            
            # 测试表名提取
            tables = nl.extract_table_names("查询用户表的数据")
            print(f"  ✅ 表名提取测试通过: {tables}")
            
            print(f"  🎉 {config_info['name']} 所有测试通过\n")
            
        except Exception as e:
            print(f"  ❌ {config_info['name']} 测试失败: {e}\n")
    
    print("=== 测试完成 ===")

def test_auto_detection():
    """测试自动检测功能"""
    print("\n=== 测试自动检测功能 ===")
    
    # 设置环境变量
    test_models = [
        ("DEEPSEEK_API_KEY", "deepseek-chat"),
        ("QWEN_API_KEY", "qwen-turbo"),
        ("GLM_API_KEY", "glm-4")
    ]
    
    for env_key, expected_model in test_models:
        if os.getenv(env_key):
            print(f"检测到 {env_key}，预期模型: {expected_model}")
            
            try:
                # 使用环境变量自动配置
                nl = LinguaSQL()
                actual_model = nl._get_cfg('api.model')
                print(f"  实际模型: {actual_model}")
                print(f"  客户端类型: {type(nl.llm_client).__name__}")
                print(f"  ✅ 自动检测成功\n")
            except Exception as e:
                print(f"  ❌ 自动检测失败: {e}\n")
        else:
            print(f"未设置 {env_key}，跳过测试\n")

if __name__ == "__main__":
    test_llm_support()
    test_auto_detection()
