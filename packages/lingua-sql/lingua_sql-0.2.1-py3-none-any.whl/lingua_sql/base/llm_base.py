from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import pandas as pd

class LLMBase(ABC):
    """大语言模型基类"""
    
    def __init__(self, config=None):
        if config is None:
            config = {}
        self.config = config
        self.vector_store = None  # 向量数据库引用，由 LinguaSQL 主类设置

    @abstractmethod
    def system_message(self, message: str) -> any:
        """系统消息"""
        pass

    @abstractmethod
    def user_message(self, message: str) -> any:
        """用户消息"""
        pass

    @abstractmethod
    def assistant_message(self, message: str) -> any:
        """助手消息"""
        pass

    @abstractmethod
    def submit_prompt(self, prompt, **kwargs) -> str:
        """提交提示到 LLM"""
        pass

    @abstractmethod
    def run_sql(self, sql: str, params: Optional[tuple] = None) -> Optional[List[Dict[str, Any]]]:
        """
        运行 SQL 查询并返回结果
        """
        pass

    def generate_sql(self, question: str, allow_llm_to_see_data=False, **kwargs) -> str:
        """
        使用 LLM 生成 SQL 查询
        """
        if self.vector_store is None:
            raise ValueError("Vector store not set. This method requires a vector store.")
        
        question_sql_list = self.vector_store.get_similar_question_sql(question, **kwargs)
        ddl_list = self.vector_store.get_related_ddl(question, **kwargs)
        doc_list = self.vector_store.get_related_documentation(question, **kwargs)
        prompt = self.get_sql_prompt(
            question=question,
            question_sql_list=question_sql_list,
            ddl_list=ddl_list,
            doc_list=doc_list,
            **kwargs,
        )
        self.log(title="SQL Prompt", message=prompt)
        llm_response = self.submit_prompt(prompt, **kwargs)
        self.log(title="LLM Response", message=llm_response)
        return self.extract_sql(llm_response)

    def get_sql_prompt(self, question: str, question_sql_list: list, ddl_list: list, doc_list: list, **kwargs) -> str:
        """生成SQL提示词"""
        # 将字典列表转换为字符串列表
        question_sql_str_list = []
        for item in question_sql_list:
            if isinstance(item, dict):
                question_sql_str_list.append(f"问题：{item['question']}\nSQL：{item['sql']}")
            else:
                question_sql_str_list.append(str(item))

        prompt = [
            self.system_message(
                "你是一个经验丰富的SQL专家和数据分析师。你的任务是：\n"
                "1. 理解用户的问题意图\n"
                "2. 分析数据库结构和相关文档\n"
                "3. 参考相似问题的解决方案\n"
                "4. 生成准确、高效的SQL查询\n"
                "5. 确保查询语法正确且符合数据库规范\n"
                "只返回SQL查询语句，不要包含任何解释或注释。"
            ),
            self.user_message(
                f"用户问题：{question}\n\n"
                f"数据库结构信息：\n"
                f"DDL语句：\n{chr(10).join(ddl_list)}\n\n"
                f"相关文档：\n{chr(10).join(doc_list)}\n\n"
                f"参考案例（相似问题及SQL）：\n{chr(10).join(question_sql_str_list)}\n\n"
                f"请基于以上信息生成准确的SQL查询。"
            ),
        ]
        return prompt

    def extract_sql(self, llm_response: str) -> str:
        """从LLM响应中提取SQL"""
        import re
        # 匹配 CREATE TABLE ... AS SELECT
        sqls = re.findall(r"\bCREATE\s+TABLE\b.*?\bAS\b.*?;", llm_response, re.DOTALL | re.IGNORECASE)
        if sqls:
            return sqls[-1]

        # 匹配 WITH 子句
        sqls = re.findall(r"\bWITH\b.*?;", llm_response, re.DOTALL | re.IGNORECASE)
        if sqls:
            return sqls[-1]

        # 匹配 SELECT 语句
        sqls = re.findall(r"\bSELECT\b.*?;", llm_response, re.DOTALL | re.IGNORECASE)
        if sqls:
            return sqls[-1]

        # 如果没有找到完整的SQL，返回整个响应
        return llm_response.strip()

    def log(self, message: str, title: str = "Info"):
        """日志记录"""
        print(f"{title}: {message}")
