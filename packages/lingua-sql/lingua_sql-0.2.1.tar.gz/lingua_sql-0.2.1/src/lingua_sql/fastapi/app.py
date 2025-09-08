import os
import re
from dotenv import load_dotenv


load_dotenv()

import uvicorn
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import pandas as pd
from .cache import MemoryCache
from mysql.connector import Error


def _build_fastapi_app(nl, cache: MemoryCache, static_dir: str) -> FastAPI:
    app = FastAPI()

    # 静态文件服务
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # 允许跨域
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class RemoveTrainingDataRequest(BaseModel):
        id: str

    class AddTrainingDataRequest(BaseModel):
        question: Optional[str] = None
        sql: Optional[str] = None
        ddl: Optional[str] = None
        documentation: Optional[str] = None

    @app.get("/api/v0/generate_questions")
    def generate_questions():
        return JSONResponse({
            "type": "question_list",
            "questions": nl.generate_questions(),
            "header": "这里有一些你可以问的问题:"
        })

    @app.get("/api/v0/generate_sql")
    def generate_sql(question: str):
        if not question:
            return JSONResponse({"type": "error", "error": "缺少问题参数"})
        id = cache.generate_id(question=question)
        sql = nl.generate_sql(question=question)
        cache.set(id=id, field='question', value=question)
        cache.set(id=id, field='sql', value=sql)
        return JSONResponse({
            "type": "sql",
            "id": id,
            "text": sql,
        })

    @app.get("/api/v0/run_sql")
    def run_sql(id: str):
        sql = cache.get(id=id, field='sql')
        if sql is None:
            return JSONResponse({"type": "error", "error": "未找到对应的SQL，请先生成SQL"})
        try:
            df = nl.run_sql(sql=sql)
            if isinstance(df, list):
                df = pd.DataFrame(df)
            cache.set(id=id, field='df', value=df)
            
            # 判断是否需要生成图表：数据行数 > 1 且列数 > 1
            should_generate_chart = False
            try:
                if hasattr(df, 'shape') and len(df.shape) == 2:
                    rows, cols = df.shape
                    should_generate_chart = rows > 1 and cols > 1
            except Exception:
                should_generate_chart = False
            
            return JSONResponse({
                "type": "df",
                "id": id,
                "df": df.head(10).to_json(orient='records'),
                "should_generate_chart": should_generate_chart,
            })
        except Exception as e:
            return JSONResponse({"type": "error", "error": str(e)})

    @app.get("/api/v0/download_csv")
    def download_csv(id: str):
        df = cache.get(id=id, field='df')
        if df is None:
            raise HTTPException(status_code=404, detail="No df found")
        csv = df.to_csv()
        return Response(content=csv, media_type="text/csv", headers={"Content-disposition": f"attachment; filename={id}.csv"})

    @app.get("/api/v0/generate_plotly_figure")
    def generate_plotly_figure(id: str):
        df = cache.get(id=id, field='df')
        question = cache.get(id=id, field='question')
        sql = cache.get(id=id, field='sql')
        if df is None or question is None or sql is None:
            return JSONResponse({"type": "error", "error": "缺少必要的缓存字段，请先生成并执行SQL"})
        try:
            code = nl.generate_plotly_code(question=question, sql=sql, df_metadata=f"Running df.dtypes gives:\n {df.dtypes}")
            fig = nl.get_plotly_figure(plotly_code=code, df=df, dark_mode=False)
            fig_json = fig.to_json()
            cache.set(id=id, field='fig_json', value=fig_json)
            return JSONResponse({
                "type": "plotly_figure",
                "id": id,
                "fig": fig_json,
            })
        except Exception as e:
            return JSONResponse({"type": "error", "error": str(e)})

    @app.get("/api/v0/get_training_data")
    def get_training_data():
        df = nl.get_training_data()
        if df is None or len(df) == 0:
            return JSONResponse({"type": "error", "error": "暂无训练数据，请先导入"})
        return JSONResponse({
            "type": "df",
            "id": "training_data",
            "df": df.head(25).to_json(orient='records'),
        })

    @app.post("/api/v0/remove_training_data")
    def remove_training_data(req: RemoveTrainingDataRequest):
        id = req.id
        if not id:
            return JSONResponse({"type": "error", "error": "缺少id参数"})
        if nl.remove_training_data(id=id):
            return JSONResponse({"success": True})
        else:
            return JSONResponse({"type": "error", "error": "删除训练数据失败"})

    @app.post("/api/v0/train")
    def add_training_data(req: AddTrainingDataRequest):
        try:
            nl.train(question=req.question, sql=req.sql, ddl=req.ddl, documentation=req.documentation)
            import uuid
            id = str(uuid.uuid4())
            return JSONResponse({"id": id})
        except Exception as e:
            return JSONResponse({"type": "error", "error": str(e)})

    @app.get("/api/v0/generate_followup_questions")
    def generate_followup_questions(id: str):
        df = cache.get(id=id, field='df')
        question = cache.get(id=id, field='question')
        sql = cache.get(id=id, field='sql')
        if df is None or question is None or sql is None:
            return JSONResponse({"type": "error", "error": "缺少必要的缓存字段，请先生成并执行SQL"})
        followup_questions = nl.generate_followup_questions(question=question, sql=sql, df=df)
        cache.set(id=id, field='followup_questions', value=followup_questions)
        return JSONResponse({
            "type": "question_list",
            "id": id,
            "questions": followup_questions,
            "header": "以下是一些可继续追问的问题："
        })

    @app.get("/api/v0/load_question")
    def load_question(id: str):
        question = cache.get(id=id, field='question')
        sql = cache.get(id=id, field='sql')
        df = cache.get(id=id, field='df')
        fig_json = cache.get(id=id, field='fig_json')
        followup_questions = cache.get(id=id, field='followup_questions')
        if None in [question, sql, df, fig_json, followup_questions]:
            return JSONResponse({"type": "error", "error": "缺少必要的缓存字段"})
        try:
            return JSONResponse({
                "type": "question_cache",
                "id": id,
                "question": question,
                "sql": sql,
                "df": df.head(10).to_json(orient='records'),
                "fig": fig_json,
                "followup_questions": followup_questions,
            })
        except Exception as e:
            return JSONResponse({"type": "error", "error": str(e)})

    @app.get("/api/v0/get_question_history")
    def get_question_history():
        return JSONResponse({"type": "question_history", "questions": cache.get_all(field_list=['question']) })

    @app.get("/")
    def root():
        index_path = os.path.join(static_dir, "index.html")
        return FileResponse(index_path)

    return app


