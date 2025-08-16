from __future__ import annotations

from typing import Optional, List

from temporalio import workflow

from .data import CITIES

IGNORED_ENDINGS = {"ь", "ъ", "ы", "й"}


def _normalize(name: str) -> str:
    return name.strip().lower()


def _last_letter(name: str) -> Optional[str]:
    for ch in reversed(_normalize(name)):
        if ch not in IGNORED_ENDINGS:
            return ch
    return None


@workflow.defn
class CityGameWorkflow:
    """Workflow that plays a cities game with a single user."""

    def __init__(self) -> None:
        self.used: List[str] = []
        self.expected_letter: Optional[str] = None
        self._pending_city: Optional[str] = None
        self.last_response = {"status": "waiting"}
        self.finished = False

    @workflow.run
    async def run(self) -> None:
        while not self.finished:
            await workflow.wait_condition(
                lambda: self._pending_city is not None or self.finished
            )
            if self.finished:
                break
            city = self._pending_city
            self._pending_city = None
            self._handle_move(city)

    @workflow.signal
    def user_move(self, city: str) -> None:
        if not self.finished:
            self._pending_city = city

    @workflow.signal
    def give_up(self) -> None:
        self.finished = True
        self.last_response = {"status": "gave_up"}

    @workflow.query
    def get_state(self) -> dict:
        return {
            "used": list(self.used),
            "expected_letter": self.expected_letter,
            "last_response": self.last_response,
            "finished": self.finished,
        }

    def _handle_move(self, city: str) -> None:
        if city not in CITIES:
            self.last_response = {"status": "error", "reason": "unknown_city"}
            self.finished = True
            return
        if city in self.used:
            self.last_response = {"status": "error", "reason": "reused_city"}
            self.finished = True
            return
        if self.expected_letter and _normalize(city)[0] != self.expected_letter:
            self.last_response = {
                "status": "error",
                "reason": "wrong_letter",
                "expected": self.expected_letter,
            }
            self.finished = True
            return

        self.used.append(city)
        letter = _last_letter(city)
        for candidate in CITIES:
            if candidate not in self.used and _normalize(candidate)[0] == letter:
                self.used.append(candidate)
                self.expected_letter = _last_letter(candidate)
                self.last_response = {"status": "ok", "city": candidate}
                return

        self.last_response = {"status": "user_wins"}
        self.finished = True
