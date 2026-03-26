"""Command handlers for the Telegram bot.

Handlers are pure functions that take input and return text.
They have no dependency on Telegram - the bot entry point
calls these functions and sends the response to Telegram.
"""

from typing import Optional, Dict, Any
from services import LMSClient, BackendError


# Global LMS client instance (initialized by bot.py)
_lms_client: Optional[LMSClient] = None


def set_lms_client(client: LMSClient) -> None:
    """Set the LMS client for handlers to use.
    
    Args:
        client: The LMS client instance.
    """
    global _lms_client
    _lms_client = client


def get_lms_client() -> Optional[LMSClient]:
    """Get the current LMS client.
    
    Returns:
        The LMS client instance or None if not set.
    """
    return _lms_client


async def handle_start(args: Optional[str] = None) -> str:
    """Handle /start command.
    
    Args:
        args: Optional arguments passed with the command.
        
    Returns:
        Welcome message string.
    """
    return (
        "👋 Welcome to SE Toolkit Bot!\n\n"
        "I can help you with:\n"
        "• Checking your lab scores\n"
        "• Getting help with commands\n"
        "• Checking backend health\n"
        "• Finding available labs\n\n"
        "Use /help to see all available commands."
    )


async def handle_help(args: Optional[str] = None) -> str:
    """Handle /help command.
    
    Args:
        args: Optional arguments passed with the command.
        
    Returns:
        Help message with command list.
    """
    return (
        "📖 Available Commands:\n\n"
        "/start - Welcome message and bot introduction\n"
        "/help - Show this help message\n"
        "/health - Check backend service status\n"
        "/labs - List available labs\n"
        "/scores <lab_id> - Get your scores for a specific lab\n\n"
        "Examples:\n"
        "• /scores lab-04 - Get pass rates for Lab 4"
    )


async def handle_health(args: Optional[str] = None) -> str:
    """Handle /health command.
    
    Args:
        args: Optional arguments passed with the command.
        
    Returns:
        Backend health status.
    """
    client = get_lms_client()
    if not client:
        return "⚠️ LMS client not configured. Please check bot configuration."
    
    is_healthy, message = await client.health_check()
    
    if is_healthy:
        return f"🏥 {message}"
    else:
        return f"⚠️ {message}"


async def handle_labs(args: Optional[str] = None) -> str:
    """Handle /labs command.
    
    Args:
        args: Optional arguments passed with the command.
        
    Returns:
        List of available labs.
    """
    client = get_lms_client()
    if not client:
        return "⚠️ LMS client not configured. Please check bot configuration."
    
    success, labs, error = await client.get_labs()
    
    if not success:
        return f"⚠️ {error}"
    
    if not labs:
        return "📚 No labs found in the system."
    
    labs_formatted = "\n".join(f"• {lab}" for lab in labs)
    return f"📚 Available Labs:\n\n{labs_formatted}"


async def handle_scores(args: Optional[str] = None) -> str:
    """Handle /scores command.
    
    Args:
        args: Lab ID or other arguments.
        
    Returns:
        Score information for the specified lab.
    """
    if not args:
        return "⚠️ Please specify a lab ID. Example: /scores lab-04"
    
    client = get_lms_client()
    if not client:
        return "⚠️ LMS client not configured. Please check bot configuration."
    
    success, pass_rates, error = await client.get_pass_rates(args)
    
    if not success:
        return f"⚠️ {error}"
    
    if not pass_rates:
        return f"📊 No pass rate data available for {args}."
    
    # Format pass rates
    lines = [f"📊 Pass rates for {args}:"]
    for rate in pass_rates:
        task = rate.get("task", "Unknown task")
        avg_score = rate.get("avg_score", 0)
        attempts = rate.get("attempts", 0)
        lines.append(f"• {task}: {avg_score:.1f}% ({attempts} attempts)")
    
    return "\n".join(lines)


async def handle_general_query(query: str) -> str:
    """Handle general natural language queries.
    
    Args:
        query: The user's natural language question.
        
    Returns:
        Response to the query.
    """
    # Simple keyword-based routing for common queries
    query_lower = query.lower()
    
    if "lab" in query_lower and ("available" in query_lower or "list" in query_lower):
        return await handle_labs()
    
    if "score" in query_lower or "pass" in query_lower:
        # Try to extract lab ID from query
        import re
        lab_match = re.search(r'lab[- ]?\d+', query_lower, re.IGNORECASE)
        if lab_match:
            lab_id = lab_match.group().replace(" ", "-")
            return await handle_scores(lab_id)
        else:
            return "Please specify which lab you want to see scores for. Example: /scores lab-04"
    
    if "help" in query_lower or "command" in query_lower:
        return await handle_help()
    
    return (
        f"🤔 You asked: \"{query}\"\n\n"
        "I can help you with:\n"
        "• /start - Welcome message\n"
        "• /help - List of commands\n"
        "• /health - Backend status\n"
        "• /labs - Available labs\n"
        "• /scores <lab_id> - Pass rates for a lab"
    )
