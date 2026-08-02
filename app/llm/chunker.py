class TextChunker:
    DEFAULT_CHUNK_SIZE = 1000
    DEFAULT_OVERLAP = 200

    @classmethod
    def chunk(
        cls,
        text: str,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap: int = DEFAULT_OVERLAP,
    ) -> list[str]:
        cls._validate_parameters(
            chunk_size=chunk_size,
            overlap=overlap,
        )

        if not text.strip():
            return []

        chunks: list[str] = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + chunk_size, text_length)

            if end < text_length:
                candidate = text[start:end]
                last_break = max(
                    candidate.rfind("\n"),
                    candidate.rfind(" "),
                )

                if last_break >= chunk_size // 2:
                    end = start + last_break

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end >= text_length:
                break

            next_start = end - overlap
            start = next_start if next_start > start else end

        return chunks

    @staticmethod
    def _validate_parameters(
        *,
        chunk_size: int,
        overlap: int,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")

        if overlap < 0:
            raise ValueError("overlap must not be negative")

        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")
