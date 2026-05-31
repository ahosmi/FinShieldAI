"""
FinShield AI — RAG Pipeline Core
Retrieval-Augmented Generation for contextual fraud explanations.
"""

import logging
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
from vector_store import FraudVectorStore

logger = logging.getLogger(__name__)

FRAUD_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are a senior fraud analyst at a fintech company in India.
You have access to historical fraud cases, RBI compliance guidelines, and AML policies.

Use ONLY the context below to answer. Be specific — cite case IDs and policy sections.
If the transaction matches a known fraud type, name it explicitly.
If the context doesn't cover the question, say so clearly.

Retrieved Context:
{context}

Analyst Question:
{question}

Fraud Analysis (be concise, specific, actionable):"""
)


class FraudRAGEngine:

    def __init__(self, ollama_url: str, model: str = "mistral"):
        self.vector_store = FraudVectorStore()
        self.llm = Ollama(
            base_url=ollama_url,
            model=model,
            temperature=0.1,
            num_predict=512,
        )
        self.retriever = self.vector_store.get_retriever(k=4)
        self.chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=self.retriever,
            chain_type="stuff",
            chain_type_kwargs={"prompt": FRAUD_PROMPT},
            return_source_documents=True,
        )

    def explain_fraud(self, transaction: dict, risk_result: dict) -> dict:
        query = self._build_query(transaction, risk_result)
        logger.info(f"RAG explain: {transaction.get('transaction_id')}")
        try:
            result = self.chain({"query": query})
            return {
                "transaction_id": transaction.get("transaction_id"),
                "explanation": result["result"].strip(),
                "sources": [
                    {
                        "source": doc.metadata.get("source", "unknown"),
                        "type": doc.metadata.get("type", "unknown"),
                        "excerpt": doc.page_content[:200] + "...",
                    }
                    for doc in result.get("source_documents", [])
                ],
            }
        except Exception as e:
            logger.error(f"RAG explain error: {e}")
            return {
                "transaction_id": transaction.get("transaction_id"),
                "explanation": f"Unable to generate explanation: {e}",
                "sources": [],
            }

    def answer_question(self, question: str, context: dict = None) -> dict:
        if context:
            enriched = (
                f"Transaction context — ID: {context.get('transaction_id')}, "
                f"User: {context.get('user_id')}, "
                f"Amount: ₹{context.get('amount', 0):,.2f}, "
                f"Risk Score: {context.get('risk_score', 'N/A')}, "
                f"Fraud Type: {context.get('fraud_type', 'Unknown')}.\n\n"
                f"Question: {question}"
            )
        else:
            enriched = question
        try:
            result = self.chain({"query": enriched})
            return {
                "answer": result["result"].strip(),
                "sources": [doc.metadata.get("source") for doc in result.get("source_documents", [])],
            }
        except Exception as e:
            logger.error(f"RAG Q&A error: {e}")
            return {"answer": f"Error: {e}", "sources": []}

    def _build_query(self, txn: dict, risk: dict) -> str:
        triggers = [t.get("description", "") for t in risk.get("rule_triggers", [])]
        return (
            f"Analyze this flagged transaction:\n"
            f"ID: {txn.get('transaction_id')} | User: {txn.get('user_id')} | "
            f"Amount: ₹{txn.get('amount', 0):,.2f} | Type: {txn.get('transaction_type')} | "
            f"Region: {txn.get('region', 'Unknown')} | City: {txn.get('city', 'Unknown')}\n"
            f"Risk Score: {risk.get('risk_score', 'N/A')}/100 | Decision: {risk.get('decision')}\n"
            f"Triggered Rules: {'; '.join(triggers) or 'None'}\n"
            f"Fraud Scenario: {txn.get('fraud_scenario', 'Unknown')}\n\n"
            f"What fraud pattern does this match? Reference similar cases and applicable "
            f"RBI/AML guidelines. What immediate action is recommended?"
        )
