# Prompt API

Prompt-as-a-function: define reusable prompts with placeholders, defaults (model/temperature/budgets), and call them like functions. The Prompt API sits atop the Transport layer and uses the same normalized types, streaming events, and typed exceptions.

---

## Goals

- Make prompts reusable and ergonomic without hiding control
- Keep call sites concise but explicit where needed
- Reuse `Fiber` context (logging/metrics/traces) via binding
- Support both sync and async flows, with streaming variants
- Allow per-prompt defaults (model, temperature, budgets) that are easily overridden

---

## Key Types

Prompt
- Immutable definition of a prompt template and its input schema
- Knows how to render its template into messages and call a `Fiber` client

PromptDefaults
- Optional defaults applied when calling a `Prompt`
- Fields commonly include: `model`, `temperature`, `max_tokens`, `token_budget`, `cost_ceiling_usd`, `provider`

ChatResult
- Same normalized result as the Transport layer (`text`, `tool_calls`, `finish_reason`, `usage`, `raw`)

StreamEvent
- Same streaming event types as Transport (`chunk` | `tool_call` | `usage` | `log`)

---

## Basic Usage

Define a prompt with a string template and a list of required inputs. Provide per-prompt defaults as needed.

    from llm_fiber import Fiber, Prompt, PromptDefaults

    fiber = Fiber.from_env(default_model="gpt-4o-mini")

    summarize = Prompt(
        template="You are concise. Summarize: {text}",
        inputs=["text"],
        defaults=PromptDefaults(
            model="claude-3-haiku-20240307",  # provider inferred
            temperature=0.2,
            max_tokens=150,
        ),
    )

Call it like a function (sync):

    res = summarize.call(fiber, text="Fiber optics transmit light through strands of glass or plastic...")
    print(res.text)

Async variant:

    # res = await summarize.acall(fiber, text="...")

Streaming variant:

    for ev in summarize.stream(fiber, text="Stream a list of three items."):
        if ev.type == "chunk":
            print(ev.delta, end="")
        elif ev.type == "usage":
            print("\nusage:", ev.usage)

---

## API Surface

Construction

- Prompt(template: str, inputs: list[str], defaults: PromptDefaults | None)

Methods

- Prompt.call(fiber: Fiber, /, **kwargs) -> ChatResult
- Prompt.acall(fiber: Fiber, /, **kwargs) -> ChatResult  (async)
- Prompt.stream(fiber: Fiber, /, **kwargs) -> Iterator[StreamEvent]
- Prompt.astream(fiber: Fiber, /, **kwargs) -> AsyncIterator[StreamEvent]  (if available in your build)

Notes
- All methods accept additional keyword arguments that map to the underlying `chat()` parameters and override `defaults` when supplied (e.g., `model`, `temperature`, `max_tokens`, `timeout_s`, `provider`, `token_budget`, `cost_ceiling_usd`, `context`).
- If `model` is absent, the prompt’s defaults are used; if still absent, the `Fiber` default is used.

---

## Templating & Inputs

- Placeholders: use `{name}` style placeholders corresponding to entries in `inputs`
- Rendering: at call time, the prompt substitutes the provided `**kwargs` into the template
- Validation: missing required inputs produces a clear error; extra inputs are ignored unless mapped to call parameters (e.g., `temperature`) or deliberately referenced by the template
- Escaping: to render a literal `{` or `}`, use double braces `{{` or `}}` in your template

Examples

    # inputs = ["topic"]
    p = Prompt(
        template="Explain {topic} in two sentences.",
        inputs=["topic"],
        defaults=PromptDefaults(temperature=0.2),
    )

    # OK: topic provided
    p.call(fiber, topic="fiber optics")

    # Error: missing required input "topic"
    # p.call(fiber)

Overriding defaults (at call time)

    p = Prompt(
        template="List three properties of {material}.",
        inputs=["material"],
        defaults=PromptDefaults(model="gpt-4o-mini", temperature=0.4),
    )

    # Use the prompt’s default model, override temperature and max_tokens
    res = p.call(fiber, material="glass", temperature=0.1, max_tokens=100)

---

## How Prompt Calls Work

- Binding: each call receives a `Fiber` instance; the call inherits any bound context (via `with fiber.bind(...):`)
- Compilation: the prompt template renders to a normalized message array at call time
- Dispatch: the call delegates to the Transport layer (`chat()`/`chat_stream()`), applying defaults and per-call overrides
- Results: you get a standard `ChatResult` or a stream of `StreamEvent` items

Context binding example

    fiber = Fiber.from_env(default_model="gpt-4o-mini")

    with fiber.bind(run_id="r-42", tenant_id="acme"):
        p = Prompt(
            template="Summarize: {text}",
            inputs=["text"],
            defaults=PromptDefaults(temperature=0.2),
        )
        text = p.call(fiber, text="Latency vs TTFB...").text
        print(text)

---

## Budgets & Controls

You can set budgets and controls in `defaults` and/or per call:

