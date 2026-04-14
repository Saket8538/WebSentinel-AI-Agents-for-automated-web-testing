# WebSentinel Technical Documentation

Version: repository snapshot documented on 2026-03-24
Project root: `WebSentinel/`
Language: Python 3.11+

---

## 1. Project Overview

WebSentinel is an AI-assisted web testing platform that combines:
- Browser automation (Playwright + `browser_use` framework)
- Multi-dimensional site analysis (functional, security, accessibility, performance, SEO, visual)
- AI-generated result interpretation
- Multi-interface execution modes (CLI, Gradio, Streamlit, FastAPI, interactive terminal)
- Report generation (JSON and PDF variants)

At runtime, user input (URL + optional task) is executed in a browser context, analyzed by test modules, optionally summarized by LLM, and exported as human-readable artifacts.

---

## 2. Repository Structure

Top-level structure and intent:

- `launch.py`: Unified launcher for all interface modes.
- `core/`: Analysis/test engines and PDF generators.
- `interfaces/`: User-facing execution surfaces.
- `browser_use/`: Agentic browser automation framework used by WebSentinel.
- `utils/`: Shared support modules (LLM provider, auth, perf monitoring, PDF utility).
- `configs/config.yaml`: Runtime config defaults.
- `tests/`: Script-style validation suites and utility testers.
- `reports/`: Generated JSON/PDF reports.
- `agent_logs/`: Agent run logs.
- `agent_screenshots/`: Screenshot artifacts per run.
- `auth_data/`: Encrypted auth state and profile-related auth material.
- `visual_baselines/`: Baselines and diffs for visual regression.

---

## 3. Runtime Entry Points

## 3.1 Launcher

File: `launch.py`

`launch.py` provides an interactive menu and routes to:
1. Gradio interface (`interfaces/web_interface.py`)
2. Streamlit interface (`interfaces/streamlit_interface.py`)
3. CLI (`interfaces/cli.py`)
4. API server (`interfaces/api_server.py`)
5. Interactive terminal agent (`interfaces/interactive_agent.py`)

Notable behavior:
- Checks for `.venv` existence.
- On Windows, attempts to free occupied ports (`7860`, `8501`, `8000`) before starting interfaces.
- Uses the venv Python executable.

## 3.2 CLI

File: `interfaces/cli.py`

Main class: `WebSentinelCLI`

Supported commands:
- `test <url>` with options:
  - `--task`
  - `--no-headless`
  - `--no-tests`
  - `--output json|pdf|all`
- `batch <file>`
- `version`

Main flow (`test_url`):
- Build browser/context.
- Navigate URL with error-aware handling (DNS, timeout, connection issues).
- Optional AI agent run (`browser_use.agent.service.Agent`).
- Comprehensive test run (`ComprehensiveTester`).
- Optional AI analysis (`AIAnalyzer`).
- PDF generation (`UltraEnhancedPDFGenerator`).
- Cleanup.

## 3.3 Gradio Web Interface

File: `interfaces/web_interface.py`

Main class: `WebSentinelInterface`

Design characteristics:
- Uses standard Playwright directly (`async_playwright`) rather than `browser_use.Browser` for UI-driven visual interactions.
- Supports visible browser mode (`headless=False`) with `slow_mo` to let users observe actions.
- Can run visual task simulation, deep tests, and report generation.

Notable methods:
- `setup_browser`, `cleanup_browser`
- `perform_visual_task`
- `run_testing`
- `create_interface`
- `find_free_port`

## 3.4 Streamlit Interface

File: `interfaces/streamlit_interface.py`

This interface combines orchestration and advanced test tabs.

Highlights:
- Handles Windows event loop policy.
- Uses `nest_asyncio` to run async tasks inside Streamlit.
- Tabs include:
  - Comprehensive tests
  - Performance
  - SEO analysis
  - Visual testing
  - API testing
  - Database testing

Core runner:
- `run_test(url, task, run_comprehensive, headless)`

## 3.5 FastAPI API Server

