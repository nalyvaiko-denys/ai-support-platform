# scripts/ingest.py
import asyncio
import sys
from pathlib import Path

# Додаємо корінь проєкту в PYTHONPATH, щоб працювали імпорти app.*
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.db.session import AsyncSessionLocal
from app.llm.openai_client import OpenAIClient
from app.models.document import DocumentChunk

# Налаштування чанкінгу
CHUNK_SIZE = 1000  # приблизна кількість символів у чанку
CHUNK_OVERLAP = 200  # перекриття між чанками для збереження контексту


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Розбиває текст на частини заданого розміру з перекриттям."""
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + size
        chunk = text[start:end]

        if end < text_length:
            last_space = max(chunk.rfind(' '), chunk.rfind('\n'))
            if last_space != -1:
                end = start + last_space
                chunk = text[start:end]

        chunks.append(chunk.strip())
        start = end - overlap

    return [c for c in chunks if c]  # відфільтровуємо порожні


async def process_file(file_path: Path, source_name: str, client: OpenAIClient) -> None:
    print(f"📄 Читаємо файл: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text(text)
    print(f"✂️ Текст розбито на {len(chunks)} чанків. Починаємо векторизацію...")

    async with AsyncSessionLocal() as session:
        for i, chunk_text_content in enumerate(chunks, 1):
            try:
                # Отримуємо вектор від OpenAI
                embedding = await client.create_embedding(chunk_text_content)

                # Створюємо запис для БД
                doc = DocumentChunk(
                    source=source_name,
                    content=chunk_text_content,
                    embedding=embedding
                )
                session.add(doc)

                print(f"✅ Оброблено чанк {i}/{len(chunks)}")

                # Невелика пауза, щоб не натрапити на Rate Limit від OpenAI
                await asyncio.sleep(0.1)

            except Exception as e:
                print(f"❌ Помилка обробки чанку {i}: {e}")

        await session.commit()
    print(f"🎉 Файл {source_name} успішно завантажено в базу знань!")


async def main() -> None:
    # Шлях до файлу з даними
    data_dir = Path(__file__).resolve().parent.parent / "data"
    sample_file = data_dir / "monobank_faq.md"

    if not sample_file.exists():
        print(f"Файл {sample_file} не знайдено! Створіть його та додайте туди текст.")
        return

    client = OpenAIClient()
    await process_file(sample_file, "monobank_faq", client)


if __name__ == "__main__":
    asyncio.run(main())