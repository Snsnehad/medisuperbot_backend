import os
import time
from pathlib import Path
from dotenv import load_dotenv
from tqdm.auto import tqdm
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from server.logger import logger

load_dotenv()

GOOGLE_API_KEY    = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY  = os.getenv("PINECONE_API_KEY")
PINECONE_ENV      = "us-east-1"
PINECONE_INDEX    = os.getenv("PINECONE_INDEX_NAME", "medical-index")

if not GOOGLE_API_KEY:
    logger.error("GOOGLE_API_KEY not found")
if not PINECONE_API_KEY:
    logger.error("PINECONE_API_KEY not found")

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY or ""

UPLOAD_DIR = "./uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── Pinecone init ──────────────────────────────────────────────────────────────
pc   = Pinecone(api_key=PINECONE_API_KEY)
spec = ServerlessSpec(cloud="aws", region=PINECONE_ENV)

try:
    existing = [i["name"] for i in pc.list_indexes()]
except Exception as e:
    logger.error(f"Pinecone connection failed: {e}")
    existing = []

if PINECONE_INDEX not in existing:
    logger.info(f"Creating Pinecone index: {PINECONE_INDEX}")
    pc.create_index(name=PINECONE_INDEX, dimension=3072, metric="cosine", spec=spec)
    while not pc.describe_index(PINECONE_INDEX).status["ready"]:
        time.sleep(1)
    logger.info("Pinecone index ready")

index = pc.Index(PINECONE_INDEX)


# ── Main function ──────────────────────────────────────────────────────────────
def load_vectorstore(file_paths: list[str]) -> None:
    """Embed and upsert already-saved PDF files into Pinecone."""

    # google-genai 1.12.1 compatible model name
    embed_model = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key=GOOGLE_API_KEY,
    )

    all_texts:     list[str]  = []
    all_metadatas: list[dict] = []
    all_ids:       list[str]  = []

    for file_path in file_paths:
        logger.info(f"Processing: {file_path}")
        loader    = PyPDFLoader(file_path)
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks   = splitter.split_documents(documents)

        timestamp = int(time.time())
        stem      = Path(file_path).stem

        for i, chunk in enumerate(chunks):
            all_texts.append(chunk.page_content)
            meta         = dict(chunk.metadata)
            meta["text"] = chunk.page_content
            meta["source"] = file_path
            all_metadatas.append(meta)
            all_ids.append(f"{stem}-{i}-{timestamp}")

    if not all_texts:
        logger.warning("No text chunks found — nothing to upsert.")
        return

    logger.info(f"Embedding {len(all_texts)} chunks...")
    embeddings = embed_model.embed_documents(all_texts)

    logger.info(f"Upserting into '{PINECONE_INDEX}'...")
    vectors = list(zip(all_ids, embeddings, all_metadatas))
    with tqdm(total=len(vectors), desc="Upserting") as pbar:
        index.upsert(vectors=vectors)
        pbar.update(len(vectors))

    logger.info(f"Done — {len(file_paths)} file(s) indexed.")
