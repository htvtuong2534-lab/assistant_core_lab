import csv
import json
from dataclasses import dataclass
from pathlib import Path

from assistant_core.errors import DataError


@dataclass(frozen=True)
class Office:
    name: str
    room: str
    hours: str


class OfficeDirectory:
    def __init__(self, offices: dict[str, Office]) -> None:
        self._offices = offices

    @classmethod
    def from_csv(cls, path: Path) -> "OfficeDirectory":
        try:
            with path.open(encoding="utf-8", newline="") as file:
                rows = list(csv.DictReader(file))
        except OSError as exc:
            raise DataError(f"could not read office file {path}: {exc}") from exc

        try:
            offices = {
                row["name"].lower(): Office(row["name"], row["room"], row["hours"])
                for row in rows
            }
        except (KeyError, TypeError) as exc:
            raise DataError(f"office file has invalid columns or rows: {path}") from exc
        return cls(offices)

    @property
    def names(self) -> set[str]:
        return set(self._offices)

    def find(self, text: str) -> Office | None:
        lowered = text.lower()
        return next(
            (office for name, office in self._offices.items() if name in lowered),
            None,
        )


@dataclass(frozen=True)
class Rule:
    id: str
    title: str
    text: str


class Handbook:
    def __init__(self, rules: list[Rule]) -> None:
        self._rules = rules

    @classmethod
    def from_json(cls, path: Path) -> "Handbook":
        try:
            with path.open(encoding="utf-8") as file:
                records = json.load(file)
            rules = [
                Rule(id=record["id"], title=record["title"], text=record["text"])
                for record in records
            ]
        except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
            raise DataError(f"could not load handbook {path}: {exc}") from exc
        return cls(rules)

    def search(self, text: str) -> Rule | None:
        terms = set(text.lower().split())
        if not terms:
            return None
        scored = [
            (len(terms & set(f"{rule.title} {rule.text}".lower().split())), rule)
            for rule in self._rules
        ]
        score, rule = max(scored, key=lambda result: result[0], default=(0, None))
        return rule if score else None
