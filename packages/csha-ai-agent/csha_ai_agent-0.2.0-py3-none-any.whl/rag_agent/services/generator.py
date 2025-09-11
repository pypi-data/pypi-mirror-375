import os
import sys
import json
import asyncio
from typing import List, AsyncGenerator, Dict, Any, Set

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

from functools import cached_property

from rag_agent.core.config import settings


class Generator:
    def __init__(
        self,
        prompt_template: str,
        query_model: str
    ) -> None:
        self.prompt_template = prompt_template
        self.query_model = query_model


    @cached_property
    def _openai_llm(self) -> ChatOpenAI:
        return ChatOpenAI(
            openai_api_key=settings.OPENAI_API_QUERY_KEY.get_secret_value(),
            model_name=self.query_model,
            temperature=0.0,
            streaming=True
        )


    @cached_property
    def _langchain_prompt_template(self) -> PromptTemplate: #This method should be resusable based on prompt input variables (find some way to format based on different input variables)
        prompt = PromptTemplate(
            template=self.prompt_template
        )
        return prompt


    async def _stream_llm_response(
        self,
        request: str
    ) -> AsyncGenerator[str, None]:
        """
        Asynchronously stream chunks from the LLM, indenting newlines
        for readability in console output.
        """
        async for chunk in self._openai_llm.astream(request):
            yield chunk.content
    

    def _llm_response(
        self,
        request: str
    ) -> str:
        return self._openai_llm.invoke(request).content
   

    def _build_request(
        self,
        *,
        query: str,
        **additional_prompt_input_variables: str
    ) -> str:
        """
        Run one retrieval+generation cycle:
        1. Get chunk IDs (or Documents)
        2. Assemble context (deduped via a set)
        3. Stream LLM response
        """
        prompt = self._langchain_prompt_template
        required_input_variables = set(prompt.input_variables)
        
        if 'query' in required_input_variables and not query:
            raise ValueError("Missing required input variable 'query'.")

        input_variables = {"query": query, **additional_prompt_input_variables}

        missing = required_input_variables - input_variables.keys()
        if missing:
            raise ValueError(f"Missing required input variables: {missing}")
        
        extra = input_variables.keys() - required_input_variables
        if extra:
            raise ValueError(f"Unexpected input variables: {extra}")
        
        request = prompt.format(
            **input_variables
        )

        return request


    async def stream_generate(
        self,
        *,
        query: str,
        **additional_prompt_input_variables: str
    ) -> AsyncGenerator[str, None]:
        request = self._build_request(query=query, **additional_prompt_input_variables)
        async for chunk in self._stream_llm_response(request):
            yield chunk
    

    def generate(
        self,
        *,
        query: str,
        **additional_prompt_input_variables: str
    ) -> str:
        request = self._build_request(query=query, **additional_prompt_input_variables)
        return self._llm_response(request)



