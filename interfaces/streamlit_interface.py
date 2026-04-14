"""
WebSentinel Streamlit Web Interface
=================================

Enhanced web interface with multiple testing modules:
- Comprehensive Tests (7 categories)
- Performance Monitoring
- SEO Analysis
- Visual Regression Testing
- API Testing
- Database Testing

Usage:
    streamlit run interfaces/streamlit_interface.py
"""

import sys
import os
import asyncio
from pathlib import Path

# Add project root to path FIRST
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# CRITICAL: Set event loop policy on Windows
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
    if hasattr(sys.stderr, 'reconfigure'):
        try:
            sys.stderr.reconfigure(encoding='utf-8')
        except Exception:
            pass
    
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    os.environ['PYTHONUTF8'] = '1'
    os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

# Import remaining modules
import json
from datetime import datetime

import nest_asyncio
import streamlit as st
import yaml

from tests.api_tester import APITester
from browser_use import Agent, Browser, BrowserConfig
from core.comprehensive_tester import ComprehensiveTester
from tests.db_tester import DatabaseTester
from utils.pdf_report_generator import PDFReportGenerator
from utils.performance_monitor import PerformanceMonitor
from utils.model_provider import get_llm
from core.seo_analyzer import SEOAnalyzer
from tests.visual_tester import VisualTester

# Apply nest_asyncio to allow nested event loops (must be before any asyncio usage)
nest_asyncio.apply()

