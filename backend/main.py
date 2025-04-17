from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from file_indexer import LogIndexer
import uvicorn
import os
import logging
from fastapi.staticfiles import StaticFiles

# 初始化应用
app = FastAPI(title="Log Analyzer API")
indexer = LogIndexer(os.path.join(os.path.dirname(__file__), "file_index.db"))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 仅在正式环境挂载静态文件
if os.getenv("ENV_MODE") == "production":
    dist_path = os.path.abspath("frontend/dist")
    if os.path.exists(dist_path):
        app.mount("/static", StaticFiles(directory=dist_path), name="static")
    else:
        print("⚠️  未找到前端构建文件，跳过静态资源挂载")

@app.get("/")
def read_root():
    return {"message": "Log Analyzer API", "status": "running"}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}

@app.post("/api/index-file")
async def index_file(file_path: str):
    if not os.path.exists(file_path):
        raise HTTPException(404, "File not found")
    try:
        indexer.index_file(file_path)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Indexing failed: {str(e)}")
        raise HTTPException(500, "Indexing error")

@app.get("/api/search-sequence")
def search_sequence(keywords: str):
    try:
        kw_list = [k.strip() for k in keywords.split(",") if k.strip()]
        sequence = indexer.get_sequence(kw_list)
        return {"data": sequence}
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(400, "Invalid request")

@app.get("/api/get-log-line")
def get_log_line(position: int, file_path: str):
    try:
        with open(file_path, "rb") as f:
            f.seek(position)
            line = f.readline().decode("utf-8", errors="replace")
            return {"content": line.strip()}
    except Exception as e:
        logger.error(f"Log read error: {str(e)}")
        raise HTTPException(500, "File read failed")

if __name__ == "__main__":
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('0.0.0.0', 8000))  # 检查端口可用性
        sock.close()
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except OSError as e:
        print(f"❌ 端口8000被占用，请关闭其他服务后再试。错误详情: {str(e)}")
        exit(1)