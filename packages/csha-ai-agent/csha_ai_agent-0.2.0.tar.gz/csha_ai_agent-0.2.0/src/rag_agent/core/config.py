#pydantic v2
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from rag_agent.core.enums import RetrievalMethod


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="CSHA_",
        extra="ignore",
    )

    APP_NAME: str = "RAG AGENT API"

    BACKEND_API_KEY: SecretStr

    OPENAI_API_EMBEDDINGS_KEY: SecretStr
    OPENAI_API_QUERY_KEY: SecretStr
    PINECONE_API_KEY: SecretStr

    EMBEDDING_MODEL: str = "text-embedding-3-large"
    QUERY_MODEL: str = "gpt-4.1-mini"

    RETRIEVAL_METHOD: RetrievalMethod = RetrievalMethod.BM25
    INDEX_NAME: str = "csha-website-data"
    SEARCH_TYPE: str = "similarity"
    TOP_K: int = 14

    # --- CORS ---
    # TODO: Add production origins
    ALLOW_ORIGINS: List[str] = ['https://dev-chsa-ai.pantheonsite.io', 'http://localhost:3000']
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: List[str] = ["*"]
    ALLOW_HEADERS: List[str] = ["*"]

    @field_validator("ALLOW_ORIGINS", mode="before")
    @classmethod
    def _parse_allow_origins(
        cls,
        urls: Union[str, List[str]]
    ) -> List[str]:
        if isinstance(urls, list):
            return urls
        if isinstance(urls, str):
            csv_urls = [string.strip() for string in urls.split(",")]
            non_empty_urls = [url for url in csv_urls if url]
            return non_empty_urls
        return urls

settings = Settings()