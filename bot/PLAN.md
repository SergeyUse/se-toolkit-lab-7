# SE Toolkit Lab 7 - Development Plan

## Overview

This document outlines the development plan for the SE Toolkit Lab 7 Telegram bot. The bot provides students with access to their lab scores, backend services, and an intelligent assistant powered by an LLM for natural language queries.

## Architecture

### Project Structure

The bot follows a layered architecture with clear separation of concerns:

```
bot/
├── bot.py              # Entry point with Telegram integration and test mode
├── config.py           # Configuration loading from environment
├── handlers/           # Command handlers (pure functions, no Telegram dependency)
├── services/           # API clients (LMS, LLM)
├── pyproject.toml      # Python project dependencies
└── .env.bot.secret     # Environment configuration
```

### Key Design Decisions

1. **Testable Handlers**: All command handlers are pure async functions that take input and return text. They have no knowledge of Telegram, making them easy to test offline using the `--test` mode.

2. **Service Layer**: API clients for LMS and LLM are encapsulated in a services layer, allowing handlers to remain focused on business logic.

3. **Configuration Management**: All configuration is loaded from environment variables via `.env.bot.secret`, keeping secrets out of source control.

## Task Breakdown

### Task 1: Scaffold (Current Task)

- Create the bot directory structure
- Implement basic handlers with placeholder responses
- Create the entry point with `--test` mode support
- Set up `pyproject.toml` with dependencies
- Create environment file templates

### Task 2: Backend Integration

- Implement real LMS API client methods in `services/lms_client.py`
- Connect `/health` command to actual backend health endpoints
- Implement `/scores` command with real API calls to fetch student scores
- Add error handling for API failures
- Implement proper response formatting

### Task 3: Intent Routing with LLM

- Implement natural language query handling
- Create intent classification system using the LLM
- Route queries to appropriate handlers based on detected intent
- Handle queries like "what labs are available" and "show my scores for lab-04"
- Add conversation context support for follow-up questions

### Task 4: Deployment

- Create Docker configuration for the bot
- Set up health check endpoints
- Configure logging and monitoring
- Document deployment procedures
- Set up CI/CD pipeline for automatic deployments

## Testing Strategy

1. **Unit Tests**: Test individual handlers with various inputs
2. **Integration Tests**: Test API client interactions with mocked responses
3. **Test Mode**: Use `--test` flag for manual testing without Telegram
4. **End-to-End Tests**: Deploy to staging and test with real Telegram bot

## Deployment Plan

1. **Development**: Local testing with `--test` mode
2. **Staging**: Deploy to VM with test Telegram bot
3. **Production**: Deploy to VM with production bot token

## Future Enhancements

- Add user authentication and session management
- Implement inline keyboard menus for common actions
- Add notification system for grade updates
- Support for multiple languages
- Analytics and usage tracking