File: `interfaces/api_server.py`

Key components:
- FastAPI app object
- `ProgressStreamer` for WebSocket job updates
- In-memory `test_jobs` registry

Models:
- `TestRequest`
- `TestResponse`
- `TestResult`

Endpoints:
- `GET /`
- `GET /health`
- `POST /api/test`
- `GET /api/test/{job_id}`
- `GET /api/test/{job_id}/pdf`
- `GET /api/test/{job_id}/json`
- `DELETE /api/test/{job_id}`
- `WS /ws/test/{job_id}`

Background job `run_test_job` flow:
- Browser setup and navigation
- Comprehensive testing
- JSON save
- AI analysis
- PDF generation
- Job status updates and WebSocket events

## 3.6 Interactive Terminal Agent

File: `interfaces/interactive_agent.py`

Main class: `InteractiveWebAgent`

Interactive flow:
- Prompt user for URL and test preferences
- Build browser/context from YAML config
- Execute AI task through `Agent`
- Execute comprehensive tests
- Display summary
- Optional PDF generation
- Cleanup

---

## 4. Core Analysis Modules

## 4.1 `core/comprehensive_tester.py`

Class: `ComprehensiveTester`

Purpose: first-line functional/site-health checks.

Implemented checks:
- `test_page_load`
- `test_links`
- `test_forms`
- `test_responsive_design`
- `test_security_headers`
- `test_accessibility`
- `test_console_errors`
- Orchestration: `run_all_tests`
- Persistence: `save_results`

Output schema pattern:
- Root metadata (`url`, `timestamp`)
- `tests` dict keyed by test category
- `overall_status` derived from test statuses

## 4.2 `core/security_scanner.py`

Class: `SecurityScanner`

Purpose: deeper security assessment beyond basic header check.

Pipeline (`run_comprehensive_scan`):
- Header checks
- Cookie security checks
- CSRF indicators
- XSS indicators
- SQLi vector indicators
- Sensitive data exposure patterns
- TLS/HTTPS checks
- Optional active probes when Playwright page is provided

Internal scoring:
- `_calculate_security_score`
- `_determine_risk_level`

## 4.3 `core/accessibility_analyzer.py`

Classes:
- `ContrastChecker`: WCAG luminance/contrast implementation with parsing for common CSS color formats.
- `AccessibilityAnalyzer`: Principle-based WCAG issue detection and recommendation generation.

Notable output fields:
- `wcag_level`
- `compliance_score`
- `issues`
- `recommendations`
- `affected_users`
- `contrast_results`

## 4.4 `core/seo_analyzer.py`

Class: `SEOAnalyzer`

Coverage includes:
- Meta tags
- Open Graph / Twitter cards
- Structured data
- Heading hierarchy
- `robots.txt`
- Sitemap

Mixes Playwright page inspection and direct HTTP requests (`requests`) for robots/sitemap checks.

## 4.5 `core/visual_regression.py`

Class: `VisualRegressionTester`

Capabilities:
- Capture baseline image (`capture_baseline`)
- Compare against baseline (`compare_with_baseline`)
- Pixel-level diff (PIL) when available
- Byte-level fallback if PIL unavailable
- Diff image generation for changed states
- Aggregated summary/report methods

## 4.6 `core/ai_analyzer.py`

Class: `AIAnalyzer`

Purpose:
- Build a business-friendly but technically grounded analysis prompt from test outputs.
- Invoke selected LLM asynchronously.

Includes:
- Sync wrapper (`analyze_results_sync`)
- Prompt construction (`_build_analysis_prompt`)
- Cache utility (`AIInsightsCache`)
- Convenience APIs (`get_ai_insights`, `get_ai_insights_sync`)

## 4.7 `core/performance_predictor.py`

Class: `PerformancePredictor`

Functions:
- Analyze current performance metrics
- Trend analysis from historical metrics
- 30-day directional predictions
- Bottleneck identification
- Recommendation generation
- Composite score generation

