# mcp-askpass

> [English version](README.md)

Servidor MCP para pedir contraseñas de forma segura en Claude Code.

Muestra el diálogo de contraseña nativo del sistema (KDE o GNOME) y devuelve el valor directamente a Claude — sin que aparezca en el chat, en los logs ni en el historial de la conversación.

## Por qué

Cuando Claude Code necesita una contraseña, la respuesta naive es escribirla en el chat. Eso es un problema:

- Queda en el **historial de la conversación**
- Queda en el **log del terminal** si copias y pegas
- Puede aparecer en los **context windows comprimidos** que Claude almacena

`mcp-askpass` resuelve esto: Claude llama a `ask_password()`, aparece un popup nativo idéntico al de `sudo`, tú escribes la contraseña, y Claude la recibe en memoria. Nada toca el chat.

## Requisitos

- Python 3.10+
- `mcp` (`pip install mcp`)
- KDE: `kdialog` (incluido en `kde-cli-tools`)
- GNOME: `zenity` (`apt install zenity` / `dnf install zenity`)

## Instalación

```bash
git clone https://github.com/jaimealberto/mcp-askpass
cd mcp-askpass
pip install mcp
```

Añadir en `~/.claude.json`:

```json
{
  "mcpServers": {
    "mcp-askpass": {
      "type": "stdio",
      "command": "python3",
      "args": ["/ruta/a/mcp-askpass/mcp_askpass_server.py"]
    }
  }
}
```

Reiniciar Claude Code.

## Uso

Claude invoca `ask_password(label)` automáticamente cuando necesita una contraseña. También puedes pedírselo explícitamente:

```
Necesito la contraseña de la base de datos para continuar
```

Claude llamará a `ask_password("base de datos")` y aparecerá el popup.

## Fallback para automatización

Si necesitas pre-cargar la contraseña (flujos automatizados, sesiones remotas):

```bash
printf 'tu_contraseña' > /tmp/.mcp-askpass
chmod 600 /tmp/.mcp-askpass
```

La próxima llamada a `ask_password()` leerá el fichero y lo borrará automáticamente.

## Seguridad

- La contraseña viaja de popup → MCP → Claude, nunca por el chat
- `/tmp/.mcp-askpass` requiere permisos `600` y se borra tras la primera lectura
- Sin almacenamiento persistente de contraseñas
- Sin dependencias externas salvo `mcp`

## Compatibilidad

| Entorno | Herramienta | Detección |
|---------|-------------|-----------|
| KDE Plasma | `kdialog` | `$KDE_FULL_SESSION`, `$XDG_CURRENT_DESKTOP`, `plasmashell` |
| GNOME | `zenity` | `$GNOME_DESKTOP_SESSION_ID`, `$XDG_CURRENT_DESKTOP`, `gnome-shell` |
| Sin GUI | — | Error descriptivo + instrucciones de fallback |

## Licencia

MIT
