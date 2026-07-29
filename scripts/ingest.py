import asyncio
from pathlib import Path

from app.db.session import AsyncSessionLocal
from app.llm.factory import get_llm_client
from app.repositories.document_repository import (
    DocumentRepository,
)
from app.services.embedding_service import EmbeddingService
from app.services.ingest_service import IngestService


async def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    sample_file = project_root / "data" / "bank_faq.md"

    if not sample_file.is_file():
        raise FileNotFoundError(
            f"Knowledge-base file was not found: {sample_file}"
        )

    client = get_llm_client()
    embedding_service = EmbeddingService(client)

    async with AsyncSessionLocal() as session:
        repository = DocumentRepository(session)

        ingest_service = IngestService(
            db=session,
            repository=repository,
            embedding_service=embedding_service,
        )

        result = await ingest_service.ingest_file(
            file_path=sample_file,
            source="monobank_faq",
        )

    if not result.changed:
        print("Knowledge base is already up to date.")
        return

    print(
        "Knowledge base updated: "
        f"{result.chunks_written} chunks written."
    )


if __name__ == "__main__":
    asyncio.run(main())
