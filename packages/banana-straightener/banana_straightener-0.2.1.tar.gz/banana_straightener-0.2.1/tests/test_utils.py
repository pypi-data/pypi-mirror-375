#!/usr/bin/env python3
"""
Unit tests for utility functions and parsing that do not require API calls.
"""

from pathlib import Path
from PIL import Image
import tempfile

from banana_straightener.utils import (
    sanitize_filename,
    resize_image_if_needed,
    create_session_zip,
)
from banana_straightener.models import GeminiModel


def test_sanitize_filename():
    original = 'bad:name<>"/\\|?* and spaces.txt'
    sanitized = sanitize_filename(original)
    assert all(c not in sanitized for c in '<>:"/\\|?*')
    assert len(sanitized) <= 50
    assert sanitized.strip() == sanitized


def test_resize_image_if_needed_downscales():
    img = Image.new('RGB', (4000, 2000), 'white')
    resized = resize_image_if_needed(img, max_size=1024)
    assert max(resized.size) == 1024
    assert resized.size[0] > 0 and resized.size[1] > 0


def test_resize_image_if_needed_no_change():
    img = Image.new('RGB', (800, 600), 'white')
    resized = resize_image_if_needed(img, max_size=1024)
    assert resized.size == img.size


def test_create_session_zip_roundtrip(tmp_path: Path):
    session_dir = tmp_path / "session"
    images = [Image.new('RGB', (100, 100), 'red'), Image.new('RGB', (120, 80), 'blue')]
    evaluations = [
        {"matches_intent": False, "confidence": 0.2, "improvements": "More red"},
        {"matches_intent": True, "confidence": 0.9, "improvements": "Looks good"},
    ]
    zip_path = create_session_zip(session_dir, images, evaluations, prompt="a red square")
    assert zip_path.exists()
    assert zip_path.stat().st_size > 0


def test_parse_evaluation_static():
    response = (
        "MATCH: YES\n"
        "CONFIDENCE: 0.85\n"
        "CORRECT_ELEMENTS: banana, straight, centered\n"
        "MISSING_ELEMENTS: none\n"
        "IMPROVEMENTS: Increase contrast; add shadow.\n"
    )
    parsed = GeminiModel._parse_evaluation(response, target_prompt="a straight banana")
    assert parsed["matches_intent"] is True
    assert 0.0 <= parsed["confidence"] <= 1.0
    assert "improvements" in parsed
