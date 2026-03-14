import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_groq import ChatGroq

load_dotenv()


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def get_llm_chain(retriever):
    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile",
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are MediSuperBot, an AI-powered assistant trained to help users understand "
         "medical documents and answer health-related questions.\n"
         "Answer based ONLY on the context below. If the context does not contain enough "
         "information, say so honestly — do not make things up.\n\n"
         "Context:\n{context}"),
        ("human", "{question}"),
    ])

    # LCEL chain — works with langchain 0.3.x without langchain.chains module
    rag_chain = (
        RunnableParallel({
            "context":  retriever | format_docs,
            "question": RunnablePassthrough(),
        })
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain
