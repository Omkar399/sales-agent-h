"""AI Tools package for Gemini integration."""

from .calendar_tool import CalendarTool
from .hubspot_tool import HubSpotTool
from .email_tool import EmailTool

# Tool registry for Gemini function calling
AVAILABLE_TOOLS = {
    "calendar": CalendarTool(),
    "hubspot": HubSpotTool(),
    "email": EmailTool(),
}

# Function schemas for Gemini
TOOL_FUNCTIONS = []

# Register all tool functions
for tool in AVAILABLE_TOOLS.values():
    TOOL_FUNCTIONS.extend(tool.get_function_schemas())

__all__ = ["AVAILABLE_TOOLS", "TOOL_FUNCTIONS", "CalendarTool", "HubSpotTool", "EmailTool"]
