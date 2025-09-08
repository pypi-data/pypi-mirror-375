import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from lingua_sql import LinguaSQL
from lingua_sql.config import LinguaSQLConfig, DatabaseConfig, IntelligentTrainingConfig, APIConfig
from lingua_sql.fastapi import LinguaSQLFastAPIApp

# 加载环境变量
load_dotenv()

# 使用新的配置对象格式
config = LinguaSQLConfig(
    # API配置
    api=APIConfig(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        model="deepseek-chat",
        client="persistent",
        path="/Users/a4869/project/python/text2sql/lingua_sql/examples",
    ),
    
    # 数据库配置
    database=DatabaseConfig(
        type="mysql",
        host="172.22.182.17",
        port=3306,
        user="root",
        password="O.-47Tz?",
        database="auto_form_filling",
        auto_connect=True,
        auto_import_ddl=False,  # 禁用自动导入DDL
    ),
    
    # 智能训练配置
    intelligent_training=IntelligentTrainingConfig(
        enabled=True,
        max_questions_per_table=30,  # 每个表最多30个问题（3个关联字段 × 10个问题）
        max_related_fields=3,        # 最多选择3个关联字段
        auto_generate_sql=True,      # 自动执行训练
        show_training_progress=True,  # 显示训练进度
        use_sample_data=True,        # 使用大模型生成问答对
        interactive_confirmation=False,  # 关闭交互以便非阻塞运行
    ),
    
    # 调试模式
    debug=True
)

# 初始化 LinguaSQL
nl = LinguaSQL(config=config)


# 方法1: 智能训练所有表

# result = nl.intelligent_auto_train()

nl.ask("查找唯一标识为1688438的学号")

app = LinguaSQLFastAPIApp(nl)


if __name__ == "__main__":
    app.run(host="localhost", port=8085)
    


    
    
