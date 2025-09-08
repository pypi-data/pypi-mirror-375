import json
import hashlib
import os
import pickle
from typing import List, Optional, Dict, Any
import numpy as np
import pandas as pd
from ..base.vector_base import VectorStoreBase

# 可选依赖导入
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    faiss = None

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None

class FAISSVectorStore(VectorStoreBase):
    def __init__(self, config=None):
        # 检查依赖是否可用
        if not FAISS_AVAILABLE:
            raise ImportError(
                "FAISS is not available. Please install it with: pip install faiss-cpu"
            )
        
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "SentenceTransformers is not available. Please install it with: pip install sentence-transformers"
            )
        
        VectorStoreBase.__init__(self, config=config)
        if config is None:
            config = {}

        # 使用新的配置对象格式
        if hasattr(config, 'api') and hasattr(config.api, 'path'):
            self.storage_path = config.api.path
        else:
            self.storage_path = "."
            
        # 确保存储目录存在
        os.makedirs(self.storage_path, exist_ok=True)
        
        # 初始化嵌入模型
        if hasattr(config, 'embedding_model'):
            self.embedding_model = config.embedding_model
        else:
            # 使用默认的中文嵌入模型
            self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        # 嵌入维度
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        
        # 配置参数
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
        
        # 初始化FAISS索引
        self._init_faiss_indices()
        
        # 加载现有数据
        self._load_existing_data()

    def _init_faiss_indices(self):
        """初始化FAISS索引"""
        # 使用IndexFlatIP进行内积搜索（适合归一化向量）
        self.sql_index = faiss.IndexFlatIP(self.embedding_dim)
        self.ddl_index = faiss.IndexFlatIP(self.embedding_dim)
        self.documentation_index = faiss.IndexFlatIP(self.embedding_dim)
        
        # 存储元数据
        self.sql_metadata = []
        self.ddl_metadata = []
        self.documentation_metadata = []

    def _load_existing_data(self):
        """加载现有的向量数据"""
        try:
            # 加载SQL数据
            sql_path = os.path.join(self.storage_path, "sql_faiss.pkl")
            if os.path.exists(sql_path):
                with open(sql_path, 'rb') as f:
                    data = pickle.load(f)
                    if data['vectors'].shape[0] > 0:
                        self.sql_index.add(data['vectors'])
                        self.sql_metadata = data['metadata']
                        print(f"加载了 {len(self.sql_metadata)} 个SQL向量")
            
            # 加载DDL数据
            ddl_path = os.path.join(self.storage_path, "ddl_faiss.pkl")
            if os.path.exists(ddl_path):
                with open(ddl_path, 'rb') as f:
                    data = pickle.load(f)
                    if data['vectors'].shape[0] > 0:
                        self.ddl_index.add(data['vectors'])
                        self.ddl_metadata = data['metadata']
                        print(f"加载了 {len(self.ddl_metadata)} 个DDL向量")
            
            # 加载文档数据
            doc_path = os.path.join(self.storage_path, "documentation_faiss.pkl")
            if os.path.exists(doc_path):
                with open(doc_path, 'rb') as f:
                    data = pickle.load(f)
                    if data['vectors'].shape[0] > 0:
                        self.documentation_index.add(data['vectors'])
                        self.documentation_metadata = data['metadata']
                        print(f"加载了 {len(self.documentation_metadata)} 个文档向量")
                        
        except Exception as e:
            print(f"加载现有数据时发生错误: {e}")

    def _save_data(self, index_type: str, vectors: np.ndarray, metadata: List[Dict]):
        """保存向量数据到磁盘"""
        try:
            file_path = os.path.join(self.storage_path, f"{index_type}_faiss.pkl")
            data = {
                'vectors': vectors,
                'metadata': metadata
            }
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"保存数据时发生错误: {e}")

    def generate_embedding(self, data: str, **kwargs) -> List[float]:
        """生成文本嵌入向量"""
        embedding = self.embedding_model.encode([data])
        # 归一化向量以使用内积搜索
        embedding = embedding / np.linalg.norm(embedding, axis=1, keepdims=True)
        return embedding[0].tolist()

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
        doc_id = f"{FAISSVectorStore._sha1(question + "\n" + sql)}-sql"

        # 去重检查
        for meta in self.sql_metadata:
            if meta['id'] == doc_id:
                return "duplicate"

        # 生成嵌入向量
        embedding = self.generate_embedding(question_sql_json)
        embedding_array = np.array([embedding], dtype=np.float32)

        # 添加到索引
        self.sql_index.add(embedding_array)
        
        # 添加元数据
        metadata = {
            'id': doc_id,
            'document': question_sql_json,
            'type': 'sql'
        }
        self.sql_metadata.append(metadata)
        
        # 保存到磁盘
        all_vectors = np.vstack([self.sql_index.reconstruct(i) for i in range(self.sql_index.ntotal)])
        self._save_data('sql', all_vectors, self.sql_metadata)
        
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

        doc_id = f"{FAISSVectorStore._sha1(ddl)}-ddl.txt"
        
        # 去重检查
        for meta in self.ddl_metadata:
            if meta['id'] == doc_id:
                return "duplicate"

        # 生成嵌入向量
        embedding = self.generate_embedding(ddl)
        embedding_array = np.array([embedding], dtype=np.float32)

        # 添加到索引
        self.ddl_index.add(embedding_array)
        
        # 添加元数据
        metadata = {
            'id': doc_id,
            'document': ddl,
            'type': 'ddl'
        }
        self.ddl_metadata.append(metadata)
        
        # 保存到磁盘
        all_vectors = np.vstack([self.ddl_index.reconstruct(i) for i in range(self.ddl_index.ntotal)])
        self._save_data('ddl', all_vectors, self.ddl_metadata)
        
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
        doc_id = f"{FAISSVectorStore._sha1(documentation)}-doc"
        
        # 去重检查
        for meta in self.documentation_metadata:
            if meta['id'] == doc_id:
                return "duplicate"

        # 生成嵌入向量
        embedding = self.generate_embedding(documentation)
        embedding_array = np.array([embedding], dtype=np.float32)

        # 添加到索引
        self.documentation_index.add(embedding_array)
        
        # 添加元数据
        metadata = {
            'id': doc_id,
            'document': documentation,
            'type': 'doc'
        }
        self.documentation_metadata.append(metadata)
        
        # 保存到磁盘
        all_vectors = np.vstack([self.documentation_index.reconstruct(i) for i in range(self.documentation_index.ntotal)])
        self._save_data('documentation', all_vectors, self.documentation_metadata)
        
        print(f"添加新文档: {documentation[:100]}...")
        return doc_id

    def get_training_data(self, **kwargs) -> pd.DataFrame:
        """获取所有训练数据"""
        df = pd.DataFrame()

        # SQL数据
        if self.sql_metadata:
            sql_data = []
            for meta in self.sql_metadata:
                try:
                    doc_data = json.loads(meta['document'])
                    sql_data.append({
                        'id': meta['id'],
                        'question': doc_data.get('question'),
                        'content': doc_data.get('sql'),
                        'training_data_type': 'sql'
                    })
                except (json.JSONDecodeError, KeyError):
                    continue
            
            if sql_data:
                df_sql = pd.DataFrame(sql_data)
                df = pd.concat([df, df_sql])

        # DDL数据
        if self.ddl_metadata:
            ddl_data = []
            for meta in self.ddl_metadata:
                ddl_data.append({
                    'id': meta['id'],
                    'question': None,
                    'content': meta['document'],
                    'training_data_type': 'ddl.txt'
                })
            
            if ddl_data:
                df_ddl = pd.DataFrame(ddl_data)
                df = pd.concat([df, df_ddl])

        # 文档数据
        if self.documentation_metadata:
            doc_data = []
            for meta in self.documentation_metadata:
                doc_data.append({
                    'id': meta['id'],
                    'question': None,
                    'content': meta['document'],
                    'training_data_type': 'documentation'
                })
            
            if doc_data:
                df_doc = pd.DataFrame(doc_data)
                df = pd.concat([df, df_doc])

        return df

    def remove_training_data(self, id: str, **kwargs) -> bool:
        """删除训练数据"""
        # FAISS不支持直接删除，需要重建索引
        if id.endswith("-sql"):
            return self._remove_from_collection('sql', id)
        elif id.endswith("-ddl.txt"):
            return self._remove_from_collection('ddl', id)
        elif id.endswith("-doc"):
            return self._remove_from_collection('documentation', id)
        return False

    def _remove_from_collection(self, collection_type: str, doc_id: str) -> bool:
        """从集合中删除数据"""
        try:
            if collection_type == 'sql':
                metadata = self.sql_metadata
                index = self.sql_index
            elif collection_type == 'ddl':
                metadata = self.ddl_metadata
                index = self.ddl_index
            elif collection_type == 'documentation':
                metadata = self.documentation_metadata
                index = self.documentation_index
            else:
                return False

            # 找到要删除的项
            to_remove = None
            for i, meta in enumerate(metadata):
                if meta['id'] == doc_id:
                    to_remove = i
                    break

            if to_remove is None:
                return False

            # 重建索引（移除指定项）
            new_metadata = [meta for i, meta in enumerate(metadata) if i != to_remove]
            
            if collection_type == 'sql':
                self.sql_metadata = new_metadata
                self._rebuild_index('sql')
            elif collection_type == 'ddl':
                self.ddl_metadata = new_metadata
                self._rebuild_index('ddl')
            elif collection_type == 'documentation':
                self.documentation_metadata = new_metadata
                self._rebuild_index('documentation')

            return True
        except Exception as e:
            print(f"删除数据时发生错误: {e}")
            return False

    def _rebuild_index(self, collection_type: str):
        """重建索引"""
        try:
            if collection_type == 'sql':
                self.sql_index = faiss.IndexFlatIP(self.embedding_dim)
                metadata = self.sql_metadata
            elif collection_type == 'ddl':
                self.ddl_index = faiss.IndexFlatIP(self.embedding_dim)
                metadata = self.ddl_metadata
            elif collection_type == 'documentation':
                self.documentation_index = faiss.IndexFlatIP(self.embedding_dim)
                metadata = self.documentation_metadata
            else:
                return

            if metadata:
                # 重新生成所有向量
                vectors = []
                for meta in metadata:
                    embedding = self.generate_embedding(meta['document'])
                    vectors.append(embedding)
                
                vectors_array = np.array(vectors, dtype=np.float32)
                
                if collection_type == 'sql':
                    self.sql_index.add(vectors_array)
                    self._save_data('sql', vectors_array, metadata)
                elif collection_type == 'ddl':
                    self.ddl_index.add(vectors_array)
                    self._save_data('ddl', vectors_array, metadata)
                elif collection_type == 'documentation':
                    self.documentation_index.add(vectors_array)
                    self._save_data('documentation', vectors_array, metadata)
        except Exception as e:
            print(f"重建索引时发生错误: {e}")

    def get_similar_question_sql(self, question: str, **kwargs) -> list:
        """获取相似的问题和SQL"""
        if self.sql_index.ntotal == 0:
            return []

        # 生成查询向量
        query_embedding = self.generate_embedding(question)
        query_array = np.array([query_embedding], dtype=np.float32)

        # 搜索相似向量
        scores, indices = self.sql_index.search(query_array, min(self.n_results_sql, self.sql_index.ntotal))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.sql_metadata):
                meta = self.sql_metadata[idx]
                try:
                    doc_data = json.loads(meta['document'])
                    if isinstance(doc_data, dict) and "question" in doc_data and "sql" in doc_data:
                        results.append(doc_data)
                    else:
                        results.append({"question": None, "sql": meta['document']})
                except Exception:
                    results.append({"question": None, "sql": meta['document']})

        return results

    def get_related_ddl(self, question: str, **kwargs) -> list:
        """获取相关的DDL"""
        if self.ddl_index.ntotal == 0:
            return []

        # 生成查询向量
        query_embedding = self.generate_embedding(question)
        query_array = np.array([query_embedding], dtype=np.float32)

        # 搜索相似向量
        scores, indices = self.ddl_index.search(query_array, min(self.n_results_ddl, self.ddl_index.ntotal))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.ddl_metadata):
                results.append(self.ddl_metadata[idx]['document'])

        return results

    def get_related_documentation(self, question: str, **kwargs) -> list:
        """获取相关的文档"""
        if self.documentation_index.ntotal == 0:
            return []

        # 生成查询向量
        query_embedding = self.generate_embedding(question)
        query_array = np.array([query_embedding], dtype=np.float32)

        # 搜索相似向量
        scores, indices = self.documentation_index.search(query_array, min(self.n_results_documentation, self.documentation_index.ntotal))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.documentation_metadata):
                results.append(self.documentation_metadata[idx]['document'])

        return results

    def get_similar_questions(self, question: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """获取相似的问题和 SQL"""
        if self.sql_index.ntotal == 0:
            return []

        # 生成查询向量
        query_embedding = self.generate_embedding(question)
        query_array = np.array([query_embedding], dtype=np.float32)

        # 搜索相似向量
        scores, indices = self.sql_index.search(query_array, min(n_results, self.sql_index.ntotal))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.sql_metadata):
                meta = self.sql_metadata[idx]
                results.append({
                    'id': meta['id'],
                    'document': meta['document'],
                    'score': float(score)
                })

        return results

    def get_ddl(self) -> List[str]:
        """获取所有 DDL"""
        return [meta['document'] for meta in self.ddl_metadata]

    def get_documentation(self) -> List[str]:
        """获取所有文档"""
        return [meta['document'] for meta in self.documentation_metadata]
    
    def clean_duplicates(self) -> Dict[str, int]:
        """
        清理重复数据
        
        Returns:
            Dict[str, int]: 各集合清理的重复数据数量
        """
        cleaned_counts = {"sql": 0, "ddl": 0, "documentation": 0}
        
        # 清理SQL集合中的重复
        seen_questions = set()
        new_sql_metadata = []
        
        for meta in self.sql_metadata:
            try:
                doc_data = json.loads(meta['document'])
                question_key = f"{doc_data.get('question')}|{doc_data.get('sql')}"
                if question_key not in seen_questions:
                    seen_questions.add(question_key)
                    new_sql_metadata.append(meta)
                else:
                    cleaned_counts["sql"] += 1
            except (json.JSONDecodeError, KeyError):
                new_sql_metadata.append(meta)
        
        if cleaned_counts["sql"] > 0:
            self.sql_metadata = new_sql_metadata
            self._rebuild_index('sql')
            print(f"清理了 {cleaned_counts['sql']} 个重复的SQL数据")
        
        # 清理DDL集合中的重复
        seen_ddl = set()
        new_ddl_metadata = []
        
        for meta in self.ddl_metadata:
            if meta['document'] not in seen_ddl:
                seen_ddl.add(meta['document'])
                new_ddl_metadata.append(meta)
            else:
                cleaned_counts["ddl"] += 1
        
        if cleaned_counts["ddl"] > 0:
            self.ddl_metadata = new_ddl_metadata
            self._rebuild_index('ddl')
            print(f"清理了 {cleaned_counts['ddl']} 个重复的DDL数据")
        
        # 清理文档集合中的重复
        seen_docs = set()
        new_doc_metadata = []
        
        for meta in self.documentation_metadata:
            if meta['document'] not in seen_docs:
                seen_docs.add(meta['document'])
                new_doc_metadata.append(meta)
            else:
                cleaned_counts["documentation"] += 1
        
        if cleaned_counts["documentation"] > 0:
            self.documentation_metadata = new_doc_metadata
            self._rebuild_index('documentation')
            print(f"清理了 {cleaned_counts['documentation']} 个重复的文档数据")
        
        return cleaned_counts

    def get_stats(self) -> Dict[str, Any]:
        """获取向量数据库统计信息"""
        return {
            'sql_count': len(self.sql_metadata),
            'ddl_count': len(self.ddl_metadata),
            'documentation_count': len(self.documentation_metadata),
            'total_vectors': self.sql_index.ntotal + self.ddl_index.ntotal + self.documentation_index.ntotal,
            'embedding_dimension': self.embedding_dim,
            'storage_path': self.storage_path
        }
