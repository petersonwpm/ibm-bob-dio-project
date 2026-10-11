# DIO Explorer 🚀

> Project developed during the **[IBM Bob: Enterprise AI for Developers and Tech Leaders](https://web.dio.me/track/6c94a3da-1f22-45f6-be56-a2bad071ef51)** bootcamp on the [DIO](https://www.dio.me) platform.

A terminal-based learning track explorer built with Python and the `curses` library. It lets users browse and filter learning tracks, track their progress, complete coding challenges, and generate certificates — all from the terminal.

**Languages:** [Português (Brasil)](README.md) | English

---

## Development Approach

This project explores AI-assisted software development using IBM Bob.

The development process focuses on five practices:

- **Agent guidance:** define project conventions, technical constraints, and collaboration rules in `AGENTS.md`.
- **Solution review:** review the alternatives suggested by Bob and discuss important architecture decisions before implementation.
- **Feature planning:** decide on features and implementation approaches together instead of automatically accepting the agent's first suggestion.
- **Code validation:** use tools like Ruff to check code quality and formatting instead of relying only on the agent's review.
- **Testing:** identify and write tests to check application behavior and validate architecture decisions.

The goal is to explore how a developer can guide an AI agent through the software development process while keeping control of design decisions and code quality.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📋 **Browse learning tracks** | Lists all 30 available tracks, including level, technology, and badges |
| 🔍 **Filter by name or technology** | Use `/trilha [filter]` to search tracks |
| ⏵ **Track progress** | Start or remove tracks from your progress list; progress is saved between sessions |
| ⚔️ **Coding challenges** | Generates a challenge based on the track's level and technology |
| 🏆 **Complete tracks** | Marks a track as completed after its challenge is finished |
| 🎓 **Generate certificates** | Creates a personalized certificate with the user's name, badges, and verification code |
| 💾 **Data storage** | Progress and certificates are saved to local JSON files |

---

## 🏗️ Architecture

The project uses the **MVC (Model–View–Controller)** pattern with an intermediate service layer to separate responsibilities and make testing easier.

```text
dio_explorer/src/
├── model.py       # Model — data types (TypedDicts) and repositories
├── service.py     # Service — business logic (search, progress, challenges, certificates)
├── controller.py  # Controller — application state and keyboard event handling
├── view.py        # View — all curses rendering, with no internal state
└── tui.py         # Entry point — connects the layers and runs the main loop
```

### Layer diagram

```text
┌─────────────────────────────────────────────────────────────┐
│                         tui.py                              │
│                  (entry point · event loop)                 │
└───────┬──────────────────────────────────────┬─────────────┘
        │                                      │
        ▼                                      ▼
┌───────────────┐                    ┌──────────────────┐
│ controller.py │                    │    view.py       │
│  AppState     │◄── reads state ────│  draw_list()     │
│  Controller   │                    │  draw_detail()   │
└───────┬───────┘                    │  show_fullscreen │
        │ delegates                  │  show_challenge  │
        ▼                            │  show_certificate│
┌───────────────┐                    └──────────────────┘
│  service.py   │
│ TrackService  │
│ ProgressSvc   │
│ ChallengeSvc  │
│ CertificateSvc│
└───────┬───────┘
        │ accesses
        ▼
┌───────────────┐
│   model.py    │
│  Track (dict) │
│ TrackRepository│
│ ProgressRepo  │
└───────┬───────┘
        │ reads/writes
        ▼
┌───────────────────────────────────┐
│  dio_explorer/data/               │
│  ├── trilhas_dio.json             │
│  ├── progress.json                │
│  └── certificados-emitidos/       │
│      └── certificado_trilha_N.json│
└───────────────────────────────────┘
```

### Layer descriptions

**`model.py` — Model**

- `Track` / `Promotion` / `Live` — `TypedDict` definitions matching the JSON schema
- `TrackRepository` — loads and provides the list of tracks from the JSON file
- `ProgressRepository` — saves the `in_progress` and `completed` sets to `progress.json`

**`service.py` — Service Layer**

- `TrackService` — searches and filters tracks; returns `SearchResult`
- `ProgressService` — business logic for starting, removing, and completing tracks
- `ChallengeService` — generates challenge text based on the track's level
- `CertificateService` — generates, saves, and reloads certificates as JSON

**`controller.py` — Controller**

- `AppState` — a dataclass containing the application state, including visible tracks, selection, command mode, and messages
- `Controller` — handles keyboard events, coordinates the services, and updates the state

**`view.py` — View**

- Rendering functions that receive data as parameters and do not store application state
- `draw_list()`, `draw_detail()`, `draw_cmdbar()` — panels in the main layout
- `show_fullscreen()`, `show_challenge()`, `show_certificate()` — overlay screens
- All rendering uses `win.noutrefresh()` and `curses.doupdate()` for atomic updates

---

## 🗂️ File structure

```text
ibm-bob-dio-project/
├── README.md
├── AGENTS.md                        # Development rules for AI agents
├── pyproject.toml                   # Project and Ruff configuration
├── .venv/                           # Virtual environment (not tracked)
├── dio_explorer/
│   ├── src/
│   │   ├── tui.py                   # Entry point
│   │   ├── model.py                 # Model layer
│   │   ├── service.py               # Service layer
│   │   ├── controller.py            # Controller layer
│   │   └── view.py                  # View layer
│   ├── data/
│   │   ├── trilhas_dio.json         # Catalog of 30 tracks (read-only)
│   │   ├── progress.json            # User progress (generated at runtime)
│   │   └── certificados-emitidos/   # Generated certificates (created at runtime)
│   ├── mcp/
│   │   └── server.py                # MCP server (exposes tools to AI agents)
│   ├── docs/
│   │   └── mvc-refactor.md          # Architecture documentation and testing roadmap
│   └── commands/                    # Reserved for future use
├── tests/
│   ├── conftest.py                  # Shared fixtures (sample data, tmp_path)
│   ├── test_model.py                # Tests for TrackRepository and ProgressRepository
│   ├── test_service.py              # Tests for TrackService, ProgressService, ChallengeService, CertificateService
│   ├── test_controller.py            # Controller tests (navigation, commands, filters)
│   └── test_mcp_tools.py             # Tests for the 7 MCP server tools
├── .bob/
│   ├── commands/                    # Bob slash commands (/trilha, /desafio, /certificado)
│   └── skills/                      # Bob skills matching those commands
```

---

## ⌨️ TUI commands

| Key / Command | Action |
|---|---|
| `↑` / `↓` | Move between tracks |
| `Enter` | Open details for the selected track |
| `/trilha [filter]` | Filter tracks by name or technology |
| `/desafio` | Show only tracks in progress |
| `/certificado` | Show only completed tracks |
| `Esc` | Clear the filter or close an overlay |
| `q` | Exit the application |

**On the track details screen (`Enter`):**

| Key | Condition | Action |
|---|---|---|
| `S` | Any track | Start or remove the track from progress |
| `D` | Track in progress | Open a coding challenge |
| `C` | Completed track | View the certificate |

---

## 🚀 Getting started

### Requirements

- Python 3.12+
- [`uv`](https://github.com/astral-sh/uv) (package manager)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd ibm-bob-dio-project

# Create the virtual environment and install dependencies
uv venv
uv pip install --python .venv/bin/python "mcp[cli]>=2.3.0" ruff
```

### Run the TUI

```bash
.venv/bin/python dio_explorer/src/tui.py
```

> **Important:** Always run the application from the project root so that data file paths resolve correctly.

---

## 🛠️ Development

### Tests

The project uses **pytest**. Each layer is tested in isolation, without a terminal or real data files.

```bash
# Run all tests
.venv/bin/python -m pytest tests/ -v

# Run a single module
.venv/bin/python -m pytest tests/test_service.py -v
```

**Test coverage:**

| File | What it tests |
|---|---|
| `test_model.py` | JSON loading, adding/removing/completing progress in `ProgressRepository`, and disk persistence |
| `test_service.py` | Track search and filtering, progress updates, challenge generation (three levels plus fallback), and certificate generation and loading |
| `test_controller.py` | Keyboard navigation, command mode (`/trilha`, `/desafio`, `/certificado`), scrolling, progress updates, and certificate caching |
| `test_mcp_tools.py` | All 7 MCP tools, using `monkeypatch` to inject services |

**Testing strategies:**

- All tests use pytest's `tmp_path` fixture. No real files are read or written.
- `test_controller.py` does not initialize curses. Key constants such as `KEY_DOWN` and `KEY_UP` are integers and can be used directly.
- `test_mcp_tools.py` uses `monkeypatch` to replace the server singletons (`_track_svc`, `_progress_svc`, etc.) with temporary instances, keeping tests isolated.

### Linting and formatting

```bash
# Check
.venv/bin/ruff check dio_explorer/
.venv/bin/ruff format --check dio_explorer/

# Apply automatic fixes
.venv/bin/ruff check --fix dio_explorer/ && .venv/bin/ruff format dio_explorer/
```

### Syntax validation

```bash
python3 -m py_compile dio_explorer/src/model.py \
                       dio_explorer/src/service.py \
                       dio_explorer/src/controller.py \
                       dio_explorer/src/view.py \
                       dio_explorer/src/tui.py
```

### Code conventions

- **Code language:** English (class names, methods, variables, and docstrings)
- **UI language:** Portuguese (text shown to users in the terminal)
- **`model.py` and `controller.py` do not import `curses`** — they can be tested without a terminal
- **`view.py` never calls `win.refresh()`** — it uses `win.noutrefresh()` and `curses.doupdate()`
- **`line-length = 100`** is configured in `pyproject.toml`

---

## 🤖 MCP server

The project includes an [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server at `dio_explorer/mcp/server.py`. It exposes DIO Explorer features as tools for AI agents such as IBM Bob.

### Available tools

| Tool | Description |
|---|---|
| `list_tracks` | Lists all tracks, with an optional name or technology filter |
| `get_track` | Returns full details for a track by ID |
| `get_progress` | Returns the IDs of tracks in progress and completed tracks |
| `toggle_progress` | Starts or removes a track from progress |
| `generate_challenge` | Generates a coding challenge for a track by ID |
| `complete_track` | Marks a track as completed (irreversible) |
| `get_certificate` | Loads or generates a certificate for a completed track |

### Register with Bob

Add the following to the workspace's `mcp.json` file (`.bob/mcp.json`):

```json
{
  "mcpServers": {
    "dio-explorer": {
      "command": ".venv/bin/python",
      "args": ["dio_explorer/mcp/server.py"]
    }
  }
}
```

> The server reads and writes the same data files as the TUI (`progress.json`, `certificados-emitidos/`), so both interfaces share the same state.

### Run the server manually (for testing)

```bash
.venv/bin/python dio_explorer/mcp/server.py
```

The server uses **stdio** transport and waits for JSON-RPC messages on standard input.

---

## 🎓 About the bootcamp

This project was developed as part of the **[IBM Bob: Enterprise AI for Developers and Tech Leaders](https://web.dio.me/track/6c94a3da-1f22-45f6-be56-a2bad071ef51)** bootcamp, offered by [DIO](https://www.dio.me) in partnership with IBM.

The bootcamp explores the use of **IBM Bob** as an AI assistant for software engineering, covering topics from application architecture to development practices supported by generative AI.

---

## 📄 License

Educational project — no commercial license.
