import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from assistant_core.errors import DataError


@dataclass(frozen=True)
class Office:
    name: str
    room: str
    hours: str


@dataclass(frozen=True)
class Rule:
    id: str
    title: str
    text: str


class Handbook:
    def __init__(self, rules: list[Rule]):
        self._rules = rules

    @classmethod
    def from_json(cls, path: Path) -> "Handbook":
        try:
            with path.open(encoding="utf-8") as f:
                rows = json.load(f)
        except FileNotFoundError as exc:
            raise DataError(f"handbook file not found: {path}") from exc
        except json.JSONDecodeError as exc:
            raise DataError(f"invalid handbook JSON: {path}") from exc

        return cls(
            [
                Rule(
                    id=row["id"],
                    title=row["title"],
                    text=row["text"],
                )
                for row in rows
            ]
        )

    def search(self, text: str) -> Optional[Rule]:
        query = text.lower()
        return next(
            (
                rule
                for rule in self._rules
                if any(word in (rule.title + " " + rule.text).lower() for word in query.split() if len(word) > 2)
            ),
            None,
        )


class OfficeDirectory:
    def __init__(self, offices: dict[str, Office]):
        self._offices = offices

    @classmethod
    def from_csv(cls, path: Path) -> "OfficeDirectory":
        try:
            with path.open(encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
        except FileNotFoundError as exc:
            raise DataError(f"office file not found: {path}") from exc

        return cls(
            {
                r["name"].lower(): Office(
                    r["name"],
                    r["room"],
                    r["hours"],
                )
                for r in rows
            }
        )

    @property
    def names(self) -> set[str]:
        return set(self._offices)

    def find(self, text: str) -> Optional[Office]:
        t = text.lower()
        return next(
            (o for name, o in self._offices.items() if name in t),
            None,
        )
