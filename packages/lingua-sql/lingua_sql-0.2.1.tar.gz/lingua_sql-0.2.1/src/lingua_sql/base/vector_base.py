from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import pandas as pd

class VectorStoreBase(ABC):
    """向量数据库基类"""
    
    def __init__(self, config=None):
        if config is None:
            config = {}
        self.config = config

    @abstractmethod
    def generate_embedding(self, data: str, **kwargs) -> List[float]:
        """生成文本的嵌入向量"""
        pass

    @abstractmethod
    def get_similar_question_sql(self, question: str, **kwargs) -> list:
        """获取相似问题的 SQL"""
        pass

    @abstractmethod
    def get_related_ddl(self, question: str, **kwargs) -> list:
        """获取相关的 DDL"""
        pass

    @abstractmethod
    def get_related_documentation(self, question: str, **kwargs) -> list:
        """获取相关的文档"""
        pass

    @abstractmethod
    def add_question_sql(self, question: str, sql: str, **kwargs) -> str:
        """添加问题和 SQL 对"""
        pass

    @abstractmethod
    def add_ddl(self, ddl: str, **kwargs) -> str:
        """添加 DDL"""
        pass

    @abstractmethod
    def add_documentation(self, documentation: str, **kwargs) -> str:
        """添加文档"""
        pass

    @abstractmethod
    def get_training_data(self, **kwargs) -> pd.DataFrame:
        """获取训练数据"""
        pass

    @abstractmethod
    def remove_training_data(self, id: str, **kwargs) -> bool:
        """删除训练数据"""
        pass
