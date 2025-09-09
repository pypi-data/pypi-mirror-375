from typing import TYPE_CHECKING, Any

from google.adk.agents import LlmAgent

from sparkden.assistants.registry import assistant_registry
from sparkden.db.schema import DataSourceStatus
from sparkden.knowledge.data_loader import DataLoader
from sparkden.knowledge.registry import knowledge_collections
from sparkden.models.knowledge import KnowledgeDataSource
from sparkden.queued_job.decorator import JobContext, JobResult, queued_job
from sparkden.services.knowledge import KnowledgeService

if TYPE_CHECKING:
    from google.adk.agents import BaseAgent
    from google.adk.events import Event
    from google.adk.models.base_llm import BaseLlm
    from google.genai import types

    from sparkden.models.knowledge import FileObject


@queued_job(queue_name="summarize_context")
async def summarize_context_job(
    ctx: JobContext,
    data_source_id: str,
    assistant_id: str,
    agent_name: str,
) -> JobResult:
    knowledge_service = KnowledgeService(user_id=ctx.user_id)

    try:
        await ctx.update_progress(5, custom_status="initializing")

        data_source = await knowledge_service.get_data_source(data_source_id)
        if not data_source:
            raise ValueError(f"Data source {data_source_id} not found")

        if data_source.status != DataSourceStatus.READY:
            collection = knowledge_collections.get_collection(data_source.collection_id)
            if not collection:
                raise ValueError(f"Collection {data_source.collection_id} not found")

            loader = DataLoader(
                data_source=data_source,
                vector_dimensions=collection.vector_dimensions,
                retrieval_mode=collection.retrieval_mode,
            )

            async for status in loader.load():
                await ctx.update_progress(30, custom_status=status)

            await knowledge_service.update_data_source(
                data_source_id, {"status": DataSourceStatus.READY}
            )

        await ctx.update_progress(50, custom_status="summarizing")
        assistant = assistant_registry.get_assistant(assistant_id)
        if not assistant:
            raise ValueError(f"Assistant {assistant_id} not found")
        agent = assistant.root_agent.find_agent(agent_name)
        if not agent:
            raise ValueError(f"Agent {agent_name} not found")
        assert isinstance(agent, LlmAgent), f"Agent {agent_name} should be a LlmAgent"
        model = agent.canonical_model

        text = await summarize_data_source(data_source, model)

        await ctx.update_progress(100, custom_status="completed")

        return {
            "summary": text,
            "data_source_creator_id": data_source.creator_id,
            "data_source_name": data_source.name,
        }

    except Exception as e:
        # Update data source status to ERROR on failure
        await knowledge_service.update_data_source(
            data_source_id, {"status": DataSourceStatus.ERROR}
        )
        # Re-raise the exception so the job is marked as failed
        raise e


async def summarize_data_source(
    data_source: "KnowledgeDataSource", model: "BaseLlm"
) -> str:
    from google.genai import types

    from sparkden.assistants.agents.chunk_summarize_agent import (
        get_chunk_summarize_agent,
    )
    from sparkden.assistants.agents.merge_summarize_agent import (
        get_merge_summarize_agent,
    )
    from sparkden.assistants.agents.summarize_agent import get_summarize_agent
    from sparkden.shared.minio import get_object

    parsed_object_name = f"{data_source.id}/parsed"
    parsed_file = get_object(data_source.collection_id, parsed_object_name)
    if not parsed_file:
        raise ValueError(
            f"data source file not found: bucket={data_source.collection_id}, object_name={parsed_object_name}"
        )

    chunks = await _split_file(parsed_file)

    if len(chunks) == 0:
        raise ValueError(f"No chunks found for data source {data_source.id}")

    if len(chunks) == 1:
        event = await _run_summarize_agent(
            get_summarize_agent(model),
            types.Content(role="user", parts=[types.Part(text=chunks[0])]),
        )
        text = _extract_event_text(event)
        if text is not None:
            return text
        raise ValueError("Failed to summarize the context")
    else:
        state = {
            "chunks_count": len(chunks),
            "summarized_chunks_count": 0,
            "summarized_chunks": [],
            "current_chunk_index": 0,
        }
        for index, chunk in enumerate(chunks):
            state["current_chunk_index"] = index + 1
            event = await _run_summarize_agent(
                get_chunk_summarize_agent(model),
                types.Content(
                    role="user", parts=[types.Part(text=f"Chunk {index + 1}:\n{chunk}")]
                ),
                state,
            )
            text = _extract_event_text(event)
            if text is None:
                raise ValueError("Failed to summarize the chunk")
            state["summarized_chunks_count"] += 1
            state["summarized_chunks"].append(text)

        event = await _run_summarize_agent(
            get_merge_summarize_agent(model),
            types.Content(
                role="user",
                parts=[
                    types.Part(
                        text="\n\n".join(
                            [
                                f"Chunk {index + 1} summary:\n{chunk}"
                                for index, chunk in enumerate(
                                    state["summarized_chunks"]
                                )
                            ]
                        )
                    )
                ],
            ),
        )

        text = _extract_event_text(event)
        if text is not None:
            return text
        raise ValueError("Failed to merge the summarized chunks")


