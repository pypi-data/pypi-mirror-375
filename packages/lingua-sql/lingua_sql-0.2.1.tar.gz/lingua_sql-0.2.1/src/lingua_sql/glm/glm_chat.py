import requests
import json
from typing import List, Optional, Dict, Any
from ..base.llm_base import LLMBase

class GLMChat(LLMBase):
    def __init__(self, config=None):
        if config is None:
            raise ValueError(
                "For GLM, config must be provided with an api_key and model"
            )
        
        # 使用新的配置对象格式
        if hasattr(config, 'api') and hasattr(config.api, 'api_key'):
            api_key = config.api.api_key
        else:
            api_key = None
            
        if hasattr(config, 'api') and hasattr(config.api, 'model'):
            model = config.api.model
        else:
            model = None
            
        if not api_key:
            raise ValueError("config must contain a GLM api_key")
        if not model:
            raise ValueError("config must contain a GLM model")
    
        self.model = model
        self.api_key = api_key
        # 智谱AI的API端点
        self.base_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        
    def system_message(self, message: str) -> any:
        return {"role": "system", "content": message}

    def user_message(self, message: str) -> any:
        return {"role": "user", "content": message}

    def assistant_message(self, message: str) -> any:
        return {"role": "assistant", "content": message}

    def generate_sql(self, question: str, **kwargs) -> str:
        # 使用父类的 generate_sql
        sql = super().generate_sql(question, **kwargs)
        
        # 替换 "\_" 为 "_"
        sql = sql.replace("\\_", "_")
        
        return sql

    def submit_prompt(self, prompt, **kwargs) -> str:
        # 构建请求数据
        data = {
            "model": self.model,
            "messages": prompt,
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 0.8),
            "max_tokens": kwargs.get("max_tokens", 2048)
        }
        
        # 构建请求头
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 发送请求
        response = requests.post(self.base_url, json=data, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]


    def run_sql(self, sql: str, params: Optional[tuple] = None) -> Optional[List[Dict[str, Any]]]:
        """
        运行 SQL 查询并返回结果
        注意：这个方法需要数据库连接，在 LinguaSQL 主类中会被重写
        """
        raise NotImplementedError("run_sql method should be implemented in LinguaSQL main class")
    def extract_field_names(self, question: str, available_fields: list = None, ddl_info: str = None) -> list:
        """
        从问题中提取字段名
        
        Args:
            question: 用户问题
            available_fields: 可用的字段列表，如果提供则只返回匹配的字段
            ddl_info: 数据库DDL信息，包含表结构和字段信息
            
        Returns:
            list: 提取到的字段名列表
        """
        try:
            # 构建提示词
            system_prompt = """你是一个专业的数据库字段提取专家。你的任务是从用户的问题中提取可能涉及到的数据库字段名。

要求：
1. 仔细分析问题中提到的实体、属性、条件等
2. 参考提供的数据库结构信息（DDL）
3. 提取所有可能的字段名
4. 字段名应该是标准的数据库字段格式（下划线分隔或驼峰命名）
5. 只返回字段名，不要其他解释
6. 如果提供了可用字段列表，只返回匹配的字段
7. 返回格式：每行一个字段名，不要编号或符号

示例：
问题："查询所有用户的姓名和年龄"
字段：user_name, age, user_age

问题："统计订单表中金额大于100的订单数量"
字段：order_amount, order_count, amount"""
            
            user_prompt = f"问题：{question}\n"
            
            # 添加DDL信息
            if ddl_info:
                user_prompt += f"\n数据库结构信息：\n{ddl_info}\n"

            if available_fields:
                user_prompt += f"\n可用字段：{', '.join(available_fields)}\n"
            
            user_prompt += "\n请提取问题中涉及的字段名："
            
            messages = [
                self.system_message(system_prompt),
                self.user_message(user_prompt)
            ]
            
            # 调用 GLM API
            response = self.submit_prompt(messages)

            # 解析响应，提取字段名
            field_names = self._parse_field_names(response, available_fields)
            
            return field_names
            
        except Exception as e:
            print(f"提取字段名时发生错误: {e}")
            return []

    def _parse_field_names(self, response: str, available_fields: list = None) -> list:
        """
        解析响应文本，提取字段名
        
        Args:
            response: API响应文本
            available_fields: 可用字段列表
            
        Returns:
            list: 解析出的字段名列表
        """
        try:
            # 清理响应文本
            response = response.strip()
            
            # 按行分割
            lines = response.split('\n')
            
            field_names = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # 移除编号、符号等
                line = line.lstrip('0123456789.-*• ')
                
                # 提取字段名（支持逗号分隔）
                if ',' in line:
                    fields = [f.strip() for f in line.split(',')]
                    field_names.extend(fields)
                else:
                    field_names.append(line)
            
            # 清理字段名
            cleaned_fields = []
            for field in field_names:
                field = field.strip()
                if field and not field.startswith(('字段', '字段名', ':')):
                    # 移除可能的引号
                    field = field.strip('"\'')
                    cleaned_fields.append(field)
            
            # 如果提供了可用字段列表，只返回匹配的字段
            if available_fields:
                matched_fields = []
                for field in cleaned_fields:
                    # 精确匹配
                    if field in available_fields:
                        matched_fields.append(field)
                    else:
                        # 模糊匹配（包含关系）
                        for available_field in available_fields:
                            if field.lower() in available_field.lower() or available_field.lower() in field.lower():
                                matched_fields.append(available_field)
                                break
                return list(set(matched_fields))  # 去重
            
            return list(set(cleaned_fields))  # 去重
            
        except Exception as e:
            print(f"解析字段名时发生错误: {e}")
            return []

    def extract_table_names(self, question: str, available_tables: list = None, ddl_info: str = None) -> list:
        """
        从问题中提取表名
        
        Args:
            question: 用户问题
            available_tables: 可用的表列表，如果提供则只返回匹配的表
            ddl_info: 数据库DDL信息，包含表结构和字段信息
            
        Returns:
            list: 提取到的表名列表
        """
        try:
            # 构建提示词
            system_prompt = """你是一个专业的数据库表名提取专家。你的任务是从用户的问题中提取可能涉及到的数据库表名。

要求：
1. 仔细分析问题中提到的实体、对象、数据源等
2. 参考提供的数据库结构信息（DDL）
3. 提取所有可能的表名
4. 表名应该是标准的数据库表格式（下划线分隔或驼峰命名）
5. 只返回表名，不要其他解释
6. 如果提供了可用表列表，只返回匹配的表
7. 返回格式：每行一个表名，不要编号或符号

示例：
问题："查询用户表中的所有数据"
表名：users, user_table

问题："统计订单和商品表的关联数据"
表名：orders, products, order_items"""
            
            user_prompt = f"问题：{question}\n"
            
            # 添加DDL信息
            if ddl_info:
                user_prompt += f"\n数据库结构信息：\n{ddl_info}\n"
            
            if available_tables:
                user_prompt += f"\n可用表：{', '.join(available_tables)}\n"
            user_prompt += "\n请提取问题中涉及的表名："
            
            messages = [
                self.system_message(system_prompt),
                self.user_message(user_prompt)
            ]
            
            # 调用 GLM API
            response = self.submit_prompt(messages)
            
            # 解析响应，提取表名
            table_names = self._parse_table_names(response, available_tables)
            
            return table_names
            
        except Exception as e:
            print(f"提取表名时发生错误: {e}")
            return []

    def _parse_table_names(self, response: str, available_tables: list = None) -> list:
        """
        解析响应文本，提取表名
        
        Args:
            response: API响应文本
            available_tables: 可用表列表
            
        Returns:
            list: 解析出的表名列表
        """
        try:
            # 清理响应文本
            response = response.strip()
            
            # 按行分割
            lines = response.split('\n')
            
            table_names = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # 移除编号、符号等
                line = line.lstrip('0123456789.-*• ')
                
                # 提取表名（支持逗号分隔）
                if ',' in line:
                    tables = [t.strip() for t in line.split(',')]
                    table_names.extend(tables)
                else:
                    table_names.append(line)
            
            # 清理表名
            cleaned_tables = []
            for table in table_names:
                table = table.strip()
                if table and not table.startswith(('表', '表名', ':')):
                    # 移除可能的引号
                    table = table.strip('"\'')
                    cleaned_tables.append(table)
            
            # 如果提供了可用表列表，只返回匹配的表
            if available_tables:
                matched_tables = []
                for table in cleaned_tables:
                    # 精确匹配
                    if table in available_tables:
                        matched_tables.append(table)
                    else:
                        # 模糊匹配（包含关系）
                        for available_table in available_tables:
                            if table.lower() in available_table.lower() or available_table.lower() in table.lower():
                                matched_tables.append(available_table)
                                break
                return list(set(matched_tables))  # 去重
            
            return list(set(cleaned_tables))  # 去重
            
        except Exception as e:
            print(f"解析表名时发生错误: {e}")
            return []

    def analyze_question_intent(self, question: str, ddl_info: str = None) -> dict:
        """
        分析问题意图，提取操作类型、目标、条件等
        
        Args:
            question: 用户问题
            ddl_info: 数据库DDL信息，包含表结构和字段信息
            
        Returns:
            dict: 包含分析结果的字典
        """
        try:
            system_prompt = """你是一个专业的SQL查询意图分析专家。你的任务是从用户问题中分析出查询的意图和结构。

请分析以下要素：
1. 操作类型：SELECT, COUNT, SUM, AVG, MAX, MIN, INSERT, UPDATE, DELETE等
2. 目标对象：要查询的表、字段等
3. 条件：WHERE条件、过滤条件等
4. 排序：ORDER BY, 排序字段等
5. 分组：GROUP BY, 分组字段等
6. 限制：LIMIT, 数量限制等

请参考提供的数据库结构信息（DDL）来准确识别表和字段。

请以JSON格式返回分析结果，格式如下：
{
    "operation_type": "操作类型",
    "target_tables": ["目标表"],
    "target_fields": ["目标字段"],
    "conditions": ["条件"],
    "order_by": ["排序字段"],
    "group_by": ["分组字段"],
    "limit": "限制数量",
    "intent": "查询意图描述"
}"""
            
            user_prompt = f"请分析以下问题的查询意图：{question}"
            
            # 添加DDL信息
            if ddl_info:
                user_prompt += f"\n\n数据库结构信息：\n{ddl_info}"
            
            messages = [
                self.system_message(system_prompt),
                self.user_message(user_prompt)
            ]
            
            # 调用 GLM API
            response = self.submit_prompt(messages)
            
            # 尝试解析JSON响应
            try:
                result = json.loads(response)
                return result
            except json.JSONDecodeError:
                # 如果JSON解析失败，返回基本分析
                return {
                    "operation_type": "SELECT",
                    "target_tables": [],
                    "target_fields": [],
                    "conditions": [],
                    "order_by": [],
                    "group_by": [],
                    "limit": None,
                    "intent": "无法解析查询意图",
                    "raw_response": response
                }
                
        except Exception as e:
            print(f"分析问题意图时发生错误: {e}")
            return {
                "operation_type": "SELECT",
                "target_tables": [],
                "target_fields": [],
                "conditions": [],
                "order_by": [],
                "group_by": [],
                "limit": None,
                "intent": f"分析失败: {str(e)}"
            }
