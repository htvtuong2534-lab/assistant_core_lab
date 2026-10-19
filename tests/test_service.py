def test_fallback_when_provider_fails(service):
service.responder = StubLLMResponder(fail=True)
r = service.handle(Message(text="thesis registration credits"))
assert r.degraded and r.sources