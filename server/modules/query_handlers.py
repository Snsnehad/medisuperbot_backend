from server.logger import logger


def query_chain(chain, user_input: str) -> dict:
    """Invoke the RAG chain and return answer + sources."""
    try:
        logger.debug(f"Running chain for: {user_input}")

        # LCEL chain returns a string directly
        answer = chain.invoke(user_input)

        response = {
            "response": answer,
            "sources":  [],   # sources handled in ask_question.py from retriever
        }
        logger.debug(f"Answer: {response}")
        return response
    except Exception:
        logger.exception("Error in query_chain")
        raise
