# mcp-askpass

> [Versión en español](README.md)

MCP server for secure password prompts in Claude Code.

Displays the native system password dialog (KDE or GNOME) and returns the value directly to Claude — without it appearing in the chat, in logs, or in the conversation history.

## Why

When Claude Code needs a password, the naive answer is to type it in the chat. That's a problem:

- It stays in the **conversation history**
- It ends up in the **terminal log** if you copy and paste
- It may appear in **compressed context windows** that Claude stores

`mcp-askpass` solves this: Claude calls `ask_password()`, a native popup identical to `sudo`'s appears, you type the password, and Claude receives it in memory. Nothing touches the chat.

## Requirements

- Python 3.10+
- `mcp` (`pip install mcp`)
- KDE: `kdialog` (included in `kde-cli-tools`)
- GNOME: `zenity` (`apt install zenity` / `dnf install zenity`)

## Installation

```bash
git clone https://github.com/jaimealberto/mcp-askpass
cd mcp-askpass
pip install mcp
```

Add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "mcp-askpass": {
      "type": "stdio",
      "command": "python3",
      "args": ["/path/to/mcp-askpass/mcp_askpass_server.py"]
    }
  }
}
```

Restart Claude Code.

## Usage

Claude invokes `ask_password(label)` automatically when it needs a password. You can also request it explicitly:

```
I need the database password to continue
```

Claude will call `ask_password("database")` and the popup will appear.

## Fallback for automation

If you need to pre-load the password (automated flows, remote sessions):

```bash
printf 'your_password' > /tmp/.mcp-askpass
chmod 600 /tmp/.mcp-askpass
```

The next call to `ask_password()` will read the file and delete it automatically.

## Security

- The password travels popup → MCP → Claude, never through the chat
- `/tmp/.mcp-askpass` requires `600` permissions and is deleted after the first read
- No persistent password storage
- No external dependencies beyond `mcp`

## Compatibility

| Environment | Tool | Detection |
|-------------|------|-----------|
| KDE Plasma | `kdialog` | `$KDE_FULL_SESSION`, `$XDG_CURRENT_DESKTOP`, `plasmashell` |
| GNOME | `zenity` | `$GNOME_DESKTOP_SESSION_ID`, `$XDG_CURRENT_DESKTOP`, `gnome-shell` |
| No GUI | — | Descriptive error + fallback instructions |

## License

MIT