## 4.8 `core/lighthouse_runner.py`

Class: `LighthouseRunner`

Purpose:
- Execute Lighthouse via `npx lighthouse`.
- Parse resulting JSON for category scores and selected metrics.
- Return graceful fallback result when lighthouse is unavailable.

## 4.9 `core/site_crawler.py`

Class: `SiteCrawler`

Design:
- BFS crawling constrained by `max_pages` and `max_depth`.
- Same-domain restriction.
- Exclusion pattern support.
- Optional robots-awareness.

Outputs discovered pages with depth/status and crawl summary.

## 4.10 PDF Generators

- `core/enhanced_pdf_generator.py`: `EnhancedPDFReportGenerator`
- `core/ultra_pdf_generator.py`: `UltraEnhancedPDFGenerator`

Both use ReportLab with custom styles, sanitization helpers, and multi-section reporting.

`UltraEnhancedPDFGenerator` is the primary generator in CLI/API/interactive flows for richer reports.

---

## 5. `browser_use` Framework Integration

WebSentinel embeds a local copy of `browser_use` and imports from it directly.

## 5.1 Public Exports

File: `browser_use/__init__.py`

Primary exports used by WebSentinel:
- `Agent`
- `Browser`
- `BrowserConfig`
- `BrowserContextConfig`
- `Controller`

## 5.2 Agent Engine

File: `browser_use/agent/service.py`

Core class: `Agent`

Agent responsibilities:
- Build and manage internal state/history
- Compose prompts + action schemas
- Invoke LLM
- Execute actions via controller
- Persist logs and optional artifacts (GIF, scripts, conversation)
- Optional memory integration

Security warning behavior:
- Emits explicit warning when sensitive data is used without domain restrictions.

## 5.3 Browser and Context

Files:
- `browser_use/browser/browser.py`
- `browser_use/browser/context.py`

Responsibilities:
- Browser process lifecycle
- Local/remote browser connection modes
- Context creation with configurable permissions, viewport, cookies, allowed domains, etc.
- Page-state extraction and tab management helpers

Key config classes:
- `BrowserConfig`
- `BrowserContextConfig`

## 5.4 Action Controller

File: `browser_use/controller/service.py`

Class: `Controller`

Provides action registry and default action implementations, including:
- Navigation (`go_to_url`, search, tab actions)
- Element interactions (`click`, input, scroll, keys)
- Extraction and completion (`done`, `extract_content`, etc.)

## 5.5 Views and State Models

File: `browser_use/agent/views.py`

Defines strongly typed models for:
- Agent settings
- Action results
- Agent state/history
- Step metadata and token/time accounting

## 5.6 Telemetry and Logging

- `browser_use/telemetry/service.py`: PostHog telemetry wrapper (`ProductTelemetry`)
- `browser_use/logging_config.py`: logging level customization and UTF-8-safe setup

---

## 6. Utility Modules

## 6.1 LLM Provider Factory

File: `utils/model_provider.py`

Function: `get_llm(...)`

Provider resolution strategy:
1. Explicit provider argument
2. `LLM_PROVIDER`
3. Auto-detect by available credentials

Built-in provider adapters:
- Google (`langchain_google_genai`)
- OpenAI (`langchain_openai`)
- Anthropic (`langchain_anthropic`)
- Ollama (`langchain_ollama`)

Fallback behavior:
- Missing cloud credentials fall back to local Ollama when possible.

## 6.2 Authentication Manager

File: `utils/auth_manager.py`

Class: `SecureAuthManager`

Features:
- Credential storage in system keyring
- Encrypted auth-state persistence with Fernet
- 7-day auth-state freshness validation
- Optional auto-login workflow support

Storage location:
- `auth_data/<profile_name>/`

## 6.3 Performance Monitor

File: `utils/performance_monitor.py`

Class: `PerformanceMonitor`

Collects:
- Page timing metrics
- Core Web Vitals (via injected web-vitals script)
- Resource timing
- System utilization metrics (`psutil`)