MIN_CHUNK_SIZE = 100000
MAX_CHUNK_SIZE = 160000
CHUNK_OVERLAP = 500


async def _split_file(file: "FileObject") -> list[str]:
    """Split the given file into text chunks suitable for summarization.

    Ensures no empty chunks are returned and applies header-aware splitting
    for markdown files.
    """
    from langchain_text_splitters import (
        MarkdownHeaderTextSplitter,
        RecursiveCharacterTextSplitter,
    )

    # Be tolerant to decoding issues and preserve as much content as possible
    text = file.content.decode("utf-8", errors="replace")
    if file.content_type == "text/plain":
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=MAX_CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
        )
        return text_splitter.split_text(text)
    elif file.content_type == "text/markdown":
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=MIN_CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
        )
        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header1"),
                ("##", "Header2"),
                ("###", "Header3"),
                ("####", "Header4"),
                ("#####", "Header5"),
                ("######", "Header6"),
            ],
        )
        documents = markdown_splitter.split_text(text)
        chunks: list[str] = []
        chunk = ""
        for document in documents:
            chunk += document.page_content
            if len(chunk) > MAX_CHUNK_SIZE:
                chunks.extend(text_splitter.split_text(chunk))
            elif len(chunk) >= MIN_CHUNK_SIZE:
                chunks.append(chunk)
                chunk = ""
        # Append the remaining chunk if any
        if chunk:
            if len(chunk) <= 5000 and len(chunks) > 0:
                chunks[-1] += chunk
            else:
                chunks.append(chunk)
        # Filter out any accidental empty strings
        return [c for c in chunks if c]

    else:
        raise ValueError(f"Unsupported data type: {file.content_type}")


async def _run_summarize_agent(
    agent: "BaseAgent",
    user_content: "types.Content",
    state: dict[str, Any] | None = None,
) -> "Event | None":
    from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
    from google.adk.runners import Runner
    from google.adk.sessions.in_memory_session_service import InMemorySessionService
    from google.adk.utils.context_utils import Aclosing

    runner = Runner(
        app_name=agent.name,
        agent=agent,
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
    )
    session = await runner.session_service.create_session(
        app_name=agent.name,
        user_id="tmp_user",
        state=state,
    )

    last_event = None
    async with Aclosing(
        runner.run_async(
            user_id=session.user_id, session_id=session.id, new_message=user_content
        )
    ) as agen:
        async for event in agen:
            last_event = event

    return last_event


def _extract_event_text(event: "Event | None") -> str | None:
    """Safely extract the first text part from an event, if any.

    Returns None if the expected structure is missing.
    """
    try:
        if not event:
            return None
        content = getattr(event, "content", None)
        if not content:
            return None
        parts = getattr(content, "parts", None)
        if not parts:
            return None
        part = parts[0]
        text = getattr(part, "text", None)
        return text if isinstance(text, str) and text else None
    except Exception:
        return None