class LinguaFastapiAPI:
    def __init__(self, nl, cache: MemoryCache = None, debug: bool = True, static_dir: str = None):
        self.nl = nl
        self.cache = cache or MemoryCache()
        self.debug = debug
        if static_dir is None:
            static_dir = os.path.join(os.path.dirname(__file__), 'static')
        self.static_dir = static_dir
        self.app = _build_fastapi_app(nl=self.nl, cache=self.cache, static_dir=self.static_dir)

    def run(self, host: str = "127.0.0.1", port: int = 8000, debug=None, app_import_string: str = None, factory: bool = False, **kwargs):
        # uvicorn 的 reload 仅支持传入 import string；当我们传 app 对象时会警告。
        if debug is None:
            debug = getattr(self, 'debug', False)

        if app_import_string and debug:
            # 使用 import string + 可选 factory 支持热重载
            kwargs.setdefault('reload', True)
            uvicorn.run(app_import_string, host=host, port=port, factory=factory, **kwargs)
            return

        # 传入对象时禁用 reload，避免告警
        kwargs.pop('reload', None)
        uvicorn.run(self.app, host=host, port=port, **kwargs)


class LinguaFastapiApp(LinguaFastapiAPI):
    def __init__(
        self,
        nl,
        cache: MemoryCache = None,
        debug: bool = True,
        static_dir: str = None,
        logo: str = None,
        title: str = None,
        subtitle: str = None,
    ):
        super().__init__(nl=nl, cache=cache, debug=debug, static_dir=static_dir)
        # 可扩展：在未来加入配置获取端点，与 Vanna 的 Flask 版本保持一致
        self.config = {
            "logo": logo,
            "title": title,
            "subtitle": subtitle,
            "debug": debug,
        }


def create_default_app() -> FastAPI:
    """仅在脚本运行时创建默认应用，避免导入时产生副作用。"""
    try:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lingua_sql', 'src'))

        from lingua_sql import LinguaSQL
        from lingua_sql.config import LinguaSQLConfig, DatabaseConfig, APIConfig

        deepseek_api_key = os.environ.get('DEEPSEEK_API_KEY')
        if not deepseek_api_key:
            print("Warning: DEEPSEEK_API_KEY not set. Some features may not work.")
            deepseek_api_key = "dummy_key"

        config = LinguaSQLConfig(
            api=APIConfig(
                api_key=deepseek_api_key,
                model="deepseek-chat",
                client="persistent",
                path=os.environ.get('CHROMA_PERSIST_DIRECTORY', './')
            ),
            database=DatabaseConfig(
                type="mysql",
                host=os.environ.get('DB_HOST', 'localhost'),
                port=3306,
                user=os.environ.get('DB_USER', 'root'),
                password=os.environ.get('DB_PASSWORD', ''),
                database=os.environ.get('DB_DATABASE', ''),
                auto_import_ddl=False
            ),
            debug=False
        )

        _nl = LinguaSQL(config=config)
    except Exception as e:
        print(f"Error initializing LinguaSQL: {e}")
        print("Creating mock LinguaSQL instance for testing...")
        class MockLinguaSQL:
            def ask(self, question):
                return [{"message": f"Mock response for: {question}"}]
            def train(self, **kwargs):
                return "mock_id"
            def run_sql(self, sql: str, params: Optional[tuple] = None) -> Optional[pd.DataFrame]:
                return pd.DataFrame([])
            def generate_questions(self, **kwargs):
                return ["示例问题1", "示例问题2", "示例问题3"]
            def generate_sql(self, question: str, **kwargs):
                return f"SELECT * FROM example WHERE condition = '{question}'"
            def generate_plotly_code(self, **kwargs):
                return "import plotly.express as px\nfig = px.bar(df, x='x', y='y')\nfig.show()"
            def get_plotly_figure(self, **kwargs):
                import plotly.graph_objects as go
                fig = go.Figure()
                fig.add_trace(go.Bar(x=[1, 2, 3], y=[1, 2, 3]))
                return fig
            def get_training_data(self):
                return pd.DataFrame({"question": ["示例问题"], "sql": ["示例SQL"]})
        _nl = MockLinguaSQL()

    _default_cache = MemoryCache()
    _STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
    return _build_fastapi_app(nl=_nl, cache=_default_cache, static_dir=_STATIC_DIR)


if __name__ == "__main__":
    app = create_default_app()
    uvicorn.run(app, host="127.0.0.1", port=8000)