## 6.4 Additional PDF Utility

File: `utils/pdf_report_generator.py`

Contains `PDFReportGenerator`, used notably in Streamlit flow for report output.

---

## 7. Configuration and Environment

## 7.1 `configs/config.yaml`

Main sections:
- `browser`
- `context`
- `llm`
- `tasks_file`, `batch_size`
- `agent`
- `auth_manager`

Important defaults from repository:
- Browser `headless: false`
- Context `disable_security: true`
- LLM provider `google`, model `gemini-2.5-flash`
- Agent `max_steps: 25`, `use_vision: true`, `enable_memory: true`

## 7.2 Environment Variables

Common variables consumed by code:
- `GOOGLE_API_KEY` / `GEMINI_API_KEY`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `OLLAMA_BASE_URL`
- `LLM_PROVIDER`
- `GOOGLE_MODEL`, `OPENAI_MODEL`, `ANTHROPIC_MODEL`, `OLLAMA_MODEL`
- `SKIP_LLM_API_KEY_VERIFICATION` (agent framework)
- `ANONYMIZED_TELEMETRY` (browser_use telemetry)
- `BROWSER_USE_LOGGING_LEVEL`
- `IN_DOCKER`

## 7.3 Dependency Sources

Dependencies are declared in:
- `pyproject.toml`
- `requirements.txt`

Major categories include:
- Browser automation (`playwright`)
- AI/LLM (`langchain-*` ecosystem)
- Interface frameworks (`gradio`, `streamlit`, `fastapi`, `uvicorn`)
- Reporting (`reportlab`, `Pillow`)
- Parsing and networking (`beautifulsoup4`, `lxml`, `requests`, `httpx`)
- Security/auth (`keyring`, `cryptography`)

---

## 8. Artifact and Output Model

Primary outputs:
- JSON test result files (from `ComprehensiveTester.save_results`)
- PDF reports (enhanced/ultra)
- Agent screenshots and logs
- Visual diff images/baselines

Observed directories used by code:
- `test_results/` (default save path for `ComprehensiveTester` unless overridden)
- `reports/` (commonly used by interfaces for generated reports)
- `agent_screenshots/`
- `agent_logs/`
- `visual_baselines/`

Common naming styles:
- `test_<safe_url>_<timestamp>.json`
- Interface-specific report names like `report_<timestamp>.pdf` or `report_<job_id>.pdf`

---

## 9. End-to-End Execution Sequences

## 9.1 CLI (`interfaces/cli.py`)

1. Parse command arguments.
2. Load YAML config.
3. Build browser/context.
4. Navigate target URL.
5. Optional agent task execution.
6. Run comprehensive tests.
7. Optional AI analysis.
8. Generate PDF/JSON outputs.
9. Print summary and clean up resources.

## 9.2 API Job (`interfaces/api_server.py`)

1. `POST /api/test` creates job ID and schedules background task.
2. Background worker updates `test_jobs[job_id]` state.
3. WebSocket clients consume progress events.
4. On completion, report paths and test results are available via `GET /api/test/{job_id}`.
5. Report downloads via dedicated PDF/JSON endpoints.

## 9.3 Interactive Agent (`interfaces/interactive_agent.py`)

1. Prompt for URL, task, and options.
2. Create LLM and agent context.
3. Run task-oriented AI browsing.
4. Run comprehensive tester.
5. Optional PDF generation.
6. Display human-readable summary.

---

## 10. Testing and Validation Assets

`tests/` contains script-style validation suites and helper testers:
- `test_comprehensive.py`: broad import and module behavior checks.
- `test_next_level_features.py`: focused tests for security/accessibility/visual/performance modules.
- `api_tester.py`: REST API endpoint testing utility.
- `db_tester.py`: database connection/query/integrity utility.
- `visual_tester.py`: screenshot-based visual testing helper.

These are a mix of utility scripts and tests, not a strict pure unit-test architecture.

---

## 11. Technical Risks and Notable Gaps

