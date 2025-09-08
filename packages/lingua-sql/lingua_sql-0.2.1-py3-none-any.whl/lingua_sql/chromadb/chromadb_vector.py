import json
import hashlib
from typing import List, Optional, Dict, Any
import chromadb
import pandas as pd
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from ..base.vector_base import VectorStoreBase

default_ef = embedding_functions.DefaultEmbeddingFunction()

class ChromaDBVectorStore(VectorStoreBase):
    def __init__(self, config=None):
        VectorStoreBase.__init__(self, config=config)
        if config is None:
            config = {}

        # 使用新的配置对象格式
        if hasattr(config, 'api') and hasattr(config.api, 'path'):
            path = config.api.path
        else:
            path = "."
            
        if hasattr(config, 'embedding_function'):
            self.embedding_function = config.embedding_function
        else:
            self.embedding_function = default_ef
            
        if hasattr(config, 'api') and hasattr(config.api, 'client'):
            curr_client = config.api.client
        else:
            curr_client = "persistent"
            
        if hasattr(config, 'collection_metadata'):
            collection_metadata = config.collection_metadata
        else:
            collection_metadata = None
            
        if hasattr(config, 'n_results_sql'):
            self.n_results_sql = config.n_results_sql
        else:
            self.n_results_sql = 10
            
        if hasattr(config, 'n_results_documentation'):
            self.n_results_documentation = config.n_results_documentation
        else:
            self.n_results_documentation = 10
            
        if hasattr(config, 'n_results_ddl'):
            self.n_results_ddl = config.n_results_ddl
        else:
            self.n_results_ddl = 10

        if curr_client == "persistent":
            self.chroma_client = chromadb.PersistentClient(
                path=path, settings=Settings(anonymized_telemetry=False)
            )
        elif curr_client == "in-memory":
            self.chroma_client = chromadb.EphemeralClient(
                settings=Settings(anonymized_telemetry=False)
            )
        elif isinstance(curr_client, chromadb.api.client.Client):
            self.chroma_client = curr_client
        else:
            raise ValueError(f"Unsupported client was set in config: {curr_client}")

        self.documentation_collection = self.chroma_client.get_or_create_collection(
            name="documentation",
            embedding_function=self.embedding_function,
            metadata=collection_metadata,
        )
        self.ddl_collection = self.chroma_client.get_or_create_collection(
            name="ddl.txt",
            embedding_function=self.embedding_function,
            metadata=collection_metadata,
        )
        self.sql_collection = self.chroma_client.get_or_create_collection(
            name="sql",
            embedding_function=self.embedding_function,
            metadata=collection_metadata,
        )

    def generate_embedding(self, data: str, **kwargs) -> List[float]:
        embedding = self.embedding_function([data])
        if len(embedding) == 1:
            return embedding[0]
        return embedding

    @staticmethod
    def _sha1(text: str) -> str:
        return hashlib.sha1(text.encode("utf-8")).hexdigest()

    def add_question_sql(self, question: str, sql: str, **kwargs) -> str:
        """
        添加问题和SQL对到向量数据库，支持去重
        
        Args:
            question: 问题
            sql: SQL语句
            **kwargs: 其他参数
            
        Returns:
            str: 添加的数据ID
        """
        # 规范化为 JSON 文本
        question_sql_json = json.dumps({"question": question, "sql": sql}, ensure_ascii=False)
        doc_id = f"{ChromaDBVectorStore._sha1(question + "\n" + sql)}-sql"

        # 去重：基于 id 精确判断
        existed = self.sql_collection.get(ids=[doc_id])
        if existed and existed.get("ids"):
            # 已存在则直接返回，不再打印噪声日志
            return "duplicate"

        # 写入（list 形式 + metadata）
        self.sql_collection.add(
            documents=[question_sql_json],
            embeddings=[self.generate_embedding(question_sql_json)],
            metadatas=[{"type": "sql"}],
            ids=[doc_id],
        )
        print(f"添加新数据: 问题='{question[:50]}...' SQL='{sql[:50]}...'")
        return doc_id

    def add_ddl(self, ddl: str, **kwargs) -> str:
        """
        添加DDL到向量数据库，支持去重
        
        Args:
            ddl: DDL语句
            **kwargs: 其他参数
            
        Returns:
            str: 添加的数据ID
        """
        # 防误存：若是 question-sql JSON，改存到 sql 集合
        ddl_stripped = (ddl or "").lstrip()
        if ddl_stripped.startswith("{"):
            try:
                obj = json.loads(ddl_stripped)
                if isinstance(obj, dict) and "question" in obj and "sql" in obj:
                    return self.add_question_sql(obj.get("question", ""), obj.get("sql", ""))
            except Exception:
                pass

        doc_id = f"{ChromaDBVectorStore._sha1(ddl)}-ddl.txt"
        existed = self.ddl_collection.get(ids=[doc_id])
        if existed and existed.get("ids"):
            # 已存在则直接返回，不再打印噪声日志
            return "duplicate"

        self.ddl_collection.add(
            documents=[ddl],
            embeddings=[self.generate_embedding(ddl)],
            metadatas=[{"type": "ddl"}],
            ids=[doc_id],
        )
        print(f"添加新DDL: {ddl[:100]}...")
        return doc_id

    def add_documentation(self, documentation: str, **kwargs) -> str:
        """
        添加文档到向量数据库，支持去重
        
        Args:
            documentation: 文档内容
            **kwargs: 其他参数
            
        Returns:
            str: 添加的数据ID
        """
        doc_id = f"{ChromaDBVectorStore._sha1(documentation)}-doc"
        existed = self.documentation_collection.get(ids=[doc_id])
        if existed and existed.get("ids"):
            # 已存在则直接返回，不再打印噪声日志
            return "duplicate"

        self.documentation_collection.add(
            documents=[documentation],
            embeddings=[self.generate_embedding(documentation)],
            metadatas=[{"type": "doc"}],
            ids=[doc_id],
        )
        print(f"添加新文档: {documentation[:100]}...")
        return doc_id

    def get_training_data(self, **kwargs) -> pd.DataFrame:
        sql_data = self.sql_collection.get()
        df = pd.DataFrame()

        if sql_data is not None:
            documents = [json.loads(doc) for doc in sql_data["documents"]]
            ids = sql_data["ids"]
            df_sql = pd.DataFrame(
                {
                    "id": ids,
                    "question": [doc["question"] for doc in documents],
                    "content": [doc["sql"] for doc in documents],
                }
            )
            df_sql["training_data_type"] = "sql"
            df = pd.concat([df, df_sql])

        ddl_data = self.ddl_collection.get()
        if ddl_data is not None:
            documents = ddl_data["documents"]
            ids = ddl_data["ids"]
            df_ddl = pd.DataFrame(
                {
                    "id": ids,
                    "question": [None for _ in documents],
                    "content": documents,
                }
            )
            df_ddl["training_data_type"] = "ddl.txt"
            df = pd.concat([df, df_ddl])

        doc_data = self.documentation_collection.get()
        if doc_data is not None:
            documents = doc_data["documents"]
            ids = doc_data["ids"]
            df_doc = pd.DataFrame(
                {
                    "id": ids,
                    "question": [None for _ in documents],
                    "content": documents,
                }
            )
            df_doc["training_data_type"] = "documentation"
            df = pd.concat([df, df_doc])

        return df

    def remove_training_data(self, id: str, **kwargs) -> bool:
        if id.endswith("-sql"):
            self.sql_collection.delete(ids=id)
            return True
        elif id.endswith("-ddl.txt"):
            self.ddl_collection.delete(ids=id)
            return True
        elif id.endswith("-doc"):
            self.documentation_collection.delete(ids=id)
            return True
        return False

    @staticmethod
    def _extract_documents(query_results) -> list:
        # 使用 _extract_documents 来提取实际需要的文档内容，屏蔽了底层数据库返回格式的复杂性
        if query_results is None:
            return []

        if "documents" in query_results:
            documents = query_results["documents"]
            # Chroma 查询通常返回嵌套列表（每个 query_text 一组）
            if documents and isinstance(documents[0], list):
                documents = documents[0]
            return documents
        return []

    def get_similar_question_sql(self, question: str, **kwargs) -> list:
        docs = ChromaDBVectorStore._extract_documents(
            self.sql_collection.query(
                query_texts=[question],
                n_results=self.n_results_sql,
            )
        )
        # Lingua_sql 风格：存 JSON 文本，这里解析为 {question, sql}
        parsed = []
        for d in docs:
            try:
                obj = json.loads(d)
                if isinstance(obj, dict) and "question" in obj and "sql" in obj:
                    parsed.append(obj)
                else:
                    # 非预期结构，作为原文透传
                    parsed.append({"question": None, "sql": d})
            except Exception:
                parsed.append({"question": None, "sql": d})
        return parsed

    def get_related_ddl(self, question: str, **kwargs) -> list:
        return ChromaDBVectorStore._extract_documents(
            self.ddl_collection.query(
                query_texts=[question],
                n_results=self.n_results_ddl,
            )
        )

    def get_related_documentation(self, question: str, **kwargs) -> list:
        return ChromaDBVectorStore._extract_documents(
            self.documentation_collection.query(
                query_texts=[question],
                n_results=self.n_results_documentation,
            )
        )

    def get_similar_questions(self, question: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """获取相似的问题和 SQL"""
        # 如需过滤，请确保与写入时的 metadata.type 一致（此实现为 'sql'）
        return self.sql_collection.query(
            query_texts=[question],
            n_results=n_results
        )

    def get_ddl(self) -> List[str]:
        """获取所有 DDL"""
        results = self.ddl_collection.get()
        return results["documents"] if results else []

    def get_documentation(self) -> List[str]:
        """获取所有文档"""
        results = self.documentation_collection.get()
        return results["documents"] if results else []
    
    def clean_duplicates(self) -> Dict[str, int]:
        """
        清理重复数据
        
        Returns:
            Dict[str, int]: 各集合清理的重复数据数量
        """
        cleaned_counts = {"sql": 0, "ddl": 0, "documentation": 0}
        
        # 清理SQL集合中的重复
        sql_data = self.sql_collection.get()
        if sql_data and sql_data.get("documents"):
            seen_questions = set()
            to_delete = []
            
            for i, doc in enumerate(sql_data["documents"]):
                try:
                    doc_data = json.loads(doc)
                    question_key = f"{doc_data.get('question')}|{doc_data.get('sql')}"
                    if question_key in seen_questions:
                        to_delete.append(sql_data["ids"][i])
                        cleaned_counts["sql"] += 1
                    else:
                        seen_questions.add(question_key)
                except (json.JSONDecodeError, KeyError):
                    continue
            
            if to_delete:
                self.sql_collection.delete(ids=to_delete)
                print(f"清理了 {cleaned_counts['sql']} 个重复的SQL数据")
        
        # 清理DDL集合中的重复
        ddl_data = self.ddl_collection.get()
        if ddl_data and ddl_data.get("documents"):
            seen_ddl = set()
            to_delete = []
            
            for i, doc in enumerate(ddl_data["documents"]):
                if doc in seen_ddl:
                    to_delete.append(ddl_data["ids"][i])
                    cleaned_counts["ddl"] += 1
                else:
                    seen_ddl.add(doc)
            
            if to_delete:
                self.ddl_collection.delete(ids=to_delete)
                print(f"清理了 {cleaned_counts['ddl']} 个重复的DDL数据")
        
        # 清理文档集合中的重复
        doc_data = self.documentation_collection.get()
        if doc_data and doc_data.get("documents"):
            seen_docs = set()
            to_delete = []
            
            for i, doc in enumerate(doc_data["documents"]):
                if doc in seen_docs:
                    to_delete.append(doc_data["ids"][i])
                    cleaned_counts["documentation"] += 1
                else:
                    seen_docs.add(doc)
            
            if to_delete:
                self.documentation_collection.delete(ids=to_delete)
                print(f"清理了 {cleaned_counts['documentation']} 个重复的文档数据")
        
        return cleaned_counts 