"""Explicit task-tool resolution for the research runtime."""

from __future__ import annotations

from collections.abc import Mapping

from deepresearch.domain.models import EvidenceRecord, ResearchCase, ResearchTask
from deepresearch.runtime.evidence import EvidenceProvider, EvidenceProviderError


class ResearchToolRegistry:
    """Resolve declared task tools without implicit provider fallback."""

    _COMPATIBILITY_ALIASES = (
        "deterministic-research",
        "external-evidence",
        "research",
        "evidence.search",
    )

    def __init__(self, tools: Mapping[str, EvidenceProvider], *, validate_providers: bool = True) -> None:
        self._tools: dict[str, EvidenceProvider] = {}
        for name, provider in tools.items():
            if not isinstance(name, str) or not name.strip():
                raise ValueError("research tool names must not be blank")
            if validate_providers and not callable(getattr(provider, "collect", None)):
                raise TypeError(f"research tool {name!r} must expose collect")
            self._tools[name] = provider

    @classmethod
    def from_provider(cls, provider: EvidenceProvider) -> ResearchToolRegistry:
        # Existing constructors may inject a configuration-only stub and never execute a run.
        return cls(
            {name: provider for name in cls._COMPATIBILITY_ALIASES},
            validate_providers=False,
        )

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._tools))

    def get(self, name: str) -> EvidenceProvider | None:
        return self._tools.get(name)

    def resolve(self, name: str) -> EvidenceProvider:
        provider = self.get(name)
        if provider is None:
            raise EvidenceProviderError(f"research tool is not registered: {name}")
        return provider

    def collect(self, task: ResearchTask, case: ResearchCase) -> list[EvidenceRecord]:
        return self.resolve(task.tool_name).collect(task, case)
