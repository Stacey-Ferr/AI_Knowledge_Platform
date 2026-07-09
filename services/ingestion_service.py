from datetime import datetime
from pathlib import Path
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.docx import partition_docx
from unstructured.partition.text import partition_text
from unstructured.partition.md import partition_md
import logging
from io import StringIO
from core.exceptions import EmptyFileException, FileException
from contextlib import contextmanager
from schemas.file import (
    FileMetadata,
    IngestionResult
)
from core.logging import logger
from pypdf import PdfReader
from unstructured.chunking.title import chunk_by_title
from chunking.semantic_chunker import SemanticChunker
from services.embedding_service import OpenAIEmbeddingService
from services.vector_store_service import VectorStoreService
from uuid import uuid4
import time

@contextmanager
def _capture_pdf_logs():
    """
    A context manager created for logging PDF related warnings that might occur partitioning
    """
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    pdfminer_logger = logging.getLogger("pdfminer")
    pypdf_logger = logging.getLogger("pypdf")
    pdfminer_logger.addHandler(handler)
    pypdf_logger.addHandler(handler)

    try:
        yield log_stream
    finally:
        pdfminer_logger.removeHandler(handler)
        pypdf_logger.removeHandler(handler)

KNOWN_WARNINGS = [
    "Data-loss while decompressing corrupted data",
    "Could not get FontBBox from font descriptor because None cannot be parsed as 4 floats"
]

PDF_CORRUPTION_INDICATORS = [
    "incorrect startxref",
    "Error -3 while decompressing data",
    "found 0 objects within Object"
]

class IngestionService:

    partitioners = {
        "pdf": lambda path: partition_pdf(filename = str(path), strategy="fast"),
        "docx" : lambda path: partition_docx(filename = str(path)),
        "txt" : lambda path: partition_text(filename = str(path)),
        "md" : lambda path: partition_md(filename = str(path)),
    }

    UPLOAD_DIR = Path("files/uploads")
    # Creates the directory '/file/uploads'
    # 'parents=True' creates all folders and subfolders if it doesn't exist and 
    # 'exist_ok=True' ignores if the folders already exist
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    async def save_file(self, file, file_path):
        """
            Reads the file that was uploaded and saves the file locally on disk
            If the length of the file is 0, an EmptyFileException is raised with message 'Document is empty'.
        """
        content = await file.read()

        if len(content) == 0:
            logger.exception(f"Document is empty")
            raise EmptyFileException("Document is empty", status_code=400)

        with open(file_path, 'wb') as f:
            f.write(content)
        return len(content)

    def partition_file(self, file_type, file_path):
        """
            This function uses the Unstructured Partitioning based on file type.
            Created the dictionary 'partitioners' to map file type to the appropriate partitioning function.
            Partitioning converts uploaded documents into structured elements such as titles, paragraphs, tables, and lists.
        """
        try:
            if file_type == "pdf":
                with _capture_pdf_logs() as log_stream:
                    elements = self.partitioners.get(file_type)(file_path)
                    # Running 'PdfReader(file_path)' to check if the PDF is corrupted
                    # PdfReader(file_path)
                # Capturing any warnings that may arise during PDF partitioning
                logs = log_stream.getvalue()
            else:
                elements = self.partitioners.get(file_type)(file_path)
                logs = ""
            return elements, logs

        except Exception as e:
            logger.exception(f"Unable to process the file: {e}")
            raise FileException(f"Unable to process the file: {e}", status_code=422) from e

    def extract_text(self, elements):
        """
            Takes the partitioned elements and extracts the 'text' value from each element.
            If no text is found, an exception is thrown.
        """
        extracted_text = []

        for element in elements:
            text = getattr(element, "text", None)

            if text and text.strip():
                extracted_text.append(text.strip())

        if not extracted_text:
            logger.exception(f"Document contains no text")
            raise EmptyFileException("Document contains no text", status_code=400)

    def logging_warnings(self, logs):
        """
            Checking the logs that were seen during partitioning against a list of known warnings listed in 'KNOWN_WARNINGS' and checking if there is any indication of PDF corruption using the list of values in 'PDF_CORRUPTION_INDICATORS'. If the PDF is corrupted we raise an Exception.
        """

        warnings = [warning for warning in KNOWN_WARNINGS if warning in logs]

        pdf_corruption = [corruption_indicator for corruption_indicator in PDF_CORRUPTION_INDICATORS if corruption_indicator in logs]

        if pdf_corruption:
            logger.exception(f"PDF appears to be corrupted")
            raise FileException("PDF appears to be corrupted", status_code=422, warnings=warnings + pdf_corruption)

        return warnings

    async def process_file(self, file, bm25_service):
        file_path = self.UPLOAD_DIR / file.filename
        file_type = Path(file.filename).suffix.lstrip(".").lower()

        try:
            # Reading and saving the file locally
            start = time.perf_counter()
            content_length = await self.save_file(file, file_path)
            print(f"\nSaving File: {time.perf_counter() - start:.2f}s")

            # Partitioning the file
            start = time.perf_counter()
            elements, logs = self.partition_file(file_type, file_path)
            print(f"\nPartitioning: {time.perf_counter() - start:.2f}s")

            # Extracting text to check if the document is empty or contains only images
            start = time.perf_counter()
            self.extract_text(elements)
            print(f"\nExtracting text: {time.perf_counter() - start:.2f}s")

            # Executing Title chunking on the partitioned data
            start = time.perf_counter()
            chunks = chunk_by_title(elements, max_characters=1500, new_after_n_chars=1000, include_orig_elements=True)
            print(f"\nTitle chunking: {time.perf_counter() - start:.2f}s")

            # Running Semantic chunking on the Title chunks
            start = time.perf_counter()
            # Passing a document_id for all the chunks, to help search for these particular vectors
            document_id = str(uuid4())
            semantic_chunking = SemanticChunker(OpenAIEmbeddingService())
            final_chunks = semantic_chunking.chunking(chunks, document_id)
            print(f"\nSemantic chunking: {time.perf_counter() - start:.2f}s\n")

            # Creating vectors to store in qdrant vector store
            start = time.perf_counter()
            vector_service = VectorStoreService()
            points = vector_service.create_point_structures(final_chunks)
            vector_service.upsert(points)
            print(f"\nStoring in qdrant vector store: {time.perf_counter() - start:.2f}s\n")

            # Builds a BM25 index for all the chunks
            start = time.perf_counter()
            bm25_service.build_index(final_chunks)
            print(f"\nBuilding Index using BM25: {time.perf_counter() - start:.2f}s\n")

            warnings = self.logging_warnings(logs)

            metadata = FileMetadata(**{
                "file_name" : file.filename,
                "file_type" : file_type,
                "size_bytes" : content_length,
                "uploaded_at" : datetime.now(),
                "element_count" : len(elements),
                "warnings": warnings
            })

            return IngestionResult(**{"metadata":metadata})
        
        except Exception as e:
            try:
                # Deletes the uploaded file incase any exception occurred during any stage of the upload 
                # process and then raises the Exception to the calling function
                if file_path.exists():
                    file_path.unlink()

            except Exception as cleanup_error:
                logger.warning(f"Failed to delete file: {cleanup_error}")
                # Added a warning field to the Exception as failure to delete the file is not the main 
                # Exception but also wanted to let the user know that file deletion failed.
                if hasattr(e, "warnings"):
                    e.warnings.append(f"Failed to delete file: {cleanup_error}")

            raise
