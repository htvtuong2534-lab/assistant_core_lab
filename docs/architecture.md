# Architecture

## 1. Module table

| Module | Responsibility |
|---|---|
| `__main__.py` | Application entry point; loads configuration, initializes components, handles CLI input and prints responses. |
| `config.py` | Loads configuration from environment variables and `.env`. |
| `models.py` | Defines data models such as `Message`, `Response`, `Source` and `Intent`. |
| `errors.py` | Defines application-specific exceptions. |
| `router.py` | Classifies user questions into intents. |
| `knowledge.py` | Loads and searches handbook rules and office information. |
| `tools.py` | Parses credit information and calculates tuition fees deterministically. |
| `responder.py` | Defines the `Responder` interface and template/stub implementations. |
| `service.py` | Coordinates routing, tools, knowledge retrieval and response generation. |
| `logging_setup.py` | Configures structured JSON logging. |

## 2. Service interface

`AssistantService` is the main application service. It receives settings, an office directory, a handbook and a responder through its constructor.

Its public interface is:

- `handle(msg: Message) -> Response`: processes a user message and returns a structured response.
- `_fee(text: str) -> Response`: parses credit information, calculates tuition and handles invalid requests.
- `_rule(text: str) -> Response`: searches the handbook, delegates explanations to the responder and uses a template fallback if the provider fails.

The service coordinates the components rather than implementing every operation itself. Tuition calculations are delegated to `tools.py`, while office and handbook lookups are delegated to `knowledge.py`.

## 3. Architecture decisions

### Decision 1: Tuition fees are calculated deterministically

Tuition calculations live in `tools.py`, not in an LLM. This makes the results predictable, testable and independent of an external AI provider.

### Decision 2: The LLM is behind the Responder interface

The `Responder` protocol separates response generation from the application service. The template and stub implementations allow tests and CI to run without an API key or network access. A real LLM provider can be added later without redesigning the service.

### Decision 3: Configuration comes from the environment

Application settings are centralized in `config.py`. The `.env.example` file documents the supported environment variables without exposing real secrets. This keeps configuration separate from source code and makes local development and CI easier to manage.
