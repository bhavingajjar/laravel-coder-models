#!/usr/bin/env python3
"""Process Laravel docs (v10–v13) into shared training data for all Bob models."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_ROOT = ROOT / "laravel-docs"
OUTPUT_DIR = Path(__file__).resolve().parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

SUPPORTED_VERSIONS = ("10.x", "11.x", "12.x", "13.x")

TOPICS = {
    "routing.md": "routing, route groups, named routes, route model binding",
    "eloquent.md": "Eloquent ORM, models, scopes, accessors, mutators",
    "eloquent-relationships.md": "Eloquent relationships: hasMany, belongsTo, morphTo, pivot",
    "migrations.md": "database migrations, schema builder, foreign keys",
    "validation.md": "form validation, rules, custom validators, Form Requests",
    "authentication.md": "authentication, guards, providers, login",
    "authorization.md": "authorization, gates, policies, can middleware",
    "middleware.md": "HTTP middleware, kernel, route middleware",
    "controllers.md": "controllers, resource controllers, invokable controllers",
    "requests.md": "HTTP requests, input, files, headers",
    "responses.md": "HTTP responses, JSON, redirects, cookies",
    "blade.md": "Blade templating, components, layouts, directives",
    "queues.md": "job queues, workers, failed jobs, Horizon",
    "events.md": "events and listeners, event discovery",
    "cache.md": "caching, Redis, cache tags, remember",
    "session.md": "session management, drivers, flash data",
    "mail.md": "Mailable classes, queues, markdown mail",
    "notifications.md": "notifications, channels, database notifications",
    "testing.md": "PHPUnit, feature tests, unit tests, assertions",
    "artisan.md": "Artisan commands, scheduling, custom commands",
    "container.md": "service container, dependency injection, bindings",
    "providers.md": "service providers, boot, register",
    "facades.md": "facades, facade pattern, real-time facades",
    "database.md": "query builder, raw queries, transactions",
    "filesystem.md": "file storage, disks, S3, local storage",
    "broadcasting.md": "WebSockets, broadcasting, Echo, Reverb",
    "sanctum.md": "API authentication with Sanctum, SPA auth, tokens",
    "passport.md": "OAuth2 with Passport, clients, scopes",
    "horizon.md": "Laravel Horizon, queue monitoring, supervisors",
    "telescope.md": "Laravel Telescope debugging, watchers",
    "octane.md": "Laravel Octane, Swoole, FrankenPHP, performance",
    "scout.md": "full-text search with Scout, Algolia, Meilisearch",
    "cashier-paddle.md": "subscriptions with Cashier, billing",
}

SKIP_FILES = {"readme.md", "license.md", "contributions.md", "documentation.md"}

VERSION_DETECTION_EXAMPLES = [
    {
        "instruction": "How do I register middleware in this Laravel app?",
        "input": 'composer.json: "laravel/framework": "^11.0"\nbootstrap/app.php uses Application::configure()',
        "output": (
            "Detected Laravel 11.x from composer.json (^11.0) and the Laravel 11+ "
            "bootstrap/app.php structure (Application::configure()).\n\n"
            "In Laravel 11+, register middleware in bootstrap/app.php:\n\n"
            "```php\n"
            "->withMiddleware(function (Middleware $middleware) {\n"
            "    $middleware->append(\\App\\Http\\Middleware\\EnsureTokenIsValid::class);\n"
            "})\n"
            "```\n\n"
            "For route-specific middleware, use the `alias` method or attach in routes. "
            "This differs from Laravel 10 which used app/Http/Kernel.php."
        ),
        "topic": "version detection middleware",
        "version": "11.x",
    },
    {
        "instruction": "How do I set up API token authentication?",
        "input": 'composer.json: "laravel/framework": "^10.48"',
        "output": (
            "Detected Laravel 10.x from composer.json (^10.48).\n\n"
            "For Laravel 10, use Laravel Sanctum:\n"
            "1. `composer require laravel/sanctum`\n"
            "2. Publish config and run migrations\n"
            "3. Add `HasApiTokens` trait to User model\n"
            "4. Protect routes with `auth:sanctum` middleware\n\n"
            "Note: Laravel 11+ uses a streamlined install flow; the bootstrap and "
            "default middleware setup differ from 10.x."
        ),
        "topic": "version detection sanctum",
        "version": "10.x",
    },
]


def strip_markdown(text: str) -> str:
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_sections(content: str) -> list[dict]:
    sections = []
    current_title = "Overview"
    current_lines: list[str] = []

    for line in content.splitlines():
        if line.startswith("#"):
            if current_lines:
                body = strip_markdown("\n".join(current_lines))
                if len(body) > 80:
                    sections.append({"title": current_title, "body": body[:2000]})
            current_title = line.lstrip("#").strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        body = strip_markdown("\n".join(current_lines))
        if len(body) > 80:
            sections.append({"title": current_title, "body": body[:2000]})

    return sections


def version_label(version: str) -> str:
    return version.replace(".x", "")


def make_qa(doc_name: str, section: dict, version: str) -> dict:
    topic = doc_name.replace(".md", "").replace("-", " ")
    ver = version_label(version)
    question = f"[Laravel {ver}] Explain {topic}: {section['title']}"
    return {
        "instruction": question,
        "input": "",
        "output": section["body"],
        "topic": topic,
        "version": version,
    }


def resolve_doc_dir(version: str) -> Path | None:
    path = DOCS_ROOT / version
    if not path.is_dir():
        return None
    if any(path.glob("*.md")):
        return path
    nested = path / version
    if nested.is_dir() and any(nested.glob("*.md")):
        return nested
    return None


def discover_version_dirs() -> list[Path]:
    if not DOCS_ROOT.exists():
        raise SystemExit(
            f"Laravel docs not found at {DOCS_ROOT}. "
            "Clone branches: git clone --depth 1 -b 13.x https://github.com/laravel/docs.git laravel-docs/13.x"
        )

    version_dirs = []
    for version in SUPPORTED_VERSIONS:
        path = resolve_doc_dir(version)
        if path is not None:
            version_dirs.append(path)

    if not version_dirs:
        # Legacy single-folder layout (pre-version split)
        if any(DOCS_ROOT.glob("*.md")):
            return [DOCS_ROOT]
        raise SystemExit(f"No Laravel doc versions found under {DOCS_ROOT}")

    return version_dirs


def resolve_version(doc_dir: Path) -> str:
    name = doc_dir.name
    if name in SUPPORTED_VERSIONS:
        return name
    return "13.x"


def build_knowledge_digest(sections_by_version: dict) -> str:
    lines = [
        "# Laravel Expert Knowledge Base (official docs, v10–v13)\n",
        "Bob supports Laravel 10.x through 13.x. Always detect the target version "
        "from composer.json, bootstrap/app.php, or code patterns before answering.\n",
    ]

    for version in SUPPORTED_VERSIONS:
        sections_by_doc = sections_by_version.get(version)
        if not sections_by_doc:
            continue

        ver = version_label(version)
        lines.append(f"\n# Laravel {ver}\n")
        for doc_name, sections in sorted(sections_by_doc.items()):
            topic = doc_name.replace(".md", "")
            lines.append(f"\n## {topic.upper()} (Laravel {ver})")
            for sec in sections[:3]:
                summary = sec["body"][:350].replace("\n", " ")
                lines.append(f"- **{sec['title']}**: {summary}")

    return "\n".join(lines)


def main():
    all_qa: list[dict] = []
    sections_by_version: dict[str, dict] = {}

    for doc_dir in discover_version_dirs():
        version = resolve_version(doc_dir)
        sections_by_doc: dict = {}

        for md_file in sorted(doc_dir.glob("*.md")):
            if md_file.name in SKIP_FILES:
                continue

            content = md_file.read_text(encoding="utf-8", errors="ignore")
            sections = extract_sections(content)
            if not sections:
                continue

            sections_by_doc[md_file.name] = sections
            per_doc_limit = 6 if version == "13.x" else 5
            for sec in sections[:per_doc_limit]:
                all_qa.append(make_qa(md_file.name, sec, version))

        if sections_by_doc:
            sections_by_version[version] = sections_by_doc

    all_qa = VERSION_DETECTION_EXAMPLES + all_qa

    jsonl_path = OUTPUT_DIR / "laravel_training.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as f:
        for item in all_qa:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    digest = build_knowledge_digest(sections_by_version)
    (OUTPUT_DIR / "laravel_knowledge.md").write_text(digest, encoding="utf-8")

    examples = list(VERSION_DETECTION_EXAMPLES)
    priority_topics = [
        "routing", "eloquent", "validation", "middleware", "queues",
        "authentication", "blade", "migrations", "testing", "container",
    ]
    seen: set[str] = set()
    for topic in priority_topics:
        for qa in all_qa:
            if topic in qa["topic"] and topic not in seen:
                examples.append(qa)
                seen.add(topic)
                break

    (OUTPUT_DIR / "few_shot_examples.json").write_text(
        json.dumps(examples[:14], indent=2, ensure_ascii=False), encoding="utf-8"
    )

    meta = {
        "supported_versions": list(sections_by_version.keys()),
        "total_docs": sum(len(d) for d in sections_by_version.values()),
        "total_qa_pairs": len(all_qa),
        "few_shot_count": len(examples[:14]),
    }
    (OUTPUT_DIR / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
