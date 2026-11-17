"""Non-production AI contract with deterministic demo implementation.

No third-party requests or voice cloning. LLM candidates never modify canonical state.
"""
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class NarrativeDraft:
    narration: str
    provider: str
    requires_human_review: bool = True


class NarrativeProvider(Protocol):
    def draft(self, approved_scene: str, memory_notes: list[str]) -> NarrativeDraft:
        ...


class DemoNarrativeProvider:
    def draft(self, approved_scene: str, memory_notes: list[str]) -> NarrativeDraft:
        notes = " ".join(memory_notes)
        return NarrativeDraft(narration=f"{approved_scene} {notes}".strip(),
                              provider="deterministic-demo", requires_human_review=False)


class DisabledRemoteProvider:
    def draft(self, approved_scene: str, memory_notes: list[str]) -> NarrativeDraft:
        raise RuntimeError("Remote AI is intentionally disabled until T006 and content-rights gate")
