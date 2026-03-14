from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from typing import List
import os

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pinecone import Pinecone

from server.modules.llm import get_llm_chain
from server.modules.query_handlers import query_chain
from server.logger import logger

router = APIRouter()


class SimpleRetriever(BaseRetriever):
    docs: List[Document]

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> List[Document]:
        return self.docs


@router.post("/ask/")
async def ask_question(question: str = Form(...)):
    try:
        logger.info(f"Question: {question}")

        pc         = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index_name = os.getenv("PINECONE_INDEX_NAME", "medical-index")
        index      = pc.Index(index_name)

        embed_model = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-001",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
        embedded_query = embed_model.embed_query(question)

        res = index.query(vector=embedded_query, top_k=5, include_metadata=True)

        docs = [
            Document(
                page_content=m["metadata"].get("text", ""),
                metadata=m["metadata"],
            )
            for m in res.get("matches", [])
        ]

        if not docs:
            logger.warning("No matching documents found")
            return JSONResponse(status_code=200, content={
                "answer": {
                    "response": "I couldn't find relevant information in the uploaded documents.",
                    "sources": [],
                }
            })

        # Collect unique source file names
        sources = list({
            m["metadata"].get("source", "")
            for m in res.get("matches", [])
            if m["metadata"].get("source")
        })

        retriever = SimpleRetriever(docs=docs)
        chain     = get_llm_chain(retriever)
        result    = query_chain(chain, question)
        result["sources"] = sources   # attach sources from pinecone matches

        logger.info("Query answered successfully")
        return JSONResponse(status_code=200, content={"answer": result})

    except Exception as e:
        logger.exception("Error processing question")
        return JSONResponse(status_code=500, content={"error": str(e)})
