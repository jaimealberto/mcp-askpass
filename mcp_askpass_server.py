#!/usr/bin/env python3
"""
mcp-askpass — Servidor MCP para pedir contraseñas de forma segura.

Muestra el diálogo de contraseña nativo del sistema (KDE/GNOME) y
devuelve el valor a Claude sin que aparezca en el chat ni en los logs.

Flujo:
  1. Comprobar /tmp/.mcp-askpass (fallback pre-cargado)
  2. Detectar entorno gráfico (KDE → kdialog, GNOME → zenity)
  3. Mostrar popup y devolver contraseña a Claude
  4. Borrar /tmp/.mcp-askpass si existía

Instalación:
  pip install mcp
  Añadir en ~/.claude.json:
    "mcp-askpass": {
      "type": "stdio",
      "command": "python3",
      "args": ["/ruta/a/mcp-askpass/mcp_askpass_server.py"]
    }
"""
import os
import subprocess
from pathlib import Path

from mcp.server.fastmcp import FastMCP

PASSFILE = Path("/tmp/.mcp-askpass")

mcp = FastMCP("mcp-askpass")


def _detect_desktop() -> str:
    """Detecta el entorno gráfico activo. Devuelve 'kde', 'gnome' o 'none'."""
    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    kde_session = os.environ.get("KDE_FULL_SESSION", "")
    gnome_session = os.environ.get("GNOME_DESKTOP_SESSION_ID", "")

    if kde_session or "kde" in desktop or "plasma" in desktop:
        return "kde"
    if gnome_session or "gnome" in desktop or "unity" in desktop:
        return "gnome"
    # Intentar detectar por proceso activo
    try:
        procs = subprocess.run(["pgrep", "-x", "plasmashell"], capture_output=True)
        if procs.returncode == 0:
            return "kde"
        procs = subprocess.run(["pgrep", "-x", "gnome-shell"], capture_output=True)
        if procs.returncode == 0:
            return "gnome"
    except FileNotFoundError:
        pass
    return "none"


def _popup_password(label: str) -> str | None:
    """Muestra popup nativo y devuelve la contraseña, o None si el usuario cancela."""
    desktop = _detect_desktop()

    if desktop == "kde":
        display = os.environ.get("DISPLAY", ":0")
        result = subprocess.run(
            ["kdialog", "--password", label, "--title", "mcp-askpass"],
            capture_output=True, text=True, timeout=120,
            env={**os.environ, "DISPLAY": display},
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None

    if desktop == "gnome":
        display = os.environ.get("DISPLAY", ":0")
        result = subprocess.run(
            ["zenity", "--password", f"--title={label}"],
            capture_output=True, text=True, timeout=120,
            env={**os.environ, "DISPLAY": display},
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None

    return None


@mcp.tool()
def ask_password(label: str = "contraseña") -> str:
    """
    Pide una contraseña de forma segura mediante popup nativo del sistema.

    La contraseña nunca aparece en el chat ni en los logs.
    Soporta KDE (kdialog) y GNOME (zenity).

    Fallback: si existe /tmp/.mcp-askpass (chmod 600), lo lee y lo borra.

    Args:
        label: Texto descriptivo que aparece en el popup (ej: 'base de datos', 'API key')

    Returns:
        La contraseña introducida por el usuario.
    """
    # 1. Comprobar fallback pre-cargado
    if PASSFILE.exists():
        try:
            password = PASSFILE.read_text().strip()
            PASSFILE.unlink()
            if password:
                return password
        except OSError:
            pass

    # 2. Popup nativo
    password = _popup_password(label)
    if password:
        return password

    # 3. Sin entorno gráfico ni fallback
    desktop = _detect_desktop()
    if desktop == "none":
        raise RuntimeError(
            "No se detectó entorno gráfico (KDE/GNOME). "
            "Usa el fallback: printf 'tu_contraseña' > /tmp/.mcp-askpass && chmod 600 /tmp/.mcp-askpass"
        )
    raise RuntimeError(
        f"El popup fue cancelado o falló (entorno: {desktop}). "
        "Comprueba que kdialog (KDE) o zenity (GNOME) están instalados."
    )


if __name__ == "__main__":
    mcp.run()
