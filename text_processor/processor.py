from typing import List, Dict
import tiktoken
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from .config import ProcessorConfig
from .utils import timing_decorator


class TextProcessor:
    def __init__(self, model_name="gpt-3.5-turbo", max_tokens=60000):
        self.encoding = tiktoken.encoding_for_model(model_name)
        self.max_tokens = max_tokens
        self.vectorizer = TfidfVectorizer()

    @timing_decorator
    def process_file_content(self, file_content: str, user_query: str) -> str:
        chunks = self.split_into_chunks(file_content)
        chunk_vectors = self.vectorize_chunks(chunks)
        relevant_chunks = self.find_relevant_chunks(user_query, chunks, chunk_vectors)
        return self.combine_chunks(relevant_chunks, user_query)