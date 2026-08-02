import pytest

from app.llm.chunker import TextChunker


def test_returns_empty_list_for_blank_text() -> None:
    assert TextChunker.chunk("") == []
    assert TextChunker.chunk("   \n\t") == []


def test_splits_long_text_into_non_empty_chunks() -> None:
    text = " ".join(f"word-{index}" for index in range(200))

    chunks = TextChunker.chunk(
        text,
        chunk_size=120,
        overlap=20,
    )

    assert len(chunks) > 1
    assert all(chunks)
    assert all(len(chunk) <= 120 for chunk in chunks)


@pytest.mark.parametrize(
    ("chunk_size", "overlap"),
    [
        (0, 0),
        (-1, 0),
        (100, -1),
        (100, 100),
        (100, 101),
    ],
)
def test_rejects_invalid_parameters(
    chunk_size: int,
    overlap: int,
) -> None:
    with pytest.raises(ValueError):
        TextChunker.chunk(
            "example text",
            chunk_size=chunk_size,
            overlap=overlap,
        )
