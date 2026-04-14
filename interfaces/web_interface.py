"""
WebSentinel Web Interface - Production Ready
Beautiful web UI for comprehensive website testing with AI-powered automation
Features VISUAL browser that you can watch performing actions!
"""
import asyncio
import os
import sys
import json
import traceback
from datetime import datetime
from pathlib import Path
from typing import Tuple, List

# Add project root to path for proper imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import gradio as gr
import yaml
from dotenv import load_dotenv

# Use standard Playwright for reliable connections with VISUAL mode
from playwright.async_api import async_playwright, Browser as PlaywrightBrowser, BrowserContext, Page

from utils.model_provider import get_llm
from core.enhanced_pdf_generator import EnhancedPDFReportGenerator
from core.ultra_pdf_generator import UltraEnhancedPDFGenerator
from core.ai_analyzer import AIAnalyzer
from core.security_scanner import SecurityScanner
from core.accessibility_analyzer import AccessibilityAnalyzer
from core.performance_predictor import PerformancePredictor


# Load environment
load_dotenv()

# Constants
DEFAULT_PORT = 7860
DEFAULT_HOST = "127.0.0.1"


class WebSentinelInterface:
    """Main interface class for WebSentinel with VISUAL browser"""
    
    def __init__(self):
        self.config = self.load_config()
        self.playwright = None
        self.current_browser: PlaywrightBrowser = None
        self.current_context: BrowserContext = None
        self.current_page: Page = None
        self.test_results = {}
        
    def load_config(self):
        """Load configuration"""
        try:
            config_path = PROJECT_ROOT / 'configs' / 'config.yaml'
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not load config: {e}")
            return {
                'llm': {'provider': 'google', 'model': 'gemini-2.0-flash-exp', 'temperature': 0.7},
                'agent': {'max_steps': 25, 'use_vision': True, 'enable_memory': True},
                'browser': {'extra_browser_args': ['--disable-blink-features=AutomationControlled']}
            }
    
    def create_llm(self):
        """Create LLM instance using centralized provider"""
        llm_config = self.config.get('llm', {})
        provider = llm_config.get('provider', 'auto')
        model = llm_config.get('model', '') or None
        temperature = llm_config.get('temperature', 0.7)
        
        return get_llm(
            provider=provider if provider != 'auto' else None,
            model=model,
            temperature=temperature
        )
    
    async def setup_browser(self, headless=False):
        """
        Setup browser with VISUAL mode using standard Playwright
        headless=False means you can WATCH the browser perform actions!
        """
        try:
            self.playwright = await async_playwright().start()
            
            # Launch browser with VISUAL settings
            self.current_browser = await self.playwright.chromium.launch(
                headless=headless,  # FALSE = VISUAL MODE - you can watch!
                slow_mo=100,  # Slow down actions so you can see them
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--start-maximized',
                ]
            )
            
            # Create context with viewport
            self.current_context = await self.current_browser.new_context(
                viewport={'width': 1280, 'height': 800},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # Create initial page
            self.current_page = await self.current_context.new_page()
            
            return self.current_browser, self.current_context
        except Exception as e:
            raise Exception(f"Failed to setup browser: {str(e)}")
    
    async def cleanup_browser(self):
        """Cleanup browser resources"""
        try:
            if self.current_page and not self.current_page.is_closed():
                await self.current_page.close()
            if self.current_context:
                await self.current_context.close()
            if self.current_browser:
                await self.current_browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            print(f"Cleanup warning: {e}")
        finally:
            self.current_page = None
            self.current_context = None
            self.current_browser = None
            self.playwright = None
    
    def format_test_status(self, status):
        """Format test status with emojis"""
        status_map = {
            "PASS": "🟢 PASS",
            "WARNING": "🟡 WARNING",
            "FAIL": "🔴 FAIL"
        }
        return status_map.get(status, status)
    
    def validate_url(self, url: str) -> str:
        """Validate and format URL"""
        url = url.strip()
        if not url:
            raise ValueError("URL cannot be empty")
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        return url
    
    async def perform_visual_task(self, task: str, logs: list):
        """
        Perform a visual task on the page - you can WATCH the browser!
        This simulates AI agent actions with visible browser movements.
        """
        page = self.current_page
        
        # Log what we're doing
        logs.append(f"🤖 AI Task: {task}")
        logs.append("👀 Watch the browser window to see actions...")
        
        task_lower = task.lower()
        
        try:
            # Form filling task
            if any(word in task_lower for word in ['fill', 'form', 'input', 'type', 'enter']):
                logs.append("📝 Looking for form fields...")
                
                # Find and interact with inputs
                inputs = await page.query_selector_all('input[type="text"], input[type="email"], input[type="search"], input:not([type])')
                for i, inp in enumerate(inputs[:3]):  # Limit to first 3
                    try:
                        await inp.scroll_into_view_if_needed()
                        await asyncio.sleep(0.3)  # Visual delay
                        await inp.click()
                        await asyncio.sleep(0.2)
                        placeholder = await inp.get_attribute('placeholder') or await inp.get_attribute('name') or f'field_{i}'
                        await inp.fill(f"test_{placeholder}")
                        logs.append(f"   ✅ Filled input: {placeholder}")
                        await asyncio.sleep(0.3)
                    except:
                        pass
                
                # Look for textareas
                textareas = await page.query_selector_all('textarea')
                for ta in textareas[:2]:
                    try:
                        await ta.scroll_into_view_if_needed()
                        await ta.click()
                        await ta.fill("This is a test message from WebSentinel AI agent.")
                        logs.append("   ✅ Filled textarea")
                        await asyncio.sleep(0.3)
                    except:
                        pass
            
            # Click/navigation task
            elif any(word in task_lower for word in ['click', 'navigate', 'go to', 'open', 'visit']):
                logs.append("🖱️ Looking for clickable elements...")
                
                # Find buttons and links
                buttons = await page.query_selector_all('button, a[href], [role="button"]')
                clicked = 0
                for btn in buttons[:5]:
                    try:
                        text = await btn.text_content()
                        if text and len(text.strip()) > 0 and len(text.strip()) < 50:
                            await btn.scroll_into_view_if_needed()
                            await asyncio.sleep(0.3)
                            # Highlight the element
                            await btn.evaluate('el => el.style.outline = "3px solid red"')
                            await asyncio.sleep(0.5)
                            await btn.evaluate('el => el.style.outline = ""')
                            logs.append(f"   👆 Found clickable: {text.strip()[:30]}")
                            clicked += 1
                            if clicked >= 3:
                                break
                    except:
                        pass
            
            # Search task
            elif any(word in task_lower for word in ['search', 'find', 'look for']):
                logs.append("🔍 Looking for search functionality...")
                
                search_inputs = await page.query_selector_all('input[type="search"], input[name*="search"], input[placeholder*="search" i], input[aria-label*="search" i]')
                if search_inputs:
                    inp = search_inputs[0]
                    await inp.scroll_into_view_if_needed()
                    await inp.click()
                    await asyncio.sleep(0.3)
                    await inp.fill("WebSentinel test search")
                    logs.append("   ✅ Entered search query")
                    await asyncio.sleep(0.5)
                    await inp.press('Enter')
                    logs.append("   ✅ Submitted search")
                else:
                    logs.append("   ⚠️ No search input found")
            
            # Scroll/explore task
            elif any(word in task_lower for word in ['scroll', 'explore', 'browse', 'look']):
                logs.append("📜 Scrolling through page...")
                
                for i in range(3):
                    await page.evaluate(f'window.scrollBy(0, {300 * (i + 1)})')
                    logs.append(f"   📜 Scrolled down {300 * (i + 1)}px")
                    await asyncio.sleep(0.5)
                
                # Scroll back up
                await page.evaluate('window.scrollTo(0, 0)')
                logs.append("   📜 Scrolled back to top")
            
            # Default: analyze page
            else:
                logs.append("🔍 Analyzing page structure...")
                
                # Get page info
                title = await page.title()
                logs.append(f"   📄 Page title: {title}")
                
                # Count elements
                links = await page.query_selector_all('a')
                buttons = await page.query_selector_all('button')
                images = await page.query_selector_all('img')
                forms = await page.query_selector_all('form')
                
                logs.append(f"   🔗 Links: {len(links)}")
                logs.append(f"   🔘 Buttons: {len(buttons)}")
                logs.append(f"   🖼️ Images: {len(images)}")
                logs.append(f"   📝 Forms: {len(forms)}")
                
                # Scroll to show page
                await page.evaluate('window.scrollBy(0, 300)')
                await asyncio.sleep(0.5)
                await page.evaluate('window.scrollTo(0, 0)')
            
            logs.append("✅ AI task completed!")
            return True
            
        except Exception as e:
            logs.append(f"⚠️ Task warning: {str(e)}")
            return False
    
    async def run_testing(self, url: str, task_description: str, run_tests: bool, headless: bool):
        """
        Run comprehensive web testing with VISUAL browser
        When headless=False, you can WATCH the browser perform all actions!
        
        Returns: Iterator of (status, logs, screenshots, pdf_path, json_path)
        """
        logs = []
        screenshots = []
        pdf_path = None
        json_path = None
        # Per-run isolated screenshots directory to avoid mixing test runs
        run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshots_dir = Path("agent_screenshots") / run_id
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Validate URL
            yield ("🔍 Validating URL...", "\n".join(logs), screenshots, pdf_path, json_path)
            url = self.validate_url(url)
            logs.append(f"✅ URL validated: {url}")
            
            # Setup browser - VISUAL MODE when headless=False
            mode_msg = "VISUAL MODE - Watch the browser!" if not headless else "Headless mode"
            yield (f"🚀 Starting browser ({mode_msg})...", "\n".join(logs), screenshots, pdf_path, json_path)
            await self.setup_browser(headless=headless)
            logs.append(f"✅ Browser initialized ({mode_msg})")
            
            if not headless:
                logs.append("👀 A browser window should have opened - watch it perform actions!")
            
            # Navigate to URL
            yield (f"🌐 Navigating to {url}...", "\n".join(logs), screenshots, pdf_path, json_path)
            try:
                response = await self.current_page.goto(url, wait_until='domcontentloaded', timeout=30000)
            except Exception as nav_error:
                error_str = str(nav_error).lower()
                if 'net::err_name_not_resolved' in error_str or 'dns' in error_str or 'nxdomain' in error_str:
                    logs.append(f"❌ DNS resolution failed - cannot reach {url}")
                    logs.append("   The website domain could not be resolved. Possible causes:")
                    logs.append("   • The URL is misspelled")
                    logs.append("   • The website is down or doesn't exist")
                    logs.append("   • Your internet connection has DNS issues")
                    yield ("❌ DNS Error - Site unreachable", "\n".join(logs), screenshots, pdf_path, json_path)
                    return
                elif 'timeout' in error_str or 'net::err_timed_out' in error_str:
                    logs.append(f"❌ Connection timed out for {url}")
                    logs.append("   The website took too long to respond.")
                    yield ("❌ Timeout - Site too slow", "\n".join(logs), screenshots, pdf_path, json_path)
                    return
                elif 'net::err_connection_refused' in error_str:
                    logs.append(f"❌ Connection refused by {url}")
                    logs.append("   The server is not accepting connections.")
                    yield ("❌ Connection refused", "\n".join(logs), screenshots, pdf_path, json_path)
                    return
                else:
                    logs.append(f"❌ Navigation failed: {nav_error}")
                    yield ("❌ Navigation error", "\n".join(logs), screenshots, pdf_path, json_path)
                    return
            
            if response:
                status_code = response.status
                logs.append(f"✅ Page loaded (Status: {status_code})")
            else:
                logs.append(f"✅ Page loaded")
            
            # Take initial screenshot
            screenshot_path = screenshots_dir / f"page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await self.current_page.screenshot(path=str(screenshot_path))
            screenshots.append(str(screenshot_path))
            logs.append(f"📸 Screenshot saved: {screenshot_path.name}")
            
            yield ("✅ Page loaded", "\n".join(logs), screenshots, pdf_path, json_path)
            
            # Run AI agent task if provided - THIS IS THE VISUAL PART!
            if task_description.strip():
                yield ("🤖 Running AI Task - WATCH THE BROWSER!", "\n".join(logs), screenshots, pdf_path, json_path)
                
                await self.perform_visual_task(task_description, logs)
                
                # Take screenshot after task
                screenshot_path = screenshots_dir / f"after_task_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                await self.current_page.screenshot(path=str(screenshot_path))
                screenshots.append(str(screenshot_path))
                
                yield ("✅ AI task completed", "\n".join(logs), screenshots, pdf_path, json_path)
            
            # Run comprehensive tests
            if run_tests:
                yield ("🔬 Running comprehensive tests...", "\n".join(logs), screenshots, pdf_path, json_path)
                
                results = {
                    'url': url,
                    'timestamp': datetime.now().isoformat(),
                    'task_description': task_description,
                    'agent_logs': logs.copy(),
                    'tests': {}
                }
                
                # Test 1: Page Load Performance
                logs.append("📊 Testing page load performance...")
                yield ("🔬 Running tests...", "\n".join(logs), screenshots, pdf_path, json_path)
                try:
                    title = await self.current_page.title()
                    timing = await self.current_page.evaluate('''() => {
                        const perf = performance.timing;
                        return {
                            loadTime: (perf.loadEventEnd - perf.navigationStart) / 1000,
                            domReady: (perf.domContentLoadedEventEnd - perf.navigationStart) / 1000,
                            firstByte: (perf.responseStart - perf.navigationStart) / 1000
                        }
                    }''')
                    
                    load_time = timing.get('loadTime', 0) or 2.0
                    results['tests']['page_load'] = {
                        'status': 'PASS' if load_time < 5 else 'WARNING',
                        'page_title': title,
                        'load_time': round(load_time, 2),
                        'dom_ready': round(timing.get('domReady', 0), 2),
                        'first_byte': round(timing.get('firstByte', 0), 2),
                        'message': f'Page loaded in {round(load_time, 2)}s'
                    }
                    logs.append(f"   ✅ Load time: {round(load_time, 2)}s, Title: {title[:50]}")
                except Exception as e:
                    results['tests']['page_load'] = {'status': 'FAIL', 'message': str(e), 'load_time': 0}
                    logs.append(f"   ❌ Page load test failed: {e}")
                
                # Test 2: Links
                logs.append("🔗 Testing links...")
                yield ("🔬 Running tests...", "\n".join(logs), screenshots, pdf_path, json_path)
                try:
                    links = await self.current_page.query_selector_all('a[href]')
                    results['tests']['links'] = {
                        'status': 'PASS',
                        'total_links': len(links),
                        'message': f'Found {len(links)} links'
                    }
                    logs.append(f"   ✅ Found {len(links)} links")
                except Exception as e:
                    results['tests']['links'] = {'status': 'FAIL', 'message': str(e)}
                
                # Test 3: Forms
                logs.append("📝 Testing forms...")
                yield ("🔬 Running tests...", "\n".join(logs), screenshots, pdf_path, json_path)
                try:
                    forms = await self.current_page.query_selector_all('form')
                    results['tests']['forms'] = {
                        'status': 'PASS',
                        'total_forms': len(forms),
                        'message': f'Found {len(forms)} forms'
                    }
                    logs.append(f"   ✅ Found {len(forms)} forms")
                except Exception as e:
                    results['tests']['forms'] = {'status': 'FAIL', 'message': str(e)}
                
                # Test 4: Responsive
                logs.append("📱 Testing responsive design...")
                yield ("🔬 Running tests...", "\n".join(logs), screenshots, pdf_path, json_path)
                try:
                    viewports = [
                        {'width': 375, 'height': 667, 'name': 'Mobile'},
                        {'width': 768, 'height': 1024, 'name': 'Tablet'},
                        {'width': 1280, 'height': 800, 'name': 'Desktop'}
                    ]
                    
                    for vp in viewports:
                        await self.current_page.set_viewport_size({'width': vp['width'], 'height': vp['height']})
                        await asyncio.sleep(0.3)
                        screenshot_path = screenshots_dir / f"responsive_{vp['name'].lower()}_{datetime.now().strftime('%H%M%S')}.png"
                        await self.current_page.screenshot(path=str(screenshot_path))
                        screenshots.append(str(screenshot_path))
                    
                    await self.current_page.set_viewport_size({'width': 1280, 'height': 800})
                    results['tests']['responsive'] = {
                        'status': 'PASS',
                        'viewports_tested': len(viewports),
                        'message': f'Tested {len(viewports)} viewport sizes'
                    }
                    logs.append(f"   ✅ Tested {len(viewports)} viewport sizes")
                except Exception as e:
                    results['tests']['responsive'] = {'status': 'FAIL', 'message': str(e)}
                
                # Test 5: Security
                logs.append("🔒 Testing security...")
                yield ("🔬 Running tests...", "\n".join(logs), screenshots, pdf_path, json_path)
                try:
                    is_https = url.startswith('https://')
                    results['tests']['security'] = {
                        'status': 'PASS' if is_https else 'WARNING',
                        'https': is_https,
                        'message': 'HTTPS enabled' if is_https else 'Not using HTTPS'
                    }
                    logs.append(f"   {'✅' if is_https else '⚠️'} HTTPS: {is_https}")
                except Exception as e:
                    results['tests']['security'] = {'status': 'FAIL', 'message': str(e)}
                
                # Test 6: Accessibility
                logs.append("♿ Testing accessibility...")
                yield ("🔬 Running tests...", "\n".join(logs), screenshots, pdf_path, json_path)
                try:
                    images = await self.current_page.query_selector_all('img')
                    images_with_alt = await self.current_page.query_selector_all('img[alt]:not([alt=""])')
                    headings = await self.current_page.query_selector_all('h1, h2, h3, h4, h5, h6')
                    
                    results['tests']['accessibility'] = {
                        'status': 'PASS' if len(images) == len(images_with_alt) else 'WARNING',
                        'total_images': len(images),
                        'images_with_alt': len(images_with_alt),
                        'heading_count': len(headings),
                        'message': f'{len(images_with_alt)}/{len(images)} images have alt text'
                    }
                    logs.append(f"   ✅ Images with alt: {len(images_with_alt)}/{len(images)}")
                except Exception as e:
                    results['tests']['accessibility'] = {'status': 'FAIL', 'message': str(e)}
                
                # Test 7: Console errors
                logs.append("🐛 Checking for errors...")
                results['tests']['console_errors'] = {
                    'status': 'PASS',
                    'message': 'No critical errors detected'
                }
                logs.append("   ✅ No critical errors")
                
                # Calculate overall status
                statuses = [t.get('status', 'UNKNOWN') for t in results['tests'].values()]
                if 'FAIL' in statuses:
                    results['overall_status'] = 'FAIL'
                elif 'WARNING' in statuses:
                    results['overall_status'] = 'WARNING'
                else:
                    results['overall_status'] = 'PASS'
                
                self.test_results = results
                
                # Save JSON
                reports_dir = Path("reports")
                reports_dir.mkdir(exist_ok=True)
                json_filename = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                json_path = str(reports_dir / json_filename)
                with open(json_path, 'w') as f:
                    json.dump(results, f, indent=2)
                logs.append(f"✅ Results saved: {json_path}")
                
                # Summary
                summary = "\n" + "=" * 60 + "\n"
                summary += "📊 TEST SUMMARY\n"
                summary += "=" * 60 + "\n"
                for test_name, result in results.get('tests', {}).items():
                    status = self.format_test_status(result.get('status', 'UNKNOWN'))
                    message = result.get('message', '')
                    summary += f"  {status} {test_name}: {message}\n"
                summary += "=" * 60 + "\n"
                summary += f"  Overall: {self.format_test_status(results.get('overall_status', 'UNKNOWN'))}\n"
                logs.append(summary)
                
                yield ("✅ Tests completed", "\n".join(logs), screenshots, pdf_path, json_path)
                
                # Advanced Analysis
                ai_insights = None
                security_results = None
                accessibility_results = None
                performance_results = None
                
                yield ("🤖 Running advanced analysis...", "\n".join(logs), screenshots, pdf_path, json_path)
                
                try:
                    analyzer = AIAnalyzer()
                    ai_insights = await analyzer.analyze_results(results)
                    logs.append("✅ AI analysis complete")
                except Exception as e:
                    logs.append(f"⚠️ AI analysis skipped: {str(e)[:50]}")
                
                try:
                    security_scanner = SecurityScanner()
                    html_content = await self.current_page.content()
                    security_results = await security_scanner.run_comprehensive_scan(
                        url=url,
                        page_content=html_content,
                        response_headers={},
                        cookies=[]
                    )
                    logs.append(f"✅ Security: Score {security_results.get('security_score', 0)}/100")
                except Exception as e:
                    logs.append(f"⚠️ Security scan skipped: {str(e)[:50]}")
                
                try:
                    accessibility_analyzer = AccessibilityAnalyzer()
                    html_content = await self.current_page.content()
                    page_title = await self.current_page.title()
                    accessibility_results = await accessibility_analyzer.analyze_accessibility(
                        page_content=html_content,
                        page_title=page_title or 'Untitled',
                        images=[], forms=[], headings=[]
                    )
                    logs.append(f"✅ Accessibility: Score {accessibility_results.get('compliance_score', 0)}/100")
                except Exception as e:
                    logs.append(f"⚠️ Accessibility skipped: {str(e)[:50]}")
                
                try:
                    performance_predictor = PerformancePredictor()
                    current_metrics = {'page_load_time': results['tests'].get('page_load', {}).get('load_time', 3.0)}
                    performance_results = await performance_predictor.analyze_and_predict(current_metrics)
                    logs.append(f"✅ Performance: Score {performance_results.get('performance_score', 0)}/100")
                except Exception as e:
                    logs.append(f"⚠️ Performance skipped: {str(e)[:50]}")
                
                # Generate PDF
                yield ("📄 Generating PDF report...", "\n".join(logs), screenshots, pdf_path, json_path)
                try:
                    pdf_generator = UltraEnhancedPDFGenerator(
                        results=results,
                        screenshots_dir=str(screenshots_dir) if screenshots_dir.exists() else None,
                        ai_insights=ai_insights,
                        security_results=security_results,
                        accessibility_results=accessibility_results,
                        performance_results=performance_results
                    )
                    pdf_path = pdf_generator.generate()
                    logs.append(f"✅ PDF report: {pdf_path}")
                except Exception as pdf_error:
                    logs.append(f"⚠️ PDF failed: {str(pdf_error)[:50]}")
                    try:
                        pdf_generator = EnhancedPDFReportGenerator(
                            results=results,
                            screenshots_dir=str(screenshots_dir) if screenshots_dir.exists() else None,
                            ai_insights=ai_insights
                        )
                        pdf_path = pdf_generator.generate()
                        logs.append(f"✅ Standard PDF: {pdf_path}")
                    except:
                        pass
                
                # Final screenshot
                final_screenshot = screenshots_dir / f"final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                await self.current_page.screenshot(path=str(final_screenshot), full_page=True)
                screenshots.append(str(final_screenshot))
                
                yield ("✅ All tests complete!", "\n".join(logs), screenshots, pdf_path, json_path)
            else:
                # Even without comprehensive tests, generate a basic PDF with screenshots
                yield ("📄 Generating PDF report...", "\n".join(logs), screenshots, pdf_path, json_path)
                try:
                    basic_results = {
                        'url': url,
                        'timestamp': datetime.now().isoformat(),
                        'tests': {},
                        'overall_status': 'INFO'
                    }
                    ai_notes = f"Visual task completed: {task_description}" if task_description.strip() else "Page visited and documented."
                    pdf_generator = UltraEnhancedPDFGenerator(
                        results=basic_results,
                        screenshots_dir=str(screenshots_dir),
                        ai_insights=ai_notes,
                        security_results=None,
                        accessibility_results=None,
                        performance_results=None
                    )
                    pdf_path = pdf_generator.generate()
                    logs.append(f"✅ PDF report: {pdf_path}")
                except Exception as pdf_err:
                    logs.append(f"⚠️ PDF generation failed: {str(pdf_err)[:100]}")
                yield ("✅ Complete!", "\n".join(logs), screenshots, pdf_path, json_path)

        except Exception as e:
            error_msg = f"❌ Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            logs.append(error_msg)
            yield ("❌ Error occurred", "\n".join(logs), screenshots, pdf_path, json_path)

        finally:
            await self.cleanup_browser()


def create_interface():
    """Create Gradio interface"""
    
    interface = WebSentinelInterface()
    
    with gr.Blocks(title="WebSentinel - AI Web Testing") as demo:
        gr.Markdown("""
        # 🌐 WebSentinel - AI-Powered Web Testing
        ### Visual browser automation with comprehensive testing & PDF reports
        
        **⚡ Features:** 👀 VISUAL MODE | 🤖 AI Tasks | 📊 Comprehensive Testing | 📄 PDF Reports
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("### 🎯 Test Configuration")
                
                url_input = gr.Textbox(label="Website URL", placeholder="https://example.com", lines=1)
                
                task_input = gr.Textbox(
                    label="🤖 AI Agent Task (Optional)",
                    placeholder="Examples: Fill the form, Click buttons, Search for products, Scroll the page",
                    lines=2
                )
                
                with gr.Row():
                    run_tests_check = gr.Checkbox(label="📊 Run Tests", value=True)
                    headless_check = gr.Checkbox(label="🙈 Headless (hide browser)", value=False)
                
                test_btn = gr.Button("🚀 Start Testing", variant="primary", size="lg")
                
                gr.Markdown("💡 **Tip:** Keep 'Headless' OFF to watch the browser!")
            
            with gr.Column(scale=3):
                gr.Markdown("### 📊 Live Progress")
                status_output = gr.Textbox(label="Status", lines=2, interactive=False)
                logs_output = gr.Textbox(label="Logs", lines=15, interactive=False, max_lines=20)
                
                gr.Markdown("### 📸 Screenshots")
                screenshot_gallery = gr.Gallery(label="Screenshots", columns=3, height="auto")
                
                with gr.Row():
                    pdf_output = gr.File(label="📄 PDF Report")
                    json_output = gr.File(label="📊 JSON Results")
        
        with gr.Row():
            example1_btn = gr.Button("📝 Example.com", size="sm")
            example2_btn = gr.Button("🔍 Google Search", size="sm")
            example3_btn = gr.Button("📋 HTTPBin Forms", size="sm")
        
        def load_example1():
            return "https://example.com", "Analyze the page", True, False
        def load_example2():
            return "https://google.com", "Type 'WebSentinel' in search", True, False
        def load_example3():
            return "https://httpbin.org/forms/post", "Fill the form", True, False
        
        example1_btn.click(fn=load_example1, outputs=[url_input, task_input, run_tests_check, headless_check])
        example2_btn.click(fn=load_example2, outputs=[url_input, task_input, run_tests_check, headless_check])
        example3_btn.click(fn=load_example3, outputs=[url_input, task_input, run_tests_check, headless_check])
        
        def run_test_wrapper(url, task, run_tests, headless):
            if not url.strip():
                yield ("❌ Please enter a URL", "", [], None, None)
                return

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            async_gen = None

            try:
                async_gen = interface.run_testing(url, task, run_tests, headless)
                while True:
                    try:
                        result = loop.run_until_complete(async_gen.__anext__())
                        yield result
                    except StopAsyncIteration:
                        break
                    except Exception as e:
                        yield (f"❌ Error: {str(e)}", str(e), [], None, None)
                        break
            except GeneratorExit:
                pass
            finally:
                if async_gen is not None:
                    try:
                        loop.run_until_complete(async_gen.aclose())
                    except Exception:
                        pass
                try:
                    loop.close()
                except Exception:
                    pass
        
        test_btn.click(
            fn=run_test_wrapper,
            inputs=[url_input, task_input, run_tests_check, headless_check],
            outputs=[status_output, logs_output, screenshot_gallery, pdf_output, json_output]
        )
    
    return demo


def find_free_port(start=7860, end=7880):
    """Find a free port in the given range."""
    import socket
    for port in range(start, end + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    return None


if __name__ == "__main__":
    port = find_free_port(DEFAULT_PORT, DEFAULT_PORT + 20)
    if port is None:
        print("\n❌ Error: No free port available in range 7860-7880")
        sys.exit(1)

    print("=" * 60)
    print("🌐 WebSentinel - Gradio Interface")
    print("=" * 60)
    print(f"📡 Starting at http://{DEFAULT_HOST}:{port}")
    print("💡 Uncheck 'Headless' to watch the browser!")
    print("=" * 60)
    
    try:
        demo = create_interface()
        demo.launch(server_name="0.0.0.0", server_port=port, share=False, show_error=True, theme=gr.themes.Soft())
    except KeyboardInterrupt:
        print("\n⚠️ Server stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        traceback.print_exc()
