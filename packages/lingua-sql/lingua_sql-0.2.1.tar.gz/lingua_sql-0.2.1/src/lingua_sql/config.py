#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LinguaSQL 配置文件
包含智能训练、数据库连接等配置参数
"""

import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class APIConfig:
    """API配置"""
    api_key: Optional[str] = None
    model: str = "deepseek-chat"
    client: str = "persistent"
    path: str = "."
    
    # 支持的大模型列表
    SUPPORTED_MODELS = {
        # DeepSeek
        "deepseek-chat": "deepseek",
        "deepseek-coder": "deepseek",
        
        # 通义千问 (Qwen)
        "qwen-turbo": "qwen",
        "qwen-plus": "qwen",
        "qwen-max": "qwen",
        "qwen-long": "qwen",
        
        # 文心一言 (ERNIE)
        "ernie-bot": "ernie",
        "ernie-bot-turbo": "ernie",
        "ernie-bot-4": "ernie",
        
        # 智谱AI (GLM)
        "glm-4": "glm",
        "glm-4-flash": "glm",
        "glm-3-turbo": "glm",
        
        # 月之暗面 (Moonshot)
        "moonshot-v1-8k": "moonshot",
        "moonshot-v1-32k": "moonshot",
        "moonshot-v1-128k": "moonshot",
        
        # 零一万物 (Yi)
        "yi-34b-chat": "yi",
        "yi-6b-chat": "yi",
    }
    
    @classmethod
    def get_provider(cls, model: str) -> str:
        """根据模型名称获取提供商"""
        return cls.SUPPORTED_MODELS.get(model, "deepseek")


@dataclass
class VectorStoreConfig:
    """向量数据库配置"""
    type: str = "chromadb"  # chromadb, faiss
    path: str = "."
    client: str = "persistent"  # persistent, in-memory
    embedding_model: Optional[str] = None  # 嵌入模型名称
    n_results_sql: int = 10
    n_results_ddl: int = 10
    n_results_documentation: int = 10
    
    # 支持的向量数据库列表
    SUPPORTED_VECTOR_STORES = {
        "chromadb": "chromadb",
        "faiss": "faiss",
    }
    
    @classmethod
    def get_provider(cls, vector_store_type: str) -> str:
        """根据向量数据库类型获取提供商"""
        return cls.SUPPORTED_VECTOR_STORES.get(vector_store_type, "chromadb")


@dataclass
class IntelligentTrainingConfig:
    """智能训练配置"""
    enabled: bool = True
    max_questions_per_table: int = 10
    max_related_fields: int = 3
    questions_per_field: int = 10  # 每个关联字段生成的问题数
    min_field_frequency: int = 2  # 最小字段使用频率
    question_types: List[str] = field(default_factory=lambda: [
        'basic_query', 'aggregation', 'join_query', 'conditional_query'
    ])
    difficulty_levels: List[str] = field(default_factory=lambda: [
        'easy', 'medium', 'hard'
    ])
    difficulty_distribution: Dict[str, float] = field(default_factory=lambda: {
        'easy': 0.6,      # 60% 简单
        'medium': 0.3,    # 30% 中等
        'hard': 0.1       # 10% 困难
    })
    auto_generate_sql: bool = True
    use_sample_data: bool = True
    use_llm_generation: bool = True  # 使用大模型生成
    max_sample_records: int = 5
    auto_execute_training: bool = True
    show_training_progress: bool = True
    interactive_confirmation: bool = False


@dataclass
class DatabaseConfig:
    """数据库配置"""
    type: str = "mysql"
    host: str = "localhost"
    port: int = 3306
    user: str = "root"
    password: str = ""
    database: str = ""
    connection_string: Optional[str] = None
    auto_connect: bool = True
    auto_import_ddl: bool = False


@dataclass
class LinguaSQLConfig:
    """LinguaSQL 主配置"""
    api: APIConfig = field(default_factory=APIConfig)
    vector_store: VectorStoreConfig = field(default_factory=VectorStoreConfig)
    intelligent_training: IntelligentTrainingConfig = field(default_factory=IntelligentTrainingConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    debug: bool = False
    
    @classmethod
    def from_env(cls) -> 'LinguaSQLConfig':
        """从环境变量创建配置"""
        config = cls()
        
        # 从环境变量读取API配置
        # 支持多种大模型的API密钥
        api_keys = {
            'DEEPSEEK_API_KEY': 'deepseek',
            'QWEN_API_KEY': 'qwen',
            'ERNIE_API_KEY': 'ernie',
            'GLM_API_KEY': 'glm',
            'MOONSHOT_API_KEY': 'moonshot',
            'YI_API_KEY': 'yi',
        }
        
        # 检查是否有API密钥
        for env_key, provider in api_keys.items():
            if os.getenv(env_key):
                config.api.api_key = os.getenv(env_key)
                # 根据API密钥类型设置默认模型
                if provider == 'deepseek':
                    config.api.model = "deepseek-chat"
                elif provider == 'qwen':
                    config.api.model = "qwen-turbo"
                elif provider == 'ernie':
                    config.api.model = "ernie-bot"
                elif provider == 'glm':
                    config.api.model = "glm-4"
                elif provider == 'moonshot':
                    config.api.model = "moonshot-v1-8k"
                elif provider == 'yi':
                    config.api.model = "yi-34b-chat"
                break
        
        # 从环境变量读取模型配置
        if os.getenv('LINGUA_SQL_MODEL'):
            config.api.model = os.getenv('LINGUA_SQL_MODEL')
        
        # 从环境变量读取向量数据库配置
        if os.getenv('LINGUA_SQL_VECTOR_STORE'):
            config.vector_store.type = os.getenv('LINGUA_SQL_VECTOR_STORE')
        if os.getenv('LINGUA_SQL_VECTOR_STORE_PATH'):
            config.vector_store.path = os.getenv('LINGUA_SQL_VECTOR_STORE_PATH')
        if os.getenv('LINGUA_SQL_EMBEDDING_MODEL'):
            config.vector_store.embedding_model = os.getenv('LINGUA_SQL_EMBEDDING_MODEL')
        
        if os.getenv('LINGUA_SQL_INTELLIGENT_TRAINING_ENABLED'):
            config.intelligent_training.enabled = os.getenv('LINGUA_SQL_INTELLIGENT_TRAINING_ENABLED').lower() == 'true'
        if os.getenv('LINGUA_SQL_INTELLIGENT_TRAINING_INTERACTIVE'):
            config.intelligent_training.interactive_confirmation = os.getenv('LINGUA_SQL_INTELLIGENT_TRAINING_INTERACTIVE').lower() == 'true'
        
        return config


def create_config() -> LinguaSQLConfig:
    """创建配置实例"""
    return LinguaSQLConfig.from_env()
