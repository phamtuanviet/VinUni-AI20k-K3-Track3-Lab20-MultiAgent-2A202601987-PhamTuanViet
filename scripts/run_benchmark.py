#!/usr/bin/env python3
import os
import sys

# Ensure .env is loaded (for benchmark script run directly)
from dotenv import load_dotenv
load_dotenv()

from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.evaluation.benchmark import run_benchmark
from multi_agent_research_lab.evaluation.report import render_markdown_report
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.services.search_client import SearchClient
import time

def baseline_runner(query_str: str) -> ResearchState:
    request = ResearchQuery(query=query_str)
    state = ResearchState(request=request)
    
    search_client = SearchClient()
    sources = search_client.search(query_str, max_results=request.max_sources)
    state.sources = sources
    
    sources_text = "\n\n".join([f"Source {i+1}: {s.title}\nURL: {s.url}\nContent: {s.snippet}" for i, s in enumerate(sources)])
    
    llm_client = LLMClient()
    system_prompt = f"You are a helpful assistant. Write a comprehensive response based on the provided sources. Tailor your response to the target audience: {request.audience}."
    user_prompt = f"Query: {query_str}\n\nSources:\n{sources_text}"
    
    response = llm_client.complete(system_prompt, user_prompt)
    state.final_answer = response.content
    
    # Store token info manually for cost calculation in benchmark
    from multi_agent_research_lab.core.schemas import AgentName, AgentResult
    state.agent_results.append(AgentResult(
        agent=AgentName.SUPERVISOR,  # Hack: bypass validation for baseline
        content=response.content,
        metadata={"cost": response.cost_usd, "input_tokens": response.input_tokens, "output_tokens": response.output_tokens}
    ))
    return state

def multi_agent_runner(query_str: str) -> ResearchState:
    request = ResearchQuery(query=query_str)
    state = ResearchState(request=request)
    workflow = MultiAgentWorkflow()
    return workflow.run(state)

def main():
    query = "Research GraphRAG state-of-the-art and write a 500-word summary"
    print(f"Running benchmark for query: '{query}'")
    
    print("Running baseline...")
    baseline_state, baseline_metrics = run_benchmark("Single-Agent Baseline", query, baseline_runner)
    
    print("Running multi-agent...")
    multi_state, multi_metrics = run_benchmark("Multi-Agent Workflow", query, multi_agent_runner)
    
    metrics = [baseline_metrics, multi_metrics]
    
    report_content = render_markdown_report(metrics)
    
    # Add Failure Mode analysis
    report_content += """
### Phân tích Failure Mode

**Failure Mode Gặp Phải:**
Khi test `SupervisorAgent`, tôi gặp lỗi Pydantic `ValidationError: String should have at least 5 characters` vì ban đầu câu query test chỉ có 4 ký tự (`"test"`). Hệ thống đã chặn lỗi này do schema `ResearchQuery` yêu cầu `min_length=5`.

**Cách Khắc Phục:**
Tôi đã sửa lại câu query trong file test từ `"test"` thành `"test_query"` (dài hơn 5 ký tự). Điều này đảm bảo dữ liệu truyền vào luôn hợp lệ theo quy định của Pydantic schema, giúp hệ thống tránh được các đầu vào "rác" hay quá ngắn ngay từ đầu.
"""
    
    with open("reports/benchmark_report.md", "w") as f:
        f.write(report_content)
        
    print("Benchmark completed. Report saved to reports/benchmark_report.md")

if __name__ == "__main__":
    main()
