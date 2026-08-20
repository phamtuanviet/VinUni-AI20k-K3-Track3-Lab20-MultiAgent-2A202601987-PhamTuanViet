"""Analyst agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`."""
        from multi_agent_research_lab.core.schemas import AgentName, AgentResult
        from multi_agent_research_lab.services.llm_client import LLMClient
        
        llm_client = LLMClient()
        
        if not state.research_notes:
            state.analysis_notes = "No research notes available to analyze."
            return state

        try:
            system_prompt = (
                "You are an expert analyst. Your task is to analyze the research notes, extract key "
                "claims, compare viewpoints, and flag any weak evidence or conflicting information "
                "from the provided research notes."
            )
            user_prompt = (
                f"Research Query: {state.request.query}\n\nResearch Notes:\n{state.research_notes}\n\n"
                "Please provide a structured analysis highlighting main themes, consensus, "
                "disagreements, and evidence quality."
            )
            
            response = llm_client.complete(system_prompt, user_prompt)
            state.analysis_notes = response.content
            
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
            
            state.add_trace_event("analyst_complete", {"status": "success"})
            
        except Exception as e:
            state.errors.append(f"Analyst error: {str(e)}")
            state.analysis_notes = f"Failed to analyze notes: {str(e)}"
            
        return state
