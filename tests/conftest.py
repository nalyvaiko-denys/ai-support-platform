import os

os.environ["DATABASE_URL"] = (
    "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_support_test"
)
os.environ["LLM_PROVIDER"] = "mock"
