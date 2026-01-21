from typing import List

from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from models.embeddings import get_embeddings_model


def build_vectorstore_from_pdfs(uploaded_files) -> FAISS:
    """Build an in-memory FAISS vector store from uploaded PDF files."""
    texts: List[str] = []

    for f in uploaded_files:
        reader = PdfReader(f)
        for page in reader.pages:
            content = page.extract_text() or ""
            if content.strip():
                texts.append(content)

    if not texts:
        raise ValueError("No extractable text found in uploaded PDFs.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.create_documents(texts)

    embeddings = get_embeddings_model()
    vectorstore = FAISS.from_documents(chunks, embeddings)
    return vectorstore


def rag_answer(query: str, vectorstore: FAISS, llm) -> str:
    """Return an answer to the query using retrieved chunks plus LLM."""
    if vectorstore is None:
        return "No documents uploaded yet. Please upload PDFs first."

    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    docs = retriever.get_relevant_documents(query)

    if not docs:
        context = ""
    else:
        context = "\n\n".join(d.page_content for d in docs)

    prompt = (
        "You are a helpful assistant answering questions based on the provided context.\n\n"  # noqa: E501
        f"Context:\n{context}\n\n"
        f"Question: {query}\n\n"
        "Answer clearly and concisely. If the answer is not in the context, say you are not sure."
    )

    response = llm.invoke(prompt)
    return getattr(response, "content", str(response))
