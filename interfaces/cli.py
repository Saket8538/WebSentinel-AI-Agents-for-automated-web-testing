"""
WebSentinel CLI - Command Line Interface for Power Users
Production-ready CLI with advanced features
"""
import asyncio
import argparse
import sys
import os
import json
from pathlib import Path
from datetime import datetime
import yaml
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich import box

# Add project root to sys.path so local packages (browser_use, utils, core) resolve
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
os.chdir(str(_PROJECT_ROOT))

from browser_use.agent.service import Agent
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContextConfig
from utils.model_provider import get_llm
from core.comprehensive_tester import ComprehensiveTester
from core.ultra_pdf_generator import UltraEnhancedPDFGenerator
from core.ai_analyzer import AIAnalyzer

load_dotenv()
console = Console()


class WebSentinelCLI:
    """Command-line interface for WebSentinel"""
    
    def __init__(self):
        self.config = self.load_config()
        
    def load_config(self):
        """Load configuration"""
        try:
            with open('configs/config.yaml', 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            console.print(f"[yellow]⚠️ Warning: Could not load config: {e}[/yellow]")
            return {'llm': {'provider': 'google', 'model': 'gemini-2.5-flash'}}
    
    def create_llm(self):
        """Create LLM instance using centralized provider"""
        llm_config = self.config.get('llm', {})
        provider = llm_config.get('provider', 'auto')
        model = llm_config.get('model', '') or None
        
        return get_llm(
            provider=provider if provider != 'auto' else None,
            model=model
        )
    
    async def test_url(self, url: str, task: str = "", headless: bool = True, 
                       comprehensive: bool = True, output_format: str = "all"):
        """Test a URL with comprehensive testing"""
        
        console.print(Panel.fit(
            f"[bold cyan]WebSentinel CLI - Testing {url}[/bold cyan]",
            border_style="cyan"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Setup browser
            task_id = progress.add_task("🚀 Setting up browser...", total=None)
            browser_config = BrowserConfig(
                headless=headless,
                chrome_remote_debugging_port=9222,
                extra_browser_args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage'
                ]
            )
            browser = Browser(config=browser_config)
            context = await browser.new_context(config=BrowserContextConfig())
            progress.update(task_id, description="✅ Browser ready")
            
            # Navigate
            progress.update(task_id, description=f"🌐 Opening {url}...")
            page = await context.get_current_page()
            try:
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            except Exception as nav_error:
                error_str = str(nav_error).lower()
                if 'net::err_name_not_resolved' in error_str or 'dns' in error_str:
                    progress.update(task_id, description="❌ DNS Error")
                    console.print(f"[red]❌ DNS Error: Cannot reach {url}. Check the URL and your internet connection.[/red]")
                elif 'timeout' in error_str or 'net::err_timed_out' in error_str:
                    progress.update(task_id, description="❌ Timeout")
                    console.print(f"[red]❌ Connection timed out for {url}[/red]")
                else:
                    progress.update(task_id, description="❌ Navigation failed")
                    console.print(f"[red]❌ Failed to open {url}: {nav_error}[/red]")
                await context.close()
                await browser.close()
                return
            progress.update(task_id, description=f"✅ Opened {url}")
            
            # Run AI agent task
            agent_logs = []

            if task:
                progress.update(task_id, description="🤖 Running AI agent...")
                llm = self.create_llm()
                agent_config = self.config.get('agent', {})
                
                agent = Agent(
                    task=task,
                    llm=llm,
                    browser_context=context,
                    max_steps=agent_config.get('max_steps', 25)
                )
                result = await agent.run()
                progress.update(task_id, description="✅ AI agent completed")
                final_result = result.final_result()
                console.print(f"[green]AI Result: {final_result}[/green]")
                if final_result:
                    agent_logs.append(f"AI task outcome: {final_result}")
                agent_logs.append(f"Requested task: {task}")
            
            # Run comprehensive tests
            if comprehensive:
                progress.update(task_id, description="🔬 Running comprehensive tests...")
                tester = ComprehensiveTester(url, context)
                results = await tester.run_all_tests()
                if task:
                    results['task_description'] = task
                if agent_logs:
                    results['agent_logs'] = agent_logs
                progress.update(task_id, description="✅ Tests completed")
                
                # Display results
                self.display_results(results)
                
                # Save outputs
                if output_format in ["json", "all"]:
                    json_path = tester.save_results('test_results')
                    console.print(f"[green]✅ JSON saved: {json_path}[/green]")
                
                if output_format in ["pdf", "all"]:
                    progress.update(task_id, description="🤖 Analyzing with AI...")
                    
                    # Get AI insights
                    ai_insights = None
                    try:
                        analyzer = AIAnalyzer()
                        ai_insights = await analyzer.analyze_results(results)
                        if ai_insights:
                            console.print("[green]✅ AI analysis complete[/green]")
                    except Exception as e:
                        console.print(f"[yellow]⚠️ AI analysis unavailable: {e}[/yellow]")
                    
                    progress.update(task_id, description="📄 Generating enhanced PDF...")
                    screenshots_dir = Path("agent_screenshots")
                    pdf_generator = UltraEnhancedPDFGenerator(
                        results=results,
                        screenshots_dir=str(screenshots_dir) if screenshots_dir.exists() else None,
                        ai_insights=ai_insights
                    )
                    pdf_path = pdf_generator.generate()
                    progress.update(task_id, description="✅ Enhanced PDF generated")
                    console.print(f"[green]✅ Enhanced PDF saved: {pdf_path}[/green]")
            
            # Cleanup
            await context.close()
            await browser.close()
        
        console.print("\n[bold green]✅ Testing complete![/bold green]")
    
    def display_results(self, results: dict):
        """Display test results in a table"""
        table = Table(title="Test Results", box=box.ROUNDED)
        table.add_column("Test", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Message", style="white")
        
        status_colors = {
            "PASS": "green",
            "WARNING": "yellow",
            "FAIL": "red"
        }
        
        for test_name, result in results.get('tests', {}).items():
            status = result.get('status', 'UNKNOWN')
            color = status_colors.get(status, "white")
            message = result.get('message', '')
            
            table.add_row(
                test_name,
                f"[{color}]{status}[/{color}]",
                message
            )
        
        console.print(table)
        
        overall = results.get('overall_status', 'UNKNOWN')
        color = status_colors.get(overall, "white")
        console.print(f"\n[bold]Overall Status: [{color}]{overall}[/{color}][/bold]")
    
    async def batch_test(self, urls_file: str, headless: bool = True):
        """Test multiple URLs from a file"""
        console.print(Panel.fit(
            "[bold cyan]WebSentinel CLI - Batch Testing[/bold cyan]",
            border_style="cyan"
        ))
        
        # Read URLs
        with open(urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        console.print(f"[cyan]Found {len(urls)} URLs to test[/cyan]\n")
        
        results_summary = []
        
        for i, url in enumerate(urls, 1):
            console.print(f"\n[bold]Testing {i}/{len(urls)}: {url}[/bold]")
            try:
                await self.test_url(url, headless=headless, comprehensive=True)
                results_summary.append((url, "✅ Success"))
            except Exception as e:
                console.print(f"[red]❌ Error: {e}[/red]")
                results_summary.append((url, f"❌ Failed: {str(e)}"))
        
        # Display summary
        console.print("\n" + "=" * 60)
        console.print("[bold cyan]Batch Testing Summary[/bold cyan]")
        console.print("=" * 60)
        for url, status in results_summary:
            console.print(f"{status} - {url}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="WebSentinel CLI - Comprehensive Web Testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test a single URL
  python cli.py test https://example.com
  
  # Test with AI agent task
  python cli.py test https://example.com --task "Test login form"
  
  # Test with visible browser
  python cli.py test https://example.com --no-headless
  
  # Generate only PDF report
  python cli.py test https://example.com --output pdf
  
  # Batch test multiple URLs
  python cli.py batch urls.txt
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test a single URL')
    test_parser.add_argument('url', help='URL to test')
    test_parser.add_argument('--task', default='', help='AI agent task description')
    test_parser.add_argument('--no-headless', action='store_true', help='Show browser window')
    test_parser.add_argument('--no-tests', action='store_true', help='Skip comprehensive tests')
    test_parser.add_argument('--output', choices=['json', 'pdf', 'all'], default='all', 
                            help='Output format')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Test multiple URLs from file')
    batch_parser.add_argument('file', help='File containing URLs (one per line)')
    batch_parser.add_argument('--no-headless', action='store_true', help='Show browser window')
    
    # Version command
    subparsers.add_parser('version', help='Show version information')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    cli = WebSentinelCLI()
    
    if args.command == 'test':
        asyncio.run(cli.test_url(
            args.url,
            task=args.task,
            headless=not args.no_headless,
            comprehensive=not args.no_tests,
            output_format=args.output
        ))
    
    elif args.command == 'batch':
        asyncio.run(cli.batch_test(
            args.file,
            headless=not args.no_headless
        ))
    
    elif args.command == 'version':
        console.print("[bold cyan]WebSentinel CLI v1.0.0[/bold cyan]")
        console.print("Production-ready web testing with AI-powered automation")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        sys.exit(1)
