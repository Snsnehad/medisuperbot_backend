from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List

from server.modules.pdf_handlers import save_uploaded_files
from server.modules.load_vectorstore import load_vectorstore
from server.logger import logger

router = APIRouter()


@router.post("/upload_pdfs/")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    """
    Upload one or more PDF files, embed them, and store in Pinecone.
    """
    try:
        logger.info(f"Received {len(files)} file(s) for upload")

        # 1. Save files to disk
        file_paths = save_uploaded_files(files)
        logger.info(f"Saved to disk: {file_paths}")

        # 2. Embed & upsert into Pinecone
        load_vectorstore(file_paths)

        logger.info("All documents indexed successfully")
        return JSONResponse(
            status_code=200,
            content={"message": f"{len(file_paths)} file(s) uploaded and indexed successfully"},
        )
    except Exception as e:
        logger.exception("Error during file upload")
        return JSONResponse(status_code=500, content={"error": str(e)})
