from fastapi import FastAPI
from fastapi.responses import JSONResponse
import logging, sys
from routers import auth, files

app = FastAPI(title="CloudFS API", version="0.2")
app.include_router(auth.router)
app.include_router(files.router)

@app.get("/health")
async def health():
    return JSONResponse({"status": "ok"})

# —— logging config ——
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("/var/log/cloudfs.log"),
        logging.StreamHandler(sys.stdout)
    ],
)

