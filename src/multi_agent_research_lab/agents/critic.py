"""Optional critic agent skeleton for bonus work."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState


class CriticAgent(BaseAgent):
    """Optional fact-checking and safety-review agent."""

    name = "critic"

    def run(self, state: ResearchState) -> ResearchState:
        """Validate final answer and append findings."""
        from multi_agent_research_lab.core.schemas import AgentName, AgentResult
        from multi_agent_research_lab.services.llm_client import LLMClient
        
        llm_client = LLMClient()
        
        if not state.final_answer:
            return state

        try:
            system_prompt = (
                "You are a critical reviewer. Evaluate the provided final answer for factual "
                "accuracy, citation coverage, and potential hallucinations against the original "
                "research notes."
            )
            user_prompt = (
                f"Original Query: {state.request.query}\n\nResearch Notes:\n{state.research_notes}\n\n"
                f"Final Answer:\n{state.final_answer}\n\nPlease provide a critique of the final answer. "
                "Note any unverified claims or missing citations."
            )
            
            response = llm_client.complete(system_prompt, user_prompt)
            
            # Append critique to the final answer or store as a result
            state.final_answer += f"\n\n--- Critic's Review ---\n{response.content}"
            
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
            
            state.add_trace_event("critic_complete", {"status": "success"})
            
        except Exception as e:
            state.errors.append(f"Critic error: {str(e)}")
            
        return state
