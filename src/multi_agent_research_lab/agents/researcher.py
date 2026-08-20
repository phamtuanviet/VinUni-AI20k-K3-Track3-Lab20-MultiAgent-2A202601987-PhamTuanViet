"""Researcher agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`."""
        from multi_agent_research_lab.core.schemas import AgentName, AgentResult
        from multi_agent_research_lab.services.llm_client import LLMClient
        from multi_agent_research_lab.services.search_client import SearchClient
        
        search_client = SearchClient()
        llm_client = LLMClient()
        
        try:
            # 1. Search for information
            query = state.request.query
            sources = search_client.search(
                query, max_results=state.request.max_sources, corpus_path=state.request.corpus_path
            )
            state.sources = sources
            
            if not sources:
                state.research_notes = "No sources found."
                state.add_trace_event("researcher_search", {"query": query, "results": 0})
                return state
                
            # 2. Compile notes from sources
            sources_text = "\n\n".join(
                [f"Source {i+1}: {s.title}\nURL: {s.url}\nContent: {s.snippet}" for i, s in enumerate(sources)]
            )
            
            system_prompt = (
                "You are a research assistant. "
                "Synthesize the provided sources into concise research notes."
            )
            user_prompt = (
                f"Research Query: {query}\n\nSources:\n{sources_text}\n\n"
                "Please summarize the key findings, statistics, and main arguments from these sources. "
                "Include citations to the source numbers."
            )
            
            response = llm_client.complete(system_prompt, user_prompt)
            state.research_notes = response.content
            
            # Record agent result
            state.agent_results.append(AgentResult(
                agent=AgentName(self.name),
                content=response.content,
                metadata={
                    "cost": response.cost_usd, 
                    "input_tokens": response.input_tokens, 
                    "output_tokens": response.output_tokens
                }
            ))
            
            state.add_trace_event("researcher_complete", {"num_sources": len(sources)})
            
        except Exception as e:
            state.errors.append(f"Researcher error: {str(e)}")
            state.research_notes = f"Failed to gather research notes: {str(e)}"
            
        return state