1. Security posture in defaults:
- `context.disable_security: true` can be risky for untrusted targets.

2. In-memory API job registry:
- `test_jobs` is process-local and non-persistent.

3. Interface inconsistency:
- Different interfaces use partially different report/output conventions.

4. Config-key mismatch risk:
- Streamlit uses `extra_chromium_args` while `BrowserConfig` uses `extra_browser_args` (because pydantic model ignores extra keys, this can silently no-op).

5. Potential runtime coupling:
- Streamlit imports `tests.*` modules as runtime feature components.

6. External dependency sensitivity:
- AI analysis depends on configured model/provider availability.
- Lighthouse module depends on Node/npm tooling and local CLI availability.

7. Mixed architecture maturity:
- Some modules are production-oriented while others are more script-like/testing utilities.

---

## 12. Extension Guide

Typical extension points:

1. Add a new analyzer module:
- Implement under `core/`.
- Integrate in `ComprehensiveTester` or interface-specific flow.
- Add output serialization and include in PDF generator sections.

2. Add a new LLM provider:
- Extend `utils/model_provider.py` with provider constructor and environment detection.

3. Add custom agent actions:
- Register in `browser_use/controller/service.py`.
- Ensure corresponding action schema in controller views/registry.

4. Extend API behavior:
- Add endpoints in `interfaces/api_server.py`.
- Add job metadata and streaming events.

5. Improve report templates:
- Expand `EnhancedPDFReportGenerator` or `UltraEnhancedPDFGenerator` sections/styles.

---

## 13. Recommended Operational Practices

1. Run with explicit domain constraints when using credentials or sensitive tasks.
2. Keep `disable_security` off unless cross-origin behavior testing requires it.
3. Standardize artifact output directories and naming across interfaces.
4. Add persistent job storage for API mode if long-running/production usage is expected.
5. Add CI to execute `tests/` and lint/type checks (`ruff`, `pyright`) on each change.
6. Document and enforce one canonical path for report generation to avoid ambiguity.

---

## 14. Quick Start Commands

Setup:

```bash
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
```

Run launcher:

```bash
python launch.py
```

Run CLI directly:

```bash
python interfaces/cli.py test https://example.com --task "Test login flow" --output all
```

Run API server:

```bash
python interfaces/api_server.py
```

Run Streamlit:

```bash
streamlit run interfaces/streamlit_interface.py
```

Run Gradio:

```bash
python interfaces/web_interface.py
```

---

## 15. File Inventory (Primary)

Core:
- `core/accessibility_analyzer.py`
- `core/ai_analyzer.py`
- `core/comprehensive_tester.py`
- `core/enhanced_pdf_generator.py`
- `core/lighthouse_runner.py`
- `core/performance_predictor.py`
- `core/security_scanner.py`
- `core/seo_analyzer.py`
- `core/site_crawler.py`
- `core/ultra_pdf_generator.py`
- `core/visual_regression.py`

Interfaces:
- `interfaces/api_server.py`
- `interfaces/cli.py`
- `interfaces/interactive_agent.py`
- `interfaces/streamlit_interface.py`
- `interfaces/web_interface.py`

Utilities:
- `utils/auth_manager.py`
- `utils/model_provider.py`
- `utils/performance_monitor.py`
- `utils/pdf_report_generator.py`

Browser framework (selected key files):
- `browser_use/__init__.py`
- `browser_use/agent/service.py`
- `browser_use/agent/views.py`
- `browser_use/browser/browser.py`
- `browser_use/browser/context.py`
- `browser_use/controller/service.py`
- `browser_use/logging_config.py`
- `browser_use/telemetry/service.py`

---

## 16. Summary

WebSentinel is a multi-interface, AI-integrated web quality platform with strong modular coverage for major QA domains. The codebase already supports advanced functionality (agentic browsing, rich report generation, security/a11y/perf/SEO checks), but would benefit from consolidation of interface behaviors, stronger production concerns for API job management, and tighter consistency around configuration and artifact conventions.
