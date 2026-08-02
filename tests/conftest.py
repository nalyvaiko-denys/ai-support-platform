import os

os.environ["DATABASE_URL"] = (
    "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_support_test"
)
os.environ["LLM_PROVIDER"] = "mock"
os.environ["AUTH_MODE"] = "jwt"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["JWT_SECRET"] = "test-secret-that-is-long-enough-for-hs256"
os.environ["JWT_ISSUER"] = "ai-support-platform"
os.environ["JWT_AUDIENCE"] = "ai-support-api"
