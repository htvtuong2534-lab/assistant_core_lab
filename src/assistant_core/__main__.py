
import logging
import sys
import time
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.config import load_settings
from assistant_core.logging_setup import setup_logging
from assistant_core.models import Message
from assistant_core.responder import StubLLMResponder, TemplateResponder
from assistant_core.service import AssistantService

log = logging.getLogger("assistant_core")


def main() -> None:
    settings = load_settings()
    setup_logging(settings.log_level)

    offices_path = settings.data_dir / "offices.csv"
    offices = OfficeDirectory.from_csv(offices_path)
    handbook = Handbook.from_json(settings.data_dir / "handbook.json")
    # Tạm thời chưa có Handbook, nên phần hỏi quy định chưa hoạt động.
    responder = (
        StubLLMResponder()
        if settings.llm_provider != "template"
        else TemplateResponder()
    )

    service = AssistantService(
        settings=settings,
        offices=offices,
        handbook=handbook,
        responder=responder,
    )

    question = " ".join(sys.argv[1:]).strip()
    if not question:
        print('Usage: python -m assistant_core "your question"')
        return

    start = time.perf_counter()
    response = service.handle(
        Message(text=question, session_id="local")
    )
    latency_ms = round((time.perf_counter() - start) * 1000, 1)

    log.info(
        "handled",
        extra={
            "intent": response.intent.value,
            "latency_ms": latency_ms,
            "session": "local",
            "degraded": response.degraded,
        },
    )

    print(response.answer)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log.exception("assistant failed")
        raise
