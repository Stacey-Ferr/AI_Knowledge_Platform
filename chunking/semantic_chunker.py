from services.embedding_service import EmbeddingService
from schemas.file_chunk import FileChunk
from core.logging import logger
import numpy as np
import re

class SemanticChunker:
    def __init__(self, embedding_service: EmbeddingService, threshold: 0.75):
        self.embedding_service = embedding_service
        self.similarity_threshold = threshold

    def extract_metadata(self, metadata):
        """
            Extracting metadata such as:
            - Document Name
            - Section Title
            - Page numbers
        """
        page_numbers, section_title, document_name = set(), [], ""
        for element in metadata:
            if type(element).__name__ == "Title":
                section_title.append(str(element))
            if getattr(element.metadata, "filename", None):
                document_name = element.metadata.filename
            if element.metadata.page_number:
                page_numbers.add(element.metadata.page_number)
        return list(page_numbers), section_title, document_name

    def chunking(self, chunks, document_id):
        """
            Further splitting chunks that have more than 15 sentences and are meaningful (i.e. average word length should be more than 5 characters and punctuations should be less than 20% of the total content)
        """
        chunk_index, final_chunks = 0, []

        for chunk in chunks:
            sentences = []
            avg_word_length = 0
            no_of_sentences = 0
            punctuation_count = 0
            # Splitting the chunk text based on '.', '!', '?' characters
            for sentence in re.split(r'(?<=[.!?])\s+|\n+', chunk.text):
                if sentence.strip():
                    sentences.append(sentence.strip())
                    avg_word_length += len(sentence.split())
                    punctuation_count += len(re.findall(r'[.:]', sentence))
                    no_of_sentences += 1
            avg_word_length /= no_of_sentences
            punctuation_count /= no_of_sentences

            page_numbers, section_title, document_name = self.extract_metadata(chunk.metadata.orig_elements)

            if no_of_sentences <= 15 or avg_word_length < 5 or punctuation_count > 0.2:
                final_chunks.append(FileChunk(
                    text = " ".join(sentences),
                    document_id = document_id,
                    document_name = document_name,
                    page_numbers = page_numbers,
                    section_title = section_title,
                    chunk_index = chunk_index
                ))
                chunk_index += 1
                continue

            embeddings = self.embedding_service.embed_batch(sentences)
            similarities = []

            # Calculating the similarity scores of adjacent sentences
            for index in range (1, len(sentences)):
                v1, v2 = np.array(embeddings[index - 1]), np.array(embeddings[index])
                similarity_score = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                similarities.append(similarity_score)

            # Calculating the mean and std dev of the similarity scores of the entire chunk
            mean_similarity = np.mean(similarities)
            std_similarity = np.std(similarities)
            # Establishing the new similarity threshold using mean and std dev
            self.similarity_threshold = mean_similarity - std_similarity            

            # Finds the index of all the sentences whose similarity score is below the threshold
            indices = [i+1 for i in range(len(similarities)) if similarities[i] < self.similarity_threshold]
            start_index = 0

            try:
                # Splits the chunks on the sentence indices which went below the similarity score threshold
                for val in indices:
                    if val+1 < len(sentences):
                        final_chunks.append(FileChunk(
                            text = " ".join(sentences[start_index:val+1]),
                            document_id = document_id,
                            document_name = document_name,
                            page_numbers = page_numbers,
                            section_title = section_title,
                            chunk_index = chunk_index
                        ))
                        chunk_index += 1
                        start_index = val + 1
                    elif val+1 == len(sentences):
                        # This is an edge case where the index is the index of the last sentence
                        val = start_index - 1
                # Adds the last part of the chunk to the final chunk
                final_chunks.append(FileChunk(
                    text = " ".join(sentences[val+1:]),
                    document_id = document_id,
                    document_name = document_name,
                    page_numbers = page_numbers,
                    section_title = section_title,
                    chunk_index = chunk_index
                ))
                chunk_index += 1
            except Exception as e:
                logger.exception(f"Exception: '{e}' occurred")

        return final_chunks