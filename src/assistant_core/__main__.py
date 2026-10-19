import argparse
import logging
import sys
from time import perf_counter

from assistant_core.config import load_settings
from assistant_core.errors import AssistantError
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.logging_setup import configure_logging
from assistant_core.models import Message
from assistant_core.responder import StubLLMResponder
from assistant_core.service import AssistantService


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="python -m assistant_core",
        description="Ask a question about fees, offices, or handbook rules.",
    )
    parser.add_argument(
        "question",
        nargs="+",
        help='question to answer, e.g. "tuition for 18 credits and 2 retake"',
    )
    args = parser.parse_args()

    try:
        settings = load_settings()
        configure_logging(settings.log_level)
        offices = OfficeDirectory.from_csv(settings.data_dir / "offices.csv")
        handbook = Handbook.from_json(settings.data_dir / "handbook.json")
        service = AssistantService(
            settings=settings,
            offices=offices,
            handbook=handbook,
            responder=StubLLMResponder(),
        )
        message = Message(text=" ".join(args.question))
        start = perf_counter()
        response = service.handle(message)
        logging.getLogger("assistant_core").info(
            "handled",
            extra={
                "intent": response.intent.value,
                "latency_ms": round((perf_counter() - start) * 1000, 1),
                "session": message.session_id,
                "degraded": response.degraded,
            },
        )
        print(response.answer)
        return 0
    except AssistantError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"Error: invalid configuration: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())