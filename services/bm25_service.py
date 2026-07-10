from services.tokenizer_service import Tokenizer
import bm25s
from core.logging import logger
import json
from pathlib import Path

class Bm25Service:
    def __init__(self, tokenizer: Tokenizer):
        self.tokenizer = tokenizer
        self.retriever = bm25s.BM25()
        self.load_index()

    def load_index(self):
        """
            Loads the 'bm25_index' if created else it returns a logger message.
        """
        try:
            self.retriever = bm25s.BM25.load("storage/bm25_index")
        except FileNotFoundError:
            logger.info("No BM25 index found. Starting with an empty index...")

    def build_index(self, chunks):
        """
            Creates a corpus using the tokens created from the text of all the chunks
            Creates an index from the corpus and stores it in bm25_index.
            Writes the chunks to 'chunks.json' in the storage folder.
            If there are chunks already present in the 'chunks.json' file then the contents
            are re-written along with the latest chunks.
        """
        tokenized_corpus = [
                            self.tokenizer.tokenize(chunk.text) 
                            for chunk in chunks
                        ]
        self.retriever.index(tokenized_corpus)
        self.retriever.save("storage/bm25_index")
        chunks_file = Path("storage/chunks.json")
        if chunks_file.exists():
            with chunks_file.open("r", encoding="utf-8") as f:
                chunks = json.load(f)
        else:
            chunks = []

        chunks.extend([chunk.model_dump(mode="json") for chunk in chunks])

        with open("storage/chunks.json", "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent = 2, ensure_ascii=False)

    def retrieval(self, query):
        """
            Tokenizes the query.
            Retrieves the top 5 chunks with highest scores from the 'bm25_index'.
            'Results' gives you the list of all the chunk indices and 'scores' gives you the list of scores.
            We then obtain the chunks by mapping the indices given in results to the chunk index in 
            'chunks.json'
        """
        tokenized_query = self.tokenizer.tokenize(query)
        results, scores = self.retriever.retrieve([tokenized_query], k=5)
        with open("storage/chunks.json", "r", encoding="utf-8") as f:
            chunks = json.load(f)
        bm25_matches = [chunks[index] for index in results[0]]
        return bm25_matches