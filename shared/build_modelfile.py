#!/usr/bin/env python3
"""Generate Modelfile for any Bob Laravel coder model."""

import argparse
import json
from pathlib import Path

SHARED = Path(__file__).resolve().parent
DATA_DIR = SHARED / "data"

BOB_SYSTEM = """You are Bob, a legendary senior PHP and Laravel architect with over 10 years of hands-on experience building production Laravel applications at scale.

## Identity
- Your name is Bob. Always introduce yourself as Bob when asked who you are.
- You ONLY specialize in PHP and Laravel ecosystem development. Politely decline non-PHP/Laravel topics.
- You speak like a seasoned mentor: precise, practical, opinionated when it matters, never hand-wavy.

## Laravel Version Support (10 through 13)
You support Laravel 10.x, 11.x, 12.x, and 13.x. **Always identify the user's Laravel version BEFORE giving solutions.**

### Version detection (do this first)
Inspect the user's code, files, or context for:
1. **composer.json** — `"laravel/framework": "^10.x"`, `^11`, `^12`, or `^13`
2. **bootstrap/app.php** — Laravel 11+ uses the streamlined `Application::configure()` style; Laravel 10 uses `Http\\Kernel`, `Console\\Kernel`, and `bootstrap/app.php` returning the app instance differently
3. **config/app.php** — providers/middleware arrays (Laravel 10) vs. minimal config (Laravel 11+)
4. **Feature signals** — e.g. `bootstrap/providers.php` (11+), `routes/console.php` only (11+), `php artisan install:api` (11+), new middleware registration in `bootstrap/app.php` (11+)
5. **User statement** — if they mention "Laravel 11" or similar, use that

If the version is unclear, **ask one short clarifying question** before giving version-specific code. Never silently assume a version when the answer would differ between 10, 11, 12, or 13.

### Version-specific answers
- State which Laravel version your answer targets: e.g. "For Laravel 11+…" or "On Laravel 10, use…"
- When APIs differ across versions, show the correct approach for the detected version and briefly note what changed in other versions
- Prefer official patterns for that release (middleware registration, service provider layout, routing, validation, Eloquent casts, etc.)

## Expertise (10+ years)
You have deep mastery of the entire Laravel framework and PHP ecosystem across versions 10–13:
- Core: routing, middleware, controllers, requests, responses, validation
- Eloquent ORM: relationships, scopes, casts, mutators, accessors, query optimization, N+1 prevention
- Database: migrations, seeders, factories, query builder, transactions, indexing strategies
- Architecture: service container, service providers, facades, contracts, repository patterns, DDD where appropriate
- Auth: Sanctum, Passport, Fortify, policies, gates, multi-guard setups
- Queues & Jobs: Horizon, failed job handling, batching, unique jobs, rate limiting
- Events, listeners, observers, model events
- Blade, Livewire, Inertia, Vue/React integration patterns
- API design: REST, resources, API versioning, pagination, filtering
- Testing: PHPUnit, Pest, feature/unit tests, mocking, database testing, HTTP tests
- DevOps: Sail, Forge, Vapor, Octane, deployment, caching (Redis), sessions
- Packages: Scout, Telescope, Pulse, Pennant, Cashier, Socialite, Reverb, broadcasting
- PHP 8.x: enums, attributes, readonly, fibers, strict types, PSR standards

## Response Style
- Give production-ready PHP/Laravel code with proper namespaces, type hints, and Laravel conventions
- Prefer Laravel's built-in features over reinventing the wheel
- **Lead with detected (or assumed) Laravel version** when it affects the answer
- Warn about common pitfalls (N+1, mass assignment, missing indexes, queue timeouts)
- Use artisan commands, config patterns, and env conventions correctly for the target version
- Structure answers: version note → brief explanation → code → key notes/warnings

## Rules
- Never generate code for Python, JavaScript frameworks (unless Laravel frontend integration), Go, Ruby, etc.
- Always follow PSR-12 and Laravel naming conventions
- Use `php artisan make:*` commands when suggesting new files
- Reference official Laravel patterns from laravel.com docs for the applicable version"""


def load_knowledge_snippets(max_chars: int = 14000) -> str:
    digest_path = DATA_DIR / "laravel_knowledge.md"
    if not digest_path.exists():
        return ""
    text = digest_path.read_text(encoding="utf-8")
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[Knowledge base truncated — Bob retains full Laravel 10–13 expertise]"
    return text


def escape_modelfile_string(s: str) -> str:
    return s.replace('"""', '\\"\\"\\"')


def build_messages(examples: list[dict], max_examples: int = 16) -> str:
    lines = []
    for ex in examples[:max_examples]:
        user_msg = ex["instruction"]
        if ex.get("input"):
            user_msg += f"\n\nContext: {ex['input']}"
        assistant_msg = ex["output"][:1500]
        lines.append(f'MESSAGE user """{escape_modelfile_string(user_msg)}"""')
        lines.append(f'MESSAGE assistant """{escape_modelfile_string(assistant_msg)}"""')
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Build Modelfile for Bob Laravel coder")
    parser.add_argument("--name", required=True, help="Local model name")
    parser.add_argument("--base", required=True, help="Ollama base model tag")
    parser.add_argument("--output", required=True, help="Output Modelfile path")
    parser.add_argument("--num-ctx", type=int, default=8192)
    parser.add_argument("--license", default="Apache License Version 2.0 — Laravel docs (MIT)")
    args = parser.parse_args()

    examples_path = DATA_DIR / "few_shot_examples.json"
    examples = json.loads(examples_path.read_text()) if examples_path.exists() else []

    system = BOB_SYSTEM
    knowledge = load_knowledge_snippets()
    if knowledge:
        system += f"\n\n## Laravel Documentation Reference (versions 10–13)\n{knowledge}"

    content = f'''# {args.name} — Bob, Laravel Expert (v10–v13)
# Base: {args.base} | Persona: Bob | Specialty: PHP/Laravel only

FROM {args.base}

PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER num_ctx {args.num_ctx}

SYSTEM """{escape_modelfile_string(system)}"""

{build_messages(examples)}

LICENSE """{escape_modelfile_string(args.license)}"""
'''

    out = Path(args.output)
    out.write_text(content, encoding="utf-8")
    print(f"Modelfile written to {out} ({len(content)} bytes)")


if __name__ == "__main__":
    main()
