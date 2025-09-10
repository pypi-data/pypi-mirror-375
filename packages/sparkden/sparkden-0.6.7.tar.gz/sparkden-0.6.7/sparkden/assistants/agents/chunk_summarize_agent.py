from typing import TYPE_CHECKING

from google.adk.agents import LlmAgent
from sparkden.models.shared import BaseModel

if TYPE_CHECKING:
    from google.adk.agents.readonly_context import ReadonlyContext
    from google.adk.models.base_llm import BaseLlm

SYSTEM_PROMPT = """
#Background
- 正在通过“分块 + 摘要 + 合并”的方式总结一篇很长的文章
- 文章被分为 {chunks_count} 个块
- 前 {summarized_chunks_count} 个块已经被总结

{summarized_chunks}

#Task
请对用户提供的第 {current_chunk_index} 个块进行简洁而全面的总结

#Rules
- 抓住主要观点和关键信息，并保持语言清晰易懂
- 总结应结构良好，可分为要点或段落，长度控制在 500 字以内，杜绝冗余内容
- 可以适当使用 emoji 和段落格式，以增强可读性
- 以 markdown 格式输出
"""


class ChunksState(BaseModel):
    chunks_count: int
    summarized_chunks_count: int
    summarized_chunks: list[str]
    current_chunk_index: int


def provide_instruction(ctx: "ReadonlyContext") -> str:
    chunks_state = ChunksState.model_validate(ctx.state)
    return SYSTEM_PROMPT.format(
        chunks_count=chunks_state.chunks_count,
        summarized_chunks_count=chunks_state.summarized_chunks_count,
        summarized_chunks="\n\n".join(
            [
                f"Chunk {index + 1} summary:\n{chunk}"
                for index, chunk in enumerate(chunks_state.summarized_chunks)
            ]
        ),
        current_chunk_index=chunks_state.current_chunk_index,
    )


def get_chunk_summarize_agent(model: "str | BaseLlm") -> LlmAgent:
    return LlmAgent(
        name="summarize",
        description="帮助用户总结长文中的其中一个分块",
        instruction=provide_instruction,
        model=model,
    )
