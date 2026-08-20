"""Writer agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`."""
        from multi_agent_research_lab.core.schemas import AgentName, AgentResult
        from multi_agent_research_lab.services.llm_client import LLMClient
        
        llm_client = LLMClient()
        
        if not state.analysis_notes:
            state.final_answer = "No analysis available to write the final answer."
            return state

        try:
            system_prompt = (
                "You are an expert technical writer. Write a comprehensive final answer based on the provided "
                f"research and analysis notes. Tailor your response to the target audience: {state.request.audience}."
            )
            user_prompt = (
                f"Research Query: {state.request.query}\n\nResearch Notes:\n{state.research_notes}\n\n"
                f"Analysis Notes:\n{state.analysis_notes}\n\nPlease synthesize a clear, well-structured "
                "final response with appropriate citations."
            )
            
            response = llm_client.complete(system_prompt, user_prompt)
            state.final_answer = response.content
            
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
            
            state.add_trace_event("writer_complete", {"status": "success"})
            
        except Exception as e:
            state.errors.append(f"Writer error: {str(e)}")
            state.final_answer = f"Failed to write final answer: {str(e)}"
            
        return state
