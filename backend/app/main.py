from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.endpoints import auth as api_v1_auth_router
from app.api.v1.endpoints import files as api_v1_files_router # Add files router
from app.api.v1.endpoints import users as api_v1_users_router # Add users router
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_auth_router.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(api_v1_files_router.router, prefix="/api/v1/files", tags=["Files"]) # Add files router
app.include_router(api_v1_users_router.router, prefix="/api/v1/users", tags=["Users"]) # Add users router
@app.get("/")
async def root():
    return {"message": "Welcome to the Cloud File System API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}