#!/usr/bin/env python3
"""DIO Explorer MCP Server.

Exposes the DIO Explorer track catalog, progress tracking, challenge
generation and certificate issuance as MCP tools.

Run via:
    .venv/bin/python dio_explorer/mcp/server.py
"""

import asyncio
import os
import sys

# Make the src package importable without installing the project
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from mcp.server.mcpserver import MCPServer
from model import ProgressRepository, TrackRepository
from service import CertificateService, ChallengeService, ProgressService, TrackService

# ── paths ────────────────────────────────────────────────────────────────────
_BASE = os.path.join(os.path.dirname(__file__), "..", "data")
DATA_PATH = os.path.join(_BASE, "trilhas_dio.json")
PROGRESS_PATH = os.path.join(_BASE, "progress.json")
CERTS_DIR = os.path.join(_BASE, "certificados-emitidos")

# ── services ─────────────────────────────────────────────────────────────────
_track_repo = TrackRepository(DATA_PATH)
_track_svc = TrackService(_track_repo)

_progress_repo = ProgressRepository(PROGRESS_PATH)
_progress_svc = ProgressService(_progress_repo)

_challenge_svc = ChallengeService()
_certificate_svc = CertificateService(CERTS_DIR)

# ── server ───────────────────────────────────────────────────────────────────
mcp = MCPServer(
    name="dio-explorer",
    title="DIO Explorer",
    description=(
        "Explore DIO learning tracks, track progress, generate challenges and certificates."
    ),
    version="0.1.0",
)


# ── tools ────────────────────────────────────────────────────────────────────


@mcp.tool(
    name="list_tracks",
    description=(
        "List DIO learning tracks. Optionally filter by name or technology. "
        "Returns id, name, technology, level, modules, total_xp and lifetime for each track."
    ),
)
def list_tracks(query: str = "") -> list[dict]:
    """Return all tracks, or those matching *query* (name or technology)."""
    result = _track_svc.search(query)
    return [
        {
            "id": t["id"],
            "name": t["name"],
            "technology": t["technology"],
            "level": t["level"],
            "modules": t["modules"],
            "total_xp": t["total_xp"],
            "lifetime": t["lifetime"],
        }
        for t in result.tracks
    ]


@mcp.tool(
    name="get_track",
    description="Return full details of a single track by its numeric ID.",
)
def get_track(track_id: int) -> dict:
    """Return the full track dict, or an error dict if not found."""
    all_tracks = _track_svc.all()
    for t in all_tracks:
        if t["id"] == track_id:
            return dict(t)
    return {"error": f"Track {track_id} not found."}


@mcp.tool(
    name="get_progress",
    description=(
        "Return the current learning progress: which track IDs are in-progress "
        "and which are completed."
    ),
)
def get_progress() -> dict:
    """Return {'in_progress': [...], 'completed': [...]}."""
    return {
        "in_progress": sorted(_progress_svc.all_ids()),
        "completed": sorted(_progress_svc.all_completed_ids()),
    }


@mcp.tool(
    name="toggle_progress",
    description=(
        "Start or remove a track from in-progress. "
        "Has no effect if the track is already completed. "
        "Returns a feedback message."
    ),
)
def toggle_progress(track_id: int) -> str:
    """Toggle in-progress state for *track_id*."""
    return _progress_svc.toggle(track_id)


@mcp.tool(
    name="generate_challenge",
    description=(
        "Generate a coding challenge for a track based on its level (Iniciante / "
        "Intermediário / Avançado) and technology. Returns the challenge text."
    ),
)
def generate_challenge(track_id: int) -> str:
    """Generate and return the challenge text for the given track."""
    for t in _track_svc.all():
        if t["id"] == track_id:
            return _challenge_svc.generate(t)
    return f"Track {track_id} not found."


@mcp.tool(
    name="complete_track",
    description=(
        "Mark a track as completed (irreversible). The track must be in-progress first. "
        "Returns a feedback message."
    ),
)
def complete_track(track_id: int) -> str:
    """Mark *track_id* as completed."""
    if not _progress_svc.is_in_progress(track_id):
        return "Trilha não está em andamento. Use toggle_progress primeiro."
    return _progress_svc.complete(track_id)


@mcp.tool(
    name="get_certificate",
    description=(
        "Return the certificate lines for a completed track. "
        "If no certificate has been issued yet, one is generated with the provided username. "
        "The track must be completed first."
    ),
)
def get_certificate(track_id: int, username: str = "") -> dict:
    """Load or generate the certificate for *track_id*."""
    all_tracks = _track_svc.all()
    track = next((t for t in all_tracks if t["id"] == track_id), None)
    if track is None:
        return {"error": f"Track {track_id} not found."}

    completed_ids = _progress_svc.all_completed_ids()
    if track_id not in completed_ids:
        return {"error": "Track is not completed yet. Complete it first with complete_track."}

    cached = _certificate_svc.load(track_id)
    if cached is not None:
        return {"lines": cached, "from_cache": True}

    if not username:
        return {"error": "username is required to generate a new certificate."}

    lines = _certificate_svc.generate(track, username)
    return {"lines": lines, "from_cache": False}


# ── entrypoint ───────────────────────────────────────────────────────────────


async def main() -> None:
    await mcp.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(main())
