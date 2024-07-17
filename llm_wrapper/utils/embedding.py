import chromadb.utils.embedding_functions as embedding_functions
import dotenv
import os

dotenv.load_dotenv()

huggingface_ef = embedding_functions.HuggingFaceEmbeddingFunction(
    api_key=os.getenv("HUGGINGFACE_APIKEY"),
    model_name="hkunlp/instructor-base"
)