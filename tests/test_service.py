from assistant_core.config import Settings
from assistant_core.knowledge import OfficeDirectory, Rule
from assistant_core.models import Message
from assistant_core.responder import StubLLMResponder
from assistant_core.service import AssistantService


class FakeHandbook:
    def search(self, text: str):
        return Rule(
            id="R001",
            title="Attendance Rule",
            text="Students must attend classes.",
        )


def test_fallback_when_provider_fails():
    service = AssistantService(
        settings=Settings(),
        offices=OfficeDirectory({}),
        handbook=FakeHandbook(),
        responder=StubLLMResponder(fail=True),
    )

    r = service.handle(Message(text="attendance rule"))

    assert r.degraded is True
    assert r.answer == "Attendance Rule: Students must attend classes."
