import re

from assistant_core.errors import InvalidRequest


def parse_credits(text: str) -> tuple[int, int]:
    """Extract (credits, retake_credits) from a tuition question."""
    retake = re.search(r"(\d+)\s*retake", text, re.IGNORECASE)
    numbers = [int(number) for number in re.findall(r"\d+", text)]
    retake_credits = int(retake.group(1)) if retake else 0
    credits = numbers.copy()
    if retake:
        credits.remove(retake_credits)
    if not credits:
        raise InvalidRequest("How many credits?")
    if len(credits) > 1:
        raise InvalidRequest("Please specify the number of enrolled credits.")
    return credits[0], retake_credits


def tuition(
    credits: int,
    retake: int,
    rate: int,
    retake_multiplier: float,
    max_credits: int,
) -> int:
    if not 1 <= credits <= max_credits:
        raise InvalidRequest(f"Credits must be between 1 and {max_credits}.")
    if retake < 0:
        raise InvalidRequest("Retake credits must not be negative.")
    if retake > max_credits:
        raise InvalidRequest(f"Retake credits must not exceed {max_credits}.")
    return int(credits * rate + retake * rate * retake_multiplier)
