"""LangGraph workflow skeleton."""

from multi_agent_research_lab.core.state import ResearchState


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph.

    Keep orchestration here; keep agent internals in `agents/`.
    """

    def __init__(self) -> None:
        from typing import Any

        from langgraph.graph import StateGraph
        self.builder = StateGraph(ResearchState)
        self.graph: Any = None

    def build(self) -> object:
        """Create a LangGraph graph."""
        from langgraph.graph import END

        from multi_agent_research_lab.agents.analyst import AnalystAgent
        from multi_agent_research_lab.agents.critic import CriticAgent
        from multi_agent_research_lab.agents.researcher import ResearcherAgent
        from multi_agent_research_lab.agents.supervisor import SupervisorAgent
        from multi_agent_research_lab.agents.writer import WriterAgent
        
        # Instantiate agents
        supervisor = SupervisorAgent()
        researcher = ResearcherAgent()
        analyst = AnalystAgent()
        writer = WriterAgent()
        critic = CriticAgent()
        
        # Add nodes
        self.builder.add_node("supervisor", supervisor.run)
        self.builder.add_node("researcher", researcher.run)
        self.builder.add_node("analyst", analyst.run)
        self.builder.add_node("writer", writer.run)
        self.builder.add_node("critic", critic.run)
        
        # Define edge routing logic from supervisor
        def router(state: ResearchState) -> str:
            if state.route_history:
                route = state.route_history[-1]
                if route == "done":
                    return END
                return route
            return END
            
        # Define edges
        self.builder.set_entry_point("supervisor")
        
        self.builder.add_conditional_edges(
            "supervisor",
            router,
            {
                "researcher": "researcher",
                "analyst": "analyst",
                "writer": "writer",
                END: END
            }
        )
        
        # Edges from workers back to supervisor
        self.builder.add_edge("researcher", "supervisor")
        self.builder.add_edge("analyst", "supervisor")
        
        # Writer goes to critic, then critic to supervisor
        self.builder.add_edge("writer", "critic")
        self.builder.add_edge("critic", "supervisor")
        
        # Compile graph
        self.graph = self.builder.compile()
        return self.graph

    def run(self, state: ResearchState) -> ResearchState:
        """Execute the graph and return final state."""
        if not self.graph:
            self.build()
            
        # Execute the compiled graph
        assert self.graph is not None
        result = self.graph.invoke(state)
        
        # The result might be returned as a dict by LangGraph or as the state model itself.
        # Handle conversion back to ResearchState if needed.
        if isinstance(result, dict):
            return ResearchState(**result)
        
        from typing import cast
        return cast(ResearchState, result)
