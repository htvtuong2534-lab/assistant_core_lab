import logging

from assistant_core.errors import InvalidRequest, ProviderError
from assistant_core.models import Intent, Message, Response, Source
from assistant_core.responder import TemplateResponder
from assistant_core.router import route
from assistant_core.tools import parse_credits, tuition

log = logging.getLogger(__name__)


class AssistantService:
    def __init__(self, settings, offices, handbook, responder):
        self.settings = settings
        self.offices = offices
        self.handbook = handbook
        self.responder = responder
        self.fallback = TemplateResponder()

    def handle(self, msg: Message) -> Response:
        intent = route(msg.text, self.offices.names)

        if intent is Intent.GREETING:
            return Response(
                answer="Hello! I can help with offices, fees and rules.",
                intent=intent,
            )

        if intent is Intent.FEE:
            return self._fee(msg.text)

        if intent is Intent.OFFICE:
            office = self.offices.find(msg.text)

            if office is None:
                return Response(
                    answer="Sorry, I couldn't find that office.",
                    intent=Intent.OFFICE,
                )

            return Response(
                answer=(f"{office.name}: room {office.room}, open {office.hours}."),
                intent=intent,
            )

        return self._rule(msg.text)

    def _fee(self, text: str) -> Response:
        try:
            credits, retake_credits = parse_credits(text)

            amount = tuition(
                credits=credits,
                retake=retake_credits,
                rate=self.settings.credit_rate_vnd,
                retake_multiplier=self.settings.retake_multiplier,
                max_credits=self.settings.max_credits,
            )

            return Response(
                answer=f"Estimated tuition: {amount:,} VND.",
                intent=Intent.FEE,
            )

        except InvalidRequest as exc:
            return Response(
                answer=str(exc),
                intent=Intent.FEE,
            )

    def _rule(self, text: str) -> Response:
        rule = self.handbook.search(text)

        if rule is None:
            return Response(
                answer="Sorry, I don't know that yet.",
                intent=Intent.UNKNOWN,
            )

        sources = [Source(id=rule.id, title=rule.title)]

        try:
            answer = self.responder.explain(text, rule)

            return Response(
                answer=answer,
                intent=Intent.RULE,
                sources=sources,
            )

        except ProviderError:
            log.warning("provider failed; using template fallback")

            answer = self.fallback.explain(text, rule)

            return Response(
                answer=answer,
                intent=Intent.RULE,
                sources=sources,
                degraded=True,
            )
