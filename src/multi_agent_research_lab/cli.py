"""Command-line entrypoint for the lab starter."""

from typing import Annotated

import typer
from pydantic import ValidationError
from rich.console import Console
from rich.panel import Panel

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging

app = typer.Typer(help="Multi-Agent Research Lab starter CLI")
console = Console()


def _init() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)


def _parse_query(query: str, corpus: str | None = None) -> ResearchQuery:
    try:
        return ResearchQuery(query=query, corpus_path=corpus)
    except ValidationError as exc:
        console.print(
            Panel.fit(
                f"Invalid query: {exc.errors()[0]['msg']}",
                title="Input Error",
                style="red",
            )
        )
        raise typer.Exit(code=1) from exc


@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
    corpus: Annotated[
        str | None, typer.Option("--corpus", "-c", help="Path to offline corpus JSON file")
    ] = None,
) -> None:
    """Run a minimal single-agent baseline."""

    _init()
    request = _parse_query(query, corpus)
    state = ResearchState(request=request)
    
    import time

    from multi_agent_research_lab.services.llm_client import LLMClient
    from multi_agent_research_lab.services.search_client import SearchClient
    
    start_time = time.time()
    
    try:
        search_client = SearchClient()
        sources = search_client.search(
            query, max_results=request.max_sources, corpus_path=request.corpus_path
        )
        state.sources = sources
        
        sources_text = "\n\n".join(
            [f"Source {i+1}: {s.title}\nURL: {s.url}\nContent: {s.snippet}" for i, s in enumerate(sources)]
        )
        
        llm_client = LLMClient()
        system_prompt = (
            "You are a helpful assistant. Write a comprehensive response based on the provided sources. "
            f"Tailor your response to the target audience: {request.audience}."
        )
        user_prompt = f"Query: {query}\n\nSources:\n{sources_text}"
        
        response = llm_client.complete(system_prompt, user_prompt)
        state.final_answer = response.content
        
        duration = time.time() - start_time
        
        console.print(Panel.fit(state.final_answer, title="Single-Agent Baseline"))
        console.print(
            f"Latency: {duration:.2f}s | Tokens: {response.input_tokens} in, "
            f"{response.output_tokens} out | Cost: ${response.cost_usd:.4f}"
        )
        
    except Exception as exc:
        console.print(Panel.fit(str(exc), title="Error", style="red"))
        raise typer.Exit(code=2) from exc


@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
    corpus: Annotated[
        str | None, typer.Option("--corpus", "-c", help="Path to offline corpus JSON file")
    ] = None,
) -> None:
    """Run the multi-agent workflow skeleton."""

    _init()
    state = ResearchState(request=_parse_query(query, corpus))
    workflow = MultiAgentWorkflow()
    try:
        result = workflow.run(state)
    except StudentTodoError as exc:
        console.print(Panel.fit(str(exc), title="Expected TODO", style="yellow"))
        raise typer.Exit(code=2) from exc
    console.print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    app()
