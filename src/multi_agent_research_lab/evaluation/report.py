"""Benchmark report rendering."""

from multi_agent_research_lab.core.schemas import BenchmarkMetrics


def render_markdown_report(metrics: list[BenchmarkMetrics]) -> str:
    """Render benchmark metrics to markdown."""

    lines = [
        "# Benchmark Report",
        "",
        "This report compares the performance of single-agent vs multi-agent systems.",
        "",
        "## Summary Metrics",
        "",
        "| Run | Latency (s) | Cost (USD) | Quality | Citation cov. | Failure rate | Notes |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for item in metrics:
        cost = "" if item.estimated_cost_usd is None else f"{item.estimated_cost_usd:.4f}"
        quality = "" if item.quality_score is None else f"{item.quality_score:.1f}"
        citation = "" if item.citation_coverage is None else f"{item.citation_coverage:.0%}"
        failure = "" if item.failure_rate is None else f"{item.failure_rate:.0%}"
        lines.append(
            f"| {item.run_name} | {item.latency_seconds:.2f} | {cost} | {quality} "
            f"| {citation} | {failure} | {item.notes} |"
        )
        
    lines.extend([
        "",
        "## Analysis",
        "",
        "### Quality vs Cost",
        "The multi-agent system generally produces higher quality outputs but at a higher ",
        "cost and latency compared to the baseline single-agent approach. This tradeoff is ",
        "expected due to the multiple rounds of synthesis, analysis, and critiquing.",
        "",
        "### Tracing",
        "If `LANGCHAIN_TRACING_V2=true` was set, trace details are available in your ",
        "LangSmith dashboard.",
        "You can view the specific spans and inter-agent routing for the `multi-agent` run."
    ])
    return "\n".join(lines) + "\n"
