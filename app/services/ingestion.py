import uuid
import fitz # PyMuPDF
import boto3
from typing import List, Tuple

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import PGVector
from langchain.docstore.document import Document

from app.core.config import settings


def parse_pdf(file_bytes: bytes) -> List[Tuple[str, int]]:
    """
    Extract text from each page of a PDF.
    Returns a list of (text, page_number) tuples.
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages = []
    for page_num in range(len(doc)):
        text = doc.load_page(page_num).get_text()
        if text.strip():
            pages.append((text, page_num + 1))  # Page numbers start at 1
    return pages


def chunk_pages(
    pages: List[Tuple[str, int]],
    document_id: str,
    filename: str
) -> List[Document]:
    """
    Split pages into smaller overlapping chunks.
    Attaches metadata: document_id, filename, page_number.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " "]
    )

    documents = []
    for text, page_num in pages:
        chunks = splitter.split_text(text)
        for chunk in chunks:
            documents.append(Document(
                page_content=chunk,
                metadata={
                    "document_id": document_id,
                    "filename": filename,
                    "page": page_num
                }
            ))
    return documents


def store_embeddings(documents: List[Document]) -> int:
    """
    Embed chunks using OpenAI and store in pgvector.
    Returns the number of chunks stored.
    """
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=settings.OPENAI_API_KEY
    )

    PGVector.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name="mediquery_docs",
        connection_string=settings.DB_URL,
        pre_delete_collection=False # append, dont overwrite
    )

    return len(documents)


def upload_to_s3(file_bytes: bytes, filename: str, document_id: str) -> str:
    """
    Upload the original PDF to S3.
    Returns the S3 object key.
    """
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )

    s3.key = f"{document_id}/{filename}"

    s3.put_object(
        Bucket=settings.AWS_S3_BUCKET,
        Key=s3.key,
        Body=file_bytes,
        ContentType="application/pdf"
    )

    return s3.key


def ingest_document(file_bytes: bytes, filename: str) -> dict:
    """
    Full ingestion pipeline:
    Parse PDF -> Chunk Pages -> Embed + Store -> Upload to S3
    """
    document_id = str(uuid.uuid4())

    #1. Parse PDF
    pages = parse_pdf(file_bytes)
    if not pages:
        raise ValueError("No text found in PDF")
    
    #2. Chunk into LangChain Documents
    documents = chunk_pages(pages, document_id, filename)

    #3. Embed and store in pgvector
    chunks_stored = store_embeddings(documents)

    #4. Upload original PDF to S3
    upload_to_s3(file_bytes, filename, document_id)

    return {
        "document_id": document_id,
        "filename": filename,
        "pages": len(pages),
        "chunks_stored": chunks_stored
    }
