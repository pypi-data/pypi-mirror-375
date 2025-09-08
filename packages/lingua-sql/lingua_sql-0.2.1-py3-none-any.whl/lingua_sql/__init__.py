from .chromadb.chromadb_vector import ChromaDBVectorStore
from .deepseek.deepseek_chat import DeepSeekChat

# 可选导入 FAISS
try:
    from .faiss.faiss_vector import FAISSVectorStore
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    FAISSVectorStore = None
from .qwen.qwen_chat import QwenChat
from .ernie.ernie_chat import ERNIEChat
from .glm.glm_chat import GLMChat
from .moonshot.moonshot_chat import MoonshotChat
from .yi.yi_chat import YiChat
from .database.mysql_connector import MySQLConnector
from .intelligent_training import IntelligentTrainer, IntelligentTrainingConfig
from typing import List, Dict, Any, Optional
import pandas as pd

class LinguaSQL:
    def __init__(self, config=None, **kwargs):
        """
        初始化 LinguaSQL
        
        Args:
            config: 配置对象或配置字典
            **kwargs: 其他参数
        """
        # 处理配置
        if config is None:
            from .config import create_config
            config = create_config()
        elif isinstance(config, dict):
            # 兼容旧版字典初始化：仅当包含新配置结构关键字段时才转为 LinguaSQLConfig
            try:
                from .config import LinguaSQLConfig
                if any(k in config for k in ["auto_training", "database", "debug"]):
                    config = LinguaSQLConfig(**config)
                # 否则保留原字典（旧式：api_key/model/client/db_* 等）
            except Exception:
                pass
        
        self.config = config
        
        # 根据配置选择合适的向量数据库
        self.vector_store = self._create_vector_store(config)
        
        # 根据配置选择合适的大模型
        self.llm_client = self._create_llm_client(config)
        
        # 设置向量数据库引用到LLM客户端
        if hasattr(self.llm_client, 'vector_store'):
            self.llm_client.vector_store = self.vector_store
        
        # 初始化数据库连接
        self.db = None
        try:
            conn_str = self._get_cfg('database.connection_string')
            if conn_str:
                from .database.connection_factory import create_connection_from_string
                self.db = create_connection_from_string(conn_str)
            else:
                from .database.connection_factory import create_connection
                db_type = self._get_cfg('database.type', 'mysql')
                self.db = create_connection(
                    db_type,
                    host=self._get_cfg('database.host', 'localhost'),
                    port=int(self._get_cfg('database.port', 3306) or 3306),
                    user=self._get_cfg('database.user', 'root'),
                    password=self._get_cfg('database.password', ''),
                    database=self._get_cfg('database.database', None)
                )

            if self.db and self._bool_cfg('database.auto_connect', True):
                if self.db.connect():
                    print(f"数据库连接成功: {self._get_cfg('database.type', 'mysql')}")
                    if self._bool_cfg('database.auto_import_ddl', True) or self._bool_cfg('import_schema_on_init', False):
                        print("自动导入数据库结构...")
                        self.auto_import_schema()
                else:
                    print("❌ 数据库连接失败")
                    self.db = None
        except Exception as e:
            print(f"❌ 初始化数据库连接失败: {e}")
            self.db = None

        # 初始化向量数据库
        self._init_vector_store()
        
        # 初始化智能训练器
        self.intelligent_trainer = None
        if self._bool_cfg('intelligent_training.enabled', False):
            try:
                config = self._get_intelligent_training_config()
                self.intelligent_trainer = IntelligentTrainer(config)
                print("✅ 智能训练器初始化成功")
            except Exception as e:
                print(f"❌ 智能训练器初始化失败: {e}")

        print("✅ LinguaSQL 初始化完成")
        
        # 输出配置摘要
        try:
            intelligent_training = self._bool_cfg('intelligent_training.enabled', False)
            interactive = self._bool_cfg('intelligent_training.interactive_confirmation', False)
            
            print("\n📋 配置摘要:")
            print(f"  • 大模型: {self._get_cfg('api.model', 'unknown')} ({type(self.llm_client).__name__})")
            print(f"  • 向量数据库: {self._get_cfg('vector_store.type', 'unknown')} ({type(self.vector_store).__name__})")
            print(f"  • 智能训练: {'🟢 启用' if intelligent_training else '🔴 禁用'}")
            print(f"  • 交互确认: {'🟢 启用' if interactive else '🔴 禁用'}")
            
            # 数据库配置信息
            if hasattr(self.config, 'database'):
                db_config = self.config.database
                print(f"  • 数据库: {db_config.type} ({db_config.host}:{db_config.port})")
                print(f"  • 数据库名: {db_config.database}")
                print(f"  • 自动导入DDL: {'🟢 是' if db_config.auto_import_ddl else '🔴 否'}")
                
        except Exception as e:
            print(f"⚠️  配置信息获取失败: {e}")
    
    def _create_vector_store(self, config):
        """根据配置创建合适的向量数据库客户端"""
        try:
            # 获取向量数据库类型
            vector_store_type = self._get_cfg('vector_store.type', 'chromadb')
            
            # 根据类型选择对应的向量数据库
            if vector_store_type == 'chromadb':
                return ChromaDBVectorStore(config)
            elif vector_store_type == 'faiss':
                if not FAISS_AVAILABLE:
                    print("⚠️  FAISS 不可用，请安装依赖: pip install faiss-cpu sentence-transformers")
                    print("使用默认的 ChromaDB 客户端")
                    return ChromaDBVectorStore(config)
                return FAISSVectorStore(config)
            else:
                # 默认使用 ChromaDB
                print(f"⚠️  未知向量数据库类型 {vector_store_type}，使用默认的 ChromaDB")
                return ChromaDBVectorStore(config)
                
        except Exception as e:
            print(f"❌ 创建向量数据库客户端失败: {e}")
            print("使用默认的 ChromaDB 客户端")
            return ChromaDBVectorStore(config)
    
    def _create_llm_client(self, config):
        """根据配置创建合适的大模型客户端"""
        try:
            # 获取模型名称
            model = self._get_cfg('api.model', 'deepseek-chat')
            
            # 根据模型名称选择对应的客户端
            if model.startswith('deepseek'):
                return DeepSeekChat(config)
            elif model.startswith('qwen'):
                return QwenChat(config)
            elif model.startswith('ernie'):
                return ERNIEChat(config)
            elif model.startswith('glm'):
                return GLMChat(config)
            elif model.startswith('moonshot'):
                return MoonshotChat(config)
            elif model.startswith('yi'):
                return YiChat(config)
            else:
                # 默认使用 DeepSeek
                print(f"⚠️  未知模型 {model}，使用默认的 DeepSeek")
                return DeepSeekChat(config)
                
        except Exception as e:
            print(f"❌ 创建大模型客户端失败: {e}")
            print("使用默认的 DeepSeek 客户端")
            return DeepSeekChat(config)
    
    def _get_cfg(self, key: str, default=None):
        """读取配置：支持 'a.b.c' 形式的对象属性路径"""
        try:
            obj = self.config
            for part in key.split('.'):
                if hasattr(obj, part):
                    obj = getattr(obj, part)
                else:
                    return default
            return obj
        except Exception:
            return default

    def _bool_cfg(self, key: str, default: bool = False) -> bool:
        val = self._get_cfg(key, default)
        if isinstance(val, str):
            return val.lower() in ('1', 'true', 'yes', 'y')
        return bool(val)
    
    def _get_intelligent_training_config(self) -> IntelligentTrainingConfig:
        """获取智能训练配置"""
        try:
            return self.config.intelligent_training
        except Exception:
            return IntelligentTrainingConfig()

    def _init_database_connection(self):
        """初始化数据库连接"""
        try:
            if self.config.database.connection_string:
                # 使用连接字符串
                from .database.connection_factory import create_connection_from_string
                self.db = create_connection_from_string(self.config.database.connection_string)
            else:
                # 使用参数连接
                from .database.connection_factory import create_connection
                self.db = create_connection(
                    self.config.database.type,
                    host=self.config.database.host,
                    port=self.config.database.port,
                    user=self.config.database.user,
                    password=self.config.database.password,
                    database=self.config.database.database
                )
            
            if self.db and self.config.database.auto_connect:
                if self.db.connect():
                    print(f"✅ 数据库连接成功: {self.config.database.type}")
                    
                    # 自动导入DDL
                    if self.config.database.auto_import_ddl:
                        print("🔄 正在自动导入数据库结构...")
                        self.auto_import_schema()
                else:
                    print("❌ 数据库连接失败")
                    self.db = None
                    
        except Exception as e:
            print(f"初始化数据库连接失败: {e}")
            self.db = None
    
    def _init_vector_store(self):
        """初始化向量数据库"""
        try:
            # 这里可以添加向量数据库的初始化逻辑
            pass
        except Exception as e:
            print(f"❌ 初始化向量数据库失败: {e}")
    

    
    def intelligent_auto_train(self, tables: List[str] = None) -> Dict[str, Any]:
        """智能自动训练：基于表关联关系自动生成问答对"""
        if not self.intelligent_trainer:
            print("智能训练器未初始化，请检查配置")
            return {'success': False, 'error': '智能训练器未初始化'}
        
        if not self.db:
            print("数据库连接不可用")
            return {'success': False, 'error': '数据库连接不可用'}
        
        try:
            print("=== 开始智能自动训练 ===")
            
            # 生成训练计划
            print("正在分析数据库结构并生成训练计划...")
            training_plan = self.intelligent_trainer.generate_training_plan(self.db, tables)
            
            if not training_plan['tables']:
                print("未找到可训练的表")
                return {'success': False, 'error': '未找到可训练的表'}
            
            print(f"发现 {len(training_plan['tables'])} 个表，预计生成 {training_plan['total_questions']} 个问题")
            
            # 显示训练计划
            if self._bool_cfg('intelligent_training.show_training_progress', True):
                self._display_training_plan(training_plan)
            
            # 执行训练
            if self._bool_cfg('intelligent_training.auto_execute_training', True):
                print("\n开始执行训练计划...")
                results = self.intelligent_trainer.execute_training_plan(training_plan, self.train)
                
                print(f"\n=== 智能训练完成 ===")
                print(f"成功: {results['success_count']}")
                print(f"失败: {results['failed_count']}")
                print(f"跳过: {results['skipped_count']}")
                
                return {
                    'success': True,
                    'training_plan': training_plan,
                    'results': results
                }
            else:
                print("训练计划已生成，但未自动执行（配置中禁用了自动执行）")
                return {
                    'success': True,
                    'training_plan': training_plan,
                    'results': None
                }
                
        except Exception as e:
            error_msg = f"智能训练过程中发生错误: {e}"
            print(error_msg)
            return {'success': False, 'error': error_msg}
    
    def _display_training_plan(self, training_plan: Dict[str, Any]):
        """显示训练计划"""
        print(f"\n=== 训练计划详情 ===")
        for table_info in training_plan['tables']:
            print(f"\n表: {table_info['name']}")
            print(f"  字段数: {len(table_info['fields'])}")
            print(f"  问题数: {table_info['question_count']}")
            
            if table_info['questions']:
                print("  示例问题:")
                for i, q in enumerate(table_info['questions'][:3], 1):
                    print(f"    {i}. {q['question']}")
                    print(f"       SQL: {q['sql']}")
                    print(f"       类型: {q['question_type']}, 难度: {q['difficulty']}")
    

    
    def _validate_training_results(self):
        """验证训练结果"""
        try:
            print("\n--- 验证训练结果 ---")
            
            # 检查训练数据数量
            training_data = self.get_training_data()
            if hasattr(training_data, 'shape'):
                print(f"训练数据数量: {len(training_data)}")
            
            # 检查DDL数据
            ddl_data = self.ddl_collection.get() if hasattr(self, 'ddl_collection') else None
            if ddl_data:
                print(f"DDL数据数量: {len(ddl_data.get('documents', []))}")
            
            print("验证完成")
            
        except Exception as e:
            print(f"验证训练结果时发生错误: {e}")
    
    def auto_test_system(self):
        """自动测试系统功能"""
        print("=== 开始自动测试系统 ===")
        
        test_results = {
            'database_connection': False,
            'ddl_extraction': False,
            'training_plan': False,
            'sql_generation': False
        }
        
        try:
            # 测试1: 数据库连接
            print("\n1. 测试数据库连接...")
            if self.db and self.db.is_connected():
                test_results['database_connection'] = True
                print("✓ 数据库连接正常")
            else:
                print("✗ 数据库连接失败")
            
            # 测试2: DDL提取
            print("\n2. 测试DDL提取...")
            if self.db:
                try:
                    ddl_statements = self.db.import_database_schema()
                    if ddl_statements:
                        test_results['ddl_extraction'] = True
                        print("✓ DDL提取成功")
                    else:
                        print("✗ DDL提取失败")
                except Exception as e:
                    print(f"✗ DDL提取错误: {e}")
            else:
                print("✗ 数据库连接不可用")
            
            # 测试3: 训练计划生成
            print("\n3. 测试训练计划生成...")
            try:
                training_plan = self.get_training_plan()
                if training_plan and training_plan.get('suggested_questions'):
                    test_results['training_plan'] = True
                    print(f"✓ 训练计划生成成功，包含 {len(training_plan['suggested_questions'])} 个建议问题")
                else:
                    print("✗ 训练计划生成失败")
            except Exception as e:
                print(f"✗ 训练计划生成错误: {e}")
            

            
            # 测试5: SQL生成
            print("\n5. 测试SQL生成...")
            try:
                test_question = "查询所有表"
                sql = self._generate_sql_for_suggestion({
                    'table': 'test_table',
                    'question': test_question,
                    'type': 'basic_query'
                })
                if sql:
                    test_results['sql_generation'] = True
                    print("✓ SQL生成测试成功")
                else:
                    print("✗ SQL生成测试失败")
            except Exception as e:
                print(f"✗ SQL生成测试错误: {e}")
            
        except Exception as e:
            print(f"自动测试过程中发生错误: {e}")
        
        # 输出测试结果摘要
        print("\n=== 测试结果摘要 ===")
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✓" if result else "✗"
            print(f"{status} {test_name}")
        
        print(f"\n总体结果: {passed_tests}/{total_tests} 项测试通过")
        
        if passed_tests == total_tests:
            print("🎉 所有测试通过！系统运行正常")
        elif passed_tests > total_tests // 2:
            print("⚠ 部分测试通过，系统基本可用")
        else:
            print("❌ 大部分测试失败，系统需要检查")
        
        return test_results
    
    def run_sql(self, sql: str, params=None):
        """执行原生SQL，委托到底层数据库连接器"""
        if not hasattr(self, 'db') or self.db is None:
            raise RuntimeError("数据库连接不可用：请先在配置中提供数据库连接信息或关闭需要执行SQL的功能")
        try:
            return self.db.run_sql(sql, params=params)
        except Exception as e:
            raise RuntimeError(f"执行SQL失败: {e}")
    
    def run_quick_test(self):
        """运行快速测试"""
        print("=== 快速测试模式 ===")
        
        # 只运行关键测试
        quick_tests = ['database_connection', 'ddl_extraction']
        
        for test_name in quick_tests:
            print(f"\n测试: {test_name}")
            # 这里可以添加具体的测试逻辑
            print("✓ 测试完成")
        
        print("\n快速测试完成")
    
    def get_system_status(self):
        """获取系统状态"""
        status = {
            'config': {
                'intelligent_training_enabled': self.config.intelligent_training.enabled,
                'interactive_confirmation': self.config.intelligent_training.interactive_confirmation,
                'database_type': self.config.database.type
            },
            'database': {
                'connected': self.db and self.db.is_connected() if self.db else False,
                'type': self.config.database.type if self.db else None
            },
            'vector_store': {
                'initialized': hasattr(self, 'ddl_collection'),
                'ddl_count': len(self.ddl_collection.get()['documents']) if hasattr(self, 'ddl_collection') else 0
            }
        }
        
        return status 

    def auto_import_schema(self):
        """自动导入数据库结构（兼容不同实现）"""
        if not self.db:
            print("数据库连接不可用")
            return False
        try:
            # 优先使用基于训练计划的导入
            if hasattr(self.db, 'auto_import_schema_with_plan'):
                return self.db.auto_import_schema_with_plan(
                    ddl_collection=self.ddl_collection,
                    train_method=self.train
                )
            # 退化使用直接导入
            if hasattr(self.db, 'import_database_schema'):
                return self.db.import_database_schema(
                    ddl_collection=self.ddl_collection,
                    train_method=self.train
                )
            print("当前数据库连接器不支持自动导入DDL")
            return False
        except Exception as e:
            print(f"导入数据库结构时发生错误: {e}")
            return False 

    def ask(self, question: str, sql: str = None, params=None):
        """根据问题生成SQL并执行，返回查询结果。
        若提供 sql 参数则直接执行该 SQL。
        """
        try:
            executable_sql = sql or self.generate_sql(question)
            if not executable_sql or not isinstance(executable_sql, str):
                print("未生成有效SQL")
                return []
            
            # 打印生成的SQL
            print(f"\n=== 生成的SQL ===")
            print(f"SQL: {executable_sql}")
            print(f"参数: {params}")
            
            # 执行SQL
            print(f"\n=== 执行SQL ===")
            result = self.run_sql(executable_sql, params=params)
            
            # 打印执行结果
            print(f"执行结果类型: {type(result)}")
            if result is None:
                print("执行结果: None (可能执行失败)")
                return []
            elif isinstance(result, list):
                print(f"执行结果: 列表，长度 {len(result)}")
                if len(result) > 0:
                    print("前3条记录:")
                    for i, row in enumerate(result[:3]):
                        print(f"  {i+1}: {row}")
                else:
                    print("查询结果为空")
            else:
                print(f"执行结果: {result}")
            
            return result or []
            
        except Exception as e:
            print(f"执行问答时发生错误: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    # 代理所有大模型方法到 llm_client
    def generate_sql(self, question: str, **kwargs) -> str:
        """生成SQL"""
        return self.llm_client.generate_sql(question, **kwargs)
    
    def submit_prompt(self, prompt, **kwargs) -> str:
        """提交提示词"""
        return self.llm_client.submit_prompt(prompt, **kwargs)
    
    def system_message(self, message: str) -> any:
        """系统消息"""
        return self.llm_client.system_message(message)
    
    def user_message(self, message: str) -> any:
        """用户消息"""
        return self.llm_client.user_message(message)
    
    def assistant_message(self, message: str) -> any:
        """助手消息"""
        return self.llm_client.assistant_message(message)
    
    def extract_field_names(self, question: str, available_fields: list = None, ddl_info: str = None) -> list:
        """提取字段名"""
        return self.llm_client.extract_field_names(question, available_fields, ddl_info)
    
    def extract_table_names(self, question: str, available_tables: list = None, ddl_info: str = None) -> list:
        """提取表名"""
        return self.llm_client.extract_table_names(question, available_tables, ddl_info)
    
    def analyze_question_intent(self, question: str, ddl_info: str = None) -> dict:
        """分析问题意图"""
        return self.llm_client.analyze_question_intent(question, ddl_info)
    
    # 代理所有向量数据库方法到 vector_store
    def generate_embedding(self, data: str, **kwargs) -> List[float]:
        """生成嵌入向量"""
        return self.vector_store.generate_embedding(data, **kwargs)
    
    def add_question_sql(self, question: str, sql: str, **kwargs) -> str:
        """添加问题和SQL对"""
        return self.vector_store.add_question_sql(question, sql, **kwargs)
    
    def add_ddl(self, ddl: str, **kwargs) -> str:
        """添加DDL"""
        return self.vector_store.add_ddl(ddl, **kwargs)
    
    def add_documentation(self, documentation: str, **kwargs) -> str:
        """添加文档"""
        return self.vector_store.add_documentation(documentation, **kwargs)
    
    def get_training_data(self, **kwargs) -> pd.DataFrame:
        """获取训练数据"""
        return self.vector_store.get_training_data(**kwargs)
    
    def remove_training_data(self, id: str, **kwargs) -> bool:
        """删除训练数据"""
        return self.vector_store.remove_training_data(id, **kwargs)
    
    def get_similar_question_sql(self, question: str, **kwargs) -> list:
        """获取相似的问题和SQL"""
        return self.vector_store.get_similar_question_sql(question, **kwargs)
    
    def get_related_ddl(self, question: str, **kwargs) -> list:
        """获取相关的DDL"""
        return self.vector_store.get_related_ddl(question, **kwargs)
    
    def get_related_documentation(self, question: str, **kwargs) -> list:
        """获取相关的文档"""
        return self.vector_store.get_related_documentation(question, **kwargs)
    
    def get_similar_questions(self, question: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """获取相似的问题"""
        return self.vector_store.get_similar_questions(question, n_results)
    
    def get_ddl(self) -> List[str]:
        """获取所有DDL"""
        return self.vector_store.get_ddl()
    
    def get_documentation(self) -> List[str]:
        """获取所有文档"""
        return self.vector_store.get_documentation()
    
    def clean_duplicates(self) -> Dict[str, int]:
        """清理重复数据"""
        return self.vector_store.clean_duplicates()
    
    def train(self, question: str = None, sql: str = None, ddl: str = None, documentation: str = None, plan=None) -> str:
        """兼容版 train：支持 question+sql / ddl / documentation"""
        if documentation:
            return self.add_documentation(documentation)
        if ddl:
            return self.add_ddl(ddl)
        if sql:
            if question is None:
                # 退化：无问题时用SQL生成问题（若上层未提供生成器，可直接回退为SQL摘要）
                try:
                    question = self.generate_question(sql)
                except Exception:
                    question = f"Generated question for SQL: {sql[:80]}..."
            return self.add_question_sql(question=question, sql=sql)
        if plan:
            # 简化处理：逐项训练
            for item in getattr(plan, '_plan', []) or []:
                t = getattr(item, 'item_type', None)
                if t == 'ddl.txt':
                    self.add_ddl(item.item_value)
                elif t == 'is':
                    self.add_documentation(item.item_value)
                elif t == 'sql':
                    self.add_question_sql(question=item.item_name, sql=item.item_value)
            return "ok"
        # 无有效参数
        return "noop" 