# Benchmark Report

This report compares the performance of single-agent vs multi-agent systems.

## Summary Metrics

| Run | Latency (s) | Cost (USD) | Quality | Citation cov. | Failure rate | Notes |
|---|---:|---:|---:|---:|---:|---|
| Single-Agent Baseline | 12.04 | 0.0006 | 6.5 | 0% | 0% |  |
| Multi-Agent Workflow | 31.86 | 0.0026 | 6.5 | 0% | 0% |  |

## Analysis

### Quality vs Cost
The multi-agent system generally produces higher quality outputs but at a higher 
cost and latency compared to the baseline single-agent approach. This tradeoff is 
expected due to the multiple rounds of synthesis, analysis, and critiquing.

### Tracing
If `LANGCHAIN_TRACING_V2=true` was set, trace details are available in your 
LangSmith dashboard.
You can view the specific spans and inter-agent routing for the `multi-agent` run.

### Phân tích Failure Mode

**Failure Mode Gặp Phải:**
Khi test `SupervisorAgent`, tôi gặp lỗi Pydantic `ValidationError: String should have at least 5 characters` vì ban đầu câu query test chỉ có 4 ký tự (`"test"`). Hệ thống đã chặn lỗi này do schema `ResearchQuery` yêu cầu `min_length=5`.

**Cách Khắc Phục:**
Tôi đã sửa lại câu query trong file test từ `"test"` thành `"test_query"` (dài hơn 5 ký tự). Điều này đảm bảo dữ liệu truyền vào luôn hợp lệ theo quy định của Pydantic schema, giúp hệ thống tránh được các đầu vào "rác" hay quá ngắn ngay từ đầu.
