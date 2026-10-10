"""Shared fixtures for the DIO Explorer test suite."""

import json
from pathlib import Path

import pytest

# ── sample data ──────────────────────────────────────────────────────────────

SAMPLE_TRACKS = [
    {
        "id": 1,
        "name": "Fundamentos de Python para Iniciantes",
        "technology": "Python",
        "level": "Iniciante",
        "modules": 8,
        "total_xp": 1200,
        "available_badges": ["Explorador Python", "Coder Novato"],
        "promotions": {"discount": "30%", "valid_until": "2025-12-31", "description": "Promo"},
        "lifetime": True,
        "lives": [{"title": "Intro ao Python", "date": "2025-02-10"}],
    },
    {
        "id": 2,
        "name": "Desenvolvimento Web Full Stack com JavaScript",
        "technology": "JavaScript",
        "level": "Intermediário",
        "modules": 15,
        "total_xp": 3500,
        "available_badges": ["Full Stack Hero", "JS Master"],
        "promotions": {"discount": "20%", "valid_until": "2025-11-30", "description": "Promo"},
        "lifetime": False,
        "lives": [],
    },
    {
        "id": 3,
        "name": "Machine Learning com Python Avançado",
        "technology": "Python",
        "level": "Avançado",
        "modules": 20,
        "total_xp": 6000,
        "available_badges": ["ML Expert"],
        "promotions": {"discount": "10%", "valid_until": "2025-10-31", "description": "Promo"},
        "lifetime": True,
        "lives": [],
    },
]


# ── path fixtures ─────────────────────────────────────────────────────────────


@pytest.fixture()
def tracks_json(tmp_path: Path) -> Path:
    """Write sample tracks to a temp JSON file and return its path."""
    p = tmp_path / "trilhas_dio.json"
    p.write_text(json.dumps({"trilhas": SAMPLE_TRACKS}), encoding="utf-8")
    return p


@pytest.fixture()
def progress_json(tmp_path: Path) -> Path:
    """Return a path for a progress file (does not exist yet)."""
    return tmp_path / "progress.json"


@pytest.fixture()
def certs_dir(tmp_path: Path) -> Path:
    """Return a path for the certificates directory (does not exist yet)."""
    return tmp_path / "certificados-emitidos"
