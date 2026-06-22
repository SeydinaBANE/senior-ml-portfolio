from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI

from app.agents.state import AgentState
from app.config import settings
from app.tools.database import query_database_tool
from app.tools.search import web_search_tool

_tools: list[BaseTool] = [web_search_tool, query_database_tool]
_tools_by_name: dict[str, BaseTool] = {t.name: t for t in _tools}

_llm = ChatOpenAI(
    model=settings.openai_model,
    api_key=settings.openai_api_key,
).bind_tools(_tools)


async def _run_tool_calls(response: AIMessage) -> list[ToolMessage]:
    results: list[ToolMessage] = []
    for call in response.tool_calls:
        tool = _tools_by_name.get(call["name"])
        if tool is None:
            content = f"Unknown tool: {call['name']}"
        else:
            try:
                content = str(await tool.ainvoke(call["args"]))
            except Exception as exc:
                content = f"Tool error: {exc}"
        results.append(ToolMessage(content=content, tool_call_id=call["id"]))
    return results


async def tool_node(state: AgentState) -> AgentState:
    response: AIMessage = await _llm.ainvoke(state.messages)

    if not response.tool_calls:
        return state.model_copy(
            update={"messages": [response], "next_agent": "supervisor"}
        )

    tool_messages = await _run_tool_calls(response)
    final: AIMessage = await _llm.ainvoke(
        list(state.messages) + [response] + tool_messages
    )
    return state.model_copy(
        update={"messages": [final], "next_agent": "supervisor"}
    )
