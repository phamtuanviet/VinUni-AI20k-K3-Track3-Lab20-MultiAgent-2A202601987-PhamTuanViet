#!/bin/bash
# Script to run multi-agent with LangSmith tracing enabled

echo "Generating trace with LangSmith..."
echo "Ensure you have set LANGCHAIN_TRACING_V2=true and LANGCHAIN_API_KEY in your .env file."

export LANGCHAIN_TRACING_V2=true

# Load environment variables from .env if it exists
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

python -m multi_agent_research_lab.cli multi-agent --query "Research GraphRAG state-of-the-art and write a 500-word summary"

echo ""
echo "Done! Please check your LangSmith dashboard (https://smith.langchain.com/) for the trace and take a screenshot."
