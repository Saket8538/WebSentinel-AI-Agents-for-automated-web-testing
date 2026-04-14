# WebSentinel-AI-Agents-for-automated-web-testing

## Comprehensive Project Documentation

---

**Project Title:** WebSentinel — AI-Powered Web Testing Platform  
**Version:** 0.1.0  
**Language:** Python 3.11+  
**License:** Apache License

---

## Table of Contents

1. [Abstract](#1-abstract)
2. [Introduction](#2-introduction)
   - 2.1 [Problem Statement](#21-problem-statement)
   - 2.2 [Objectives](#22-objectives)
   - 2.3 [Scope](#23-scope)
3. [Literature Survey](#3-literature-survey)
   - 3.1 [Web Application Testing](#31-web-application-testing)
   - 3.2 [AI Agents in Software Testing](#32-ai-agents-in-software-testing)
   - 3.3 [OWASP Top 10 Security Risks](#33-owasp-top-10-security-risks)
   - 3.4 [WCAG 2.1 Accessibility Standards](#34-wcag-21-accessibility-standards)
   - 3.5 [Core Web Vitals and Performance Metrics](#35-core-web-vitals-and-performance-metrics)
4. [System Requirements](#4-system-requirements)
   - 4.1 [Hardware Requirements](#41-hardware-requirements)
   - 4.2 [Software Requirements](#42-software-requirements)
   - 4.3 [Dependencies](#43-dependencies)
5. [System Architecture](#5-system-architecture)
   - 5.1 [High-Level Architecture](#51-high-level-architecture)
   - 5.2 [Module Architecture](#52-module-architecture)
   - 5.3 [Data Flow Diagram](#53-data-flow-diagram)
   - 5.4 [Directory Structure](#54-directory-structure)
6. [System Design](#6-system-design)
   - 6.1 [Design Principles](#61-design-principles)
   - 6.2 [LLM Provider Design](#62-llm-provider-design)
   - 6.3 [Browser Automation Architecture](#63-browser-automation-architecture)
   - 6.4 [Testing Engine Design](#64-testing-engine-design)
   - 6.5 [Report Generation Pipeline](#65-report-generation-pipeline)
7. [Implementation Details](#7-implementation-details)
   - 7.1 [Entry Point — launch.py](#71-entry-point--launchpy)
   - 7.2 [Core Modules](#72-core-modules)
   - 7.3 [Interface Modules](#73-interface-modules)
   - 7.4 [Utility Modules](#74-utility-modules)
   - 7.5 [Browser-Use Agent Framework](#75-browser-use-agent-framework)
   - 7.6 [Testing Modules](#76-testing-modules)
8. [Configuration](#8-configuration)
   - 8.1 [Environment Variables (.env)](#81-environment-variables-env)
   - 8.2 [Application Configuration (config.yaml)](#82-application-configuration-configyaml)
9. [User Interfaces](#9-user-interfaces)
   - 9.1 [Gradio Web Interface](#91-gradio-web-interface)
   - 9.2 [Streamlit Interface](#92-streamlit-interface)
   - 9.3 [CLI Interface](#93-cli-interface)
   - 9.4 [FastAPI REST API](#94-fastapi-rest-api)
   - 9.5 [Interactive Terminal Agent](#95-interactive-terminal-agent)
10. [Testing and Results](#10-testing-and-results)
    - 10.1 [Test Categories](#101-test-categories)
    - 10.2 [Security Scanning Results](#102-security-scanning-results)
    - 10.3 [Accessibility Audit Results](#103-accessibility-audit-results)
    - 10.4 [Performance Analysis Results](#104-performance-analysis-results)
    - 10.5 [AI-Generated Insights](#105-ai-generated-insights)
11. [Report Generation](#11-report-generation)
    - 11.1 [Basic PDF Reports](#111-basic-pdf-reports)
    - 11.2 [Enhanced PDF Reports](#112-enhanced-pdf-reports)
    - 11.3 [Ultra PDF Reports (25+ Pages)](#113-ultra-pdf-reports-25-pages)
12. [Installation and Setup](#12-installation-and-setup)
    - 12.1 [Prerequisites](#121-prerequisites)
    - 12.2 [Step-by-Step Installation](#122-step-by-step-installation)
    - 12.3 [Running the Application](#123-running-the-application)
13. [Future Scope](#13-future-scope)
14. [Conclusion](#14-conclusion)
15. [References](#15-references)

---

## 1. Abstract

WebSentinel is an AI-powered web testing platform that automates comprehensive quality assurance for web applications. The platform combines browser automation through Playwright with Large Language Model (LLM) intelligence to perform security scanning, accessibility auditing, performance analysis, SEO evaluation, visual regression testing, API validation, and database connectivity checks — all from a single unified tool.

The system leverages the `browser-use` agent framework to enable an AI agent that can visually navigate web pages, interact with UI elements, fill forms, click buttons, and observe the application in real time — mimicking human behavior while generating detailed, actionable test reports. WebSentinel supports multiple LLM providers (Google Gemini, OpenAI GPT, Anthropic Claude, and local Ollama models) with automatic fallback, ensuring the platform works with or without cloud API access.

Five distinct user interfaces — Gradio, Streamlit, CLI, FastAPI REST API, and an Interactive Terminal Agent — cater to different user workflows, from visual dashboards for manual testers to programmatic APIs for CI/CD pipeline integration. Generated reports include professional-grade PDF documents (up to 25+ pages) with charts, vulnerability breakdowns, WCAG compliance scores, and AI-powered remediation recommendations.

---

## 2. Introduction

### 2.1 Problem Statement

Modern web applications are complex, multi-layered systems that must meet stringent standards for security, accessibility, performance, and search engine optimization. Manual testing is time-consuming, error-prone, and difficult to scale. Existing automated tools focus on individual aspects (e.g., only security or only accessibility) and require significant configuration effort, producing reports that are fragmented and difficult to act on.

There is a need for a single, intelligent testing platform that:
- Automates multi-dimensional web testing from one entry point
- Uses AI to interpret test results and provide actionable, human-readable insights
- Supports visual browser interaction so testers can observe testing in real time
- Generates comprehensive, professional-grade reports suitable for technical and non-technical stakeholders
- Works with multiple AI providers or entirely offline with local models

### 2.2 Objectives

1. **Automated Security Scanning:** Detect OWASP Top 10 vulnerabilities including missing security headers, cookie misconfigurations, XSS vectors, SQL injection patterns, CSRF weaknesses, and TLS issues.

2. **Accessibility Auditing:** Evaluate WCAG 2.1 Level AA compliance across four principles — Perceivable, Operable, Understandable, and Robust — with specific success criterion references (e.g., 1.1.1 Non-text Content).

3. **Performance Analysis:** Measure page load times, Core Web Vitals (LCP, FID, CLS), resource loading metrics, DNS lookup times, TTFB, and provide trend predictions.

4. **SEO Evaluation:** Analyze meta tags, Open Graph data, structured data, robots.txt, sitemaps, heading hierarchy, and mobile friendliness.

5. **AI-Powered Insights:** Use LLMs to analyze raw test data and generate prioritized, actionable recommendations with severity ratings.

6. **Visual Browser Testing:** Enable a real-time visual agent that navigates websites, fills forms, clicks elements, and captures screenshots for manual observation.

7. **Multi-Format Reporting:** Generate JSON data exports and professional PDF reports (basic, enhanced with charts, and ultra-comprehensive 25+ page variants).

8. **Multi-Interface Access:** Provide Gradio, Streamlit, CLI, REST API, and interactive terminal interfaces for diverse user workflows.

### 2.3 Scope

The project covers:
- Front-end testing: page loading, link validation, form detection, responsive design
- Security testing: HTTP headers, cookies, XSS, SQL injection, CSRF, TLS
- Accessibility testing: WCAG 2.1 Level A/AA/AAA criteria
- Performance testing: load times, Core Web Vitals, resource analysis
- SEO analysis: meta tags, structured data, Open Graph, sitemap/robots
- Visual regression: screenshot capture and pixel-level comparison
- API testing: REST endpoint validation with response time measurement
- Database testing: connectivity testing for PostgreSQL, MySQL, MongoDB, SQLite, Redis
- AI analysis: LLM-powered test result interpretation
- Report generation: JSON + PDF (3 tiers)

The project does not cover:
- Mobile native application testing
- Load/stress testing at scale (e.g., thousands of concurrent users)
- Continuous monitoring/alerting services

---

## 3. Literature Survey

### 3.1 Web Application Testing

Web application testing encompasses functional, non-functional, and security verification. Key categories include:

- **Functional Testing:** Verifying that links, forms, buttons, and navigation behave correctly.
- **Cross-Browser Testing:** Ensuring consistent behavior across browsers (Chrome, Firefox, Safari, Edge).
- **Responsive Testing:** Validating layouts at different viewport sizes — mobile (375px), tablet (768px), and desktop (1920px).
- **Regression Testing:** Comparing current behavior or UI screenshots to known baselines.

Tools like Selenium, Playwright, and Cypress have automated browser interaction. WebSentinel builds on Playwright via the `patchright` library (a stealth-enhanced fork) and the `browser-use` agent framework to add AI-driven navigation.

### 3.2 AI Agents in Software Testing

AI agents in testing represent a paradigm shift from script-based automation to goal-based automation. Instead of writing explicit instructions ("click button X, fill field Y"), the tester provides a natural-language task ("navigate to the login page and test the form"), and the AI agent:

1. Observes the current browser state (DOM tree, screenshots)
2. Plans the next action using an LLM
3. Executes the action via browser automation
4. Evaluates the result and decides the next step

The `browser-use` framework used in WebSentinel implements this loop with:
- **DOM Tree Extraction:** A JavaScript injector (`buildDomTree.js`) that serializes the live DOM into a structured representation
- **Vision Support:** Screenshot analysis for visual understanding of pages
- **Memory:** Agent memory for retaining context across multi-step tasks
- **Controller Registry:** A set of registered browser actions (click, type, navigate, scroll, etc.)

### 3.3 OWASP Top 10 Security Risks

The Open Web Application Security Project (OWASP) Top 10 is the industry standard for web application security risks. WebSentinel's security scanner addresses:

| # | OWASP Category | WebSentinel Check |
|---|----------------|--------------------|
| A01 | Broken Access Control | CSRF token detection |
| A02 | Cryptographic Failures | TLS/HTTPS verification, sensitive data exposure |
| A03 | Injection | SQL injection pattern scanning, XSS vector detection |
| A04 | Insecure Design | Security header analysis |
| A05 | Security Misconfiguration | Missing CSP, X-Frame-Options, HSTS, X-Content-Type-Options |
| A06 | Vulnerable Components | Header analysis for server version disclosure |
| A07 | Authentication Failures | Cookie security (Secure, HttpOnly flags) |
| A08 | Data Integrity Failures | Content-Security-Policy analysis |
| A09 | Logging & Monitoring | Security header completeness |
| A10 | SSRF | URL pattern analysis |

### 3.4 WCAG 2.1 Accessibility Standards

The Web Content Accessibility Guidelines (WCAG) 2.1 define how to make web content accessible to people with disabilities. WebSentinel checks against three conformance levels (A, AA, AAA) across four principles:

1. **Perceivable:** Information must be presentable to users in ways they can perceive.
   - 1.1.1 Non-text Content: All images must have `alt` attributes
   - 1.3.1 Info and Relationships: Proper heading hierarchy (h1→h2→h3)
   - 1.4.1 Use of Color: Color must not be the sole means of conveying information
   - 1.4.3 Contrast Minimum: 4.5:1 ratio for normal text, 3:1 for large text

2. **Operable:** Interface components must be operable.
   - 2.1.1 Keyboard: All functionality available via keyboard
   - 2.4.2 Page Titled: Pages must have descriptive titles

3. **Understandable:** Information and UI operation must be understandable.
   - 3.2.2 On Input: Form elements must have associated labels

4. **Robust:** Content must be robust enough for diverse user agents.
   - 4.1.2 Name, Role, Value: ARIA attributes must be valid

### 3.5 Core Web Vitals and Performance Metrics

Google's Core Web Vitals measure real-world user experience:

- **Largest Contentful Paint (LCP):** Loading performance — should occur within 2.5 seconds.
- **First Input Delay (FID):** Interactivity — should be less than 100 milliseconds.
- **Cumulative Layout Shift (CLS):** Visual stability — should be less than 0.1.

WebSentinel also measures Navigation Timing API metrics: DNS lookup, TCP connection, TTFB, DOM interactive, DOM complete, and total load time.

---

## 4. System Requirements

### 4.1 Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Processor | Dual-core 2.0 GHz | Quad-core 3.0 GHz+ |
| RAM | 4 GB | 8 GB+ |
| Storage | 2 GB free | 5 GB+ free |
| Display | 1280×720 | 1920×1080+ |
| Network | Broadband internet | High-speed broadband |

### 4.2 Software Requirements

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.11 or higher | Runtime environment |
| pip | Latest | Package management |
| Git | Any | Version control |
| Chromium | Auto-installed via Playwright | Browser automation |
| Ollama (optional) | Latest | Local LLM inference |

**Supported Operating Systems:** Windows 10/11, macOS 12+, Ubuntu 20.04+

### 4.3 Dependencies

WebSentinel uses 60+ Python packages organized by function:

**Browser Automation:**
| Package | Version | Purpose |
|---------|---------|---------|
| patchright | ≥1.51.0 | Stealth-enhanced Playwright fork |
| playwright | ≥1.40.0 | Core browser automation |

**AI / LLM Integration:**
| Package | Version | Purpose |
|---------|---------|---------|
| langchain-core | 0.3.49 | LangChain core abstractions |
| langchain-google-genai | 2.1.2 | Google Gemini integration |
| langchain-openai | 0.3.11 | OpenAI GPT integration |
| langchain-anthropic | 0.3.3 | Anthropic Claude integration |
| langchain-ollama | 0.3.0 | Local Ollama model integration |
| langchain | ≥0.3.21 | LangChain framework |

**Web Interfaces:**
| Package | Version | Purpose |
|---------|---------|---------|
| streamlit | ≥1.40.1 | Streamlit dashboard UI |
| gradio | ≥4.44.0 | Gradio visual web interface |
| fastapi | ≥0.115.8 | REST API framework |
| uvicorn | ≥0.34.0 | ASGI server for FastAPI |

**Testing & Analysis:**
| Package | Version | Purpose |
|---------|---------|---------|
| beautifulsoup4 | ≥4.12.0 | HTML parsing for SEO/security analysis |
| lxml | ≥5.0.0 | Fast XML/HTML parser |
| psutil | ≥7.0.0 | System resource monitoring |

**Reporting:**
| Package | Version | Purpose |
|---------|---------|---------|
| reportlab | ≥4.4.5 | PDF generation engine |
| Pillow | ≥10.0.0 | Image processing for screenshots |

**CLI & Terminal:**
| Package | Version | Purpose |
|---------|---------|---------|
| rich | ≥14.0.0 | Rich terminal formatting |
| textual | ≥3.2.0 | Terminal UI framework |
| click | ≥8.1.8 | CLI argument parsing |

**Security & Authentication:**
| Package | Version | Purpose |
|---------|---------|---------|
| keyring | ≥25.6.0 | Secure credential storage |
| cryptography | ≥45.0.5 | Fernet encryption for auth data |

**Database Connectors:**
| Package | Version | Purpose |
|---------|---------|---------|
| psycopg2-binary | ≥2.9.0 | PostgreSQL driver |
| mysql-connector-python | ≥8.0.0 | MySQL driver |
| pymongo | ≥4.0.0 | MongoDB driver |
| redis | ≥5.0.0 | Redis driver |

---

## 5. System Architecture

### 5.1 High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         USER LAYER                                │
│  ┌──────────┐ ┌──────────┐ ┌──────┐ ┌─────────┐ ┌────────────┐  │
│  │  Gradio  │ │Streamlit │ │ CLI  │ │ FastAPI │ │ Interactive│  │
│  │  :7860   │ │  :8501   │ │      │ │  :8000  │ │   Agent    │  │
│  └────┬─────┘ └────┬─────┘ └──┬───┘ └────┬────┘ └─────┬──────┘  │
│       │             │          │           │            │          │
├───────┴─────────────┴──────────┴───────────┴────────────┴─────────┤
│                       CORE ENGINE LAYER                           │
│  ┌────────────────┐ ┌─────────────────┐ ┌──────────────────────┐ │
│  │ Comprehensive  │ │    Security     │ │   Accessibility      │ │
│  │    Tester      │ │    Scanner      │ │     Analyzer         │ │
│  └────────────────┘ └─────────────────┘ └──────────────────────┘ │
│  ┌────────────────┐ ┌─────────────────┐ ┌──────────────────────┐ │
│  │  Performance   │ │  SEO Analyzer   │ │   AI Analyzer        │ │
│  │   Predictor    │ │                 │ │  (LLM-powered)       │ │
│  └────────────────┘ └─────────────────┘ └──────────────────────┘ │
│  ┌────────────────┐                                               │
│  │ Visual         │                                               │
│  │ Regression     │                                               │
│  └────────────────┘                                               │
├───────────────────────────────────────────────────────────────────┤
│                      BROWSER LAYER                                │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │               browser-use Agent Framework                    │ │
│  │  ┌──────────┐ ┌────────────┐ ┌──────────┐ ┌─────────────┐  │ │
│  │  │  Agent   │ │  Browser   │ │Controller│ │    DOM      │  │ │
│  │  │ Service  │ │  Context   │ │ Registry │ │  Service    │  │ │
│  │  └──────────┘ └────────────┘ └──────────┘ └─────────────┘  │ │
│  └──────────────────────┬──────────────────────────────────────┘ │
│                         │                                         │
│                   ┌─────┴─────┐                                   │
│                   │ Playwright│                                   │
│                   │ (Chromium)│                                   │
│                   └───────────┘                                   │
├───────────────────────────────────────────────────────────────────┤
│                     LLM PROVIDER LAYER                            │
│  ┌────────────┐ ┌──────────┐ ┌───────────┐ ┌──────────────────┐ │
│  │Google      │ │ OpenAI   │ │ Anthropic │ │  Ollama (local)  │ │
│  │Gemini      │ │ GPT      │ │ Claude    │ │  llama3.2        │ │
│  └────────────┘ └──────────┘ └───────────┘ └──────────────────┘ │
├───────────────────────────────────────────────────────────────────┤
│                     OUTPUT LAYER                                  │
│  ┌──────────┐ ┌──────────────┐ ┌────────────────┐ ┌───────────┐ │
│  │   JSON   │ │  Basic PDF   │ │ Enhanced PDF   │ │ Ultra PDF │ │
│  │  Export  │ │  (5-8 pages) │ │ (10-15 pages)  │ │(25+ pages)│ │
│  └──────────┘ └──────────────┘ └────────────────┘ └───────────┘ │
└───────────────────────────────────────────────────────────────────┘
```

### 5.2 Module Architecture

The codebase is organized into five primary packages:

| Package | Location | Responsibility |
|---------|----------|----------------|
| `core/` | Core analysis engines | Testing, scanning, AI analysis, PDF generation |
| `interfaces/` | User-facing interfaces | Gradio, Streamlit, CLI, FastAPI, Interactive Agent |
| `utils/` | Shared utilities | Model provider, PDF reports, performance monitoring, auth |
| `browser_use/` | Browser agent framework | AI agent, browser control, DOM processing, controller |
| `tests/` | Test runners and testers | API tester, DB tester, visual tester, comprehensive tests |

### 5.3 Data Flow Diagram

```
  User Input (URL + Task)
        │
        ▼
  ┌─────────────┐
  │  Interface   │  (Gradio / Streamlit / CLI / API / Interactive)
  └──────┬──────┘
         │
         ▼
  ┌─────────────────┐     ┌──────────────────────┐
  │  LLM Provider   │────▶│  AI Agent (browser-   │
  │  (model_provider│     │  use) navigates site  │
  │   .py)          │     └──────────┬───────────┘
  └─────────────────┘                │
                                     ▼
                            ┌────────────────┐
                            │   Browser       │
                            │   (Playwright)  │
                            └───────┬────────┘
                                    │
                      ┌─────────────┼─────────────┐
                      ▼             ▼              ▼
              ┌──────────────┐ ┌─────────┐ ┌──────────────┐
              │Comprehensive │ │Security │ │Accessibility │
              │   Tester     │ │Scanner  │ │  Analyzer    │
              └──────┬───────┘ └────┬────┘ └──────┬───────┘
                     │              │              │
              ┌──────┴──────┐ ┌────┴────┐ ┌──────┴───────┐
              │ Performance │ │  SEO    │ │    Visual    │
              │ Predictor   │ │Analyzer │ │  Regression  │
              └──────┬──────┘ └────┬────┘ └──────┬───────┘
                     │              │              │
                     └──────────────┼──────────────┘
                                    ▼
                            ┌──────────────┐
                            │  AI Analyzer │
                            │ (LLM Insights│
                            │  Generation) │
                            └──────┬───────┘
                                   │
                                   ▼
                          ┌───────────────────┐
                          │  Report Generator  │
                          │  (JSON + PDF)      │
                          └───────────────────┘
```

### 5.4 Directory Structure

```
WebSentinel/
├── launch.py                    # Main entry point — menu launcher
├── pyproject.toml               # Project metadata and build configuration
├── requirements.txt             # Python package dependencies
├── setup.bat                    # Windows setup script
├── setup.sh                     # Linux/macOS setup script
├── .env                         # Environment variables (API keys, provider config)
├── configs/
│   └── config.yaml              # Browser, LLM, agent configuration
├── core/
│   ├── __init__.py
│   ├── comprehensive_tester.py  # 7-category automated test runner
│   ├── security_scanner.py      # OWASP Top 10 vulnerability scanner
│   ├── accessibility_analyzer.py# WCAG 2.1 compliance auditor
│   ├── ai_analyzer.py           # LLM-powered test result analyzer
│   ├── performance_predictor.py # Performance metrics and trend prediction
│   ├── seo_analyzer.py          # SEO analysis (meta, OG, structured data)
│   ├── visual_regression.py     # Screenshot comparison engine
│   ├── enhanced_pdf_generator.py# Enhanced PDF reports (10-15 pages)
│   └── ultra_pdf_generator.py   # Ultra PDF reports (25+ pages)
├── interfaces/
│   ├── __init__.py
│   ├── streamlit_interface.py   # Streamlit 6-tab visual dashboard
│   ├── web_interface.py         # Gradio visual browser interface
│   ├── cli.py                   # Rich CLI with batch testing
│   ├── api_server.py            # FastAPI REST API
│   └── interactive_agent.py     # Rich interactive terminal agent
├── utils/
│   ├── __init__.py
│   ├── model_provider.py        # Centralized LLM provider management
│   ├── pdf_report_generator.py  # Basic PDF generation
│   ├── performance_monitor.py   # Core Web Vitals measurement
│   └── auth_manager.py          # Secure credential/session management
├── browser_use/                 # AI Agent Framework
│   ├── agent/                   # Agent service, prompts, memory, views
│   ├── browser/                 # Browser creation and context management
│   ├── controller/              # Action controller and registry
│   ├── dom/                     # DOM tree extraction and processing
│   └── telemetry/               # Usage telemetry
├── tests/
│   ├── api_tester.py            # REST API endpoint tester
│   ├── db_tester.py             # Multi-database connectivity tester
│   ├── visual_tester.py         # Visual screenshot tester
│   ├── test_comprehensive.py    # Comprehensive test runner script
│   └── test_next_level_features.py # Advanced features test script
├── reports/                     # Generated test result JSON files
├── agent_logs/                  # AI agent execution logs
├── agent_screenshots/           # Screenshots captured during testing
├── visual_baselines/            # Baseline images for visual regression
└── auth_data/                   # Encrypted authentication state
```

---

## 6. System Design

### 6.1 Design Principles

1. **Modularity:** Each testing capability (security, accessibility, performance, SEO) is encapsulated in its own class within `core/`. Interfaces are decoupled from the testing engine — any interface can invoke any core module.

2. **Provider Agnosticism:** The `model_provider.py` module abstracts away all LLM differences. Every module calls `get_llm()` to obtain a LangChain `BaseChatModel` instance without knowing the underlying provider.

3. **Graceful Degradation:** If no cloud API key is available, the system falls back to local Ollama models. If AI analysis fails entirely, tests still run and reports are still generated — AI insights are simply omitted.

4. **Async-First:** All browser interactions and test execution use Python's `asyncio`. Interfaces that require synchronous behavior (CLI, Streamlit) use `nest_asyncio` or `asyncio.run()` wrappers.

5. **Single Entry Point:** The `launch.py` menu provides one-command access to all 8 system functions, abstracting away the complexity of individual module invocations.

### 6.2 LLM Provider Design

The centralized LLM provider (`utils/model_provider.py`) implements a resolution chain:

```
Provider Resolution:
  1. Explicit argument   →  get_llm(provider='openai')
  2. LLM_PROVIDER env    →  LLM_PROVIDER=google in .env
  3. Auto-detect          →  Check for API keys in order:
                              GOOGLE_API_KEY → OPENAI_API_KEY → ANTHROPIC_API_KEY → Ollama
  4. Fallback             →  Ollama (local, no API key needed)

Model Resolution:
  1. Explicit argument   →  get_llm(model='gpt-4o')
  2. Per-provider env    →  GOOGLE_MODEL, OPENAI_MODEL, etc.
  3. Default             →  gemini-2.5-flash / gpt-4o-mini / claude-3-5-haiku / llama3.2
```

**Supported Providers:**

| Provider | Class | Default Model | API Key Env Var |
|----------|-------|---------------|-----------------|
| Google Gemini | `ChatGoogleGenerativeAI` | gemini-2.5-flash | GOOGLE_API_KEY / GEMINI_API_KEY |
| OpenAI | `ChatOpenAI` | gpt-4o-mini | OPENAI_API_KEY |
| Anthropic | `ChatAnthropic` | claude-3-5-haiku-20241022 | ANTHROPIC_API_KEY |
| Ollama (local) | `ChatOllama` | llama3.2 | None (always available) |

The `get_provider_info()` function returns a dictionary indicating which providers are available and which is active — used by UI sidebars to display provider status.

### 6.3 Browser Automation Architecture

WebSentinel uses a layered browser automation stack:

1. **Playwright / Patchright:** Low-level browser control (navigation, clicks, screenshots). Patchright adds anti-detection measures (stealth mode, fingerprint randomization) to avoid bot detection.

2. **browser-use Framework:** Mid-level AI agent framework that wraps Playwright with:
   - **Agent Service (`agent/service.py`):** Orchestrates the think-act-observe loop. Accepts a natural-language task and an LLM, then iteratively plans and executes actions up to a configurable `max_steps` (default 25).
   - **Browser Context (`browser/context.py`):** Manages browser state, pages, cookies, and sessions.
   - **Controller Registry (`controller/registry/`):** Defines available browser actions — click, type, navigate, scroll, screenshot, extract_content, etc.
   - **DOM Service (`dom/`):** Injects `buildDomTree.js` into pages to extract a structured DOM representation, identifying interactive elements with unique indices.
   - **Memory (`agent/memory/`):** Retains conversation history and page context across agent steps.

3. **Configuration (`configs/config.yaml`):**
   ```yaml
   browser:
     headless: false           # Visual mode enabled by default
     extra_chromium_args:
       - "--disable-blink-features=AutomationControlled"
       - "--disable-features=IsolateOrigins,site-per-process"
   agent:
     max_steps: 25
     use_vision: true
     enable_memory: true
   ```

### 6.4 Testing Engine Design

Each core testing module follows a consistent pattern:

```python
class ModuleName:
    def __init__(self, url_or_context):
        self.url = url
        self.results = {}

    async def run_analysis(self) -> Dict[str, Any]:
        """Execute all checks and return structured results"""
        # Run individual checks
        # Aggregate results with status (PASS / WARNING / FAIL)
        # Calculate overall score (0-100)
        return self.results
```

**Class Hierarchy:**

| Class | Input | Output | Scoring |
|-------|-------|--------|---------|
| `ComprehensiveTester` | URL + BrowserContext | 7 test categories | Per-test PASS/WARNING/FAIL |
| `SecurityScanner` | URL (HTTP) | Vulnerabilities list | security_score (0-100) + risk_level |
| `AccessibilityAnalyzer` | URL + Page | WCAG issues list | compliance_score (0-100) |
| `PerformancePredictor` | Metrics dict | Predictions + bottlenecks | performance_score (0-100) |
| `SEOAnalyzer` | URL + Page | SEO checks | Per-check PASS/WARNING/FAIL |
| `VisualRegressionTester` | Screenshots | Diff analysis | difference_percentage |
| `AIAnalyzer` | Results dict | Natural-language insights | N/A (text output) |

### 6.5 Report Generation Pipeline

```
Test Results (dict)
       │
       ├──▶ JSON Export (direct serialization)
       │
       ├──▶ PDFReportGenerator          →  Basic PDF (5-8 pages)
       │     - Header, summary table
       │     - Per-test results
       │     - Screenshots (if available)
       │
       ├──▶ EnhancedPDFReportGenerator  →  Enhanced PDF (10-15 pages)
       │     - Custom styles and branding
       │     - Pie charts, bar charts, line charts
       │     - AI insights section
       │     - Detailed vulnerability tables
       │
       └──▶ UltraEnhancedPDFGenerator   →  Ultra PDF (25+ pages)
             - Executive summary
             - Security deep-dive with OWASP mapping
             - Accessibility audit with WCAG criteria
             - Performance analysis with Core Web Vitals
             - SEO evaluation
             - AI-generated recommendations
             - Appendices
```

All PDF generators use **ReportLab** with custom `ParagraphStyle` definitions for consistent typography and color schemes (primary: #1a1a2e, accent: #e94560, section: #0f3460).

---

## 7. Implementation Details

### 7.1 Entry Point — launch.py

The `launch.py` file serves as the singular entry point for the entire platform. It presents a numbered menu of 8 options and spawns the selected component as a subprocess using the virtual environment's Python executable.

**Key Functions:**

| Function | Option | Description |
|----------|--------|-------------|
| `launch_web_interface()` | 1 | Starts Gradio on port 7860 |
| `launch_streamlit_interface()` | 2 | Starts Streamlit on port 8501 |
| `launch_cli()` | 3 | Launches Rich CLI in interactive mode |
| `launch_api_server()` | 4 | Starts FastAPI/Uvicorn on port 8000 |
| `launch_interactive_agent()` | 5 | Launches Rich interactive terminal agent |
| `run_comprehensive_tests()` | 6 | Executes all test modules |
| `run_next_level_tests()` | 7 | Executes advanced feature tests |
| `generate_sample_report()` | 8 | Creates a sample Ultra PDF report |

Each launch function calls `get_python_executable()` which resolves to `.venv/Scripts/python.exe` (Windows) or `.venv/bin/python` (Linux/macOS).

### 7.2 Core Modules

#### 7.2.1 ComprehensiveTester (`core/comprehensive_tester.py`)

Runs 7 automated test categories against a target URL:

1. **Page Load Test (`test_page_load`):**
   - Navigates to the URL with `page.goto()`
   - Measures load time using `time.time()` before and after
   - Records HTTP status code
   - Status: PASS (<3s), WARNING (3-5s), FAIL (>5s or error)

2. **Link Validation (`test_links`):**
   - Extracts all `<a>` tags with `href` attributes
   - Categorizes into internal and external links
   - Tests each link with HEAD requests (timeout: 10s)
   - Reports broken links (non-2xx status or timeout)

3. **Form Detection (`test_forms`):**
   - Finds all `<form>` elements on the page
   - Extracts form action URLs, methods (GET/POST), and input fields
   - Checks for CSRF tokens and proper labels

4. **Responsive Design (`test_responsive_design`):**
   - Tests at three viewport sizes:
     - Mobile: 375×667
     - Tablet: 768×1024
     - Desktop: 1920×1080
   - Detects horizontal scrollbar overflow (`scrollWidth > clientWidth`)
   - FAIL if any viewport shows overflow

5. **Security Headers (`test_security_headers`):**
   - Checks for presence of key HTTP response headers
   - Required: Content-Security-Policy, X-Frame-Options, Strict-Transport-Security, X-Content-Type-Options

6. **Accessibility (`test_accessibility`):**
   - Quick checks for images without alt text
   - Verifies heading hierarchy
   - Returns issue count

7. **Console Errors (`test_console_errors`):**
   - Captures browser console output during page load
   - Counts errors vs. warnings
   - FAIL if errors > 0

#### 7.2.2 SecurityScanner (`core/security_scanner.py`)

Performs deep security analysis aligned with OWASP Top 10:

**Checks Performed:**

| Check | Description | OWASP Category |
|-------|-------------|----------------|
| Security Headers | Validates 7 headers: CSP, X-Frame-Options, HSTS, X-Content-Type-Options, X-XSS-Protection, Referrer-Policy, Permissions-Policy | A05 |
| Cookie Security | Checks Secure and HttpOnly flags on all cookies | A07 |
| CSRF Protection | Detects CSRF tokens in forms and meta tags | A01 |
| XSS Vulnerabilities | Scans for reflected XSS patterns in page source | A03 |
| SQL Injection | Detects SQL error messages and injection vectors | A03 |
| Sensitive Data Exposure | Checks for exposed credentials, API keys, or PII in source | A02 |
| TLS/HTTPS | Verifies HTTPS usage and certificate validity | A02 |

**Output Format:**
```python
{
    "security_score": 65,       # 0-100
    "risk_level": "MEDIUM",     # LOW / MEDIUM / HIGH / CRITICAL
    "vulnerabilities": [
        {
            "owasp_category": "A05",
            "severity": "MEDIUM",
            "cvss_score": 5.3,
            "finding": "Missing Content-Security-Policy header",
            "impact": "Allows XSS attacks and content injection",
            "fix": "Add Content-Security-Policy header with restrictive policy"
        }
    ]
}
```

Each header check includes severity (LOW/MEDIUM/HIGH), description, impact explanation, and a specific fix recommendation.

#### 7.2.3 AccessibilityAnalyzer (`core/accessibility_analyzer.py`)

Evaluates WCAG 2.1 compliance across four principles:

**Perceivable Checks:**
- **Alt Text (SC 1.1.1):** Finds all `<img>` tags without `alt` attributes. Checks both empty and missing `alt`. Reports affected groups: visual disabilities, screen reader users.
- **Heading Structure (SC 1.3.1):** Validates heading levels don't skip (e.g., h1→h3 without h2). Reports all headings and their sequence.
- **Color Usage (SC 1.4.1):** Warns if color is the sole means of conveying information.
- **Contrast (SC 1.4.3):** Checks for text with insufficient contrast ratios.
- **Page Title (SC 2.4.2):** Verifies `<title>` tag exists and has meaningful content.

**Operable Checks:**
- **Keyboard Access (SC 2.1.1):** Checks interactive elements for `tabindex`, `role`, and keyboard event handlers.
- **Form Labels (SC 3.2.2):** Validates all `<input>`, `<select>`, and `<textarea>` elements have associated `<label>` tags or `aria-label` attributes.

**Output Format:**
```python
{
    "compliance_score": 72,     # 0-100
    "level": "AA",              # Target level
    "issues": [
        {
            "wcag_sc": "1.1.1",
            "level": "A",
            "issue": "Image missing alt text",
            "severity": "HIGH",
            "affected_groups": ["blind", "screen_reader_users"],
            "fix": "Add alt attribute",
            "code_example": '<img src="photo.jpg" alt="Description of the image">'
        }
    ]
}
```

#### 7.2.4 AIAnalyzer (`core/ai_analyzer.py`)

Uses the centralized LLM provider to generate intelligent insights from test results:

- **Input:** Dictionary of test results from `ComprehensiveTester`
- **Process:** Constructs a detailed prompt including all metrics (load time, status code, security headers, accessibility issues, broken links, form count, responsive status, console errors) and asks the LLM to provide:
  1. Executive summary
  2. Critical issues requiring immediate attention
  3. Performance optimization suggestions
  4. Security hardening recommendations
  5. Accessibility improvements
  6. Overall quality grade

- **Output:** Natural-language text (typically 500-1500 words) with structured recommendations
- **Fallback:** If no LLM is available, returns `None` — reports are still generated without AI insights

#### 7.2.5 PerformancePredictor (`core/performance_predictor.py`)

Analyzes current performance metrics and predicts future trends:

- **Current Analysis:** Evaluates load time, response time, resource count, and page size against benchmarks:
  - Load time: <3s excellent, 3-5s good, >5s poor
  - Response time: <200ms excellent, 200-500ms good, >500ms poor
  - Resource count: <50 excellent, 50-100 good, >100 poor
  - Page size: <1MB excellent, 1-3MB good, >3MB poor

- **Trend Analysis:** If historical data (2+ data points) is provided, calculates improvement/degradation trends.

- **Bottleneck Identification:** Identifies the primary performance bottleneck (slow TTFB, large page size, too many resources, etc.).

- **Optimization Recommendations:** Generates specific recommendations based on identified bottlenecks (e.g., "Enable compression to reduce page size", "Implement browser caching for static assets").

- **Performance Score:** Weighted 0-100 score combining all metrics.

#### 7.2.6 SEOAnalyzer (`core/seo_analyzer.py`)

Comprehensive SEO evaluation through JavaScript evaluation on the live page:

| Check | What It Evaluates |
|-------|-------------------|
| Meta Tags | Title (30-60 chars), description (120-160 chars), viewport, canonical URL, robots meta |
| Open Graph | og:title, og:description, og:image, og:url for social media sharing |
| Structured Data | JSON-LD, Microdata, RDFa markup presence |
| Heading Hierarchy | Proper h1-h6 nesting, single h1, keyword presence |
| Robots.txt | File accessibility and content analysis |
| Sitemap | XML sitemap detection and URL count |
| Mobile Friendliness | Viewport meta tag, responsive design indicators |

Uses `page.evaluate()` to extract DOM data and `requests` for HTTP-level checks (robots.txt, sitemap).

#### 7.2.7 VisualRegressionTester (`core/visual_regression.py`)

Detects visual changes between test runs through screenshot comparison:

- **Baseline Capture (`capture_baseline`):** Saves a screenshot as the known-good reference image.
- **Comparison (`compare_with_baseline`):** Compares current screenshot against baseline:
  - Byte-level comparison for exact matches
  - Pixel-level difference calculation using PIL (if available)
  - Configurable threshold (default: 5% difference tolerance)
- **Diff Report:** Generates a diff image highlighting changed regions with bounding boxes.

### 7.3 Interface Modules

#### 7.3.1 Streamlit Interface (`interfaces/streamlit_interface.py`)

A 6-tab visual dashboard built with Streamlit:

**Tabs:**
1. **Comprehensive Tests:** Enter URL → runs all 7 ComprehensiveTester categories → displays results with color-coded status badges
2. **Performance:** Performance metrics, Core Web Vitals analysis
3. **SEO:** SEO audit results with meta tag details
4. **Visual Testing:** Screenshot capture and visual regression
5. **API Testing:** REST endpoint testing interface
6. **Database Testing:** Database connectivity testing with configurable connection parameters

**Key Technical Details:**
- Uses `WindowsProactorEventLoopPolicy` on Windows to avoid event loop conflicts
- Patches event loop with `nest_asyncio` for Streamlit compatibility
- Sidebar displays: active LLM provider, available providers, configuration status
- AI agent integration: creates browser-use `Agent` with LLM for visual task execution
- Generates PDF reports inline with download button

**Configuration Loading:**
```python
def load_config():
    config_path = Path("configs/config.yaml")
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)
```

#### 7.3.2 Gradio Web Interface (`interfaces/web_interface.py`)

A visual browser interface where users watch the AI agent interact with websites in real time:

**Class: `WebSentinelInterface`**

- **`setup_browser(headless)`:** Creates a Playwright browser with anti-detection settings and `slow_mo=100` for visual observation
- **`run_testing(url, task_type, headless)`:** Async generator that yields progress updates as the agent works:
  1. Validates URL
  2. Sets up browser (visual or headless mode)
  3. Runs AI agent task based on `task_type`:
     - Navigate & Test: Visit URL and test all elements
     - Fill Forms: Find and fill all forms
     - Click & Navigate: Discover and test navigation paths
     - Search: Test search functionality
     - Scroll & Explore: Scroll through and catalog page content
  4. Runs SecurityScanner, AccessibilityAnalyzer, PerformancePredictor in parallel
  5. Generates AIAnalyzer insights
  6. Produces Enhanced and Ultra PDF reports
  7. Yields final results

- **Port:** 7860

#### 7.3.3 CLI Interface (`interfaces/cli.py`)

Rich terminal CLI for power users:

**Class: `WebSentinelCLI`**

- **Usage:**
  ```bash
  python interfaces/cli.py test https://example.com
  python interfaces/cli.py test https://example.com --headless --format pdf
  python interfaces/cli.py batch urls.txt --output results/
  ```

- **Features:**
  - `test` subcommand: Test a single URL
  - `batch` subcommand: Test multiple URLs from a file
  - `--headless` flag: Run without visible browser
  - `--format json|pdf`: Output format selection
  - Rich console output with progress bars, tables, and status indicators
  - Integrated AI insights generation

#### 7.3.4 FastAPI REST API (`interfaces/api_server.py`)

RESTful API for programmatic access and CI/CD integration:

**Endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/test` | Submit a new test job (returns job_id) |
| GET | `/api/test/{job_id}` | Get test status and results |
| GET | `/api/test/{job_id}/pdf` | Download PDF report |
| GET | `/api/test/{job_id}/json` | Download JSON results |
| DELETE | `/api/test/{job_id}` | Delete test results |
| GET | `/health` | Health check endpoint |

**Request Schema (Pydantic):**
```python
class TestRequest(BaseModel):
    url: str
    task: str = "comprehensive"
    headless: bool = True
    generate_pdf: bool = True
```

**Response Schema:**
```python
class TestResponse(BaseModel):
    job_id: str
    status: str     # "pending" | "running" | "completed" | "failed"
    results: Optional[dict]
    pdf_path: Optional[str]
```

- **Background Execution:** Tests run as FastAPI `BackgroundTasks` so the API returns immediately with a `job_id`
- **Port:** 8000
- **Interactive Docs:** Swagger UI at `http://localhost:8000/docs`

#### 7.3.5 Interactive Terminal Agent (`interfaces/interactive_agent.py`)

A guided, conversational testing experience in the terminal:

**Class: `InteractiveWebAgent`**

**User Flow:**
1. **Banner:** Displays ASCII art banner with system info
2. **URL Input:** Prompts for target URL with validation
3. **Task Description:** User describes what to test in natural language
4. **Test Options:** Select which test categories to run
5. **Browser Setup:** Configures browser (visual or headless)
6. **AI Agent Execution:** Runs browser-use agent with the user's natural-language task
7. **Comprehensive Tests:** Runs ComprehensiveTester categories
8. **Results Display:** Rich formatted summary in terminal
9. **PDF Report:** Generates and saves PDF report

Uses Rich console for colored output, progress spinners, and formatted tables.

### 7.4 Utility Modules

#### 7.4.1 Model Provider (`utils/model_provider.py`)

See [Section 6.2](#62-llm-provider-design) for detailed design.

Core functions:
- `get_llm(provider, model, temperature, max_tokens)` → Returns `BaseChatModel` instance
- `get_provider_info()` → Returns dict with `active_provider`, `google_available`, `openai_available`, `anthropic_available`, `ollama_available` flags

#### 7.4.2 PDF Report Generator (`utils/pdf_report_generator.py`)

Basic PDF generation using ReportLab:

**Class: `PDFReportGenerator`**

- Input: Test results dict + optional screenshots directory
- Output: 5-8 page PDF with:
  - Custom title page
  - Summary table with color-coded status
  - Detailed per-test results
  - Screenshots (if available)
- Custom styles: CustomTitle (24pt), SectionHeader (16pt), SubsectionHeader (14pt), StatusPASS/FAIL/WARNING

#### 7.4.3 Performance Monitor (`utils/performance_monitor.py`)

Collects real browser performance metrics via JavaScript evaluation:

**Class: `PerformanceMonitor`**

**Measurements:**
1. **Page Load Timing:**
   - DNS lookup, TCP connect, request time, response time
   - DOM loading, DOM interactive, DOM complete, load complete
   - TTFB, redirect time, cache time

2. **Core Web Vitals:**
   - Injects `web-vitals` library from CDN
   - Measures LCP, FID, CLS in real browser context

3. **Resource Timing:**
   - Analyzes all resource entries (scripts, stylesheets, images, fonts)
   - Reports per-resource load times and sizes

4. **System Metrics:**
   - CPU usage via `psutil.cpu_percent()`
   - Memory usage via `psutil.virtual_memory()`

#### 7.4.4 Auth Manager (`utils/auth_manager.py`)

Secure credential and session management:

**Class: `SecureAuthManager`**

- **Credential Storage:** Uses `keyring` for OS-level secure credential storage
- **Session Persistence:** Saves browser cookies to encrypted files using `Fernet` symmetric encryption
- **Session Replay:** Loads saved cookies to resume authenticated sessions without re-login
- **Session Expiry:** Auto-expires saved sessions after 7 days
- **Profile Support:** Multiple test profiles under `auth_data/<profile_name>/`

### 7.5 Browser-Use Agent Framework

The `browser_use/` package is the AI agent framework that powers visual browser interaction:

#### Agent Service (`agent/service.py`)

The main orchestrator. Accepts:
- `task` (str): Natural language description of what to do
- `llm` (BaseChatModel): LangChain chat model instance
- `browser` (Browser): Playwright browser wrapper
- `max_steps` (int): Maximum actions before stopping (default 25)

**Think-Act-Observe Loop:**
1. **Think:** Send current browser state (DOM tree + optional screenshot) to the LLM
2. **Act:** LLM returns a structured action (click element #5, type "hello" in element #12, navigate to URL, etc.)
3. **Observe:** Execute the action via Playwright, capture the new browser state
4. **Repeat:** Until the task is complete or `max_steps` is reached

#### DOM Service (`dom/`)

- **`buildDomTree.js`:** JavaScript that traverses the live DOM and creates a serialized tree with:
  - Element type, attributes, text content
  - Unique indices for interactive elements (links, buttons, inputs)
  - Visibility and position information
- **Clickable Element Processor:** Identifies elements that can be clicked, typed into, or otherwise interacted with
- **History Tree Processor:** Tracks DOM changes across agent steps for context

#### Controller Registry (`controller/registry/`)

Defines available browser actions the agent can take:
- `click(element_id)` — Click an element by its index
- `type(element_id, text)` — Type text into an input field
- `navigate(url)` — Go to a URL
- `scroll(direction, amount)` — Scroll the page
- `screenshot()` — Capture a screenshot
- `extract_content()` — Extract page text content
- `go_back()` / `go_forward()` — Browser navigation
- `wait(seconds)` — Wait for dynamic content

### 7.6 Testing Modules

#### 7.6.1 API Tester (`tests/api_tester.py`)

**Class: `APITester`**

Tests REST API endpoints with comprehensive validation:

- **Authentication:** Supports Bearer token, Basic auth, API key, and custom header authentication
- **Endpoint Testing (`test_endpoint`):**
  - Sends HTTP requests (GET, POST, PUT, DELETE, PATCH)
  - Validates response status codes
  - Measures response time in milliseconds
  - Validates JSON response parsing
  - Optional JSON schema validation
- **Batch Testing:** Test multiple endpoints in sequence
- **Output:** Per-endpoint results with status, response time, and validation messages

#### 7.6.2 Database Tester (`tests/db_tester.py`)

**Class: `DatabaseTester`**

Tests database connectivity for 5 database systems:

| Database | Driver | Default Port |
|----------|--------|-------------|
| PostgreSQL | psycopg2 | 5432 |
| MySQL | mysql-connector-python | 3306 |
| MongoDB | pymongo | 27017 |
| SQLite | sqlite3 | N/A (file) |
| Redis | redis | 6379 |

**Test Sequence:**
1. **Connection Test:** Attempts to connect and measures connection time
2. **Query Test:** Executes a simple query (e.g., `SELECT 1`) and measures latency
3. **Schema Test:** Lists tables/collections in the database
4. **Performance Test:** Runs repeated simple queries to measure average latency

#### 7.6.3 Visual Tester (`tests/visual_tester.py`)

Screenshot-based visual testing:
- Captures full-page screenshots at configurable viewports
- Saves screenshots with timestamps for history
- Integrates with `VisualRegressionTester` for baseline comparison

---

## 8. Configuration

### 8.1 Environment Variables (.env)

The `.env` file in the project root controls API keys and provider selection:

```bash
# ─── LLM Provider Selection ───
# Options: auto | google | openai | anthropic | ollama
# "auto" detects based on available API keys
LLM_PROVIDER=auto

# ─── Google Gemini ───
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_MODEL=gemini-2.5-flash

# ─── OpenAI ───
# OPENAI_API_KEY=your_openai_api_key_here
# OPENAI_MODEL=gpt-4o-mini

# ─── Anthropic ───
# ANTHROPIC_API_KEY=your_anthropic_api_key_here
# ANTHROPIC_MODEL=claude-3-5-haiku-20241022

# ─── Ollama (Local) ───
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# ─── Encoding ───
PYTHONUTF8=1
```

**Priority:** Uncomment and set the API key for your preferred provider. With `LLM_PROVIDER=auto`, the system checks for API keys in order: Google → OpenAI → Anthropic → Ollama.

### 8.2 Application Configuration (config.yaml)

Located at `configs/config.yaml`:

```yaml
browser:
  headless: false
  disable_security: true
  extra_chromium_args:
    - "--disable-blink-features=AutomationControlled"
    - "--disable-features=IsolateOrigins,site-per-process"

llm:
  provider: "auto"
  model: ""           # Empty = use provider default
  temperature: 0.7
  max_tokens: 1000

agent:
  max_steps: 25
  use_vision: true
  enable_memory: true
  max_failures: 5
  retry_delay: 10

auth:
  profile: "test_profile"
```

| Section | Key | Default | Description |
|---------|-----|---------|-------------|
| browser.headless | false | false | Run browser in headless mode |
| browser.extra_chromium_args | list | Anti-detection args | Chromium startup flags |
| llm.provider | "auto" | "auto" | LLM provider selection |
| llm.temperature | 0.7 | 0.7 | LLM response creativity |
| llm.max_tokens | 1000 | 1000 | Maximum response length |
| agent.max_steps | 25 | 25 | Maximum AI agent actions per task |
| agent.use_vision | true | true | Enable screenshot analysis |
| agent.enable_memory | true | true | Enable agent memory |

---

## 9. User Interfaces

### 9.1 Gradio Web Interface

**Access:** `http://localhost:7860`  
**Launch:** Option 1 in `launch.py`

The Gradio interface provides a visual browser experience where users can watch the AI agent navigate and test websites in real time (with `slow_mo=100` for observable browser actions).

**Interface Layout:**
- **Input Panel:** URL field, task type dropdown (Navigate & Test, Fill Forms, Click & Navigate, Search, Scroll & Explore), visual/headless toggle
- **Output Panel:** Real-time progress log, test results display, PDF download button
- **Task Types:** Each task type maps to a specific agent instruction that guides the AI on how to interact with the page

### 9.2 Streamlit Interface

**Access:** `http://localhost:8501`  
**Launch:** Option 2 in `launch.py`

A feature-rich dashboard with 6 testing tabs:

**Sidebar:**
- Configuration display (active LLM provider, available providers)
- Settings (headless mode toggle, URL input)

**Tabs:**
1. **Comprehensive Tests** — Full 7-category test suite with expandable result sections
2. **Performance** — Core Web Vitals, page load metrics, resource analysis
3. **SEO** — Meta tags, Open Graph, structured data, sitemap check
4. **Visual Testing** — Screenshot capture, baseline management, diff view
5. **API Testing** — Endpoint URL input, method selection, response validation
6. **Database Testing** — Connection string input, database type selection, connectivity test

### 9.3 CLI Interface

**Launch:** Option 3 in `launch.py` or directly:
```bash
python interfaces/cli.py test https://example.com
python interfaces/cli.py test https://example.com --headless --format pdf
python interfaces/cli.py batch urls.txt --output results/
```

**Features:**
- Rich terminal output with colored status indicators
- Progress bars for multi-step tests
- Formatted result tables
- Inline AI insights display
- JSON and PDF export

### 9.4 FastAPI REST API

**Access:** `http://localhost:8000`  
**Docs:** `http://localhost:8000/docs` (Swagger UI)  
**Launch:** Option 4 in `launch.py`

**Example Usage:**
```bash
# Submit a test
curl -X POST http://localhost:8000/api/test \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "task": "comprehensive"}'

# Check results
curl http://localhost:8000/api/test/{job_id}

# Download PDF
curl http://localhost:8000/api/test/{job_id}/pdf --output report.pdf
```

Suitable for CI/CD pipeline integration — submit tests programmatically and retrieve results via polling.

### 9.5 Interactive Terminal Agent

**Launch:** Option 5 in `launch.py`

A guided, step-by-step terminal experience:
1. Displays an ASCII art WebSentinel banner
2. Prompts the user for a target URL
3. Asks for a natural-language task description
4. Offers test category selection
5. Runs the AI agent and comprehensive tests
6. Displays a rich summary in the terminal
7. Offers PDF report generation

Ideal for users who want a conversational, guided testing experience without a web browser.

---

## 10. Testing and Results

### 10.1 Test Categories

WebSentinel performs tests across 7 primary categories plus 4 advanced categories:

**Primary Categories (ComprehensiveTester):**

| Category | Metrics | Pass Criteria |
|----------|---------|---------------|
| Page Load | Load time (s), HTTP status | <3s, status 200 |
| Link Validation | Total, internal, external, broken | 0 broken links |
| Form Detection | Form count, CSRF tokens, fields | All forms have CSRF tokens |
| Responsive Design | Mobile/Tablet/Desktop overflow | No horizontal overflow |
| Security Headers | 7 headers checked | All critical headers present |
| Accessibility | Image alt, headings, labels | 0 issues |
| Console Errors | Error count, warning count | 0 errors |

**Advanced Categories:**

| Category | Module | Output |
|----------|--------|--------|
| Security Scan | SecurityScanner | Score (0-100), risk level, vulnerabilities |
| Accessibility Audit | AccessibilityAnalyzer | Score (0-100), WCAG issues |
| Performance Analysis | PerformancePredictor | Score (0-100), bottlenecks, predictions |
| SEO Evaluation | SEOAnalyzer | Per-check PASS/WARNING/FAIL |

### 10.2 Security Scanning Results

The SecurityScanner produces a structured vulnerability report:

**Security Score Calculation:**
- Starts at 100
- Deducts points per severity: CRITICAL (-20), HIGH (-15), MEDIUM (-10), LOW (-5)
- Minimum score: 0

**Risk Level Mapping:**
| Score Range | Risk Level |
|-------------|------------|
| 80-100 | LOW |
| 60-79 | MEDIUM |
| 40-59 | HIGH |
| 0-39 | CRITICAL |

**Headers Checked:**

| Header | Severity | Purpose |
|--------|----------|---------|
| Content-Security-Policy | HIGH | Prevents XSS and content injection |
| X-Frame-Options | MEDIUM | Prevents clickjacking |
| Strict-Transport-Security | HIGH | Enforces HTTPS |
| X-Content-Type-Options | MEDIUM | Prevents MIME sniffing |
| X-XSS-Protection | LOW | Legacy XSS filter |
| Referrer-Policy | LOW | Controls referrer information |
| Permissions-Policy | LOW | Controls browser feature access |

### 10.3 Accessibility Audit Results

**Compliance Score Calculation:**
- Starts at 100
- Deducts points per issue severity: HIGH (-10), MEDIUM (-5), LOW (-2)
- Minimum score: 0

**Common Issues Detected:**

| WCAG SC | Issue | Severity | Affected Groups |
|---------|-------|----------|-----------------|
| 1.1.1 | Images without alt text | HIGH | Blind users, screen readers |
| 1.3.1 | Skipped heading levels | MEDIUM | Screen readers, cognitive |
| 1.4.3 | Insufficient contrast | MEDIUM | Low vision users |
| 2.1.1 | Non-keyboard-accessible elements | HIGH | Motor disabilities |
| 2.4.2 | Missing page title | MEDIUM | Screen readers |
| 3.2.2 | Form inputs without labels | HIGH | Screen readers, cognitive |

### 10.4 Performance Analysis Results

**Benchmark Thresholds:**

| Metric | Excellent | Good | Poor |
|--------|-----------|------|------|
| Page Load Time | <3s | 3-5s | >5s |
| TTFB | <200ms | 200-500ms | >500ms |
| Resource Count | <50 | 50-100 | >100 |
| Page Size | <1MB | 1-3MB | >3MB |
| LCP | <2.5s | 2.5-4s | >4s |
| FID | <100ms | 100-300ms | >300ms |
| CLS | <0.1 | 0.1-0.25 | >0.25 |

### 10.5 AI-Generated Insights

When an LLM is available, the AIAnalyzer generates a comprehensive natural-language report covering:

1. **Executive Summary:** Overall website quality assessment
2. **Critical Issues:** Top 3-5 issues requiring immediate attention
3. **Performance Recommendations:** Specific optimization suggestions
4. **Security Hardening:** Actionable security improvements
5. **Accessibility Improvements:** WCAG compliance recommendations
6. **Overall Grade:** Letter grade (A+ through F) with justification

The AI analysis prompt includes all raw test metrics and asks the LLM to act as "an expert web developer, security analyst, and UX consultant."

---

## 11. Report Generation

### 11.1 Basic PDF Reports

**Generator:** `PDFReportGenerator` (`utils/pdf_report_generator.py`)  
**Pages:** 5-8  
**Contents:**
- Title page with URL and timestamp
- Executive summary table (PASS/WARNING/FAIL counts)
- Per-test category details
- Screenshots (if available)

### 11.2 Enhanced PDF Reports

**Generator:** `EnhancedPDFReportGenerator` (`core/enhanced_pdf_generator.py`)  
**Pages:** 10-15  
**Additional Contents:**
- Custom branding and typography
- Pie charts: Test pass/fail distribution
- Bar charts: Performance metrics comparison
- Line charts: Historical trend data
- AI insights section (full LLM analysis text)
- Detailed vulnerability tables with severity indicators

### 11.3 Ultra PDF Reports (25+ Pages)

**Generator:** `UltraEnhancedPDFGenerator` (`core/ultra_pdf_generator.py`)  
**Pages:** 25+  
**Contents:**
- **Cover Page:** Project title, URL, date, branding
- **Table of Contents**
- **Executive Summary:** High-level findings and overall score
- **Security Deep-Dive:** Full OWASP-aligned vulnerability report with severity, CVSS scores, impact, and remediation steps
- **Accessibility Audit:** Complete WCAG compliance report with per-criterion results, affected groups, and code-level fixes
- **Performance Analysis:** Core Web Vitals, navigation timing breakdown, resource analysis, optimization roadmap
- **SEO Evaluation:** Meta tag analysis, Open Graph verification, structured data check, mobile friendliness
- **AI Analysis:** Full LLM-generated insights and recommendations
- **Test Screenshots:** Captured screenshots from testing session
- **Appendices:** Raw data tables, full header dumps, methodology notes

Accepts optional parameters: `security_results`, `accessibility_results`, `performance_results`, `seo_results`, and `ai_insights` for maximum detail.

---

## 12. Installation and Setup

### 12.1 Prerequisites

1. **Python 3.11+** installed and available in PATH
2. **Git** for cloning the repository
3. **Internet connection** for installing packages and browser binaries
4. **(Optional) Ollama** installed for local LLM inference without cloud APIs

### 12.2 Step-by-Step Installation

**Windows:**
```powershell
# 1. Clone the repository
git clone <repository-url>
cd Sentinel

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
.venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Install Playwright browser binary (REQUIRED)
python -m playwright install chromium

# 6. Configure environment
# Edit .env file with your API key(s)

# 7. Launch the application
python launch.py
```

**Linux / macOS:**
```bash
# 1. Clone the repository
git clone <repository-url>
cd Sentinel

# 2. Create virtual environment
python3 -m venv .venv

# 3. Activate virtual environment
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Install Playwright browser binary (REQUIRED)
python -m playwright install chromium

# 6. Configure environment
# Edit .env file with your API key(s)

# 7. Launch the application
python launch.py
```

**Or use the setup scripts:**
- Windows: `setup.bat`
- Linux/macOS: `bash setup.sh`

### 12.3 Running the Application

After installation, run `python launch.py` and select an option:

```
══════════════════════════════════════════════════════════════════
  🛡️  WebSentinel - AI-Powered Web Testing Platform
══════════════════════════════════════════════════════════════════

📦 Interfaces:
  1. Gradio Web Interface (Recommended) - Full visual UI
  2. Streamlit Interface - Alternative visual UI
  3. CLI Interface - Command line testing
  4. FastAPI Server - REST API for integrations
  5. Interactive Terminal Agent - AI chat interface

🧪 Testing:
  6. Run Comprehensive Tests (All modules)
  7. Run Next-Level Features Test

📄 Reports:
  8. Generate Sample Ultra PDF Report (25+ pages)

  0. Exit
```

**Quick Start:**
1. Select **Option 1** (Gradio) or **Option 2** (Streamlit) for a visual UI
2. Enter a URL (e.g., `https://example.com`)
3. Click the test button
4. View results and download the generated report

---

## 13. Future Scope

1. **Continuous Monitoring:** Schedule periodic tests and track quality trends over time with historical dashboards.

2. **CI/CD Integration Plugins:** Native GitHub Actions, GitLab CI, and Jenkins plugins for automated testing on every deployment.

3. **Load/Stress Testing:** Integration with tools like Locust or k6 for high-concurrency performance testing.

4. **Mobile Application Testing:** Extend browser automation to mobile emulation with device-specific testing profiles.

5. **Multi-Browser Support:** Test across Chrome, Firefox, Safari, and Edge simultaneously with cross-browser reports.

6. **Collaborative Reports:** Multi-user report sharing, annotations, and issue tracking integration (Jira, GitHub Issues).

7. **Custom Rule Engine:** Allow users to define custom test rules (e.g., "all pages must load in under 2 seconds") with configurable pass/fail thresholds.

8. **Machine Learning Predictions:** Train models on historical test data to predict failures before deployment.

9. **Real User Monitoring (RUM):** Collect and analyze performance data from actual user sessions.

10. **Accessibility Automation:** Auto-generate WCAG fixes (add alt text, fix contrast) using AI.

---

## 14. Conclusion

WebSentinel is a comprehensive, AI-powered web testing platform that unifies security scanning, accessibility auditing, performance analysis, SEO evaluation, and visual regression testing into a single tool. By leveraging the browser-use agent framework with Playwright, the platform enables an AI agent to navigate and test websites through natural-language instructions, mimicking human interaction while conducting thorough, automated assessments.

The multi-provider LLM architecture ensures flexibility — supporting Google Gemini, OpenAI, Anthropic, and local Ollama models with automatic fallback. Five distinct user interfaces (Gradio, Streamlit, CLI, FastAPI, Interactive Agent) cater to diverse workflows, from visual dashboards for manual testers to REST APIs for CI/CD pipeline integration.

The professional-grade PDF report generation system produces detailed, actionable reports (up to 25+ pages) with charts, vulnerability breakdowns, WCAG compliance scores, and AI-powered remediation recommendations — suitable for both technical teams and non-technical stakeholders.

WebSentinel demonstrates how AI agents can transform web quality assurance from a manual, fragmented process into an intelligent, unified, and scalable testing platform.

---

## 15. References

1. OWASP Foundation. *OWASP Top 10 – 2021*. https://owasp.org/www-project-top-ten/

2. W3C Web Accessibility Initiative. *Web Content Accessibility Guidelines (WCAG) 2.1*. https://www.w3.org/TR/WCAG21/

3. Google Developers. *Web Vitals*. https://web.dev/vitals/

4. Playwright Documentation. *Microsoft Playwright*. https://playwright.dev/

5. LangChain Documentation. *LangChain Framework*. https://python.langchain.com/

6. Google. *Gemini API Documentation*. https://ai.google.dev/

7. OpenAI. *API Reference*. https://platform.openai.com/docs/

8. Anthropic. *Claude API Documentation*. https://docs.anthropic.com/

9. Ollama. *Local LLM Inference*. https://ollama.ai/

10. Streamlit Documentation. https://docs.streamlit.io/

11. Gradio Documentation. https://www.gradio.app/docs/

12. FastAPI Documentation. https://fastapi.tiangolo.com/

13. ReportLab Documentation. *PDF Generation in Python*. https://docs.reportlab.com/

14. MDN Web Docs. *Navigation Timing API*. https://developer.mozilla.org/en-US/docs/Web/API/Navigation_timing_API

15. BeautifulSoup Documentation. https://www.crummy.com/software/BeautifulSoup/bs4/doc/

---

*Document generated for WebSentinel v0.1.0*
