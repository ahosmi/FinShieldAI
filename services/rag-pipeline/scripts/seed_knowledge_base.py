"""
FinShield AI — Seed / Rebuild the FAISS Vector Store
Run this whenever you add new documents to the knowledge base.
"""
import sys
sys.path.insert(0, "/app")

from vector_store import FraudVectorStore

if __name__ == "__main__":
    print("Seeding FAISS vector store from knowledge base...")
    vs = FraudVectorStore()
    vs.rebuild()
    print("Vector store built and saved.")
