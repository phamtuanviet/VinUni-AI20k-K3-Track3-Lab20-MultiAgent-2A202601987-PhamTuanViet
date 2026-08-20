"""Benchmark skeleton for single-agent vs multi-agent."""

from collections.abc import Callable
from time import perf_counter

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState

Runner = Callable[[str], ResearchState]


def run_benchmark(
    run_name: str, query: str, runner: Runner
) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency and return a metric object."""

    started = perf_counter()
    try:
        state = runner(query)
        latency = perf_counter() - started
        
        # Calculate cost
        total_cost = sum(res.metadata.get("cost", 0) for res in state.agent_results)
        
        # Quality check using LLM
        import re

        from multi_agent_research_lab.services.llm_client import LLMClient
        
        quality_score = 0.0
        if state.final_answer:
            try:
                llm = LLMClient()
                eval_sys = (
                    "You are an evaluator. Grade the answer from 1 to 10 based on depth, "
                    "clarity, and factual grounding. Output only a number."
                )
                eval_usr = f"Query: {query}\n\nAnswer: {state.final_answer}"
                eval_resp = llm.complete(eval_sys, eval_usr)
                match = re.search(r"(\d+)", eval_resp.content)
                if match:
                    quality_score = float(match.group(1))
            except Exception:
                pass

        metrics = BenchmarkMetrics(
            run_name=run_name, 
            latency_seconds=latency,
            estimated_cost_usd=total_cost,
            quality_score=quality_score,
            citation_coverage=1.0 if "[1]" in (state.final_answer or "") else 0.0,
            failure_rate=1.0 if state.errors else 0.0
        )
        return state, metrics
        
    except Exception as e:
        latency = perf_counter() - started
        metrics = BenchmarkMetrics(
            run_name=run_name,
            latency_seconds=latency,
            failure_rate=1.0,
            notes=str(e)
        )
        from multi_agent_research_lab.core.schemas import ResearchQuery
        return ResearchState(request=ResearchQuery(query=query)), metrics
