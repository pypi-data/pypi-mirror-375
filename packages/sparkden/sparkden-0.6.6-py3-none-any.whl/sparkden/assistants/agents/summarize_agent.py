from typing import TYPE_CHECKING

from google.adk.agents import LlmAgent

if TYPE_CHECKING:
    from google.adk.models.base_llm import BaseLlm

SYSTEM_PROMPT = """
#Task
请对用户提供的文本进行简洁而全面的总结

#Rules
- 抓住主要观点和关键信息，并保持语言清晰易懂
- 总结应结构良好，可分为要点或段落，长度控制在 500 字以内，杜绝冗余内容
- 可以适当使用 emoji 和段落格式，以增强可读性
- 以 markdown 格式输出
"""


def get_summarize_agent(model: "str | BaseLlm") -> LlmAgent:
    return LlmAgent(
        name="summarize",
        description="帮助用户总结长文",
        model=model,
        instruction=SYSTEM_PROMPT,
    )
