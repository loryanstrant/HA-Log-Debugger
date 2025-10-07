"""AI-powered log analysis using Home Assistant AI Tasks."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.core import HomeAssistant

if TYPE_CHECKING:
    from .log_monitor import LogEntry

_LOGGER = logging.getLogger(__name__)


class AIAnalyzer:
    """Analyze log entries using AI."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the AI analyzer."""
        self.hass = hass

    async def analyze_log_entry(self, entry: LogEntry) -> dict[str, Any] | None:
        """Analyze a log entry using AI."""
        try:
            # Build the analysis prompt
            prompt = self._build_analysis_prompt(entry)
            
            # Check if conversation integration is available
            if not self.hass.services.has_service("conversation", "process"):
                _LOGGER.warning("Conversation integration not available for AI analysis")
                return self._fallback_analysis(entry)
            
            # Use the conversation API to analyze
            response = await self.hass.services.async_call(
                "conversation",
                "process",
                {
                    "text": prompt,
                },
                blocking=True,
                return_response=True,
            )
            
            if response and "response" in response:
                return self._parse_ai_response(response["response"].get("speech", {}).get("plain", {}).get("speech", ""))
            
            return self._fallback_analysis(entry)
            
        except Exception as e:
            _LOGGER.error("Error during AI analysis: %s", e, exc_info=True)
            return self._fallback_analysis(entry)

    def _build_analysis_prompt(self, entry: LogEntry) -> str:
        """Build the prompt for AI analysis."""
        prompt_parts = [
            "You are a Home Assistant expert helping to debug log errors. Analyze the following log entry and provide:",
            "1. A clear explanation of what the error means (in simple terms)",
            "2. The likely root cause",
            "3. Step-by-step instructions to fix it",
            "4. If applicable, provide corrected YAML configuration",
            "",
            f"**Log Level:** {entry.level}",
            f"**Component:** {entry.component or 'Unknown'}",
            f"**Message:** {entry.message}",
        ]
        
        if entry.entity_id:
            prompt_parts.append(f"**Entity ID:** {entry.entity_id}")
        
        if entry.device_id:
            prompt_parts.append(f"**Device ID:** {entry.device_id}")
        
        if entry.context.get("error_type"):
            prompt_parts.append(f"**Error Type:** {entry.context['error_type']}")
        
        if entry.context.get("basic_explanation"):
            prompt_parts.append(f"**Basic Info:** {entry.context['basic_explanation']}")
        
        if entry.context.get("device_name"):
            prompt_parts.append(f"**Device Name:** {entry.context['device_name']}")
        
        if entry.context.get("manufacturer"):
            prompt_parts.append(f"**Manufacturer:** {entry.context['manufacturer']}")
        
        if entry.context.get("model"):
            prompt_parts.append(f"**Model:** {entry.context['model']}")
        
        prompt_parts.extend([
            "",
            "Please provide your response in the following format:",
            "EXPLANATION: [your explanation here]",
            "ROOT CAUSE: [the root cause]",
            "SOLUTION: [step-by-step fix]",
            "YAML FIX: [corrected configuration if applicable, otherwise write 'N/A']",
        ])
        
        return "\n".join(prompt_parts)

    def _parse_ai_response(self, response: str) -> dict[str, Any]:
        """Parse the AI response into structured data."""
        result = {
            "explanation": "",
            "root_cause": "",
            "solution": "",
            "yaml_fix": "",
        }
        
        # Try to extract sections
        import re
        
        explanation_match = re.search(r"EXPLANATION:\s*(.+?)(?=ROOT CAUSE:|SOLUTION:|YAML FIX:|$)", response, re.DOTALL | re.IGNORECASE)
        if explanation_match:
            result["explanation"] = explanation_match.group(1).strip()
        
        root_cause_match = re.search(r"ROOT CAUSE:\s*(.+?)(?=EXPLANATION:|SOLUTION:|YAML FIX:|$)", response, re.DOTALL | re.IGNORECASE)
        if root_cause_match:
            result["root_cause"] = root_cause_match.group(1).strip()
        
        solution_match = re.search(r"SOLUTION:\s*(.+?)(?=EXPLANATION:|ROOT CAUSE:|YAML FIX:|$)", response, re.DOTALL | re.IGNORECASE)
        if solution_match:
            result["solution"] = solution_match.group(1).strip()
        
        yaml_match = re.search(r"YAML FIX:\s*(.+?)$", response, re.DOTALL | re.IGNORECASE)
        if yaml_match:
            yaml_content = yaml_match.group(1).strip()
            if yaml_content.lower() != "n/a":
                result["yaml_fix"] = yaml_content
        
        # If parsing failed, use the whole response as explanation
        if not any([result["explanation"], result["root_cause"], result["solution"]]):
            result["explanation"] = response
        
        return result

    def _fallback_analysis(self, entry: LogEntry) -> dict[str, Any]:
        """Provide basic analysis without AI."""
        explanation = "Unable to perform AI analysis. "
        solution = "Please check the Home Assistant documentation for this component. "
        
        # Use context-based explanation if available
        if entry.context.get("basic_explanation"):
            explanation += entry.context["basic_explanation"]
        else:
            explanation += "This log entry indicates an issue with the component."
        
        # Add specific guidance based on error type
        error_type = entry.context.get("error_type", "")
        
        if error_type == "template":
            solution += "For template errors:\n1. Check your Jinja2 syntax\n2. Verify all referenced entities exist\n3. Use the Template Editor in Developer Tools to test"
        elif error_type == "connection":
            solution += "For connection errors:\n1. Verify the device/service is online\n2. Check network connectivity\n3. Confirm firewall settings\n4. Restart the integration"
        elif error_type == "authentication":
            solution += "For authentication errors:\n1. Verify your credentials\n2. Check if tokens/API keys have expired\n3. Regenerate authentication tokens if needed\n4. Reconfigure the integration"
        elif error_type == "unknown" or error_type == "unavailable":
            solution += "For state issues:\n1. Wait for the entity to receive data\n2. Check if the source device is online\n3. Restart the integration\n4. Check entity state in Developer Tools"
        else:
            solution += "General troubleshooting:\n1. Check the integration's documentation\n2. Review your configuration\n3. Check system logs for more details\n4. Consider restarting Home Assistant"
        
        if entry.github_url:
            solution += f"\n\nCheck the integration repository: {entry.github_url}"
        
        return {
            "explanation": explanation,
            "solution": solution,
        }
