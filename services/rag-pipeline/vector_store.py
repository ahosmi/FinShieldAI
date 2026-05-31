"""
FinShield AI — FAISS Vector Store
Builds and serves the fraud knowledge base for retrieval.
"""

import json
import logging
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from embeddings import get_embedder

logger = logging.getLogger(__name__)

KB_PATH = Path(__file__).parent / "knowledge_base"
INDEX_PATH = "faiss_index"


class FraudVectorStore:

    def __init__(self):
        self.embedder = get_embedder()
        self.vectorstore = self._load_or_build()

    def _load_or_build(self) -> FAISS:
        if Path(INDEX_PATH).exists():
            logger.info("Loading existing FAISS index...")
            return FAISS.load_local(
                INDEX_PATH,
                self.embedder,
                allow_dangerous_deserialization=True,
            )
        logger.info("Building FAISS index from knowledge base...")
        return self._build_index()

    def _build_index(self) -> FAISS:
        documents = []
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=60)

        # Load fraud cases JSON
        cases_file = KB_PATH / "fraud_cases.json"
        if cases_file.exists():
            cases = json.loads(cases_file.read_text())
            for case in cases:
                text = (
                    f"Case ID: {case['case_id']}\n"
                    f"Fraud Type: {case['fraud_type']}\n"
                    f"Summary: {case['summary']}\n"
                    f"Pattern: {case['pattern']}\n"
                    f"Indicators: {case.get('indicators', '')}\n"
                    f"Outcome: {case['outcome']}\n"
                    f"Recommendation: {case.get('recommendation', '')}"
                )
                documents.append(Document(
                    page_content=text.strip(),
                    metadata={"source": f"fraud_case_{case['case_id']}", "type": "case"},
                ))
            logger.info(f"Loaded {len(cases)} fraud cases")

        # Load text compliance files
        for txt_file in KB_PATH.glob("*.txt"):
            content = txt_file.read_text(encoding="utf-8")
            chunks = splitter.split_text(content)
            for chunk in chunks:
                documents.append(Document(
                    page_content=chunk,
                    metadata={"source": txt_file.name, "type": "compliance"},
                ))
            logger.info(f"Loaded {len(chunks)} chunks from {txt_file.name}")

        if not documents:
            # Fallback: minimal built-in knowledge so RAG still functions
            documents = [Document(
                page_content="Fraud detection system is operational. Knowledge base is being loaded.",
                metadata={"source": "system", "type": "system"},
            )]

        logger.info(f"Building FAISS index with {len(documents)} documents...")
        vs = FAISS.from_documents(documents, self.embedder)
        vs.save_local(INDEX_PATH)
        logger.info("FAISS index saved.")
        return vs

    def get_retriever(self, k: int = 4):
        return self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k},
        )

    def rebuild(self):
        """Force-rebuild index (call after adding new documents)."""
        import shutil
        if Path(INDEX_PATH).exists():
            shutil.rmtree(INDEX_PATH)
        self.vectorstore = self._build_index()
