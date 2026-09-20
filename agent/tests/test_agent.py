import pytest
from fastapi.testclient import TestClient
from agent.models.reminder_schema import ReminderDraft, ReminderProposal, AgentRequest, AgentResponse
from agent.tools.reminder_tools import create_reminder, proposal_tracker
from agent.reminder_agent import ReminderAgent
from agent.app import app

def test_reminder_draft_schema_valid():
    draft = ReminderDraft(
        title="Amazon Interview",
        description="Prepare system design questions",
        dueDate="2026-09-21",
        dueHour=21,
        dueMinute=0,
        priority="high",
        recurrence="none",
        url="https://amazon.jobs",
        reasoning="Extracted Amazon interview reminder with high priority at 9 PM.",
    )
    assert draft.title == "Amazon Interview"
    assert draft.priority == "high"
    assert draft.dueHour == 21
    assert draft.dueMinute == 0

def test_reminder_proposal_requires_confirmation():
    draft = ReminderDraft(title="Team Standup", priority="medium")
    proposal = ReminderProposal(
        status="PROPOSED",
        action="create_reminder",
        requires_confirmation=True,
        raw_prompt="Remind me tomorrow for team standup",
        draft=draft,
    )
    assert proposal.requires_confirmation is True
    assert proposal.status == "PROPOSED"
    assert proposal.action == "create_reminder"

def test_create_reminder_tool_execution():
    proposal_tracker.reset()

    result = create_reminder(
        title="Doctor Appointment",
        description="Bring blood test reports",
        due_date="2026-09-22",
        due_hour=10,
        due_minute=30,
        priority="HIGH",
        recurrence="NONE",
        url=None,
        reasoning="Medical appointment marked high priority",
    )

    assert result["status"] == "PROPOSED"
    assert result["action"] == "create_reminder"
    assert result["requires_confirmation"] is True
    assert result["draft"]["title"] == "Doctor Appointment"
    assert result["draft"]["priority"] == "high"
    assert result["draft"]["recurrence"] == "none"
    assert result["draft"]["dueHour"] == 10
    assert result["draft"]["dueMinute"] == 30

    # Verify tracker was updated
    captured = proposal_tracker.get_proposal()
    assert captured is not None
    assert captured["draft"]["title"] == "Doctor Appointment"
    assert proposal_tracker.get_call_count() == 1

def test_create_reminder_tool_defaults_and_normalization():
    result = create_reminder(
        title="Casual Walk",
        priority="INVALID_PRIORITY",
        recurrence="INVALID_RECURRENCE",
    )
    assert result["draft"]["priority"] == "medium"
    assert result["draft"]["recurrence"] == "none"

def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["sdk"] == "strands-agents"
    assert data["model_provider"] == "ollama"

def test_create_reminder_endpoint_validation():
    client = TestClient(app)
    response = client.post("/agent/reminder", json={"prompt": ""})
    assert response.status_code == 400

def test_create_reminder_endpoint_with_mocked_agent(monkeypatch):
    client = TestClient(app)
    
    mock_draft = ReminderDraft(
        title="Amazon interview",
        description="prepare interview questions",
        dueDate="2026-09-21",
        dueHour=21,
        dueMinute=0,
        priority="high",
        recurrence="none",
        reasoning="Identified high priority interview reminder for tomorrow 9 PM.",
    )
    mock_proposal = ReminderProposal(
        status="PROPOSED",
        action="create_reminder",
        requires_confirmation=True,
        raw_prompt="Remind me tomorrow at 9 PM about my Amazon interview",
        draft=mock_draft,
    )
    mock_response = AgentResponse(
        success=True,
        proposal=mock_proposal,
        message="I have proposed an Amazon interview reminder for tomorrow at 9:00 PM.",
    )

    async def mock_async_process(**kwargs):
        return mock_response

    from agent.app import agent
    monkeypatch.setattr(agent, "process_prompt_async", mock_async_process)

    payload = {
        "prompt": "Remind me tomorrow at 9 PM about my Amazon interview because I need to prepare interview questions.",
        "current_date": "2026-09-20",
        "current_time": "04:20",
    }
    res = client.post("/agent/reminder", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["proposal"]["requires_confirmation"] is True
    assert body["proposal"]["draft"]["title"] == "Amazon interview"
    assert body["proposal"]["draft"]["dueHour"] == 21
    assert body["proposal"]["draft"]["dueMinute"] == 0

def test_system_prompt_rules():
    agent_inst = ReminderAgent.__new__(ReminderAgent)
    prompt = agent_inst._build_system_prompt("2026-09-20", "05:00")
    assert "Call the `create_reminder` tool EXACTLY ONCE" in prompt
    assert "present a brief confirmation to the user in text" in prompt
    assert "You must NOT call `create_reminder` again for the same request." in prompt

def test_extract_fallback_proposal():
    agent_inst = ReminderAgent.__new__(ReminderAgent)
    sample_text = """
The reminder has been created with the following details:  
**Title:** Amazon interview  
**Description:** I need to prepare interview questions  
**Due Date:** 2026-09-21  
**Due Time:** 21:00  
**Priority:** High  
**Recurrence:** None  
"""
    proposal = agent_inst._extract_fallback_proposal(sample_text, "test prompt")
    assert proposal is not None
    assert proposal.status == "PROPOSED"
    assert proposal.action == "create_reminder"
    assert proposal.requires_confirmation is True
    assert proposal.draft.title == "Amazon interview"
    assert proposal.draft.dueDate == "2026-09-21"
    assert proposal.draft.dueHour == 21
    assert proposal.draft.dueMinute == 0
    assert proposal.draft.priority == "high"
    assert proposal.draft.recurrence == "none"
