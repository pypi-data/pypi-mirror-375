#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能训练提示词
用于生成数据库训练问答对
"""

# 系统提示词 - 智能训练问答对生成
INTELLIGENT_TRAINING_SYSTEM_PROMPT = """你是一个专业的数据库训练数据生成专家。你的任务是根据数据库表结构信息，生成高质量的问答对用于训练自然语言转SQL模型。

## 你的职责
1. 分析表结构和关联关系
2. 生成多样化的自然语言问题
3. 提供准确的SQL查询语句
4. 确保问题的泛化能力和实用性

## 生成要求
- 问题要自然、多样化，避免重复
- SQL语句要准确、高效
- 问题要具有泛化能力，适用于任何具有类似结构的数据库
- 不要使用具体的字段名或表名，使用自然语言描述

## 输出格式
严格按照JSON格式返回，不要包含任何解释说明。"""

# 用户提示词 - 生成训练问答对
INTELLIGENT_TRAINING_USER_PROMPT = """请为表 {table_name} 生成训练问答对。

=== 表结构信息 ===
{table_info}

=== 表关联关系 ===
{relationships}

=== 表文档说明 ===
{table_comment}

=== 关联字段（用于查询条件）===
{related_fields}

=== 样本值 ===
{sample_values}

=== 生成要求 ===
1. 为每个关联字段生成{questions_per_field}个问题，总共{total_questions}个问题
2. 问题类型包括：基础查询、聚合查询、关联查询、条件查询
3. 难度分布：简单({easy_percent}%)、中等({medium_percent}%)、困难({hard_percent}%)
4. 每个问题都要有对应的SQL语句
5. 问题要自然、多样化，避免重复
6. 额外随机生成10个可能常用的业务问题（不限制关联字段）
7. 返回JSON格式，不要任何解释说明

=== 重要约束 ===
- 生成的问题中不要出现具体的字段名（如id、name、code等）
- 生成的问题中不要出现具体的表名（如user、order、product等）
- 使用自然语言描述，如"编号"、"名称"、"代码"等
- 问题要具有泛化能力，适用于任何具有类似结构的数据库

=== 额外问题生成指导 ===
- 额外生成10个常用业务问题，不限制使用特定关联字段
- 这些问题应该涵盖常见的业务场景和查询需求
- 可以包括但不限于：统计分析、趋势分析、排名查询、条件筛选等
- 问题应该实用、贴近真实业务需求
- 难度可以灵活分布，重点考虑实用性

=== 返回格式 ===
{{
    "questions": [
        {{
            "question": "问题内容",
            "sql": "SQL语句",
            "question_type": "问题类型",
            "difficulty": "难度"
        }}
    ]
}}

请严格按照上述要求生成问题，确保每个关联字段都有{questions_per_field}个问题，总共{total_questions}个问题，并额外生成10个常用业务问题。"""

# 问题类型模板
QUESTION_TYPE_TEMPLATES = {
    "basic_query": {
        "name": "基础查询",
        "description": "简单的单表查询，如查询特定条件的记录"
    },
    "aggregation": {
        "name": "聚合查询", 
        "description": "使用聚合函数的查询，如统计、平均值、最大值等"
    },
    "join_query": {
        "name": "关联查询",
        "description": "涉及多表关联的查询，如JOIN操作"
    },
    "conditional_query": {
        "name": "条件查询",
        "description": "包含复杂条件的查询，如范围、模糊匹配等"
    }
}

# 难度级别模板
DIFFICULTY_TEMPLATES = {
    "easy": {
        "name": "简单",
        "description": "基础的单表查询，条件简单",
        "percentage": 60
    },
    "medium": {
        "name": "中等", 
        "description": "涉及条件组合或简单聚合的查询",
        "percentage": 30
    },
    "hard": {
        "name": "困难",
        "description": "复杂的多表关联或高级聚合查询",
        "percentage": 10
    }
}

# 字段类型映射（用于生成自然语言描述）
FIELD_TYPE_MAPPING = {
    "varchar": "文本",
    "int": "整数",
    "decimal": "小数",
    "datetime": "日期时间",
    "date": "日期",
    "time": "时间",
    "text": "长文本",
    "char": "固定长度文本",
    "bigint": "大整数",
    "float": "浮点数",
    "double": "双精度浮点数"
}

# 常见字段名映射（用于生成自然语言描述）
# 这个映射现在是空的，由大模型动态生成，不依赖硬编码
COMMON_FIELD_MAPPING = {}

# 问题生成提示词模板
# 这些模板现在是空的，由大模型动态生成，不依赖硬编码
QUESTION_GENERATION_TEMPLATES = {}

# SQL生成模板
# 这些模板现在是空的，由大模型动态生成，不依赖硬编码
SQL_GENERATION_TEMPLATES = {}

# 验证提示词
VALIDATION_PROMPT = """请验证以下生成的问答对是否符合要求：

1. 问题数量是否正确（{expected_count}个）
2. 难度分布是否合理（简单{easy_percent}%、中等{medium_percent}%、困难{hard_percent}%）
3. 问题是否自然、多样化
4. SQL语句是否准确、可执行
5. 是否避免了具体的字段名和表名

如果发现问题，请指出并给出修改建议。"""

# 优化提示词
OPTIMIZATION_PROMPT = """请优化以下生成的问答对：

1. 提高问题的自然性和多样性
2. 确保SQL语句的准确性和效率
3. 调整难度分布，使其更合理
4. 增强问题的泛化能力
5. 确保每个关联字段都有足够的问题

请返回优化后的完整JSON格式。"""
