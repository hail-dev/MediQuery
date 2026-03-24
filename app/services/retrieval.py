from typing import Optional
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores.pgvector import PGVector
from langchain.chains import retrieval_qa as RetrievalQA
from langchain.prompts import PromptTemplate

from app.core.config import settings


MEDICAL_QA_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are a helpful medical document assistant.
Use ONLY the context below to answer the question.
If the answer is not found in the context, say "I could not find this information in the provided documents."
Always be precise, factual, and cite relevant details from the context.

Context:
{context}

Question: {question}

Answer:"""
)


def get_vector_store(document_id: Optional[str] = None) -> PGVector:
    """
    Returns a PGVector retriever.
    Optionally filters by document_id via metadata.
    """
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=settings.OPENAI_API_KEY
    )

    vector_store = PGVector(
        collection_name="mediquery_docs",
        connection_string=settings.DB_URL,
        embedding_function=embeddings
    )

    return vector_store


def answer_question(question: str, document_id: Optional[str] = None) -> dict:
    """
    RAG pipeline:
    1. Embed the question
    2. Retrieve top-K relevant chunks
    3. Pass chunks + question to LLM
    4. Return answer + source citations
    """
    vectore_store = get_vector_store()

    # Build retriever - filter by document_id if provided
    search_kwargs = {"k": settings.RETRIEVER_TOP_K}
    if document_id:
        search_kwargs["filter"] = {"document_id": document_id}

    retriever = vectore_store.as_retriever(search_kwargs=search_kwargs)

    #LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        openai_api_key=settings.OPENAI_API_KEY
    )

    # RAG chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_document=True,
        chain_type_kwargs={"prompt": MEDICAL_QA_PROMPT}
    )

    result = qa_chain.invoke({"query": question})

    # Format source citations
    sources = []
    seen = set()
    for doc in result["source_documents"]:
        meta = doc.metadata
        key = f"{meta['document_id']}_p{meta['page']}"
        if key not in seen:
            seen.add(key)
            sources.append({
                "content": doc.page_content[:300],
                "page": meta["page"],
                "document_id": meta["document_id"],
                "filename": meta["filename"]
            })

    return {
        "answer": result["result"],
        "sources": sources
    }