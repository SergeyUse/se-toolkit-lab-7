"""Intent-based natural language routing using LLM.

This module handles routing user queries to appropriate backend tools
using LLM-based intent recognition and tool execution.
"""

import json
import re
import sys
from typing import Optional, Dict, Any, List, Tuple

from services import LMSClient, LLMClient, TOOL_DEFINITIONS


# System prompt for the LLM to guide tool usage
SYSTEM_PROMPT = """You are a helpful assistant for a university course management system. 
You have access to backend tools that provide information about labs, student scores, pass rates, and more.

When a user asks a question:
1. First understand what information they need
2. Call the appropriate tool(s) to get that information
3. Analyze the tool results
4. Provide a clear, helpful answer based on the data

Available tools:
- get_items: List all labs and tasks - use when user asks about available labs
- get_learners: List enrolled students - use for enrollment questions
- get_pass_rates(lab): Get scores and attempts for a lab - use for score questions
- get_scores(lab): Get score distribution - use for distribution questions
- get_timeline(lab): Get submission timeline - use for timeline questions
- get_groups(lab): Compare group performance - use for group comparisons
- get_top_learners(lab, limit): Get top students - use for leaderboard questions
- get_completion_rate(lab): Get completion percentage - use for completion questions
- trigger_sync: Refresh data from autochecker - use when user asks to update data

For multi-step questions (like "which lab has the lowest pass rate"):
1. First call get_items to get all labs
2. Then call get_pass_rates for each lab
3. Compare the results and provide the answer

Always be specific and include numbers from the data. If you don't have enough information, 
ask clarifying questions or suggest what tools could help.

If the user's message is a greeting (hello, hi, hey) or doesn't make sense, 
respond naturally without calling tools. For greetings, mention you can help with labs, scores, and analytics.
"""


