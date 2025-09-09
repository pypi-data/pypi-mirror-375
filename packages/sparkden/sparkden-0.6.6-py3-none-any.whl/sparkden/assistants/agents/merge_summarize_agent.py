from typing import TYPE_CHECKING

from google.adk.agents import LlmAgent

if TYPE_CHECKING:
    from google.adk.models.base_llm import BaseLlm

SYSTEM_PROMPT = """
#Background
- 正在通过“分块 + 摘要 + 合并”的方式总结一篇很长的文章
- 文章被分为多个块，并且已分别总结

#Task
请根据用户提供的分块总结，将它们按照原文顺序合并为一个连贯、结构清晰、简洁的摘要

#Rules
- 抓住主要观点和关键信息，并保持语言清晰易懂
- 总结应结构良好，可分为要点或段落，长度控制在 500 字以内，杜绝冗余内容
- 可以适当使用 emoji 和段落格式，以增强可读性
- 以 markdown 格式输出
"""


def get_merge_summarize_agent(model: "str | BaseLlm") -> LlmAgent:
    return LlmAgent(
        name="summarize",
        description="帮助用户合并长文分块总结",
        instruction=SYSTEM_PROMPT,
        model=model,
    )
