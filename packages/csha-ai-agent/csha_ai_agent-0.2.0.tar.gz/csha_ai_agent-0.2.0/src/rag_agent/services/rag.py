import logging
import rag_agent.core.logging_config
logger = logging.getLogger(__name__)

import os
import json
import asyncio
from typing import List, Dict, Any, Set, AsyncGenerator
from functools import lru_cache

from rag_agent.core.config import settings, Settings
from rag_agent.services.retriever.base_retriever import BaseRetriever
from rag_agent.services.retriever.bm25 import OkapiBM25Retriever
from rag_agent.services.retriever.vector import PineconeVectorRetriever
from rag_agent.services.generator import Generator
from rag_agent.core.enums import RetrievalMethod

from rag_agent.core.resources import (
    load_json
)

from rag_agent.core.prompt_templates import DEFAULT_TEMPLATE


def get_text_by_id(
    chunk_id: str,
    pages: List[Dict[str, Any]],
) -> str:
    """
    Retrieve the text and reference information for a given chunk ID 
    from a hierarchical JSON structure consisting of headings and subheadings.
    """
    for page in pages:
        if (str(page.get('content_id')) == chunk_id) or (str(page.get('excerpt_id')) == chunk_id):
            return (
                f"<text> {page['content']} </text>\n"
                f"<reference>\n"
                f"  <url> {page['link']} </url>\n"
                f"</reference>"
            ) 

        for child_page in page.get("children", []):
            if (str(child_page.get('content_id')) == chunk_id) or (str(child_page.get('excerpt_id')) == chunk_id):
                return (
                    f"<text> {child_page['content']} </text>\n"
                    f"<reference>\n"
                    f"  <url> {child_page['link']} </url>\n"
                    f"</reference>"
                ) 

    return ""


async def handle_query(
    query: str,
    retriever: BaseRetriever,
    generator: Generator,
    data: List[Dict[str, Any]]
) -> AsyncGenerator[str, None]:
    """
    Run one retrieval+generation cycle:
    1. Get chunk IDs (or Documents)
    2. Assemble context (deduped via a set)
    3. Stream LLM response
    """
    ids: List[str] = retriever.retrieve(query)

    if not ids:
        raise ValueError("No IDs retrieved from retriever.")

    # Use a set so duplicate <text> blocks are automatically ignored
    seen_ids: Set[str] = set()
    context_parts: List[str] = []
    
    for chunk_id in ids:
        if chunk_id in seen_ids:
            continue
        seen_ids.add(chunk_id)
        context_part = get_text_by_id(chunk_id, data)
        if context_part:
            context_parts.append(context_part)
            
    # Print out all retrieved documents for inspection
    print("\nRetrieved Documents:")
    for text in context_parts:
        print("Text Document:")
        print(text)
        print()  

    context = " ".join(context_parts).replace("\n", "\n\t")
    response = ""
    async for response_chunk in generator.stream_generate(query=query, context=context):
        response += response_chunk
        yield response_chunk
    
    logger.info("Final response: %s", response)


def make_retriever(
    *,
    method: RetrievalMethod, 
    cfg: Settings
) -> BaseRetriever:
    """Return a retriever based on the method."""
    if method is RetrievalMethod.VECTOR_DB:
        return PineconeVectorRetriever(
            top_k=cfg.TOP_K,
            embedding_model=cfg.EMBEDDING_MODEL,
            index_name=cfg.INDEX_NAME,
            search_type=cfg.SEARCH_TYPE
        )
    elif method is RetrievalMethod.BM25:
        return OkapiBM25Retriever(
            top_k=cfg.TOP_K, 
            query_model=cfg.QUERY_MODEL
        )
    else:
        raise ValueError(f"Unsupported retrieval method: {method}")


async def retrieval_augmented_generation(query: str) -> AsyncGenerator[str, None]:
    generator = Generator(
        prompt_template=DEFAULT_TEMPLATE,
        query_model=settings.QUERY_MODEL
    )

    retriever = make_retriever(
            method=settings.RETRIEVAL_METHOD,
            cfg=settings
    )

    data = load_json()

    async for response_chunk in handle_query(
        query,
        retriever,
        generator,
        data
    ):
        yield response_chunk


async def main() -> None:
    """CLI REPL: read a query and print streamed chunks."""
    while True:
        raw_query = await asyncio.to_thread(
            input, "\nEnter your query (or 'quit' to exit):\n>>> "
        )
        query = raw_query.strip()
        if not query or query.lower() == "quit":
            break

        async for response_chunk in retrieval_augmented_generation(query):
            print(response_chunk, end="")
        print()


if __name__ == "__main__":
    asyncio.run(main())