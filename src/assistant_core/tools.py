
import re

from assistant_core.errors import InvalidRequest


def parse_credits(text: str) -> tuple[int, int]:
    """Extract (credits, retake_credits) from a tuition question."""
    retake = re.search(r"(\d+)\s*retake", text)
    numbers = [int(n) for n in re.findall(r"\d+", text)]

    retake_n = int(retake.group(1)) if retake else 0
    others = numbers.copy()

    if retake:
        others.remove(retake_n)

    if not others:
        raise InvalidRequest("How many credits?")

    if len(others) > 1:
        raise InvalidRequest("Please specify the number of enrolled credits.")

    return others[0], retake_n


def tuition(
    credits: int,
    retake: int,
    rate: int,
    retake_multiplier: float,
    max_credits: int,
) -> int:
    if not 1 <= credits <= max_credits:
        raise InvalidRequest(
            f"Credits must be between 1 and {max_credits}."
        )

    if retake < 0:
        raise InvalidRequest("Retake credits must not be negative.")

    return int(credits * rate + retake * rate * retake_multiplier)
