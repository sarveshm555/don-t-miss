import os
import re
import asyncio
import datetime
from typing import Optional
from strands import Agent
from strands.models.ollama import OllamaModel
from agent.tools.reminder_tools import create_reminder, proposal_tracker
from agent.models.reminder_schema import ReminderDraft, ReminderProposal, AgentRequest, AgentResponse

DEFAULT_OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:1.7b")

class ReminderAgent:
    def __init__(self, host: str = DEFAULT_OLLAMA_HOST, model_id: str = DEFAULT_OLLAMA_MODEL):
        self.host = host
        self.model_id = model_id
        self.model = OllamaModel(host=self.host, model_id=self.model_id)

    def _build_system_prompt(self, current_date: str, current_time: str) -> str:
        return f"""You are the AI Reminder Assistant for the "Don't Miss" task management app.
Your task is to extract reminder details from user requests and call the `create_reminder` tool.

CURRENT TIME CONTEXT:
- Today's date is: {current_date}
- Current local time is: {current_time}

EXECUTION RULES:
1. Call the `create_reminder` tool EXACTLY ONCE with the extracted reminder details.
2. After the `create_reminder` tool returns, present a brief confirmation to the user in text.
3. You must NOT call `create_reminder` again for the same request.

FIELD EXTRACTION GUIDELINES:
- Calculate relative dates using today's date ({current_date}):
  * 'tomorrow' -> exactly 1 day after {current_date} (formatted as YYYY-MM-DD)
  * 'today' -> {current_date}
  * 'day after tomorrow' -> 2 days after {current_date}
- Convert times to 24-hour integer due_hour (0-23) and due_minute (0-59). E.g. '9 PM' -> due_hour=21, due_minute=0.
- Priority: 'high' for interviews, exams, deadlines, medical, or urgent tasks; 'low' for leisure/casual; else 'medium'.
- Recurrence: 'daily', 'weekly', 'monthly', or 'none'.
- Extract URLs if present.
- Title: concise core task (e.g. 'Amazon interview'). Description: reasons/details (e.g. 'prepare interview questions').
"""

    def _extract_fallback_proposal(self, text: str, raw_prompt: str) -> Optional[ReminderProposal]:
        title_match = re.search(r"\*\*Title:\*\*\s*(.+)", text, re.IGNORECASE) or re.search(r"Title:\s*(.+)", text, re.IGNORECASE)
        date_match = re.search(r"\*\*Due Date:\*\*\s*(\d{4}-\d{2}-\d{2})", text, re.IGNORECASE) or re.search(r"Due Date:\s*(\d{4}-\d{2}-\d{2})", text, re.IGNORECASE)
        time_match = re.search(r"\*\*Due Time:\*\*\s*(\d{1,2}):(\d{2})", text, re.IGNORECASE) or re.search(r"Due Time:\s*(\d{1,2}):(\d{2})", text, re.IGNORECASE)
        desc_match = re.search(r"\*\*Description:\*\*\s*(.+)", text, re.IGNORECASE) or re.search(r"Description:\s*(.+)", text, re.IGNORECASE)
        prio_match = re.search(r"\*\*Priority:\*\*\s*(low|medium|high)", text, re.IGNORECASE) or re.search(r"Priority:\s*(low|medium|high)", text, re.IGNORECASE)
        recur_match = re.search(r"\*\*Recurrence:\*\*\s*(none|daily|weekly|monthly)", text, re.IGNORECASE) or re.search(r"Recurrence:\s*(none|daily|weekly|monthly)", text, re.IGNORECASE)

        if title_match:
            title = title_match.group(1).strip().replace("*", "")
            due_date = date_match.group(1).strip() if date_match else None
            due_hour = int(time_match.group(1)) if time_match else None
            due_minute = int(time_match.group(2)) if time_match else None
            description = desc_match.group(1).strip().replace("*", "") if desc_match else None
            priority = prio_match.group(1).lower().strip() if prio_match else "medium"
            recurrence = recur_match.group(1).lower().strip() if recur_match else "none"

            draft = ReminderDraft(
                title=title,
                description=description,
                dueDate=due_date,
                dueHour=due_hour,
                dueMinute=due_minute,
                priority=priority,
                recurrence=recurrence,
                reasoning="Extracted from assistant text response (fallback)",
            )
            return ReminderProposal(
                status="PROPOSED",
                action="create_reminder",
                requires_confirmation=True,
                raw_prompt=raw_prompt,
                draft=draft,
            )
        return None

    async def process_prompt_async(
        self,
        prompt: str,
        current_date: Optional[str] = None,
        current_time: Optional[str] = None,
    ) -> AgentResponse:
        now = datetime.datetime.now()
        cur_d = current_date or now.strftime("%Y-%m-%d")
        cur_t = current_time or now.strftime("%H:%M")

        system_prompt = self._build_system_prompt(cur_d, cur_t)
        proposal_tracker.reset()

        agent = Agent(
            model=self.model,
            tools=[create_reminder],
            system_prompt=system_prompt,
            callback_handler=None,
        )

        try:
            result = await agent.invoke_async(prompt)
            result_str = str(result)
            proposal_data = proposal_tracker.get_proposal()

            # 1. Primary: If Strands executed the tool, use the tool's structured proposal
            if proposal_data:
                draft_data = proposal_data.get("draft", {})
                draft = ReminderDraft(**draft_data)
                proposal = ReminderProposal(
                    status="PROPOSED",
                    action="create_reminder",
                    requires_confirmation=True,
                    raw_prompt=prompt,
                    draft=draft,
                )
                return AgentResponse(
                    success=True,
                    proposal=proposal,
                    message=result_str,
                )
            
            # 2. Secondary fallback: only if tool was not called
            fallback = self._extract_fallback_proposal(result_str, prompt)
            if fallback:
                return AgentResponse(
                    success=True,
                    proposal=fallback,
                    message=result_str,
                )

            return AgentResponse(
                success=False,
                message=result_str,
                error="Agent did not propose a reminder for this prompt.",
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"Error executing agent: {str(e)}",
            )

    def process_prompt(
        self,
        prompt: str,
        current_date: Optional[str] = None,
        current_time: Optional[str] = None,
    ) -> AgentResponse:
        return asyncio.run(self.process_prompt_async(prompt, current_date, current_time))
