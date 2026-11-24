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

> ⚠️ **When wrapping the MCP in a shell script, do not capture `kdialog`/`zenity` with command substitution.** Assigning the output to a variable (`pass=$(kdialog --password …)`) makes the password appear **in plain text in Claude Code's Bash tool output panel**, visible to anyone watching the screen. The server itself is **not affected** (it uses `subprocess.run(capture_output=True)`, so the password never reaches the output); the risk only arises in shell wrappers. Always redirect the popup straight to the file:
>
> ```bash
> # ❌ VULNERABLE — the password appears in Claude Code's output
> pass=$(DISPLAY=:0 kdialog --password "Enter password")
> printf '%s' "$pass" > /tmp/.mcp-askpass
>
> # ✅ SAFE — only "OK" appears in the output
> DISPLAY=:0 kdialog --password "Enter password" > /tmp/.mcp-askpass 2>/dev/null
> chmod 600 /tmp/.mcp-askpass
> echo "OK — password captured."
> ```

## Compatibility

| Environment | Tool | Detection |
|-------------|------|-----------|
| KDE Plasma | `kdialog` | `$KDE_FULL_SESSION`, `$XDG_CURRENT_DESKTOP`, `plasmashell` |
| GNOME | `zenity` | `$GNOME_DESKTOP_SESSION_ID`, `$XDG_CURRENT_DESKTOP`, `gnome-shell` |
| No GUI | — | Descriptive error + fallback instructions |

## License

MIT
