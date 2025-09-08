#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能训练配置文件
包含默认参数和配置选项
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class IntelligentTrainingConfig:
    """智能训练配置"""
    # 关联字段和问题数量配置
    max_related_fields: int = 3  # 默认选择3个关联字段
    questions_per_field: int = 10  # 每个字段生成10个问题
    total_questions: int = 30  # 总问题数 = max_related_fields × questions_per_field
    
    # 难度分布配置
    difficulty_distribution: Dict[str, float] = field(default_factory=lambda: {
        "easy": 0.60,      # 简单问题占60%
        "medium": 0.30,    # 中等问题占30%
        "hard": 0.10       # 困难问题占10%
    })
    
    # 问题类型配置
    question_types: List[str] = field(default_factory=lambda: [
        "basic_query",      # 基础查询
        "aggregation",      # 聚合查询
        "join_query",       # 关联查询
        "conditional_query" # 条件查询
    ])
    
    # 字段选择策略
    field_selection_strategy: str = "relationship_based"  # 基于关联关系选择字段
    min_field_frequency: int = 2  # 最小字段使用频率
    prefer_primary_keys: bool = True  # 优先选择主键
    prefer_foreign_keys: bool = True  # 优先选择外键
    
    # 问题生成配置
    use_llm_generation: bool = True  # 使用大模型生成问题
    enable_generalization: bool = True  # 启用泛化模式
    avoid_specific_names: bool = True  # 避免使用具体的字段名和表名
    use_natural_language: bool = True  # 使用自然语言描述
    
    # 质量控制配置
    validate_generated_questions: bool = True  # 验证生成的问题
    optimize_question_distribution: bool = True  # 优化问题分布
    ensure_diversity: bool = True  # 确保问题多样性
    
    # 输出格式配置
    output_format: str = "json"  # 输出格式
    include_metadata: bool = True  # 包含元数据
    include_explanations: bool = False  # 包含解释说明

@dataclass
class QuestionGenerationConfig:
    """问题生成配置"""
    # 问题模板配置
    use_templates: bool = True  # 使用问题模板
    template_variation: float = 0.3  # 模板变化程度
    
    # 语言配置
    language: str = "zh"  # 默认中文
    formal_style: bool = True  # 正式风格
    
    # 复杂度配置
    min_question_length: int = 10  # 最小问题长度
    max_question_length: int = 50  # 最大问题长度
    
    # 内容配置
    include_context: bool = True  # 包含上下文信息
    use_synonyms: bool = True  # 使用同义词

@dataclass
class SQLGenerationConfig:
    """SQL生成配置"""
    # SQL类型配置
    sql_dialect: str = "mysql"  # SQL方言
    use_standard_sql: bool = True  # 使用标准SQL
    
    # 性能配置
    optimize_for_performance: bool = True  # 优化性能
    use_indexes: bool = True  # 使用索引
    
    # 安全配置
    prevent_sql_injection: bool = True  # 防止SQL注入
    use_parameterized_queries: bool = True  # 使用参数化查询
    
    # 可读性配置
    format_sql: bool = True  # 格式化SQL
    add_comments: bool = False  # 添加注释

# 默认配置实例
DEFAULT_INTELLIGENT_TRAINING_CONFIG = IntelligentTrainingConfig()
DEFAULT_QUESTION_GENERATION_CONFIG = QuestionGenerationConfig()
DEFAULT_SQL_GENERATION_CONFIG = SQLGenerationConfig()

# 配置验证函数
def validate_config(config: IntelligentTrainingConfig) -> bool:
    """验证配置参数"""
    try:
        # 验证关联字段数量
        if config.max_related_fields <= 0:
            raise ValueError("max_related_fields 必须大于0")
        
        # 验证每个字段的问题数量
        if config.questions_per_field <= 0:
            raise ValueError("questions_per_field 必须大于0")
        
        # 验证总问题数
        expected_total = config.max_related_fields * config.questions_per_field
        if config.total_questions != expected_total:
            raise ValueError(f"total_questions 应该等于 {expected_total}")
        
        # 验证难度分布
        total_percentage = sum(config.difficulty_distribution.values())
        if abs(total_percentage - 1.0) > 0.01:  # 允许0.01的误差
            raise ValueError("难度分布百分比总和应该等于100%")
        
        return True
        
    except Exception as e:
        print(f"配置验证失败: {e}")
        return False

# 配置工厂函数
def create_training_config(
    max_related_fields: int = 3,
    questions_per_field: int = 10,
    difficulty_distribution: Dict[str, float] = None,
    **kwargs
) -> IntelligentTrainingConfig:
    """创建训练配置"""
    config = IntelligentTrainingConfig()
    
    # 设置基本参数
    config.max_related_fields = max_related_fields
    config.questions_per_field = questions_per_field
    config.total_questions = max_related_fields * questions_per_field
    
    # 设置难度分布
    if difficulty_distribution:
        config.difficulty_distribution = difficulty_distribution
    
    # 设置其他参数
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    # 验证配置
    if not validate_config(config):
        raise ValueError("配置参数无效")
    
    return config

# 预定义配置模板
CONFIG_TEMPLATES = {
    "default": DEFAULT_INTELLIGENT_TRAINING_CONFIG,
    "balanced": create_training_config(
        max_related_fields=3,
        questions_per_field=10,
        difficulty_distribution={"easy": 0.50, "medium": 0.35, "hard": 0.15}
    ),
    "beginner": create_training_config(
        max_related_fields=2,
        questions_per_field=8,
        difficulty_distribution={"easy": 0.70, "medium": 0.25, "hard": 0.05}
    ),
    "advanced": create_training_config(
        max_related_fields=5,
        questions_per_field=12,
        difficulty_distribution={"easy": 0.40, "medium": 0.40, "hard": 0.20}
    )
}
