"""Supervisor / router skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState


class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = "supervisor"

    def run(self, state: ResearchState) -> ResearchState:
        """Update `state.route_history` with the next route."""
        
        # Enforce max iterations
        if state.iteration >= 5:
            state.record_route("done")
            state.add_trace_event(
                "supervisor_decision", {"route": "done", "reason": "max_iterations_reached"}
            )
            return state

        # If any errors occurred that we can't recover from, stop
        if state.errors and len(state.errors) > 2:
             state.record_route("done")
             state.add_trace_event(
                 "supervisor_decision", {"route": "done", "reason": "too_many_errors"}
             )
             return state

        # Routing logic
        if not state.research_notes:
            route = "researcher"
        elif not state.analysis_notes:
            route = "analyst"
        elif not state.final_answer:
            route = "writer"
        else:
            route = "done"

        state.record_route(route)
        state.add_trace_event("supervisor_decision", {"route": route, "iteration": state.iteration})
        return state
