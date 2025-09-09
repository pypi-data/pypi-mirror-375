from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from google.adk.tools import ToolContext

    from sparkden.models.assistant import ToolResponse


async def summarize_context(
    data_source_id: str, tool_context: "ToolContext"
) -> "ToolResponse":
    """Get a brief summary of the long context with data_source_id.

    Args:
        data_source_id: The id of the data source to search from.

    Returns:
        A brief summary of the long context.
    """
    from google.adk.agents import LlmAgent

    from sparkden.db.schema import DataSourceStatus
    from sparkden.models.assistant import ToolResponse, ToolResponseStatus
    from sparkden.queued_job.summarize_context_job import (
        summarize_context_job,
        summarize_data_source,
    )
    from sparkden.services.knowledge import KnowledgeService

    user_id = tool_context._invocation_context.user_id
    knowledge_service = KnowledgeService(user_id=user_id)

    try:
        data_source = await knowledge_service.get_data_source(data_source_id)
    except Exception:
        return ToolResponse(
            status=ToolResponseStatus.ERROR,
            error=f"Failed to get data source with id {data_source_id}",
        )

    if not data_source:
        return ToolResponse(
            status=ToolResponseStatus.ERROR,
            error=f"Data source {data_source_id} not found",
        )

    if data_source.status != DataSourceStatus.READY:
        tool_context.actions.skip_summarization = True

        message = summarize_context_job.send(
            data_source_id=data_source_id,
            assistant_id=tool_context._invocation_context.app_name,
            agent_name=tool_context.agent_name,
            user_id=user_id,
        )
        job_id = message.message_id

        return ToolResponse(
            result={
                "job_id": job_id,
                "data_source_creator_id": data_source.creator_id,
                "data_source_name": data_source.name,
            },
            status=ToolResponseStatus.PENDING,
        )

    agent = tool_context._invocation_context.agent
    assert isinstance(agent, LlmAgent)
    agent_model = agent.canonical_model

    text = await summarize_data_source(data_source, agent_model)

    return ToolResponse(
        status=ToolResponseStatus.SUCCESS,
        result={
            "summary": text,
            "data_source_creator_id": data_source.creator_id,
            "data_source_name": data_source.name,
        },
    )
