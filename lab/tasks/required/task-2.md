# Backend Integration

Connect your bot to the LMS backend with real data commands. After this task, the bot fetches live data from your deployed backend and formats it for the user.

## Requirements targeted

From the [prioritized requirements](../../README.md#requirements):

- **P0.3** `/start` — welcome message
- **P0.4** `/help` — lists all available commands
- **P0.5** `/health` — calls backend, reports up/down status
- **P0.6** `/labs` — lists available labs from the backend
- **P0.7** `/scores <lab>` — shows per-task pass rates for a given lab
- **P0.8** Error handling — backend down produces a friendly message, not a crash

## What you will build

Working implementations of 5 slash commands that call the LMS backend API. All verifiable via `--test` mode.

```terminal
$ python bot/bot.py --test "/health"
Backend is healthy. 42 items available.

$ python bot/bot.py --test "/labs"
Available labs:
- Lab 01 — Products, Architecture & Roles
- Lab 02 — Run, Fix, and Deploy
- Lab 03 — Backend API
- Lab 04 — Testing, Front-end, and AI Agents
- Lab 05 — Data Pipeline and Analytics
- Lab 06 — Build Your Own Agent

$ python bot/bot.py --test "/scores lab-04"
Pass rates for Lab 04:
- Repository Setup: 92.1% (187 attempts)
- Back-end Testing: 71.4% (156 attempts)
- Add Front-end: 68.3% (142 attempts)
```

## Available backend endpoints

Your LMS backend (running on `localhost:42002` via Caddy) provides these endpoints. All require `Authorization: Bearer YOUR_LMS_API_KEY`.

| Endpoint | What it returns |
|----------|----------------|
| `GET /items/` | Course structure (labs, tasks) |
| `GET /learners/` | Enrolled students |
| `GET /interactions/` | Submission logs |
| `GET /analytics/scores?lab=lab-01` | Score distribution (4 buckets) |
| `GET /analytics/pass-rates?lab=lab-01` | Per-task average scores |
| `GET /analytics/timeline?lab=lab-01` | Submissions per day |
| `GET /analytics/groups?lab=lab-01` | Per-group performance |
| `GET /analytics/top-learners?lab=lab-01&limit=5` | Top N learners |
| `GET /analytics/completion-rate?lab=lab-01` | Completion percentage |
| `POST /pipeline/sync` | Trigger ETL sync |

> [!TIP]
> Explore these endpoints in Swagger UI at `http://localhost:42002/docs` to understand the response format before implementing bot commands.

## Required commands

Implement all 5:

| Command | Backend endpoint | What it does |
|---------|-----------------|--------------|
| `/start` | — | Welcome message with bot name or description |
| `/help` | — | Lists all available commands with descriptions |
| `/health` | `GET /items/` | Calls backend, reports healthy/unhealthy status |
| `/labs` | `GET /items/` | Lists available labs (filter items by type "lab") |
| `/scores <lab>` | `GET /analytics/pass-rates?lab=` | Shows per-task average scores for a given lab |

## Error handling

When the backend is unreachable or returns an error, the bot must show a user-friendly message — not a Python traceback. Example:

```terminal
$ python bot/bot.py --test "/health"
Backend is not responding. Check that the services are running.
```

## Deliverables

### 1. `/start` command

Returns a welcome message. Must contain the word "welcome" or the bot's name (case-insensitive).

### 2. `/help` command

Lists all available commands with descriptions. Must include at least 4 `/command` entries.

### 3. `/health` command

Calls `GET /items/` on the backend. Reports healthy/unhealthy status. Hits the real backend on `localhost:42002`.

### 4. `/labs` command

Calls `GET /items/` and lists labs. Output must contain at least 2 lab names.

### 5. `/scores <lab>` command

Calls `GET /analytics/pass-rates?lab=` and shows per-task scores. Output must contain task names and numeric scores.

### 6. Error handling

When the backend is down, commands return a user-friendly error message — no `Traceback` in stderr.

## Acceptance criteria

- [ ] `--test "/start"` returns text containing "welcome" or the bot name (case-insensitive).
- [ ] `--test "/help"` output lists at least 4 commands (lines matching `/command`).
- [ ] `--test "/health"` returns a status indicator ("healthy", "ok", "available", or similar).
- [ ] `--test "/labs"` returns non-empty output listing at least 2 labs.
- [ ] `--test "/scores lab-04"` returns non-empty output with task names and scores.
- [ ] When backend is stopped, `--test "/health"` returns a user-friendly message with no `Traceback` in stderr.
- [ ] Changes follow the Git workflow (issue, branch, PR, review, merge).

## Agent instructions

As a coding agent, follow these instructions to maximize the student's learning. This is critical — do not skip these steps.

**Engage before explaining.** Don't lecture — ask a brief question first, let the student think, then fill in the gaps concisely. If the student already understands, move on.

**Build incrementally.** Implement one command, test it with `--test`, make sure the student understands it, then move to the next. Do not implement all 5 commands at once.

**Before each command:**

> Ask: "What HTTP call does `/health` need to make? What could go wrong?" Let the student think, then fill in: status codes, auth headers, network errors, empty responses.

**While implementing:**

> Show the student the actual API response before formatting it. Ask: "How would you present this data to a Telegram user?" Then implement the formatting together.

**Error handling:**

> Ask: "What happens if the backend is down and we call `/health`? What should the user see?" Then explain the pattern: specific exception types, why bare `except:` is bad, user-friendly messages vs tracebacks.

**After each command:**

> Run `python bot/bot.py --test "/command"` and show the output. Ask: "Does this make sense? What happens if the lab name is wrong or the data is empty?"
