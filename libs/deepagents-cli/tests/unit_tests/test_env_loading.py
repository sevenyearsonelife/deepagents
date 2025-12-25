"""Tests for .env loading behavior in CLI config."""

from __future__ import annotations

import importlib
import os
import ssl
from pathlib import Path


def test_config_loads_dotenv_from_cwd(monkeypatch, tmp_path: Path) -> None:
    """Ensure config loads `.env` relative to the current working directory.

    This matters for runners like `uvx` where the installed package lives in a temp env,
    but the user runs the CLI from their project directory.
    """
    original = os.environ.get("ANTHROPIC_API_KEY")
    try:
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".env").write_text("ANTHROPIC_API_KEY=abc\n", encoding="utf-8")

        if "ANTHROPIC_API_KEY" in os.environ:
            del os.environ["ANTHROPIC_API_KEY"]

        import deepagents_cli.config as cfg  # noqa: PLC0415

        importlib.reload(cfg)
        assert os.environ.get("ANTHROPIC_API_KEY") == "abc"
    finally:
        if original is None:
            os.environ.pop("ANTHROPIC_API_KEY", None)
        else:
            os.environ["ANTHROPIC_API_KEY"] = original


def test_anthropic_base_url_forces_tls12(monkeypatch, tmp_path: Path) -> None:
    """Ensure custom Anthropic base URL enables TLSv1.2 cap (workaround for some gateways)."""
    original_ssl_create_default_context = ssl.create_default_context
    original_env = dict(os.environ)
    try:
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".env").write_text(
            "ANTHROPIC_API_KEY=abc\nANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic\n",
            encoding="utf-8",
        )

        import deepagents_cli.config as cfg  # noqa: PLC0415

        importlib.reload(cfg)
        cfg.create_model()

        assert ssl.create_default_context is not original_ssl_create_default_context
        ctx = ssl.create_default_context()
        if hasattr(ssl, "TLSVersion"):
            assert ctx.maximum_version == ssl.TLSVersion.TLSv1_2
    finally:
        ssl.create_default_context = original_ssl_create_default_context
        os.environ.clear()
        os.environ.update(original_env)