- token_budget: limit prompt+completion tokens
- cost_ceiling_usd: maximum spend per call (estimate)
- timeout_s: overall or granular timeouts via `Timeouts`
- provider: per-call override (otherwise inferred from `model`)

Examples

    guarded = Prompt(
        template="Explain: {topic}",
        inputs=["topic"],
        defaults=PromptDefaults(
            model="gemini-1.5-pro",
            token_budget=300,
            cost_ceiling_usd=0.0015,
        ),
    )

    # Stricter budget at call time:
    res = guarded.call(
        fiber,
        topic="backpressure",
        token_budget=200,
        cost_ceiling_usd=0.0010,
    )

---

## Structured Outputs

When your prompt asks for JSON:

- Use `res.json()` to get a `dict` (if the response is valid JSON)
- Use `res.json(parse=MyModel)` to parse into a typed model (requires `pydantic-core` optional extra)
- If `pydantic-core` is not installed and `parse=` is provided, a `FiberParsingError` is raised with a clear message

Example

    from typing import TypedDict

    class Summary(TypedDict):
        title: str
        bullets: list[str]

    json_prompt = Prompt(
        template="Respond in JSON with keys: title, bullets. Text: {text}",
        inputs=["text"],
        defaults=PromptDefaults(temperature=0.0),
    )

    res = json_prompt.call(fiber, text="Fiber optics transmit light through glass.")
    data = res.json()  # dict (if valid JSON)

    # If pydantic-core available:
    # parsed = res.json(parse=Summary)

Tips
- For robust parsing, prefer constraining the model (e.g., system prompt) and validate with `parse=`.
- For streaming JSON, consider assembling deltas carefully or prefer non-streaming calls for strict JSON validity.

---

## Streaming Prompts

    stream_three = Prompt(
        template="Stream a numbered list of three concise items about {topic}.",
        inputs=["topic"],
        defaults=PromptDefaults(temperature=0.2, max_tokens=120),
    )

    for ev in stream_three.stream(fiber, topic="fiber optics"):
        if ev.type == "chunk":
            print(ev.delta, end="")
        elif ev.type == "usage":
            print("\nusage:", ev.usage)

Notes
- Event types and semantics are identical to Transport streaming
- TTFB and latency histograms reflect streaming behavior
- Cancellation works by breaking the loop (no final `usage` after cancellation)

---

## Composition Patterns

- Wrap common preambles: define prompts that set a style or role, and accept a single `{content}` slot
- Layer defaults: define stricter budgets or timeouts in specialized prompts
- Parameterize models: expose `model` at call time to experiment without rewriting templates

Examples

    style = Prompt(
        template="You are concise and factual. {content}",
        inputs=["content"],
        defaults=PromptDefaults(temperature=0.1),
    )

    # Compose at call site by formatting outer content with another template
    text = style.call(
        fiber,
        content=f"Summarize: {{topic}}",  # nested brace requires careful rendering if further formatting is done
        topic="fiber optics",             # if supported by your implementation
    )

Notes
- If you need multi-phase templating, prefer a two-step render: first produce the inner text, then feed it into the outer prompt’s `{content}`.
- Keep templates simple and explicit to avoid accidental placeholder collisions.

---

## Errors & Testing

Typed exceptions (same as Transport)
- Catch `FiberError` for general handling
- Use `FiberTimeout`, `FiberRateLimited`, `FiberAuthError`, `FiberAPIError`, `FiberParsingError` for specific cases

Testing prompts
- Provide a `Fiber` with a fake or test adapter to assert template rendering and call parameters
- Use small `Timeouts` and `token_budget` to surface constraint behavior
- Assert that defaults are applied, and per-call args override them

Example (pseudo-test)

    fiber = make_test_fiber()  # your fake
    p = Prompt(
        template="Hello {name}",
        inputs=["name"],
        defaults=PromptDefaults(model="gpt-4o-mini", temperature=0.0, max_tokens=16),
    )
    res = p.call(fiber, name="Alice", temperature=0.3)  # override temperature
    assert "Alice" in res.text

---

## Best Practices

- Keep templates short and explicit; avoid deeply nested templating
- Use prompt defaults to standardize behavior across a service or team
- Use `fiber.bind(...)` to attach request/run context for observability
- Add budgets (tokens and/or cost) for production calls
- Prefer `parse=` with `pydantic-core` when you rely on JSON contracts
- Avoid using raw provider payloads except when absolutely necessary

---

## Known Limitations (MVP)

- Tool/function calling normalization inside prompt-driven flows is limited; shapes may evolve post-MVP
- Template engine is intentionally simple; advanced templating features (conditions/loops) are out of scope
- Some providers may not return accurate token usage for streamed responses; final usage may be absent or partial

---

## See Also

- Transport/Core API: ./transport.md
- Streaming: ./streaming.md
- Ergonomics (DX): ./ergonomics.md
- Model Registry & Routing: ./model-registry.md
- Observability: ./observability.md
- Retries & Budgets: ./retries-and-budgets.md
- Configuration: ./configuration.md
