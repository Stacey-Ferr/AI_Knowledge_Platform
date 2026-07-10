from services.embedding_service import EmbeddingService
from schemas.file_chunk import FileChunk
import numpy as np
import re

class SemanticChunker:
    def __init__(self, embedding_service: EmbeddingService, batch_size = 500):
        self.embedding_service = embedding_service
        self.max_embedding_batch_size = batch_size

    def sentence_processing(self, chunk_text):
        """
            Splits the chunk text into sentences whenever a '.', '!' or a '?' is encountered.
            Calculates the average word count and average punctuation count in a sentence.
        """
        sentences, avg_word_count, avg_punctuation_count  = [], 0, 0
        for sentence in re.split(r'(?<=[.!?])\s+|\n+', chunk_text):
            if sentence.strip():
                sentences.append(sentence.strip())
                avg_word_count += len(sentence.split())
                avg_punctuation_count += len(re.findall(r'[.,;:!?]', sentence))

        sentence_length = len(sentences)

        if sentence_length > 0:
            avg_word_count /= sentence_length
            avg_punctuation_count /= sentence_length

        return sentences, sentence_length, avg_word_count, avg_punctuation_count

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

    def calculate_similarity_score(self, embeddings):
        """
            Calculates the cosine similarity, as the similarity score, of two adjacent sentences.
            Similarity threshold is dynamically calculated per batch using the mean and standard deviation 
            of all the similarity scores.
            If the similarity score is less than the similarity threshold it indicates that the sentence 
            should be the start of a new chunk.
        """
        similarities = []
        vectors = [np.array(embedding) for embedding in embeddings]
        
        for index in range(1,len(vectors)):
            v1, v2 = vectors[index-1], vectors[index]
            similarity_score = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            similarities.append(similarity_score)

        mean_similarity = np.mean(similarities)
        std_similarity = np.std(similarities)
        similarity_threshold = mean_similarity - std_similarity

        indices = [i+1 for i, similarity in enumerate(similarities) if similarity < similarity_threshold]

        return indices

    def splitting_sentences(self, sentence_indices, batch_to_chunk_map, batch, chunks, final_chunks, document_id):
        """
           For each chunk in the batch we further split the chunk based on the occurrence of sentence number
           in sentence indices. We updated final chunks for the same 'chunk_id'.
        """
        batch_start = batch_to_chunk_map[0]["chunk_index"]

        for chunk in batch_to_chunk_map:
            chunk_number = chunk["chunk_index"]
            chunk_start = chunk["start"]
            chunk_end = chunk["end"]
            chunk_id = chunk_number - batch_start

            sentences = [sentence_number for sentence_number in sentence_indices if chunk_start <= sentence_number and sentence_number < chunk_end]
            boundaries = [chunk_start, *sentences, chunk_end]
            
            semantic_chunks = []
            page_numbers, section_title, document_name = self.extract_metadata(chunks[chunk_id].metadata.orig_elements)
            
            for start, end in zip(boundaries, boundaries[1:]):
                if end > start:
                    semantic_chunks.append(FileChunk(
                        text = " ".join(batch[start:end]),
                        document_id = document_id,
                        document_name = document_name,
                        page_numbers = page_numbers,
                        section_title = section_title,
                        chunk_index = chunk_number
                    ))            
            final_chunks[chunk_id] = semantic_chunks
        
        return final_chunks

    def batch_processing(self, batch, batch_to_chunk_map, chunks, final_chunks, document_id):
        """
            A helper function that calls the appropriate functions to create embeddings for a batch of 
            sentences and calculates the similarity scores for each batch.
            It then returns a list of chunks after splitting the batch of chunks.
        """
        embeddings = self.embedding_service.embed_batch(batch)
        sentence_indices = self.calculate_similarity_score(embeddings)

        return self.splitting_sentences(sentence_indices, batch_to_chunk_map, batch, chunks, final_chunks, document_id)

    def chunking(self, chunks, document_id):
        """
            Further splitting chunks that have more than 15 sentences and are meaningful (i.e. average word 
            count should be more than 5 characters and punctuations should be less than 20% of the total 
            content).
            Batches are created from several chunks, where each batch contains at the most 'self.max_embedding_batch_size' 
            sentences. No individual chunk is split to fit into a batch.
            'batch_to_chunk_mapping' is used to track which chunks have been added to a batch and what are 
            the 'start' and 'end' indices for each chunk within the batch.
            Flattened chunks is created because the chunks that were originally split were all added as a
            list to the original index and this then gets flattened to then insert into the qdrant vector 
            database.
        """
        final_chunks = [None] * len(chunks)
        batches, batch_index = [[]], 0
        batch_to_chunk_mapping = {}
        batch_to_chunk_mapping[batch_index] = []

        for chunk_index, chunk in enumerate(chunks):
            sentences, sentence_length, avg_word_count, avg_punctuation_count = self.sentence_processing(chunk.text)

            if sentence_length <= 15 or avg_word_count < 5 or avg_punctuation_count < 0.2:
                page_numbers, section_title, document_name = self.extract_metadata(chunk.metadata.orig_elements)
                final_chunks[chunk_index] = [FileChunk(
                    text = " ".join(sentences),
                    document_id = document_id,
                    document_name = document_name,
                    page_numbers = page_numbers,
                    section_title = section_title,
                    chunk_index = chunk_index
                )]
                continue

            batch_length = len(batches[batch_index])
            
            if batch_length + sentence_length <= self.max_embedding_batch_size:
                batch_to_chunk_mapping[batch_index].append({
                    "chunk_index": chunk_index,
                    "start" : batch_length,
                    "end" : batch_length + sentence_length
                })
                batches[batch_index].extend(sentences)
            else:
                batch_start, batch_end = batch_to_chunk_mapping[batch_index][0]["chunk_index"], batch_to_chunk_mapping[batch_index][-1]["chunk_index"] + 1
                final_chunks[batch_start : batch_end] = self.batch_processing(batches[batch_index], batch_to_chunk_mapping[batch_index], chunks[batch_start : batch_end], final_chunks[batch_start : batch_end], document_id)
                batch_index += 1
                batch_to_chunk_mapping[batch_index] = [{
                    "chunk_index": chunk_index,
                    "start" : 0,
                    "end" : sentence_length
                }]
                batches.append(sentences)

        # There will always be one batch pending for embedding and final splitting
        if batches[batch_index]:
            batch_start, batch_end = batch_to_chunk_mapping[batch_index][0]["chunk_index"], batch_to_chunk_mapping[batch_index][-1]["chunk_index"] + 1
            final_chunks[batch_start : batch_end] = self.batch_processing(batches[batch_index], batch_to_chunk_mapping[batch_index], chunks[batch_start : batch_end], final_chunks[batch_start : batch_end], document_id)

        flattened_chunks = [chunk for chunk_list in final_chunks for chunk in chunk_list]
        
        return flattened_chunks