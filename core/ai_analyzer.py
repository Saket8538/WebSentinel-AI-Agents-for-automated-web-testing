"""
AI-Powered Test Results Analyzer
Uses available LLM (Google Gemini / OpenAI / Anthropic / Ollama) to provide intelligent insights
"""
import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime

from utils.model_provider import get_llm
from rich.console import Console

console = Console()


class AIAnalyzer:
    """Analyze test results with AI and generate actionable insights"""
    
    def __init__(self, model: str = None):
        """Initialize AI analyzer with specified model (or auto-detect)"""
        self.model = model
        try:
            self.llm = get_llm(model=model)
        except Exception as e:
            console.print(f"[yellow]⚠️  AI initialization warning: {e}[/yellow]")
            self.llm = None
    
    async def analyze_results(self, results: Dict[str, Any]) -> Optional[str]:
        """
        Analyze test results and provide detailed insights
        
        Args:
            results: Dictionary of test results from comprehensive tester
            
        Returns:
            String containing detailed AI-generated insights, or None if unavailable
        """
        if not self.llm:
            return None
        
        try:
            console.print("[cyan]🤖 Analyzing results with AI...[/cyan]")
            prompt = self._build_analysis_prompt(results)
            
            response = await self.llm.ainvoke(prompt)
            insights = response.content
            
            console.print(f"[green]✓ AI analysis complete ({len(insights)} chars)[/green]")
            return insights
            
        except Exception as e:
            console.print(f"[yellow]⚠️  AI analysis unavailable: {e}[/yellow]")
            return None
    
    def analyze_results_sync(self, results: Dict[str, Any]) -> Optional[str]:
        """Synchronous wrapper for analyze_results"""
        try:
            return asyncio.run(self.analyze_results(results))
        except Exception as e:
            console.print(f"[yellow]⚠️  AI analysis failed: {e}[/yellow]")
            return None
    
    def _build_analysis_prompt(self, results: Dict[str, Any]) -> str:
        """Build comprehensive analysis prompt for AI"""
        
        tests = results.get('tests', {})
        url = results.get('url', 'Unknown')
        task_description = results.get('task_description', '').strip()
        
        # Extract key metrics
        page_load = tests.get('page_load', {})
        load_time = page_load.get('load_time', 0)
        status_code = page_load.get('status_code', 'N/A')
        
        security = tests.get('security', {})
        security_headers = security.get('headers', {})
        present_headers = [k for k, v in security_headers.items() if v]
        missing_headers = security.get('missing_headers', [])
        
        accessibility = tests.get('accessibility', {})
        a11y_issues_raw = accessibility.get('issues', [])
        if isinstance(a11y_issues_raw, list):
            a11y_issues = len(a11y_issues_raw)
        else:
            a11y_issues = int(a11y_issues_raw or 0)
        
        links = tests.get('links', {})
        broken_links = links.get('broken_links', [])
        total_links = links.get('total_links', 0)
        
        forms = tests.get('forms', {})
        form_count = forms.get('total_forms', forms.get('form_count', 0))
        
        responsive = tests.get('responsive', {})
        responsive_status = responsive.get('status', 'N/A')
        
        console_errors = tests.get('console_errors', {})
        errors_raw = console_errors.get('errors', [])
        warnings_raw = console_errors.get('warnings', [])
        errors = len(errors_raw) if isinstance(errors_raw, list) else int(errors_raw or 0)
        warnings = len(warnings_raw) if isinstance(warnings_raw, list) else int(warnings_raw or 0)
        
        agent_logs = results.get('agent_logs', [])
        if isinstance(agent_logs, list):
            agent_log_text = '\n'.join(str(item) for item in agent_logs if item)
        else:
            agent_log_text = str(agent_logs)
        if not agent_log_text.strip():
            agent_log_text = "No explicit visual agent task was run."
        
        if task_description:
            user_context = f"The user requested this specific goal: '{task_description}'."
        else:
            user_context = "Provide a general comprehensive health and security check for this website."
        
        prompt = f"""
You are an expert web consultant speaking to a non-technical business owner. Analyze these test results for {url}.

🎯 PRIMARY OBJECTIVE:
{user_context}
You MUST heavily tailor your analysis to address this prompt and explicitly detail EXACTLY what you tested on the website based on the logs below. Do NOT output a generic, pre-designed report. It must be highly specific to {url}.

═══════════════════════════════════════════════════════════════
ROBOT/AGENT ACTIONS (What I actually did on the website)
═══════════════════════════════════════════════════════════════
{agent_log_text}

═══════════════════════════════════════════════════════════════
TEST RESULTS SUMMARY
═══════════════════════════════════════════════════════════════
📅 Tested: {results.get('timestamp', 'N/A')}
⚡ Load Time: {load_time:.2f}s (Status: {page_load.get('status', 'N/A')})
🔒 Security Missing Headers: {len(missing_headers)} (Status: {security.get('status', 'N/A')})
♿ Accessibility Issues: {a11y_issues} (Status: {accessibility.get('status', 'N/A')})
🔗 Total Links: {total_links} | Broken: {len(broken_links)}
📝 Forms Found: {form_count}
🐛 Console Errors: {errors} | Warnings: {warnings}

═══════════════════════════════════════════════════════════════
ANALYSIS REQUIREMENTS
═══════════════════════════════════════════════════════════════

Provide a customized, Plain English report with these sections:

1️⃣ PLAIN ENGLISH NARRATIVE (Most important!)
   • Speak directly to the site owner in simple terms.
   • Tell a story of exactly what you, the AI agent, just did on their website (based on the ROBOT ACTIONS logs).
   • Did you fill a form? Did you search? Did you click buttons? Explicitly say "I went to your site and tested the...".
   • Explain how the site handled your specific goal ({task_description}).
   • Explain the overall health of the site based on the results without using confusing technical jargon.

2️⃣ THE 3 BIGGEST WINS & CONCERNS
   • Give them the top 3 things they are doing right.
   • Give them the top 3 things that need to be fixed immediately.
   • Explain the BUSINESS impact of the concerns (e.g., "missing this header means hackers could steal customer data").

3️⃣ TECHNICAL DEEP DIVE (For their developers)
   • Performance Analysis (Load time implications)
   • Security Assessment (Specific missing headers and their risks)
   • Accessibility Concerns (WCAG issues)
   • Include concrete code examples of how to fix the top 2 issues.

4️⃣ RECOMMENDED ACTION PLAN
   • Simple roadmap of what to fix Today, This Week, and This Month.

GUIDELINES:
• Absolutely NO generic filler. Use the exact URL {url} and reference specific actions taken.
• Keep the tone helpful, professional, but very easy to understand for normal people in section 1 and 2.
Begin your analysis now:
"""
        
        return prompt


