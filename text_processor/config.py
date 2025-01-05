from dataclasses import dataclass

@dataclass
class ProcessorConfig:
    default_chunk_size: int = 2000
    min_similarity_score: float = 0.3
    max_chunks_to_combine: int = 5