# File: crewplus/callbacks/async_langfuse_handler.py
import asyncio
import contextvars
from contextlib import contextmanager
from typing import Any, Dict, List, Union

try:
    from langfuse.langchain import CallbackHandler as LangfuseCallbackHandler
    from langchain_core.callbacks import AsyncCallbackHandler
    from langchain_core.outputs import LLMResult
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    LangfuseCallbackHandler = None
    AsyncCallbackHandler = object

# This token is a simple flag to indicate that we are in an async context.
# We use a context variable to make it available only within the async task.
_ASYNC_CONTEXT_TOKEN = "in_async_context"
in_async_context = contextvars.ContextVar(_ASYNC_CONTEXT_TOKEN, default=False)

@contextmanager
def async_context():
    """A context manager to signal that we are in an async execution context."""
    token = in_async_context.set(True)
    try:
        yield
    finally:
        in_async_context.reset(token)

class AsyncLangfuseCallbackHandler(AsyncCallbackHandler):
    """
    Wraps the synchronous LangfuseCallbackHandler to make it compatible with
    LangChain's async methods.
    
    This works by running the synchronous handler's methods in a separate thread
    using `asyncio.to_thread`. This is crucial because `asyncio`'s default
    executor can correctly propagate `contextvars`, which solves the
    `ValueError: <Token ...> was created in a different Context` from OpenTelemetry.
    """
    def __init__(self, *args: Any, **kwargs: Any):
        if not LANGFUSE_AVAILABLE:
            raise ImportError("Langfuse is not available. Please install it with 'pip install langfuse'")
        self.sync_handler = LangfuseCallbackHandler(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        # Delegate any other attribute access to the sync handler
        return getattr(self.sync_handler, name)

    async def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        # WORKAROUND: LangChain's async implementation can sometimes pass a raw
        # string for prompts instead of a list. We wrap it in a list to ensure
        # compatibility with the synchronous handler.
        corrected_prompts = prompts if isinstance(prompts, list) else [prompts]
        await asyncio.to_thread(
            self.sync_handler.on_llm_start, serialized, corrected_prompts, **kwargs
        )

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        await asyncio.to_thread(
            self.sync_handler.on_llm_end, response, **kwargs
        )
    
    async def on_llm_error(self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any) -> None:
        await asyncio.to_thread(
            self.sync_handler.on_llm_error, error, **kwargs
        )
    
    async def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> Any:
        await asyncio.to_thread(
            self.sync_handler.on_tool_start, serialized, input_str, **kwargs
        )

    async def on_tool_end(self, output: str, **kwargs: Any) -> Any:
        await asyncio.to_thread(
            self.sync_handler.on_tool_end, output, **kwargs
        )

    async def on_tool_error(self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any) -> Any:
        await asyncio.to_thread(
            self.sync_handler.on_tool_error, error, **kwargs
        )

    async def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any) -> Any:
        await asyncio.to_thread(
            self.sync_handler.on_chain_start, serialized, inputs, **kwargs
        )

    async def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> Any:
        await asyncio.to_thread(
            self.sync_handler.on_chain_end, outputs, **kwargs
        )

    async def on_chain_error(self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any) -> Any:
        await asyncio.to_thread(
            self.sync_handler.on_chain_error, error, **kwargs
        )