class AIInsightsCache:
    """Cache AI insights to avoid redundant API calls"""
    
    def __init__(self, cache_file: str = "ai_insights_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load cache from file"""
        try:
            from pathlib import Path
            cache_path = Path(self.cache_file)
            if cache_path.exists():
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def _save_cache(self):
        """Save cache to file"""
        try:
            from pathlib import Path
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2)
        except Exception:
            pass
    
    def get_cached_insights(self, url: str, test_hash: str) -> Optional[str]:
        """Get cached insights for a URL and test configuration"""
        cache_key = f"{url}_{test_hash}"
        return self.cache.get(cache_key)
    
    def cache_insights(self, url: str, test_hash: str, insights: str):
        """Cache insights for a URL and test configuration"""
        cache_key = f"{url}_{test_hash}"
        self.cache[cache_key] = {
            'insights': insights,
            'timestamp': datetime.now().isoformat()
        }
        self._save_cache()


# Convenience function
async def get_ai_insights(results: Dict[str, Any], use_cache: bool = True) -> Optional[str]:
    """
    Quick function to get AI insights for test results
    
    Args:
        results: Test results dictionary
        use_cache: Whether to use cached insights
        
    Returns:
        AI-generated insights or None
    """
    try:
        analyzer = AIAnalyzer()
        
        if use_cache:
            cache = AIInsightsCache()
            url = results.get('url', 'unknown')
            # Simple hash of test results
            test_hash = str(hash(json.dumps(results.get('tests', {}), sort_keys=True)))
            
            # Check cache
            cached = cache.get_cached_insights(url, test_hash)
            if cached:
                console.print("[cyan]📦 Using cached AI insights[/cyan]")
                return cached.get('insights')
        
        # Generate new insights
        insights = await analyzer.analyze_results(results)
        
        if use_cache and insights:
            cache.cache_insights(url, test_hash, insights)
        
        return insights
        
    except Exception as e:
        console.print(f"[yellow]⚠️  Failed to get AI insights: {e}[/yellow]")
        return None


def get_ai_insights_sync(results: Dict[str, Any], use_cache: bool = True) -> Optional[str]:
    """Synchronous wrapper for get_ai_insights"""
    try:
        return asyncio.run(get_ai_insights(results, use_cache))
    except Exception as e:
        console.print(f"[yellow]⚠️  Failed to get AI insights: {e}[/yellow]")
        return None
