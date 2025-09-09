import importlib
import os
from collections.abc import Callable
from typing import Any, ClassVar

from beartype import beartype
from MCPStack.core.tool.base import BaseTool

from mcpstack_jupyter.tools.jupyter.utils.config_loader import (
    load_env_defaults,
    load_known_tools,
)


@beartype
class Jupyter(BaseTool):
    KNOWN_TOOLS: ClassVar[list[str]] = []

    def __init__(self, include: list[str] | None = None) -> None:
        super().__init__()
        self.include = include
        self._server = None
        self._bound: list[Callable[..., Any]] = []

        env_cfg = load_env_defaults()
        self._env_defaults = env_cfg

        self.required_env_vars = {
            "DOCUMENT_TOKEN": None,
            "RUNTIME_TOKEN": None,
        }

        tools_cfg = load_known_tools()
        if not self.KNOWN_TOOLS:
            self.KNOWN_TOOLS = list(tools_cfg.get("known_tools", []))

    def _initialize(self) -> None:
        self._import_and_bind()

    def initialize(self) -> None:  # type: ignore[override]
        self._import_and_bind()

    def _teardown(self) -> None:
        self._bound.clear()
        self._server = None

    def _post_load(self) -> None:
        pass

    def actions(self) -> list[Callable[..., Any]]:
        return list(self._bound)

    def to_dict(self) -> dict[str, Any]:
        return {"include": self.include}

    @classmethod
    def from_dict(cls, params: dict[str, Any]) -> "Jupyter":
        return cls(include=params.get("include"))

    def _import_and_bind(self) -> None:
        try:
            self._server = importlib.import_module("jupyter_mcp_server.server")
        except ModuleNotFoundError as e:
            raise ImportError(
                "Could not import 'jupyter_mcp_server.server'. "
                "Install the Jupyter MCP Server package."
            ) from e

        env_cfg = self._env_defaults
        provider_default = env_cfg.get("provider", "jupyter")
        doc_url_default = env_cfg.get("document_url", "http://127.0.0.1:8888")
        doc_id_default = env_cfg.get("document_id", "notebook.ipynb")
        rt_url_default = env_cfg.get("runtime_url") or doc_url_default

        provider = os.getenv("PROVIDER", provider_default)
        doc_url = os.getenv("DOCUMENT_URL", doc_url_default)
        doc_id = os.getenv("DOCUMENT_ID", doc_id_default)
        doc_token = os.getenv("DOCUMENT_TOKEN")
        rt_url = os.getenv("RUNTIME_URL", rt_url_default)
        rt_id = os.getenv("RUNTIME_ID")
        rt_token = os.getenv("RUNTIME_TOKEN")

        self._server.PROVIDER = provider
        self._server.DOCUMENT_URL = doc_url
        self._server.DOCUMENT_ID = doc_id
        self._server.DOCUMENT_TOKEN = doc_token
        self._server.RUNTIME_URL = rt_url
        self._server.RUNTIME_ID = rt_id
        self._server.RUNTIME_TOKEN = rt_token

        wanted = self.include or self.KNOWN_TOOLS
        self._bound.clear()
        for name in wanted:
            if name not in self.KNOWN_TOOLS:
                raise AttributeError(
                    f"Requested tool '{name}' is not in KNOWN_TOOLS. "
                    f"Allowed: {', '.join(self.KNOWN_TOOLS)}"
                )
            try:
                fn = getattr(self._server, name)
            except AttributeError as e:
                raise AttributeError(
                    f"'{name}' not found in jupyter_mcp_server.server. "
                    "Install a compatible version that provides this tool."
                ) from e
            self._bound.append(fn)
