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
        chunks: list[str] = []

        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size

            chunk = text[start:end]

            if end < text_length:
                last_space = max(
                    chunk.rfind(" "),
                    chunk.rfind("\n"),
                )

                if last_space != -1:
                    end = start + last_space
                    chunk = text[start:end]

            chunks.append(chunk.strip())

            start = end - overlap

        return [chunk for chunk in chunks if chunk]