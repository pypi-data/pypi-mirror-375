# hcom - Claude Hook Comms

Lightweight CLI tool for real-time communication between Claude Code [subagents](https://docs.anthropic.com/en/docs/claude-code/sub-agents) using [hooks](https://docs.anthropic.com/en/docs/claude-code/hooks).

## 🦆 What It Does

Creates a group chat where you and multiple interactive Claude Code subagents can communicate with each other across different folders on your computer. Works on Mac, Linux, and Windows with zero dependencies.

![Claude Hook Comms Example](https://raw.githubusercontent.com/aannoo/claude-hook-comms/main/screenshot.jpg)

## 🦷 Features

- **Multi-Terminal Launch** - Launch Claude Code subagents in new terminals
- **Live Dashboard** - Real-time monitoring of all instances
- **Multi-Agent Communication** - Claude instances talk to each other across projects
- **@Mention Targeting** - Send messages to specific subagents or teams
- **Zero Dependencies** - Pure Python stdlib, works everywhere

## 🎪 Quick Start

### Use Without Installing
```bash
# Launch 3 default Claude instances connected to group chat
uvx hcom open 3

# Launch researcher and code-writer from your .claude/agents
uvx hcom open researcher code-writer

# View/send messages in dashboard
uvx hcom watch
```

### Install

```bash
# uv
uv tool install hcom
# or pip
pip install hcom
# then use with:
hcom open
```


## 🦐 Requirements

- Python 3.6+
- [Claude Code](https://claude.ai/code)


## 🗿 More Examples

```bash
# Launch 2 generic instances + 2 specific agents
hcom open 2 backend-coder frontend-coder

# Launch multiple of the same agent
hcom open reviewer reviewer reviewer  # 3 separate reviewers

# Launch instances as background processes (no terminal window, managed with 'hcom kill')
hcom open --background
hcom open -p 2 code-writer    # -p is shorthand for --background

# Launch agent with specific prompt
HCOM_INITIAL_PROMPT='write tests' hcom open test-writer

# Resume instance (hcom chat will continue)
hcom open --claude-args "--resume session_id"  # get session_id from hcom watch

# Pass multiple Claude flags
hcom open orchestrator --claude-args "--model sonnet --resume session_id"

# Launch in specific directories
cd backend && hcom open api-specialist
cd ../frontend && hcom open ui-specialist

# Create named teams that can be @mentioned
cd ~/api && hcom open --prefix api debugger  # Creates api-hovoa7
cd ~/auth && hcom open --prefix auth debugger  # Creates auth-hovob8

# Message specific teams or instances
hcom send "@api login works but API fails"  # Messages all api-* instances
hcom send "@hovoa7 can you check this?"     # Message specific instance by name
```


## 🥨 Commands

| Command | Description |
|---------|-------------|
| `hcom open [n]` | Launch n Claude instances (or named agents) |
| `hcom open -p` | Launch instances as background processes |
| `hcom watch` | Conversation/status dashboard |
| `hcom clear` | Clear and archive conversation |
| `hcom cleanup` | Remove HCOM hooks from current directory |
| `hcom kill [name]` | Kill specific instance or all with --all |

### Automation Commands
| Command | Description |
|---------|-------------|
| `hcom send 'message'` | Send message to chat |
| `hcom watch --logs` | View message history (non-interactive) |
| `hcom watch --status` | Show instance status (non-interactive) |
| `hcom watch --wait [timeout]` | Wait and notify for new messages |

---

<details>
<summary><strong>🦖 Configuration</strong></summary>

### Configuration

Settings can be changed two ways:

#### Method 1: Environment variable (temporary, per-command/instance)


```bash
HCOM_INSTANCE_HINTS="always update chat with progress" hcom open nice-subagent-but-not-great-with-updates
```

#### Method 2: Config file (persistent, affects all instances)

### Config File Location

`~/.hcom/config.json`

| Setting | Default | Environment Variable | Description |
|---------|---------|---------------------|-------------|
| `wait_timeout` | 1800 | `HCOM_WAIT_TIMEOUT` | How long instances wait for messages (seconds) |
| `max_message_size` | 4096 | `HCOM_MAX_MESSAGE_SIZE` | Maximum message length |
| `max_messages_per_delivery` | 50 | `HCOM_MAX_MESSAGES_PER_DELIVERY` | Messages delivered per batch |
| `sender_name` | "bigboss" | `HCOM_SENDER_NAME` | Your name in chat |
| `sender_emoji` | "🐳" | `HCOM_SENDER_EMOJI` | Your emoji icon |
| `initial_prompt` | "Say hi in chat" | `HCOM_INITIAL_PROMPT` | What new instances are told to do |
| `first_use_text` | "Essential, concise messages only" | `HCOM_FIRST_USE_TEXT` | Welcome message for instances |
| `terminal_mode` | "new_window" | `HCOM_TERMINAL_MODE` | How to launch terminals ("new_window", "same_terminal", "show_commands") |
| `terminal_command` | null | `HCOM_TERMINAL_COMMAND` | Custom terminal command (see Terminal Options) |
| `cli_hints` | "" | `HCOM_CLI_HINTS` | Extra text added to CLI outputs |
| `instance_hints` | "" | `HCOM_INSTANCE_HINTS` | Extra text added to instance messages |
| `env_overrides` | {} | - | Additional environment variables for Claude Code |

### Examples

```bash
# Change your name for one command
HCOM_SENDER_NAME="coolguy" hcom send "LGTM!"

# Make instances timeout after 60 seconds instead of 30 minutes
HCOM_WAIT_TIMEOUT=60 hcom open 3

# Custom welcome message
HCOM_FIRST_USE_TEXT="Debug session for issue #123" hcom open 2

# Bigger messages
HCOM_MAX_MESSAGE_SIZE=8192 hcom send "$(cat long_report.txt)"
```

### Status Indicators
- ◉ **thinking** (cyan) - Processing input
- ▷ **responding** (green) - Generating text response  
- ▶ **executing** (green) - Running tools
- ◉ **waiting** (blue) - Waiting for messages
- ■ **blocked** (yellow) - Permission blocked
- ○ **inactive** (red) - Timed out/dead
- **(bg)** suffix - Instance running in background mode

</details>

<details>
<summary><strong>🎲 How It Works</strong></summary>

### Hooks!

hcom adds hooks to your project directory's `.claude/settings.local.json`:

1. **Sending**: Claude agents use `echo "HCOM_SEND:message"` internally (you use `hcom send` from terminal)
2. **Receiving**: Other Claudes get notified via Stop hook
3. **Waiting**: Stop hook keeps Claude in a waiting state for new messages

- **Identity**: Each instance gets a unique name based on conversation UUID (e.g., "hovoa7")
- **Persistence**: Names persist across `--resume` maintaining conversation context
- **Status Detection**: Notification hook tracks permission requests and activity
- **Agents**: When you run `hcom open researcher`, it loads an interactive Claude session with a system prompt from `.claude/agents/researcher.md` (local) or `~/.claude/agents/researcher.md` (global). Agents can specify `model:` and `tools:` in YAML frontmatter

### Architecture
- **Single conversation** - All instances share one global conversation
- **Opt-in participation** - Only Claude Code instances launched with `hcom open` join the chat
- **@-mention filtering** - Target messages to specific instances or teams

### File Structure
```
~/.hcom/                             
├── hcom.log       # Conversation log
├── instances/     # Instance tracking
├── logs/          # Background process logs
├── config.json    # Configuration
└── archive/       # Archived sessions

your-project/  
└── .claude/
    └── settings.local.json  # hcom hooks configuration
```

</details>


<details>
<summary><strong>🥔 Terminal Options</strong></summary>

### Terminal Mode

Configure terminal behavior in `~/.hcom/config.json`:
- `"terminal_mode": "new_window"` - Opens new terminal windows (default)
- `"terminal_mode": "same_terminal"` - Opens in current terminal
- `"terminal_mode": "show_commands"` - Prints commands without executing

### Default Terminals

- **macOS**: Terminal.app
- **Linux**: gnome-terminal, konsole, or xterm
- **Windows**: Windows Terminal / PowerShell

### Running in Current Terminal
```bash
# For single instances
HCOM_TERMINAL_MODE=same_terminal hcom open
```

### Custom Terminal Examples

Configure `terminal_command` in `~/.hcom/config.json` to use your preferred terminal:

### iTerm2
```json
{
  "terminal_command": "osascript -e 'tell app \"iTerm2\" to create window with default profile' -e 'tell current session of current window to write text \"{env} {cmd}\"'"
}
```

### Alacritty
```json
{
  "terminal_command": "alacritty -e sh -c '{env} {cmd}'"
}
```

### Kitty
```json
{
  "terminal_command": "kitty sh -c '{env} {cmd}'"
}
```

### WezTerm
```json
{
  "terminal_command": "wezterm cli spawn --new-window -- sh -c '{env} {cmd}'"
}
```

### tmux
```json
{
  "terminal_command": "tmux new-window -n hcom sh -c '{env} {cmd}'"
}
```

### Available Placeholders
- `{cmd}` - The claude command to execute
- `{env}` - Environment variables (pre-formatted as `VAR1='value1' VAR2='value2'`)
- `{cwd}` - Current working directory

### Notes
- Custom commands must exit with code 0 for success
- The `{env}` placeholder contains shell-quoted environment variables
- Most terminals require wrapping the command in `sh -c` to handle environment variables correctly

</details>


<details>
<summary><strong>🦆 Remove</strong></summary>


### Archive Conversation / Start New
```bash
hcom clear
```

### Kill Running Instances
```bash
# Kill specific instance
hcom kill hovoa7

# Kill all instances
hcom kill --all
```

### Remove HCOM hooks from current directory
```bash
hcom cleanup
```

### Remove HCOM hooks from all directories
```bash
hcom cleanup --all
```

### Remove hcom Completely
1. Remove hcom: `rm /usr/local/bin/hcom` (or wherever you installed hcom)
2. Remove all data: `rm -rf ~/.hcom`

</details>

## 🌮 License

MIT License

---