class IntentRouter:
    """Routes user queries to appropriate backend tools using LLM."""
    
    def __init__(self, lms_client: LMSClient, llm_client: LLMClient):
        """Initialize the intent router.
        
        Args:
            lms_client: LMS API client for tool execution.
            llm_client: LLM client for intent recognition.
        """
        self.lms_client = lms_client
        self.llm_client = llm_client
    
    def _debug(self, message: str) -> None:
        """Print debug message to stderr."""
        print(f"[router] {message}", file=sys.stderr)
    
    async def _execute_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool and return the result.
        
        Args:
            name: Tool name.
            arguments: Tool arguments.
            
        Returns:
            Tool execution result.
        """
        self._debug(f"Executing tool: {name}({arguments})")
        
        try:
            if name == "get_items":
                success, result, error = await self.lms_client.get_items()
            elif name == "get_learners":
                success, result, error = await self.lms_client.get_learners()
            elif name == "get_pass_rates":
                lab = arguments.get("lab", "")
                success, result, error = await self.lms_client.get_pass_rates(lab)
            elif name == "get_scores":
                lab = arguments.get("lab", "")
                success, result, error = await self.lms_client.get_scores(lab)
            elif name == "get_timeline":
                lab = arguments.get("lab", "")
                success, result, error = await self.lms_client.get_timeline(lab)
            elif name == "get_groups":
                lab = arguments.get("lab", "")
                success, result, error = await self.lms_client.get_groups(lab)
            elif name == "get_top_learners":
                lab = arguments.get("lab", "")
                limit = arguments.get("limit", 5)
                success, result, error = await self.lms_client.get_top_learners(lab, limit)
            elif name == "get_completion_rate":
                lab = arguments.get("lab", "")
                success, result, error = await self.lms_client.get_completion_rate(lab)
            elif name == "trigger_sync":
                success, result, error = await self.lms_client.trigger_sync()
            else:
                return {"error": f"Unknown tool: {name}"}
            
            if success:
                self._debug(f"Tool {name} returned: {len(str(result))} chars")
                return result
            else:
                self._debug(f"Tool {name} failed: {error}")
                return {"error": error}
                
        except Exception as e:
            self._debug(f"Tool {name} exception: {e}")
            return {"error": str(e)}
    
    def _is_greeting(self, message: str) -> bool:
        """Check if message is a simple greeting."""
        greetings = ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"]
        return message.lower().strip() in greetings
    
    def _is_gibberish(self, message: str) -> bool:
        """Check if message appears to be gibberish."""
        # Very short or very long
        if len(message) < 2 or len(message) > 200:
            return True
        
        # Check for reasonable word patterns
        words = message.split()
        if len(words) == 1 and len(message) > 3:
            # Single long word - check if it has vowels
            if not re.search(r'[aeiou]', message.lower()):
                return True
        
        # Check for random character sequences
        if re.match(r'^[asdfghjklqwertyuiopzxcvbnm]+$', message.lower()):
            return True
        
        return False
    
    def _get_fallback_response(self, message: str) -> str:
        """Generate a fallback response for unrecognized input."""
        if self._is_greeting(message):
            return (
                "👋 Hello! I'm your SE Toolkit assistant. I can help you with:\n\n"
                "• Listing available labs\n"
                "• Showing pass rates and scores\n"
                "• Comparing group performance\n"
                "• Finding top students\n"
                "• Checking completion rates\n\n"
                "Just ask me a question like:\n"
                "• 'What labs are available?'\n"
                "• 'Show me scores for lab 4'\n"
                "• 'Which lab has the lowest pass rate?'"
            )
        
        if self._is_gibberish(message):
            return (
                "🤔 I'm not sure I understand. Here's what I can help you with:\n\n"
                "• /start - Welcome message\n"
                "• /help - List of commands\n"
                "• /health - Backend status\n"
                "• /labs - Available labs\n"
                "• /scores <lab_id> - Pass rates\n\n"
                "Or ask me questions like:\n"
                "• 'What labs are available?'\n"
                "• 'Show scores for lab 4'"
            )
        
        # Ambiguous input - try to help
        return (
            f"🤔 You mentioned: \"{message}\"\n\n"
            "I can help you with:\n"
            "• 'What labs are available?'\n"
            "• 'Show scores for lab 4'\n"
            "• 'Which lab has the lowest pass rate?'\n"
            "• 'Who are the top students?'"
        )
    
    async def route(self, user_message: str) -> str:
        """Route a user message through the LLM tool-calling loop.
        
        Args:
            user_message: The user's input message.
            
        Returns:
            The final response to send to the user.
        """
        # Check for simple cases first
        if self._is_greeting(user_message) or self._is_gibberish(user_message):
            return self._get_fallback_response(user_message)
        
        # Initialize conversation
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]
        
        max_iterations = 5  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            self._debug(f"Iteration {iteration}")
            
            # Call LLM
            try:
                response_text, tool_calls = await self.llm_client.chat_completion(
                    messages=messages,
                    tools=TOOL_DEFINITIONS,
                    tool_choice="auto"
                )
            except Exception as e:
                self._debug(f"LLM error: {e}")
                return f"⚠️ LLM error: {str(e)}. Please try again later."
            
            # If no tool calls, return the response
            if not tool_calls:
                self._debug(f"LLM returned text response: {len(response_text)} chars")
                return response_text or "I'm not sure how to help with that. Try asking about labs, scores, or students."
            
            # Execute tool calls
            tool_results = []
            for tool_call in tool_calls:
                function = tool_call.get("function", {})
                name = function.get("name", "")
                arguments_str = function.get("arguments", "{}")
                
                try:
                    arguments = json.loads(arguments_str) if arguments_str else {}
                except json.JSONDecodeError:
                    arguments = {}
                
                self._debug(f"LLM called: {name}({arguments})")
                
                # Execute the tool
                result = await self._execute_tool(name, arguments)
                
                # Store tool result
                tool_results.append({
                    "tool_call_id": tool_call.get("id", ""),
                    "name": name,
                    "result": result,
                })
            
            # Add tool calls and results to conversation
            messages.append({
                "role": "assistant",
                "tool_calls": tool_calls,
            })
            
            for tool_result in tool_results:
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_result["tool_call_id"],
                    "content": json.dumps(tool_result["result"], default=str),
                })
            
            self._debug(f"Feeding {len(tool_results)} tool results back to LLM")
        
        # If we hit max iterations, ask for clarification
        return "I'm having trouble processing your request. Could you please rephrase your question?"


# Global router instance
_router: Optional[IntentRouter] = None


def set_router(router: IntentRouter) -> None:
    """Set the global intent router instance."""
    global _router
    _router = router


def get_router() -> Optional[IntentRouter]:
    """Get the global intent router instance."""
    return _router