# Set page config
st.set_page_config(
    page_title="WebSentinel - AI Testing Agent",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_config():
    """Load configuration from config.yaml.
    
    Returns:
        dict: Configuration dictionary loaded from YAML
    """
    config_path = Path("configs/config.yaml")
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def run_async(coro):
    """Helper to run async code in Streamlit environment.
    
    Args:
        coro: Coroutine to execute
    
    Returns:
        Any: Result from coroutine execution
    
    Raises:
        RuntimeError, ValueError, OSError: If coroutine execution fails
    """
    # nest_asyncio allows us to use asyncio.run in already running event loops
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, nest_asyncio allows nested calls
            return loop.run_until_complete(coro)
        else:
            # If no loop is running, create and run
            return asyncio.run(coro)
    except (RuntimeError, ValueError, OSError) as e:
        # If there's an error, ensure the coroutine is properly closed
        if hasattr(coro, 'close'):
            coro.close()
        raise


async def run_test(url: str, task: str, run_comprehensive: bool, headless: bool):
    """Run WebSentinel AI agent test with browser automation.
    
    Args:
        url: Target website URL to test
        task: Task description for AI agent
        run_comprehensive: Whether to run comprehensive tests afterward
        headless: Whether to run browser in headless mode
    
    Returns:
        tuple: (agent_result, comprehensive_result) - results from agent and tests
    """
    results = {}
    browser = None
    context = None
    agent = None
    # Unique run ID to isolate screenshots per test run
    run_task_name = datetime.now().strftime('%Y%m%d_%H%M%S')

    try:
        # Load config
        config = load_config()
        llm_config = config.get('llm', {})
        
        # Initialize LLM using centralized provider (auto-detects API keys or falls back to Ollama)
        provider = llm_config.get('provider', 'auto')
        model = llm_config.get('model', '') or None
        llm = get_llm(
            provider=provider if provider != 'auto' else None,
            model=model,
            temperature=llm_config.get('temperature', 0.7)
        )
        
        # Create browser
        browser_config = BrowserConfig(
            headless=headless,
            disable_security=True,
            extra_chromium_args=config.get('browser', {}).get('extra_browser_args', [])
        )
        
        browser = Browser(config=browser_config)
        
        # Initialize agent with unique task_name for per-run screenshot isolation
        agent = Agent(
            task=f"Navigate to {url} and {task}" if task else f"Navigate to {url}",
            llm=llm,
            browser=browser,
            task_name=run_task_name
        )
        
        # Run agent
        st.info("Running AI agent...")
        history = await agent.run(max_steps=10)
        final_result = history.final_result() if history else "No result"
        results['agent'] = {
            'final_result': final_result,
            'steps': len(history.history) if history else 0
        }
        
        # Run comprehensive tests if requested
        if run_comprehensive:
            st.info("Running comprehensive tests...")
            # Get browser context properly
            context = await browser.new_context()
            # Get the current page from the context instead of creating a new one
            page = await context.get_current_page()
            tester = ComprehensiveTester(url, context)
            test_results = await tester.run_all_tests()
            test_results['task_description'] = task.strip()
            test_results['agent_logs'] = [
                f"Requested task: {task.strip() or 'general navigation'}",
                f"Agent outcome: {final_result}"
            ]
            results['tests'] = test_results
            
            # Generate PDF report
            st.info("Generating PDF report...")
            report_dir = Path("reports")
            report_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_path = report_dir / f"report_{timestamp}.pdf"

            # Use the per-run agent screenshots subdirectory so old runs don't bleed in
            agent_screenshots_subdir = Path("agent_screenshots") / f"agent_screenshots_{run_task_name}"
            generator = PDFReportGenerator(
                results=test_results,
                screenshots_dir=str(agent_screenshots_subdir) if agent_screenshots_subdir.exists() else None
            )
            pdf_file = generator.generate(str(pdf_path))

            results['pdf_path'] = pdf_file
        
        return results
    
    except (RuntimeError, ValueError, IOError, OSError) as e:
        st.error(f"Error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return None
        
    finally:
        # Proper cleanup of async resources
        try:
            if agent:
                await agent.close()
        except Exception:
            pass  # Silently ignore cleanup errors
        
        try:
            if context:
                await context.close()
        except (RuntimeError, ValueError, OSError):
            pass  # Silently ignore cleanup errors
        
        try:
            if browser:
                await browser.close()
        except (RuntimeError, ValueError, OSError):
            pass  # Silently ignore cleanup errors


def main():
    # Initialize session state for caching results
    if 'test_results' not in st.session_state:
        st.session_state.test_results = {}
    if 'last_tested_url' not in st.session_state:
        st.session_state.last_tested_url = None
    
    # Header
    st.title("🌐 WebSentinel - Advanced Testing Platform")
    st.markdown("### Comprehensive testing suite with 12+ test categories")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        url = st.text_input(
            "Website URL",
            placeholder="https://example.com",
            help="Enter the full URL including https://"
        )
        
        task = st.text_area(
            "AI Agent Task (Optional)",
            placeholder="Describe what the AI should do (e.g., 'Test login form')",
            height=100,
            help="Leave empty for basic navigation"
        )
        
        headless = st.checkbox(
            "Headless Mode",
            value=False,
            help="Run browser in background (faster, no visual)"
        )
        
        st.markdown("---")
        st.markdown("### 📋 Available Test Modules")
        st.markdown("""
        **Comprehensive Tests** (7 categories):
        - 📊 Page Load Performance
        - 🔗 Link Validation
        - 📝 Form Testing
        - 📱 Responsive Design
        - 🔒 Security Headers
        - ♿ Accessibility
        - 🐛 Console Errors
        
        **Advanced Modules**:
        - ⚡ Performance Monitor
        - 🔍 SEO Analysis
        - 👁️ Visual Regression
        - 🔌 API Testing
        - 🗄️ Database Testing
        """)
    
    # Main content - Tabs for different testing modules
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Comprehensive Tests",
        "⚡ Performance",
        "🔍 SEO Analysis",
        "👁️ Visual Testing",
        "🔌 API Testing",
        "🗄️ Database Testing"
    ])
    
    # Tab 1: Comprehensive Tests (Original functionality)
    with tab1:
        st.markdown("### Run AI Agent + Comprehensive Tests")
        
        # Show cached results indicator
        if url in st.session_state.test_results:
            st.info(f"📌 Cached results available for this URL. Last tested: {st.session_state.test_results[url].get('timestamp', 'Unknown')}")
            if st.button("Clear Cache", key="clear_cache_btn"):
                del st.session_state.test_results[url]
                st.rerun()
        
        run_comprehensive = st.checkbox(
            "Enable Comprehensive Tests",
            value=True,
            help="Run all 7 test categories",
            key="comp_enable"
        )
        
        force_retest = st.checkbox(
            "Force Re-test (Ignore Cache)",
            value=False,
            help="Run test even if cached results exist",
            key="force_retest"
        )
        
        if st.button("Start Comprehensive Testing", type="primary", use_container_width=True, key="comp_button"):
            if not url.strip():
                st.error("Please enter a valid URL")
            else:
                # Ensure URL has protocol
                test_url = url if url.startswith(('http://', 'https://')) else f"https://{url}"
                
                # Check if we have cached results
                if test_url in st.session_state.test_results and not force_retest:
                    st.warning("Using cached results. Enable 'Force Re-test' to run a new test.")
                    results = st.session_state.test_results[test_url]
                else:
                    with st.spinner("Running tests..."):
                        coro = None
                        try:
                            coro = run_test(test_url, task, run_comprehensive, headless)
                            results = run_async(coro)
                        except Exception as e:
                            error_msg = str(e).lower()
                            if 'net::err_name_not_resolved' in error_msg or 'dns' in error_msg:
                                st.error("❌ DNS Error: Cannot reach the website. Check the URL and your internet connection.")
                            else:
                                st.error(f"❌ Testing failed: {str(e)}")
                            results = None
                            # Close coroutine if it wasn't awaited
                            if coro and hasattr(coro, 'close'):
                                coro.close()
                    
                        if results:
                            # Cache the results
                            results['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            st.session_state.test_results[test_url] = results
                            st.session_state.last_tested_url = test_url
                            st.success("Testing completed!")
                            
                            # Display results
                            st.subheader("🤖 AI Agent Results")
                            st.json(results.get('agent', {}))
                            
                            if 'tests' in results:
                                st.subheader("🧪 Test Results")
                                tests = results['tests']
                                
                                col_a, col_b, col_c = st.columns(3)
                                total_tests = len(tests)
                                # Safely handle test results that might be strings or dicts
                                passed = sum(1 for t in tests.values() 
                                           if isinstance(t, dict) and t.get('status', '').upper() == 'PASS')
                                failed = sum(1 for t in tests.values() 
                                           if isinstance(t, dict) and t.get('status', '').upper() == 'FAIL')
                                
                                col_a.metric("Total Tests", total_tests)
                                col_b.metric("Passed", passed)
                                col_c.metric("Failed", failed)
                                
                                for category, result in tests.items():
                                    # Safely check status for both dict and string types
                                    if isinstance(result, dict):
                                        status = result.get('status', '').upper()
                                        status_icon = "✅" if status == 'PASS' else "❌" if status == 'FAIL' else "⚠️"
                                    else:
                                        status_icon = "❓"
                                    with st.expander(f"{status_icon} {category.replace('_', ' ').title()}"):
                                        st.json(result)
                            
                            if 'pdf_path' in results:
                                pdf_path = Path(results['pdf_path'])
                                if pdf_path.exists():
                                    with open(pdf_path, 'rb') as f:
                                        st.download_button(
                                            "📄 Download PDF Report",
                                            data=f.read(),
                                            file_name=pdf_path.name,
                                            mime="application/pdf"
                                        )
    
    # Tab 2: Performance Testing
    with tab2:
        st.markdown("### Performance Monitoring & Core Web Vitals")
        st.info("Measure page load times, Core Web Vitals (LCP, FID, CLS), resource loading, and system metrics")
        
        if st.button("⚡ Run Performance Tests", type="primary", use_container_width=True, key="perf_button"):
            if not url.strip():
                st.error("❌ Please enter a valid URL")
            else:
                test_url = url if url.startswith(('http://', 'https://')) else f"https://{url}"
                
                async def run_perf_test():
                    browser_config = BrowserConfig(headless=headless)
                    browser = Browser(config=browser_config)
                    context = await browser.new_context()
                    page = await context.get_current_page()
                    try:
                        await page.goto(test_url, timeout=30000)
                    except Exception as nav_err:
                        await browser.close()
                        raise nav_err
                    
                    monitor = PerformanceMonitor(page)
                    results = await monitor.run_all_tests()
                    
                    await browser.close()
                    return results
                
                with st.spinner("⚡ Running performance tests..."):
                    coro = None
                    perf_results = None
                    try:
                        coro = run_perf_test()
                        perf_results = run_async(coro)
                        st.success("✅ Performance tests completed!")
                    except Exception as e:
                        error_msg = str(e).lower()
                        if 'net::err_name_not_resolved' in error_msg or 'dns' in error_msg:
                            st.error("❌ DNS Error: Cannot reach the website. Check the URL and your connection.")
                        else:
                            st.error(f"❌ Performance tests failed: {str(e)}")
                        if coro and hasattr(coro, 'close'):
                            coro.close()
                    
                    # Display metrics if available
                    if perf_results and 'performance_metrics' in perf_results:
                        col1, col2, col3, col4 = st.columns(4)
                        metrics = perf_results['performance_metrics']
                        col1.metric("TTFB", f"{metrics.get('ttfb', 0):.0f}ms")
                        col2.metric("Load Time", f"{metrics.get('load_complete', 0):.0f}ms")
                        col3.metric("DNS Lookup", f"{metrics.get('dns_lookup', 0):.0f}ms")
                        col4.metric("TCP Connect", f"{metrics.get('tcp_connect', 0):.0f}ms")
                        st.json(perf_results)
    
    # Tab 3: SEO Analysis
    with tab3:
        st.markdown("### SEO Analysis & Optimization")
        st.info("Check meta tags, Open Graph, structured data, robots.txt, sitemap, and heading structure")
        
        if st.button("🔍 Run SEO Analysis", type="primary", use_container_width=True, key="seo_button"):
            if not url.strip():
                st.error("❌ Please enter a valid URL")
            else:
                test_url = url if url.startswith(('http://', 'https://')) else f"https://{url}"
                
                async def run_seo_test():
                    browser_config = BrowserConfig(headless=headless)
                    browser = Browser(config=browser_config)
                    context = await browser.new_context()
                    page = await context.get_current_page()
                    try:
                        await page.goto(test_url, timeout=30000)
                    except Exception as nav_err:
                        await browser.close()
                        raise nav_err
                    
                    analyzer = SEOAnalyzer(test_url, page)
                    results = await analyzer.run_all_checks()
                    
                    await browser.close()
                    return results
                
                with st.spinner("🔍 Running SEO analysis..."):
                    coro = None
                    try:
                        coro = run_seo_test()
                        seo_results = run_async(coro)
                        st.success("✅ SEO analysis completed!")
                        st.json(seo_results)
                    except Exception as e:
                        error_msg = str(e).lower()
                        if 'net::err_name_not_resolved' in error_msg or 'dns' in error_msg:
                            st.error("❌ DNS Error: Cannot reach the website. Check the URL and your connection.")
                        else:
                            st.error(f"❌ SEO analysis failed: {str(e)}")
                        if coro and hasattr(coro, 'close'):
                            coro.close()
    
    # Tab 4: Visual Regression Testing
    with tab4:
        st.markdown("### Visual Regression Testing")
        st.info("Capture screenshots, compare with baselines, detect visual differences")
        
        create_baseline = st.checkbox("Create new baseline", value=False, key="vis_baseline")
        threshold = st.slider("Difference threshold (%)", 0.0, 5.0, 0.1, key="vis_threshold")
        
        if st.button("👁️ Run Visual Tests", type="primary", use_container_width=True, key="vis_button"):
            if not url.strip():
                st.error("❌ Please enter a valid URL")
            else:
                test_url = url if url.startswith(('http://', 'https://')) else f"https://{url}"
                async def run_visual_test():
                    browser_config = BrowserConfig(headless=headless)
                    browser = Browser(config=browser_config)
                    context = await browser.new_context()
                    page = await context.get_current_page()
                    try:
                        await page.goto(test_url, timeout=30000)
                    except Exception as nav_err:
                        await browser.close()
                        raise nav_err
                    
                    tester = VisualTester(page)
                    results = await tester.run_all_tests(
                        name='visual_test',
                        create_baseline=create_baseline,
                        threshold=threshold
                    )
                    
                    await browser.close()
                    return results
                
                with st.spinner("📸 Running visual tests..."):
                    coro = None
                    try:
                        coro = run_visual_test()
                        visual_results = run_async(coro)
                        st.success("✅ Visual tests completed!")
                        st.json(visual_results)
                    except Exception as e:
                        error_msg = str(e).lower()
                        if 'net::err_name_not_resolved' in error_msg or 'dns' in error_msg:
                            st.error("❌ DNS Error: Cannot reach the website. Check the URL and your connection.")
                        else:
                            st.error(f"❌ Visual tests failed: {str(e)}")
                        if coro and hasattr(coro, 'close'):
                            coro.close()
    
    # Tab 5: API Testing
    with tab5:
        st.markdown("### API Testing")
        st.info("Test REST endpoints, validate responses, check authentication")
        
        api_base_url = st.text_input("API Base URL", placeholder="https://api.example.com", key="api_url")
        
        st.markdown("#### Endpoints to Test")
        endpoint_input = st.text_area(
            "Endpoints (JSON format)",
            placeholder='[{"endpoint": "/users", "method": "GET", "expected_status": 200}]',
            height=150,
            key="api_endpoints"
        )
        
        if st.button("🔌 Run API Tests", type="primary", use_container_width=True, key="api_button"):
            if not api_base_url.strip():
                st.error("❌ Please enter API base URL")
            else:
                try:
                    endpoints = json.loads(endpoint_input) if endpoint_input else [{"endpoint": "/", "method": "GET"}]
                    
                    with st.spinner("🔌 Running API tests..."):
                        tester = APITester(api_base_url)
                        api_results = tester.run_all_tests(endpoints=endpoints)
                        
                        st.success("✅ API tests completed!")
                        st.json(api_results)
                except (ValueError, TypeError, RuntimeError) as e:
                    st.error(f"❌ Error: {e}")
    
    # Tab 6: Database Testing
    with tab6:
        st.markdown("### Database Testing")
        st.info("Test database connections, query performance, data integrity")
        
        db_type = st.selectbox("Database Type", ["postgresql", "mysql", "mongodb", "sqlite", "redis"], key="db_type")
        
        col1, col2 = st.columns(2)
        with col1:
            db_host = st.text_input("Host", value="localhost", key="db_host")
            db_port = st.number_input("Port", value=5432, key="db_port")
        with col2:
            db_name = st.text_input("Database Name", key="db_name")
            db_user = st.text_input("Username", key="db_user")
        
        db_password = st.text_input("Password", type="password", key="db_password")
        
        test_query = st.text_input("Test Query", placeholder="SELECT * FROM users LIMIT 10", key="db_query")
        
        if st.button("🗄️ Run Database Tests", type="primary", use_container_width=True, key="db_button"):
            if not all([db_host, db_name]):
                st.error("❌ Please fill in required database fields")
            else:
                try:
                    db_config = {
                        'type': db_type,
                        'host': db_host,
                        'port': db_port,
                        'database': db_name,
                        'user': db_user,
                        'password': db_password
                    }
                    
                    with st.spinner("🗄️ Running database tests..."):
                        tester = DatabaseTester(db_config)
                        db_results = tester.run_all_tests(
                            test_query=test_query if test_query else None
                        )
                        tester.close()
                        
                        st.success("✅ Database tests completed!")
                        st.json(db_results)
                except (ValueError, TypeError, RuntimeError, ConnectionError) as e:
                    st.error(f"❌ Error: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    💡 **Tips:** 
    - Use tabs to access different testing modules
    - Keep headless OFF to watch the browser automation
    - Export results as JSON for further analysis
    - Use visual baselines for regression testing
    
    🔒 **Privacy:** All testing runs locally. Database credentials are not stored.
    """)


# Run the main app when script is executed directly
if __name__ == "__main__":
    main()
