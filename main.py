from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from database import init_db
from routers import collect, knowledge, search

app = FastAPI(
    title="ScribeAI API",
    description="个人知识管理AI助手后端",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(collect.router)
app.include_router(knowledge.router)
app.include_router(search.router)


@app.on_event("startup")
def startup_event():
    init_db()
    print("=== ScribeAI 后端启动成功 ===")


@app.middleware("http")
async def log_requests(request, call_next):
    print(f"收到请求: {request.method} {request.url.path}")
    response = await call_next(request)
    print(f"响应状态: {response.status_code}")
    return response


@app.get("/")
def root():
    return {"message": "ScribeAI API", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/index.html")
def serve_index():
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    return FileResponse(frontend_path)


@app.get("/app")
@app.get("/frontend")
@app.get("/home")
def serve_index_alias():
    return serve_index()


if __name__ == "__main__":
    import uvicorn
    import os
    from dotenv import load_dotenv

    load_dotenv()

    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
