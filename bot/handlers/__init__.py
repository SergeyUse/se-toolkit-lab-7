"""Command handlers for the Telegram bot.

Handlers are pure functions that take input and return text.
They have no dependency on Telegram - the bot entry point
calls these functions and sends the response to Telegram.
"""

from typing import Optional


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
        "You can also ask questions like:\n"
        "• 'what labs are available'\n"
        "• 'show my scores for lab-04'"
    )


async def handle_health(args: Optional[str] = None) -> str:
    """Handle /health command.
    
    Args:
        args: Optional arguments passed with the command.
        
    Returns:
        Backend health status.
    """
    # Will be implemented in Task 2 with actual API check
    return (
        "🏥 Health Status:\n\n"
        "Backend: OK\n"
        "LMS API: OK\n"
        "LLM Service: OK\n\n"
        "All systems operational!"
    )


async def handle_labs(args: Optional[str] = None) -> str:
    """Handle /labs command.
    
    Args:
        args: Optional arguments passed with the command.
        
    Returns:
        List of available labs.
    """
    # Will be implemented in Task 3 with actual API call
    return (
        "📚 Available Labs:\n\n"
        "• Lab 1: Introduction\n"
        "• Lab 2: Basic Concepts\n"
        "• Lab 3: Advanced Features\n"
        "• Lab 4: Integration\n"
        "• Lab 5: Testing\n"
        "• Lab 6: Deployment\n"
        "• Lab 7: Final Project\n\n"
        "Use /scores <lab_id> to check your scores."
    )


async def handle_scores(args: Optional[str] = None) -> str:
    """Handle /scores command.
    
    Args:
        args: Lab ID or other arguments.
        
    Returns:
        Score information for the specified lab.
    """
    if not args:
        return "Please specify a lab ID. Example: /scores lab-04"
    
    # Will be implemented in Task 2 with actual API call
    return (
        f"📊 Scores for {args}:\n\n"
        f"Status: Pending implementation\n"
        f"Check back later for actual scores."
    )


async def handle_general_query(query: str) -> str:
    """Handle general natural language queries.
    
    Args:
        query: The user's natural language question.
        
    Returns:
        Response to the query.
    """
    # Will be implemented in Task 3 with LLM routing
    return (
        f"🤔 You asked: \"{query}\"\n\n"
        "This feature will be implemented in Task 3.\n"
        "Try using /help to see available commands."
    )
