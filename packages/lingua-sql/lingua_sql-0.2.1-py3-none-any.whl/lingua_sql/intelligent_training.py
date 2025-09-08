#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能训练模块
实现基于数据库关联关系的自动问答对生成
具有泛化能力，不依赖特定数据库结构
"""

import random
import logging
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import re

# 提示词模板将在类初始化时导入

logger = logging.getLogger(__name__)


@dataclass
class TableField:
    """表字段信息"""
    name: str
    data_type: str
    comment: str
    is_primary: bool = False
    is_foreign: bool = False
    is_unique: bool = False
    nullable: bool = True
    usage_frequency: int = 0  # 字段在数据库中的使用频率


@dataclass
class TableRelationship:
    """表关联关系"""
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    constraint_name: str


@dataclass
class TrainingQuestion:
    """训练问题"""
    question: str
    sql: str
    table: str
    question_type: str
    difficulty: str = "medium"


@dataclass
class IntelligentTrainingConfig:
    """智能训练配置"""
    max_questions_per_table: int = 30  # 每个表最多30个问题（3个关联字段 × 10个问题）
    max_related_fields: int = 3  # 最多选择3个关联字段
    questions_per_field: int = 10  # 每个关联字段生成的问题数量
    total_questions: int = 30  # 总问题数量
    difficulty_distribution: Dict[str, float] = field(default_factory=lambda: {
        "easy": 0.60,      # 简单60%
        "medium": 0.30,    # 中等30%
        "hard": 0.10       # 困难10%
    })
    question_types: List[str] = field(default_factory=lambda: [
        'basic_query', 'aggregation', 'join_query', 'conditional_query'
    ])
    difficulty_levels: List[str] = field(default_factory=lambda: [
        'easy', 'medium', 'hard'
    ])
    auto_generate_sql: bool = True
    use_sample_data: bool = True
    max_sample_records: int = 5
    enable_generalization: bool = True  # 启用泛化模式
    min_field_frequency: int = 2  # 最小字段使用频率
    use_llm_generation: bool = True  # 使用大模型生成问答对


class IntelligentTrainer:
    """智能训练器"""
    
    def __init__(self, config: IntelligentTrainingConfig = None):
        self.config = config or IntelligentTrainingConfig()
        self._validate_config()
        self.question_templates = self._init_question_templates()
        self.sql_templates = self._init_sql_templates()
        self.field_mapping = self._init_field_mapping()
        
        # 导入提示词模板
        try:
            from .prompts.intelligent_training_prompts import (
                INTELLIGENT_TRAINING_SYSTEM_PROMPT,
                INTELLIGENT_TRAINING_USER_PROMPT
            )
            self.USE_PROMPT_TEMPLATES = True
            self.INTELLIGENT_TRAINING_SYSTEM_PROMPT = INTELLIGENT_TRAINING_SYSTEM_PROMPT
            self.INTELLIGENT_TRAINING_USER_PROMPT = INTELLIGENT_TRAINING_USER_PROMPT
        except ImportError:
            self.USE_PROMPT_TEMPLATES = False
            self.INTELLIGENT_TRAINING_SYSTEM_PROMPT = "你是一个专业的数据库训练问题生成专家。请根据提供的表结构信息生成高质量的问答对。请严格按照要求的JSON格式返回，不要添加任何解释说明。"
            self.INTELLIGENT_TRAINING_USER_PROMPT = "请根据表结构生成训练问答对。"
        
        # 初始化统计信息
        self.stats = {
            'total_tables_processed': 0,
            'total_questions_generated': 0,
            'successful_llm_calls': 0,
            'failed_llm_calls': 0,
            'fallback_to_templates': 0
        }
    
    def _validate_config(self):
        """验证配置参数"""
        if self.config.max_questions_per_table <= 0:
            raise ValueError("max_questions_per_table 必须大于0")
        
        if self.config.max_related_fields <= 0:
            raise ValueError("max_related_fields 必须大于0")
        
        if self.config.max_questions_per_table < self.config.max_related_fields:
            raise ValueError("max_questions_per_table 必须大于等于 max_related_fields")
        
        if not self.config.question_types:
            raise ValueError("question_types 不能为空")
        
        if not self.config.difficulty_levels:
            raise ValueError("difficulty_levels 不能为空")
    
    def _init_field_mapping(self) -> Dict[str, str]:
        """初始化字段映射 - 动态生成，不依赖硬编码"""
        # 字段映射现在由大模型动态生成，基于DDL和文档内容
        return {}
    
    def _init_question_templates(self) -> Dict[str, List[str]]:
        """初始化问题模板 - 动态生成，不依赖硬编码"""
        # 问题模板现在由大模型动态生成，基于表结构和业务逻辑
        return {}
    
    def _init_sql_templates(self) -> Dict[str, str]:
        """初始化SQL模板 - 动态生成，不依赖硬编码"""
        # SQL模板现在由大模型动态生成，基于表结构和业务逻辑
        return {}
    
    def analyze_table_structure(self, table_schema: List[Dict[str, Any]]) -> List[TableField]:
        """分析表结构，提取字段信息"""
        fields = []
        for column in table_schema:
            field = TableField(
                name=column['COLUMN_NAME'],
                data_type=column['DATA_TYPE'],
                comment=column['COLUMN_COMMENT'] or column['COLUMN_NAME'],
                is_primary=column['COLUMN_KEY'] == 'PRI',
                is_foreign=column['COLUMN_KEY'] == 'MUL',
                is_unique=column['COLUMN_KEY'] == 'UNI',
                nullable=column['IS_NULLABLE'] == 'YES'
            )
            fields.append(field)
        return fields
    
    def find_common_identifier_fields(self, all_tables_fields: Dict[str, List[TableField]]) -> List[str]:
        """找出所有表都在使用的通用标识字段"""
        if not all_tables_fields:
            return []
        
        # 统计每个字段在多少个表中出现
        field_usage = {}
        total_tables = len(all_tables_fields)
        
        for table_name, fields in all_tables_fields.items():
            for field in fields:
                field_name = field.name.lower()
                if field_name not in field_usage:
                    field_usage[field_name] = set()
                field_usage[field_name].add(table_name)
        
        # 找出在多个表中都出现的字段
        common_fields = []
        for field_name, tables in field_usage.items():
            frequency = len(tables)
            if frequency >= self.config.min_field_frequency and frequency >= total_tables * 0.3:  # 至少30%的表都有
                common_fields.append(field_name)
                # 更新字段使用频率
                for table_name, fields in all_tables_fields.items():
                    for field in fields:
                        if field.name.lower() == field_name:
                            field.usage_frequency = frequency
        
        # 按使用频率排序
        common_fields.sort(key=lambda x: field_usage[x], reverse=True)
        return common_fields
    
    def find_key_fields(self, fields: List[TableField], common_identifiers: List[str] = None) -> Tuple[List[TableField], List[TableField]]:
        """找出关联字段（主键、外键、唯一键、通用标识字段）"""
        primary_fields = [f for f in fields if f.is_primary]
        key_fields = [f for f in fields if f.is_primary or f.is_foreign or f.is_unique]
        
        # 如果没有主键，使用通用标识字段
        if not primary_fields and common_identifiers:
            for identifier in common_identifiers:
                for field in fields:
                    if field.name.lower() == identifier.lower():
                        if field not in key_fields:
                            key_fields.append(field)
                        if not primary_fields:
                            primary_fields.append(field)
        
        # 如果还是没有，选择使用频率最高的字段
        if not primary_fields and key_fields:
            key_fields.sort(key=lambda x: x.usage_frequency, reverse=True)
            primary_fields = [key_fields[0]]
        
        return primary_fields, key_fields
    
    def generate_sample_values(self, field: TableField, db_connector, table_name: str) -> List[str]:
        """生成字段的样本值"""
        if not self.config.use_sample_data:
            return [f"sample_{field.name}_value"]
        
        try:
            # 限制查询数量避免性能问题
            limit = min(self.config.max_sample_records, 10)
            query = f"SELECT DISTINCT {field.name} FROM {table_name} WHERE {field.name} IS NOT NULL LIMIT {limit}"
            results = db_connector.run_sql(query)
            
            if results:
                return [str(row[field.name]) for row in results if row[field.name] is not None]
            else:
                return [f"sample_{field.name}_value"]
        except Exception as e:
            logger.warning(f"获取样本数据失败: {e}")
            return [f"sample_{field.name}_value"]
    
    def _prepare_llm_prompt(self, table_name: str, fields: List[TableField], 
                           key_fields: List[TableField], relationships: List[TableRelationship],
                           sample_values: Dict[str, List[str]], ddl_info: str = "", 
                           table_documentation: str = "") -> str:
        """准备发送给大模型的提示 - 使用我们的提示词模板"""
        
        # 构建表结构信息
        table_info = ""
        for field in fields:
            # 动态生成字段类型描述，不依赖硬编码
            field_type_parts = []
            if field.is_primary:
                field_type_parts.append("主键")
            if field.is_foreign:
                field_type_parts.append("外键")
            if field.is_unique:
                field_type_parts.append("唯一键")
            if not field.is_primary and not field.is_foreign and not field.is_unique:
                field_type_parts.append("普通字段")
            
            field_type = "、".join(field_type_parts) if field_type_parts else "字段"
            table_info += f"- {field.name} ({field.data_type}): {field.comment} [{field_type}]\n"
        
        # 构建关联字段信息
        related_fields = ""
        for field in key_fields:
            related_fields += f"- {field.name}: {field.comment}\n"
        
        # 构建关联关系信息
        relationships_info = ""
        if relationships:
            for rel in relationships:
                if rel.from_table == table_name or rel.to_table == table_name:
                    relationships_info += f"- {rel.from_table}.{rel.from_column} -> {rel.to_table}.{rel.to_column}\n"
        
        # 构建样本值信息
        sample_values_info = ""
        max_sample_values = getattr(self.config, 'max_sample_records', 5)  # 使用配置的样本值数量
        for field_name, values in sample_values.items():
            sample_values_info += f"- {field_name}: {', '.join(values[:max_sample_values])}\n"
        
        # 完全依赖我们的提示词模板
        # 计算配置参数
        questions_per_field = self.config.questions_per_field
        total_questions = len(key_fields) * questions_per_field
        easy_percent = int(self.config.difficulty_distribution["easy"] * 100)
        medium_percent = int(self.config.difficulty_distribution["medium"] * 100)
        hard_percent = int(self.config.difficulty_distribution["hard"] * 100)
        
        # 使用模板格式化提示词
        prompt = self.INTELLIGENT_TRAINING_USER_PROMPT.format(
            table_name=table_name,
            table_info=table_info,
            relationships=relationships_info,
            table_comment=table_documentation or "无",
            related_fields=related_fields,
            sample_values=sample_values_info,
            questions_per_field=questions_per_field,
            total_questions=total_questions,
            easy_percent=easy_percent,
            medium_percent=medium_percent,
            hard_percent=hard_percent
        )
        
        return prompt
    
    def _call_llm_for_questions(self, prompt: str, table_name: str = "") -> List[TrainingQuestion]:
        """调用大模型生成问答对"""
        try:
            # 直接使用DeepSeek API生成问答对
            import os
            import requests
            
            # 从环境变量获取API配置
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                logger.error("未找到DEEPSEEK_API_KEY环境变量")
                return []
            
            # 构建API请求
            api_url = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")  # 使用环境变量配置API URL
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # 构建消息
            messages = [
                {"role": "system", "content": self.INTELLIGENT_TRAINING_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
            
            data = {
                "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),  # 使用环境变量配置模型
                "messages": messages,
                "temperature": float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7")),  # 使用环境变量配置温度
                "max_tokens": int(os.getenv("DEEPSEEK_MAX_TOKENS", "2000"))  # 使用环境变量配置最大token数
            }
            
            # 调用DeepSeek API（增加超时时间，添加重试机制）
            logger.info(f"正在调用DeepSeek API为表 {table_name} 生成问答对...")
            
            # 重试机制
            max_retries = int(os.getenv("DEEPSEEK_MAX_RETRIES", "3"))  # 使用环境变量配置重试次数
            for attempt in range(max_retries):
                try:
                    timeout = int(os.getenv("DEEPSEEK_TIMEOUT", "60"))  # 使用环境变量配置超时时间
                    response = requests.post(api_url, headers=headers, json=data, timeout=timeout)
                    response.raise_for_status()
                    break
                except requests.exceptions.Timeout:
                    if attempt < max_retries - 1:
                        logger.warning(f"API调用超时，正在重试 ({attempt + 1}/{max_retries})...")
                        continue
                    else:
                        logger.error("API调用多次超时，放弃重试")
                        return []
                except requests.exceptions.RequestException as e:
                    logger.error(f"API请求失败: {e}")
                    return []
            
            result = response.json()
            llm_response = result["choices"][0]["message"]["content"]
            
            if not llm_response:
                logger.error("DeepSeek API返回空响应")
                return []
            
            # 显示大模型的回复
            print(f"\n=== 大模型回复（表 {table_name}）===")
            print(llm_response)
            print("=" * 80)
            
            # 解析API返回的JSON响应
            try:
                response_data = json.loads(llm_response)
                if "questions" in response_data:
                    questions = []
                    for q in response_data["questions"]:
                        question = TrainingQuestion(
                            question=q["question"],
                            sql=q["sql"],
                            table=table_name,
                            question_type=q["question_type"],
                            difficulty=q["difficulty"]
                        )
                        questions.append(question)
                    
                    logger.info(f"DeepSeek API为表 {table_name} 生成了 {len(questions)} 个问题")
                    print(f"✓ 成功解析大模型回复，生成了 {len(questions)} 个问题")
                    return questions
                else:
                    logger.error("API响应中未找到questions字段")
                    print(f"❌ API响应中未找到questions字段")
                    print(f"响应内容: {llm_response}")
                    return []
                    
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {e}")
                logger.error(f"原始响应: {llm_response}")
                print(f"❌ JSON解析失败: {e}")
                print(f"原始响应: {llm_response}")
                
                # 尝试从响应中提取JSON部分
                import re
                json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
                if json_match:
                    try:
                        json_str = json_match.group()
                        response_data = json.loads(json_str)
                        if "questions" in response_data:
                            questions = []
                            for q in response_data["questions"]:
                                question = TrainingQuestion(
                                    question=q["question"],
                                    sql=q["sql"],
                                    table=table_name,
                                    question_type=q["question_type"],
                                    difficulty=q["difficulty"]
                                )
                                questions.append(question)
                            
                            logger.info(f"DeepSeek API为表 {table_name} 生成了 {len(questions)} 个问题（通过正则提取）")
                            print(f"✓ 通过正则提取成功，生成了 {len(questions)} 个问题")
                            return questions
                    except json.JSONDecodeError:
                        pass
                
                logger.error("无法从API响应中提取有效的JSON格式")
                print("❌ 无法从API响应中提取有效的JSON格式")
                return []
            
        except requests.exceptions.RequestException as e:
            logger.error(f"DeepSeek API请求失败: {e}")
            return []
        except Exception as e:
            logger.error(f"调用大模型生成问题时发生错误: {e}")
            return []
    
    def generate_questions_for_table(self, 
                                   table_name: str, 
                                   fields: List[TableField], 
                                   relationships: List[TableRelationship],
                                   db_connector,
                                   all_tables_fields: Dict[str, List[TableField]] = None) -> List[TrainingQuestion]:
        """为单个表生成训练问题"""
        questions = []
        
        # 找出通用标识字段
        common_identifiers = []
        if all_tables_fields:
            common_identifiers = self.find_common_identifier_fields(all_tables_fields)
        
        primary_fields, key_fields = self.find_key_fields(fields, common_identifiers)
        
        if not primary_fields and not key_fields:
            logger.warning(f"表 {table_name} 没有可用的关联字段，跳过问题生成")
            return questions
        
        # 选择最多3个关联字段
        selected_key_fields = key_fields[:min(self.config.max_related_fields, len(key_fields))]
        
        if self.config.use_llm_generation:
            # 使用大模型生成问答对
            try:
                # 为每个关联字段收集样本值
                sample_values = {}
                for field in selected_key_fields:
                    values = self.generate_sample_values(field, db_connector, table_name)
                    sample_values[field.name] = values
                
                # 准备提示词
                # 获取表的DDL和文档信息
                ddl_info = ""
                table_documentation = ""
                
                try:
                    # 尝试从数据库连接器获取DDL
                    if hasattr(db_connector, 'get_table_ddl'):
                        ddl_info = db_connector.get_table_ddl(table_name)
                    elif hasattr(db_connector, 'get_create_table_sql'):
                        ddl_info = db_connector.get_create_table_sql(table_name)
                    else:
                        # 手动构建DDL
                        ddl_info = self._build_ddl_from_fields(table_name, fields)
                    
                    # 尝试从数据库连接器获取文档
                    if hasattr(db_connector, 'get_table_comment'):
                        table_documentation = db_connector.get_table_comment(table_name)
                    elif hasattr(db_connector, 'get_table_documentation'):
                        table_documentation = db_connector.get_table_documentation(table_name)
                    else:
                        # 手动构建文档
                        table_documentation = self._build_documentation_from_fields(table_name, fields, relationships)
                        
                except Exception as e:
                    logger.warning(f"获取表 {table_name} 的DDL或文档时发生错误: {e}")
                    # 使用备用方案
                    ddl_info = self._build_ddl_from_fields(table_name, fields)
                    table_documentation = self._build_documentation_from_fields(table_name, fields, relationships)
                
                prompt = self._prepare_llm_prompt(table_name, fields, selected_key_fields, relationships, sample_values, ddl_info, table_documentation)
                
                # 打印提示词
                print(f"\n=== 表 {table_name} 的提示词 ===")
                print(prompt)
                print("=" * 80)
                
                # 调用大模型
                questions = self._call_llm_for_questions(prompt, table_name)
                
                # 更新统计信息
                if questions:
                    self.stats['successful_llm_calls'] += 1
                    self.stats['total_questions_generated'] += len(questions)
                else:
                    self.stats['failed_llm_calls'] += 1
                
                # 设置表名
                for q in questions:
                    q.table = table_name
                
                return questions[:self.config.max_questions_per_table]
                
            except Exception as e:
                logger.error(f"使用大模型生成问题时发生错误: {e}")
                # 如果大模型失败，回退到模板生成
                self.stats['fallback_to_templates'] += 1
        
        # 回退到模板生成方法
        for key_field in selected_key_fields:
            # 为每个关联字段生成问题
            field_questions = self._generate_questions_for_field(
                table_name, key_field, fields, relationships, db_connector
            )
            questions.extend(field_questions)
            
            # 限制每个表的问题数量
            if len(questions) >= self.config.max_questions_per_table:
                break
        
        return questions[:self.config.max_questions_per_table]
    
    def _build_ddl_from_fields(self, table_name: str, fields: List[TableField]) -> str:
        """根据字段信息构建DDL语句"""
        try:
            ddl_lines = [f"CREATE TABLE {table_name} ("]
            
            # 添加字段定义
            field_definitions = []
            primary_keys = []
            
            for field in fields:
                field_def = f"    {field.name} {field.data_type}"
                
                # 添加约束
                if field.is_primary:
                    field_def += " PRIMARY KEY"
                    primary_keys.append(field.name)
                elif field.is_unique:
                    field_def += " UNIQUE"
                elif not field.nullable:
                    field_def += " NOT NULL"
                
                # 添加注释
                if field.comment and field.comment != field.name:
                    field_def += f" COMMENT '{field.comment}'"
                
                field_definitions.append(field_def)
            
            # 添加主键约束（如果有多个主键）
            if len(primary_keys) > 1:
                field_definitions.append(f"    PRIMARY KEY ({', '.join(primary_keys)})")
            
            # 添加索引
            for field in fields:
                if field.is_unique and not field.is_primary:
                    field_definitions.append(f"    INDEX idx_{field.name} ({field.name})")
            
            ddl_lines.extend(field_definitions)
            ddl_lines.append(");")
            
            return "\n".join(ddl_lines)
            
        except Exception as e:
            logger.error(f"构建DDL时发生错误: {e}")
            return f"-- 表 {table_name} 的DDL构建失败"
    
    def _build_documentation_from_fields(self, table_name: str, fields: List[TableField], 
                                       relationships: List[TableRelationship]) -> str:
        """根据字段信息构建表文档"""
        try:
            # 分析表类型
            table_type = self._analyze_table_type(table_name, fields)
            
            # 构建文档
            doc_lines = [f"表 {table_name} 用于存储{table_type}，包括："]
            
            # 添加字段说明
            for field in fields:
                if field.comment and field.comment != field.name:
                    constraint_desc = []
                    if field.is_primary:
                        constraint_desc.append("主键")
                    if field.is_unique:
                        constraint_desc.append("唯一")
                    if not field.nullable:
                        constraint_desc.append("非空")
                    
                    constraint_str = f" [{', '.join(constraint_desc)}]" if constraint_desc else ""
                    doc_lines.append(f"- {field.comment}{constraint_str}")
                else:
                    # 如果没有注释，生成通用描述
                    desc = self._generate_field_description(field)
                    doc_lines.append(f"- {desc}")
            
            # 添加关联关系说明
            if relationships:
                doc_lines.append("")
                doc_lines.append("表关联关系：")
                for rel in relationships:
                    if rel.from_table == table_name:
                        doc_lines.append(f"- 通过 {rel.from_column} 字段关联到 {rel.to_table} 表")
                    elif rel.to_table == table_name:
                        doc_lines.append(f"- 通过 {rel.to_column} 字段关联到 {rel.from_table} 表")
            
            return "\n".join(doc_lines)
            
        except Exception as e:
            logger.error(f"构建文档时发生错误: {e}")
            return f"表 {table_name} 的文档构建失败"
    
    def _analyze_table_type(self, table_name: str, fields: List[TableField]) -> str:
        """分析表类型 - 基于字段特征动态分析"""
        # 根据字段特征动态判断表类型，而不是硬编码表名模式
        primary_fields = [f for f in fields if f.is_primary]
        foreign_fields = [f for f in fields if f.is_foreign]
        
        if primary_fields and foreign_fields:
            return "关联数据表"
        elif primary_fields:
            return "主数据表"
        else:
            return "数据表"
    
    def _generate_field_description(self, field: TableField) -> str:
        """生成字段描述 - 动态生成，不依赖硬编码"""
        # 字段描述现在由大模型动态生成，基于字段注释和上下文
        if field.comment and field.comment != field.name:
            return field.comment
        else:
            return field.name
    
    def _generate_questions_for_field(self, 
                                    table_name: str, 
                                    key_field: TableField, 
                                    fields: List[TableField],
                                    relationships: List[TableRelationship],
                                    db_connector) -> List[TrainingQuestion]:
        """为单个字段生成问题（模板方法）"""
        questions = []
        
        # 获取样本值
        sample_values = self.generate_sample_values(key_field, db_connector, table_name)
        
        # 找出目标字段（非关联字段）
        target_fields = [f for f in fields if not f.is_primary and not f.is_foreign and f != key_field]
        
        if not target_fields:
            return questions
        
        # 找出关联表
        related_tables = self._find_related_tables(table_name, key_field.name, relationships)
        
        # 为每个关联字段生成10个问题
        questions_per_field = self.config.max_questions_per_table // self.config.max_related_fields
        
        for sample_value in sample_values[:3]:  # 每个字段最多3个样本值
            for target_field in target_fields[:2]:  # 每个目标字段最多2个问题
                for question_type in self.config.question_types:
                    question = self._create_question(
                        table_name, key_field, target_field, sample_value, 
                        question_type, related_tables, relationships
                    )
                    
                    if question:
                        questions.append(question)
                        
                        if len(questions) >= questions_per_field:
                            break
                
                if len(questions) >= questions_per_field:
                    break
            
            if len(questions) >= questions_per_field:
                break
        
        return questions
    
    def _find_related_tables(self, table_name: str, field_name: str, 
                            relationships: List[TableRelationship]) -> List[Dict[str, str]]:
        """找出关联表"""
        related = []
        for rel in relationships:
            if rel.from_table == table_name and rel.from_column == field_name:
                related.append({
                    'table': rel.to_table,
                    'field': rel.to_column,
                    'relation_field': rel.from_column
                })
            elif rel.to_table == table_name and rel.to_column == field_name:
                related.append({
                    'table': rel.from_table,
                    'field': rel.from_column,
                    'relation_field': rel.to_column
                })
        return related
    
    def _create_question(self, table_name: str, key_field: TableField, 
                        target_field: TableField, sample_value: str,
                        question_type: str, related_tables: List[Dict[str, str]],
                        relationships: List[TableRelationship]) -> Optional[TrainingQuestion]:
        """创建单个问题 - 现在完全依赖大模型生成"""
        # 此方法已废弃，问题现在完全由大模型生成
        # 保留方法签名以兼容现有代码
        return None
    
    def _get_generalized_field_description(self, field: TableField) -> str:
        """获取泛化的字段描述 - 动态生成，不依赖硬编码"""
        # 字段描述现在由大模型动态生成
        return field.comment or field.name
    
    def _generate_sql_for_question(self, table_name: str, key_field: TableField,
                                  target_field: TableField, sample_value: str,
                                  question_type: str, related_tables: List[Dict[str, str]]) -> str:
        """为问题生成SQL - 现在完全依赖大模型生成"""
        # 此方法已废弃，SQL现在完全由大模型生成
        # 保留方法签名以兼容现有代码
        return ""
    
    def _get_entity_name(self, table_name: str) -> str:
        """从表名提取实体名称 - 动态生成，不依赖硬编码"""
        if not self.config.enable_generalization:
            return table_name
        
        # 移除表前缀（如 t_aixl_）
        entity_name = re.sub(r'^t_[a-z_]+_', '', table_name)
        entity_name = re.sub(r'^[a-z]+_', '', entity_name)
        
        # 实体名称现在由大模型动态生成，基于表结构和业务逻辑
        # 这里只做基本的清理，不进行硬编码映射
        return entity_name
    
    def generate_training_plan(self, db_connector, tables: List[str] = None) -> Dict[str, Any]:
        """生成完整的训练计划"""
        try:
            if not tables:
                tables = db_connector.get_tables()
            
            # 先收集所有表的结构信息
            all_tables_fields = {}
            for table_name in tables:
                try:
                    schema = db_connector.get_table_schema(table_name)
                    fields = self.analyze_table_structure(schema)
                    all_tables_fields[table_name] = fields
                except Exception as e:
                    logger.error(f"获取表 {table_name} 结构时发生错误: {e}")
                    continue
            
            training_plan = {
                'tables': [],
                'total_questions': 0,
                'relationships': db_connector.get_table_relationships(),
                'common_identifiers': self.find_common_identifier_fields(all_tables_fields)
            }
            
            print(f"发现通用标识字段: {', '.join(training_plan['common_identifiers'])}")
            
            for table_name, fields in all_tables_fields.items():
                try:
                    # 生成问题
                    questions = self.generate_questions_for_table(
                        table_name, fields, training_plan['relationships'], 
                        db_connector, all_tables_fields
                    )
                    
                    # 更新统计信息
                    self.stats['total_tables_processed'] += 1
                    
                    table_info = {
                        'name': table_name,
                        'fields': [f.__dict__ for f in fields],
                        'questions': [q.__dict__ for q in questions],
                        'question_count': len(questions)
                    }
                    
                    training_plan['tables'].append(table_info)
                    training_plan['total_questions'] += len(questions)
                    
                except Exception as e:
                    logger.error(f"处理表 {table_name} 时发生错误: {e}")
                    continue
            
            return training_plan
        
        except Exception as e:
            logger.error(f"生成训练计划时发生错误: {e}")
            return {'tables': [], 'total_questions': 0, 'relationships': [], 'common_identifiers': []}
    
    def execute_training_plan(self, training_plan: Dict[str, Any], 
                            train_method) -> Dict[str, Any]:
        """执行训练计划"""
        results = {
            'success_count': 0,
            'failed_count': 0,
            'skipped_count': 0,
            'details': []
        }
        
        for table_info in training_plan['tables']:
            table_name = table_info['name']
            print(f"\n处理表: {table_name}")
            
            for question_data in table_info['questions']:
                try:
                    question = question_data['question']
                    sql = question_data['sql']
                    
                    print(f"  训练问题: {question}")
                    print(f"  SQL: {sql}")
                    
                    # 调用训练方法
                    result = train_method(question=question, sql=sql)
                    
                    if result == "duplicate":
                        results['skipped_count'] += 1
                        print("    ✓ 跳过重复数据")
                    else:
                        results['success_count'] += 1
                        print("    ✓ 训练成功")
                    
                    results['details'].append({
                        'table': table_name,
                        'question': question,
                        'sql': sql,
                        'result': result
                    })
                    
                except Exception as e:
                    results['failed_count'] += 1
                    print(f"    ✗ 训练失败: {e}")
                    results['details'].append({
                        'table': table_name,
                        'question': question_data.get('question', ''),
                        'sql': question_data.get('sql', ''),
                        'result': f"error: {str(e)}"
                    })
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats.copy()
    
    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            'total_tables_processed': 0,
            'total_questions_generated': 0,
            'successful_llm_calls': 0,
            'failed_llm_calls': 0,
            'fallback_to_templates': 0
        }
    
    def print_stats(self):
        """打印统计信息"""
        print("\n=== 智能训练统计信息 ===")
        print(f"处理表数: {self.stats['total_tables_processed']}")
        print(f"生成问题数: {self.stats['total_questions_generated']}")
        print(f"成功调用大模型: {self.stats['successful_llm_calls']}")
        print(f"大模型调用失败: {self.stats['failed_llm_calls']}")
        print(f"回退到模板: {self.stats['fallback_to_templates']}")
        
        if self.stats['total_tables_processed'] > 0:
            success_rate = (self.stats['successful_llm_calls'] / self.stats['total_tables_processed']) * 100
            print(f"大模型成功率: {success_rate:.1f}%")
