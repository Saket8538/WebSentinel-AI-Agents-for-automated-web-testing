"""
Interactive Web Testing Agent
User-friendly CLI for comprehensive web testing with AI-powered analysis and PDF reports
Like Comet browser agent but with advanced testing capabilities
"""
import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from urllib.parse import urlparse
import yaml

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich import box
import sys

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


console = Console()


class InteractiveWebAgent:
    """Interactive web testing agent with Comet-style interface"""
    
    def __init__(self, config_path='configs/config.yaml'):
        load_dotenv()
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.browser = None
        self.context = None
        self.test_url = None
        self.test_results = {}
        self.screenshots_dir = None
        self.agent_task_result = None
        self.current_task_description = ""
        self.agent_logs = []
    
    def display_banner(self):
        """Display welcome banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         🌐 Interactive Web Testing Agent 🌐                 ║
║                                                              ║
║     AI-Powered Browser Testing & Analysis Platform          ║
║     Like Comet Agent with Comprehensive Testing             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
        console.print(Panel(banner, border_style="cyan", box=box.DOUBLE))
    
    def get_user_input(self) -> Dict[str, Any]:
        """Get testing parameters from user"""
        console.print("\n[bold cyan]📝 Test Configuration[/bold cyan]\n")
        
        # Get URL
        while True:
            url = Prompt.ask("[cyan]Enter the URL to test[/cyan]", default="https://example.com")
            
            # Validate URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            try:
                parsed = urlparse(url)
                if parsed.netloc:
                    self.test_url = url
                    console.print(f"[green]✓[/green] URL validated: {url}")
                    break
                else:
                    console.print("[red]✗[/red] Invalid URL format. Please try again.")
            except:
                console.print("[red]✗[/red] Invalid URL. Please try again.")
        
        # Get test description
        console.print("\n[cyan]What should the AI agent test?[/cyan]")
        console.print("[dim]Examples:[/dim]")
        console.print("[dim]  - Test the login functionality[/dim]")
        console.print("[dim]  - Navigate through the website and check all pages[/dim]")
        console.print("[dim]  - Test the contact form and verify submission[/dim]")
        
        task_description = Prompt.ask(
            "\n[cyan]AI Testing Task[/cyan]",
            default="Thoroughly explore this website, test all major features, links, and functionality"
        )
        
        # Test options
        console.print("\n[bold cyan]🧪 Test Options[/bold cyan]\n")
        
        run_comprehensive = Confirm.ask(
            "[cyan]Run comprehensive automated tests?[/cyan] (links, forms, responsive, security, accessibility)",
            default=True
        )
        
        generate_pdf = Confirm.ask(
            "[cyan]Generate PDF report?[/cyan]",
            default=True
        )
        
        headless = Confirm.ask(
            "[cyan]Run browser in headless mode?[/cyan] (faster but no visual feedback)",
            default=False
        )
        
        return {
            'url': self.test_url,
            'task_description': task_description,
            'run_comprehensive': run_comprehensive,
            'generate_pdf': generate_pdf,
            'headless': headless
        }
    
    def create_llm(self):
        """Create LLM instance based on configuration"""
        llm_config = self.config['llm']
        provider = llm_config.get('provider', 'auto')
        model = llm_config.get('model', '') or None
        
        return get_llm(
            provider=provider if provider != 'auto' else None,
            model=model,
            temperature=llm_config.get('temperature', 0.7),
            max_tokens=llm_config.get('max_tokens', 1000)
        )
    
    async def setup_browser(self, headless: bool = False):
        """Initialize browser and context"""
        console.print("\n[cyan]🌐 Initializing browser...[/cyan]")
        
        browser_config = self.config['browser'].copy()
        browser_config['headless'] = headless
        
        context_config = self.config['context']
        
        browser_cfg = BrowserConfig(
            headless=browser_config['headless'],
            use_test_profile=browser_config['use_test_profile'],
            test_profile_name=browser_config['test_profile_name'],
            extra_browser_args=browser_config['extra_browser_args'],
        )
        
        context_cfg = BrowserContextConfig(
            disable_security=context_config['disable_security'],
            cookies_file=context_config.get('cookies_file'),
            user_agent=context_config.get('user_agent'),
            permissions=context_config.get('permissions', []),
            allowed_domains=context_config.get('allowed_domains'),
        )
        
        try:
            self.browser = Browser(config=browser_cfg)
            self.context = await self.browser.new_context(config=context_cfg)
        except Exception as e:
            console.print(f"[red]✗ Failed to initialize browser: {e}[/red]")
            console.print("[yellow]  Tip: Make sure all Chrome windows are closed, then try again.[/yellow]")
            raise
        
        console.print("[green]✓[/green] Browser ready")
    
    async def run_ai_agent_task(self, task_description: str):
        """Run AI agent task"""
        self.current_task_description = task_description.strip()
        self.agent_logs = []
        console.print(f"\n[bold cyan]🤖 AI Agent Analysis[/bold cyan]")
        console.print(Panel(
            f"[white]{task_description}[/white]",
            title="Task",
            border_style="cyan"
        ))
        
        agent_config = self.config['agent']
        llm = self.create_llm()
        
        # Create task name
        task_name = f"interactive_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            agent = Agent(
                task=f"{task_description}\n\nURL to test: {self.test_url}",
                llm=llm,
                task_name=task_name,
                browser=self.browser,
                browser_context=self.context,
                max_failures=agent_config.get('max_failures', 3),
                retry_delay=agent_config.get('retry_delay', 10),
                use_vision=agent_config.get('use_vision', True),
                enable_memory=agent_config.get('enable_memory', True),
                max_actions_per_step=agent_config.get('max_actions_per_step', 10)
            )
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                console=console
            ) as progress:
                task_id = progress.add_task(
                    f"[cyan]AI agent working...",
                    total=None
                )
                
                result = await agent.run(max_steps=agent_config['max_steps'])
                progress.update(task_id, completed=True)
            
            console.print("[green]✓[/green] AI agent completed task")
            
            # Store screenshot directory
            self.screenshots_dir = Path("agent_screenshots") / f"agent_screenshots_{task_name}"
            self.agent_task_result = result
            try:
                if hasattr(result, 'final_result'):
                    final_result = result.final_result()
                    if final_result:
                        self.agent_logs.append(f"AI task outcome: {final_result}")
            except Exception:
                pass
            self.agent_logs.append(f"AI task executed for URL: {self.test_url}")
            self.agent_logs.append(f"Requested task: {self.current_task_description}")
            
            return result
            
        except Exception as e:
            console.print(f"[red]✗[/red] AI agent error: {e}")
            return None
    
    async def run_comprehensive_tests(self):
        """Run comprehensive automated tests"""
        console.print(f"\n[bold cyan]🔬 Comprehensive Testing Suite[/bold cyan]\n")
        
        tester = ComprehensiveTester(self.test_url, self.context)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task_id = progress.add_task("[cyan]Running comprehensive tests...", total=None)
            
            results = await tester.run_all_tests()
            
            progress.update(task_id, completed=True)
        
        # Save results
        results_file = tester.save_results()
        
        self.test_results = results
        self.test_results['task_description'] = self.current_task_description
        if self.agent_logs:
            self.test_results['agent_logs'] = list(self.agent_logs)
        console.print(f"[green]✓[/green] Comprehensive tests completed")
        
        return results
    
    def display_summary(self):
        """Display test summary"""
        console.print(f"\n[bold cyan]{'='*80}[/bold cyan]")
        console.print(Panel.fit(
            "[bold white]📊 Test Summary[/bold white]",
            border_style="cyan"
        ))
        
        if not self.test_results:
            console.print("[yellow]⚠[/yellow] No test results available")
            return
        
        # Create summary table
        table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
        table.add_column("Test Category", style="white")
        table.add_column("Status", justify="center")
        table.add_column("Details")
        
        tests = self.test_results.get('tests', {})
        
        test_names = {
            'page_load': '📊 Page Load',
            'links': '🔗 Links',
            'forms': '📝 Forms',
            'responsive': '📱 Responsive',
            'security': '🔒 Security',
            'accessibility': '♿ Accessibility',
            'console_errors': '🐛 Console'
        }
        
        for test_key, test_result in tests.items():
            status = test_result.get('status', 'FAIL')
            message = test_result.get('message', 'No details')
            
            # Color-code status
            if status == 'PASS':
                status_display = "[green]✓ PASS[/green]"
            elif status == 'FAIL':
                status_display = "[red]✗ FAIL[/red]"
            else:
                status_display = "[yellow]⚠ WARN[/yellow]"
            
            table.add_row(
                test_names.get(test_key, test_key),
                status_display,
                message
            )
        
        console.print(table)
        
        # Overall status
        overall = self.test_results.get('overall_status', 'FAIL')
        if overall == 'PASS':
            console.print(f"\n[bold green]✓ Overall Status: PASS[/bold green]")
        elif overall == 'FAIL':
            console.print(f"\n[bold red]✗ Overall Status: FAIL[/bold red]")
        else:
            console.print(f"\n[bold yellow]⚠ Overall Status: WARNING[/bold yellow]")
    
    async def generate_pdf_report(self):
        """Generate PDF report"""
        console.print(f"\n[cyan]📄 Analyzing results with AI...[/cyan]")
        
        try:
            # AI Analysis
            ai_analyzer = AIAnalyzer()
            ai_insights = await ai_analyzer.analyze_results(self.test_results)
            
            console.print(f"[green]✓[/green] AI analysis complete")
            console.print(f"\n[cyan]📄 Generating enhanced PDF report...[/cyan]")
            
            generator = UltraEnhancedPDFGenerator(
                results=self.test_results,
                screenshots_dir=str(self.screenshots_dir) if self.screenshots_dir else None,
                ai_insights=ai_insights
            )
            
            pdf_path = generator.generate()
            
            console.print(f"[green]✓[/green] Enhanced PDF report generated: [cyan]{pdf_path}[/cyan]")
            return pdf_path
            
        except Exception as e:
            console.print(f"[red]✗[/red] PDF generation failed: {e}")
            return None
    
    async def cleanup(self):
        """Cleanup browser resources"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        console.print("\n[green]✓[/green] Browser closed")
    
    async def run(self):
        """Main execution flow"""
        try:
            # Display banner
            self.display_banner()
            
            # Get user input
            config = self.get_user_input()
            
            # Setup browser
            await self.setup_browser(headless=config['headless'])
            
            # Run AI agent task
            console.print(f"\n[bold cyan]{'='*80}[/bold cyan]")
            await self.run_ai_agent_task(config['task_description'])
            
            # Run comprehensive tests if requested
            if config['run_comprehensive']:
                console.print(f"\n[bold cyan]{'='*80}[/bold cyan]")
                await self.run_comprehensive_tests()
            
            # Display summary
            if self.test_results:
                self.display_summary()
            
            # Generate PDF if requested
            if config['generate_pdf'] and self.test_results:
                pdf_path = await self.generate_pdf_report()
            
            # Final message
            console.print(f"\n[bold cyan]{'='*80}[/bold cyan]")
            console.print(Panel.fit(
                "[bold green]✓ Testing Complete![/bold green]\n\n"
                "[white]Check the following locations:[/white]\n"
                f"  • Screenshots: [cyan]agent_screenshots/[/cyan]\n"
                f"  • Logs: [cyan]agent_logs/[/cyan]\n"
                f"  • Test Results: [cyan]test_results/[/cyan]\n"
                f"  • PDF Reports: [cyan]reports/[/cyan]",
                border_style="green",
                title="🎉 Success"
            ))
            
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠ Testing interrupted by user[/yellow]")
        except Exception as e:
            console.print(f"\n[red]✗ Error: {e}[/red]")
            import traceback
            traceback.print_exc()
        finally:
            await self.cleanup()


async def main():
    """Entry point"""
    agent = InteractiveWebAgent()
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
