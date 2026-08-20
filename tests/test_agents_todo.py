"""Skeleton guard test.

NOTE(student): Test này chỉ xác nhận skeleton còn nguyên TODO. Sau khi bạn implement
SupervisorAgent, test này SẼ FAIL - đó là điều bình thường. Hãy xóa hoặc thay thế nó
bằng unit test thật cho routing policy của bạn.
"""


from multi_agent_research_lab.agents import SupervisorAgent
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState


def test_supervisor_routes_to_researcher() -> None:
    state = ResearchState(request=ResearchQuery(query="Explain multi-agent systems"))
    agent = SupervisorAgent()
    new_state = agent.run(state)
    assert new_state.route_history[-1] == "researcher"
    
def test_supervisor_routes_to_analyst() -> None:
    state = ResearchState(request=ResearchQuery(query="test_query"), research_notes="Notes here")
    agent = SupervisorAgent()
    new_state = agent.run(state)
    assert new_state.route_history[-1] == "analyst"

def test_supervisor_routes_to_writer() -> None:
    state = ResearchState(
        request=ResearchQuery(query="test_query"), 
        research_notes="Notes here",
        analysis_notes="Analysis here"
    )
    agent = SupervisorAgent()
    new_state = agent.run(state)
    assert new_state.route_history[-1] == "writer"
    
def test_supervisor_routes_to_done_when_all_present() -> None:
    state = ResearchState(
        request=ResearchQuery(query="test_query"), 
        research_notes="Notes here",
        analysis_notes="Analysis here",
        final_answer="Final answer"
    )
    agent = SupervisorAgent()
    new_state = agent.run(state)
    assert new_state.route_history[-1] == "done"
