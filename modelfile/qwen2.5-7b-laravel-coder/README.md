# qwen2.5-7b-laravel-coder

**Bob** — a Laravel & PHP coding assistant built on [Qwen2.5-Coder 7B](https://ollama.com/library/qwen2.5-coder), customized with official [Laravel documentation](https://github.com/laravel/docs) (v10–v13) and a senior-architect persona.

## Overview

| | |
|---|---|
| **Model** | `qwen2.5-7b-laravel-coder` |
| **Base** | `qwen2.5-coder` (7B) |
| **Persona** | Bob — senior PHP/Laravel specialist |
| **Laravel** | 10.x, 11.x, 12.x, 13.x (version-aware) |
| **Focus** | PHP & Laravel ecosystem only |

Bob detects your Laravel version from `composer.json`, `bootstrap/app.php`, and project patterns, then gives version-specific answers. He follows PSR-12, flags common pitfalls (N+1 queries, mass assignment, missing indexes), and declines topics outside PHP/Laravel.

## Quick start

```bash
ollama pull bhavingajjar/qwen2.5-7b-laravel-coder
ollama run bhavingajjar/qwen2.5-7b-laravel-coder
```

**Model page:** https://ollama.com/bhavingajjar/qwen2.5-7b-laravel-coder

### Example prompts

- *"How do I register middleware? Here's my composer.json and bootstrap/app.php…"*
- *"Create a Form Request and Policy for updating a Post model (Laravel 11)."*
- *"Set up Sanctum SPA authentication — project uses Laravel 10."*
- *"Who are you?"* — Bob introduces himself as your Laravel mentor.

## Capabilities

- **Version detection** from composer.json, bootstrap/app.php, config layout
- Routing, middleware, controllers, validation, Form Requests
- Eloquent ORM, relationships, scopes, migrations, query optimization
- Auth (Sanctum, Passport, Fortify), policies, gates
- Queues, Horizon, events, caching, broadcasting
- Blade, API resources, testing (PHPUnit/Pest)
- Laravel 10–13 patterns and PHP 8.x best practices

## Parameters

| Parameter | Value |
|-----------|-------|
| temperature | 0.3 |
| top_p | 0.9 |
| num_ctx | 8192 |

## License

- [Qwen2.5-Coder](https://github.com/QwenLM/Qwen2.5-Coder) — Apache 2.0
- [Laravel documentation](https://github.com/laravel/docs) — MIT
- Custom prompt & examples — Apache 2.0
