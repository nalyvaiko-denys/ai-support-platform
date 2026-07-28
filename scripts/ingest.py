import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.db.session import AsyncSessionLocal
from app.llm.openai_client import OpenAIClient
from app.services.embedding_service import EmbeddingService
from app.services.ingest_service import IngestService


async def main() -> None:
    data_dir = Path(__file__).resolve().parent.parent / "data"
    sample_file = data_dir / "monobank_faq.md"

    if not sample_file.exists():
        print(f"Файл {sample_file} не знайдено!")
        return

    client = OpenAIClient()
    embedding_service = EmbeddingService(client)

    async with AsyncSessionLocal() as session:
        ingest_service = IngestService(
            db=session,
            embedding_service=embedding_service,
        )

        await ingest_service.ingest_file(
            file_path=sample_file,
            source="monobank_faq",
        )

    print("✅ База знань успішно завантажена!")


if __name__ == "__main__":
    asyncio.run(main())