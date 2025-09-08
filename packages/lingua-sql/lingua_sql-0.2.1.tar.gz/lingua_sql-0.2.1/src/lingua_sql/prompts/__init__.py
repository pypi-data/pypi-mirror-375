#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能训练提示词包
包含用于生成数据库训练问答对的提示词和配置
"""

from .intelligent_training_prompts import (
    INTELLIGENT_TRAINING_SYSTEM_PROMPT,
    INTELLIGENT_TRAINING_USER_PROMPT,
    QUESTION_TYPE_TEMPLATES,
    DIFFICULTY_TEMPLATES,
    FIELD_TYPE_MAPPING,
    COMMON_FIELD_MAPPING,
    QUESTION_GENERATION_TEMPLATES,
    SQL_GENERATION_TEMPLATES,
    VALIDATION_PROMPT,
    OPTIMIZATION_PROMPT
)

from .training_config import (
    IntelligentTrainingConfig,
    QuestionGenerationConfig,
    SQLGenerationConfig,
    DEFAULT_INTELLIGENT_TRAINING_CONFIG,
    DEFAULT_QUESTION_GENERATION_CONFIG,
    DEFAULT_SQL_GENERATION_CONFIG,
    create_training_config,
    validate_config,
    CONFIG_TEMPLATES
)

__all__ = [
    # 提示词
    "INTELLIGENT_TRAINING_SYSTEM_PROMPT",
    "INTELLIGENT_TRAINING_USER_PROMPT",
    "QUESTION_TYPE_TEMPLATES",
    "DIFFICULTY_TEMPLATES",
    "FIELD_TYPE_MAPPING",
    "COMMON_FIELD_MAPPING",
    "QUESTION_GENERATION_TEMPLATES",
    "SQL_GENERATION_TEMPLATES",
    "VALIDATION_PROMPT",
    "OPTIMIZATION_PROMPT",
    
    # 配置类
    "IntelligentTrainingConfig",
    "QuestionGenerationConfig", 
    "SQLGenerationConfig",
    
    # 配置实例
    "DEFAULT_INTELLIGENT_TRAINING_CONFIG",
    "DEFAULT_QUESTION_GENERATION_CONFIG",
    "DEFAULT_SQL_GENERATION_CONFIG",
    
    # 配置函数
    "create_training_config",
    "validate_config",
    "CONFIG_TEMPLATES"
]

# 版本信息
__version__ = "1.0.0"
__author__ = "LinguaSQL Team"
__description__ = "智能训练提示词和配置包"
