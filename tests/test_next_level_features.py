"""
Comprehensive Test Suite for Next-Level Features
Tests all new AI-powered modules:
- Visual Regression Testing
- Security Scanner
- Accessibility Analyzer
- Performance Predictor
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn

from core.visual_regression import VisualRegressionTester
from core.security_scanner import SecurityScanner
from core.accessibility_analyzer import AccessibilityAnalyzer
from core.performance_predictor import PerformancePredictor

console = Console()


class NextLevelFeatureTester:
    """Test all next-level AI features"""
    
    def __init__(self):
        self.test_results = []
        self.output_dir = Path("test_outputs/next_level_tests")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def test_visual_regression(self):
        """Test Visual Regression module"""
        console.print("\n[bold cyan]Testing Visual Regression Module...[/bold cyan]")
        
        try:
            # Create tester instance
            tester = VisualRegressionTester(baseline_dir=str(self.output_dir / "baselines"))
            
            # Mock screenshot data (in real scenario, this comes from browser)
            mock_screenshot = b"fake_image_data_baseline"
            
            # Capture baseline (NOT async)
            tester.capture_baseline("test_page", mock_screenshot)
            console.print("[green]✓[/green] Baseline captured successfully")
            
            # Compare with same screenshot (should be identical) (NOT async)
            result1 = tester.compare_with_baseline("test_page", mock_screenshot)
            assert result1["passed"], "Identical screenshots should match"
            console.print(f"[green]✓[/green] Baseline comparison: {result1['difference_percentage']}% difference")
            
            # Compare with different screenshot
            mock_screenshot_changed = b"fake_image_data_different"
            result2 = tester.compare_with_baseline("test_page", mock_screenshot_changed)
            console.print(f"[yellow]●[/yellow] Changed screenshot: {result2['difference_percentage']}% difference")
            
            # Export report
            report_path = self.output_dir / "visual_regression_report.json"
            tester.export_report(str(report_path))
            console.print(f"[green]✓[/green] Report exported to {report_path}")
            
            self.test_results.append({
                "module": "Visual Regression",
                "status": "PASSED",
                "details": "Baseline capture and comparison working correctly"
            })
            
            return True
            
        except Exception as e:
            console.print(f"[red]✗[/red] Visual Regression test failed: {e}")
            self.test_results.append({
                "module": "Visual Regression",
                "status": "FAILED",
                "error": str(e)
            })
            return False
    
    async def test_security_scanner(self):
        """Test Security Scanner module"""
        console.print("\n[bold cyan]Testing Security Scanner Module...[/bold cyan]")
        
        try:
            # Create scanner instance
            scanner = SecurityScanner()
            
            # Mock page content with security issues
            mock_content = """
            <html>
                <head><title>Test Page</title></head>
                <body>
                    <script>alert('xss')</script>
                    <form method="GET">
                        <input name="query" />
                    </form>
                    <div onclick="malicious()">Click me</div>
                    <img src="http://example.com/image.jpg" />
                    <p>Contact: user@example.com</p>
                    <p>SSN: 123-45-6789</p>
                </body>
            </html>
            """
            
            # Mock response headers (insecure)
            mock_headers = {
                "content-type": "text/html"
            }
            
            # Mock cookies (insecure)
            mock_cookies = [
                {"name": "session", "value": "abc123", "secure": False, "httpOnly": False}
            ]
            
            # Run comprehensive scan
            results = await scanner.run_comprehensive_scan(
                url="http://example.com",
                page_content=mock_content,
                response_headers=mock_headers,
                cookies=mock_cookies
            )
            
            console.print(f"[cyan]Security Score:[/cyan] {results['security_score']}/100")
            console.print(f"[cyan]Risk Level:[/cyan] {results['risk_level']}")
            console.print(f"[cyan]Vulnerabilities Found:[/cyan] {results['total_vulnerabilities']}")
            
            # Display findings table
            if results["vulnerabilities"]:
                table = Table(title="Security Findings", box=box.ROUNDED)
                table.add_column("Category", style="cyan")
                table.add_column("Severity", style="yellow")
                table.add_column("CVSS", style="red")
                
                for vuln in results["vulnerabilities"][:5]:  # Show first 5
                    table.add_row(
                        vuln["owasp_category"],
                        vuln["severity"],
                        str(vuln["cvss_score"])
                    )
                
                console.print(table)
            
            # Export report
            report_path = self.output_dir / "security_scan_report.json"
            with open(report_path, 'w') as f:
                json.dump(results, f, indent=2)
            console.print(f"[green]✓[/green] Report exported to {report_path}")
            
            self.test_results.append({
                "module": "Security Scanner",
                "status": "PASSED",
                "details": f"Found {results['total_vulnerabilities']} vulnerabilities, Score: {results['security_score']}"
            })
            
            return True
            
        except Exception as e:
            console.print(f"[red]✗[/red] Security Scanner test failed: {e}")
            self.test_results.append({
                "module": "Security Scanner",
                "status": "FAILED",
                "error": str(e)
            })
            return False
    
    async def test_accessibility_analyzer(self):
        """Test Accessibility Analyzer module"""
        console.print("\n[bold cyan]Testing Accessibility Analyzer Module...[/bold cyan]")
        
        try:
            # Create analyzer instance
            analyzer = AccessibilityAnalyzer()
            
            # Mock page content with accessibility issues
            mock_content = """
            <html>
                <head><title>Test</title></head>
                <body>
                    <img src="logo.png" />
                    <div style="color: #ccc; background: #ddd;">Low contrast text</div>
                    <form>
                        <input type="text" />
                        <input type="email" />
                    </form>
                </body>
            </html>
            """
            
            # Mock images without alt text
            mock_images = [
                {"src": "logo.png", "alt": ""},
                {"src": "banner.jpg", "alt": ""}
            ]
            
            # Mock forms with unlabeled inputs
            mock_forms = [
                {
                    "action": "/submit",
                    "inputs": [
                        {"type": "text", "name": "username", "label": ""},
                        {"type": "email", "name": "email", "label": ""}
                    ]
                }
            ]
            
            # Mock headings
            mock_headings = []  # No H1
            
            # Run analysis
            results = await analyzer.analyze_accessibility(
                page_content=mock_content,
                page_title="Test",
                images=mock_images,
                forms=mock_forms,
                headings=mock_headings
            )
            
            console.print(f"[cyan]Compliance Score:[/cyan] {results['compliance_score']}/100")
            console.print(f"[cyan]WCAG Level:[/cyan] {results['wcag_level']}")
            console.print(f"[cyan]Issues Found:[/cyan] {len(results['issues'])}")
            
            # Display issues table
            if results["issues"]:
                table = Table(title="Accessibility Issues", box=box.ROUNDED)
                table.add_column("WCAG SC", style="cyan")
                table.add_column("Level", style="yellow")
                table.add_column("Issue", style="white")
                table.add_column("Severity", style="red")
                
                for issue in results["issues"][:5]:  # Show first 5
                    table.add_row(
                        issue["wcag_sc"],
                        issue["level"],
                        issue["issue"][:50] + "...",
                        issue["severity"]
                    )
                
                console.print(table)
            
            # Show recommendations
            console.print("\n[bold]Recommendations:[/bold]")
            for rec in results["recommendations"][:3]:
                console.print(f"  {rec}")
            
            # Show affected users
            console.print(f"\n[bold]Affected Users:[/bold] {', '.join(results['affected_users'])}")
            
            # Export report
            report_path = self.output_dir / "accessibility_report.json"
            with open(report_path, 'w') as f:
                json.dump(results, f, indent=2)
            console.print(f"\n[green]✓[/green] Report exported to {report_path}")
            
            self.test_results.append({
                "module": "Accessibility Analyzer",
                "status": "PASSED",
                "details": f"Found {len(results['issues'])} issues, Score: {results['compliance_score']}"
            })
            
            return True
            
        except Exception as e:
            console.print(f"[red]✗[/red] Accessibility Analyzer test failed: {e}")
            self.test_results.append({
                "module": "Accessibility Analyzer",
                "status": "FAILED",
                "error": str(e)
            })
            return False
    
    async def test_performance_predictor(self):
        """Test Performance Predictor module"""
        console.print("\n[bold cyan]Testing Performance Predictor Module...[/bold cyan]")
        
        try:
            # Create predictor instance
            predictor = PerformancePredictor()
            
            # Mock current performance metrics
            current_metrics = {
                "page_load_time": 4.5,  # seconds
                "first_response_time": 800,  # ms
                "resource_count": 120,
                "page_size_kb": 2500
            }
            
            # Mock historical metrics (simulating degrading performance)
            historical_metrics = [
                {"page_load_time": 2.5, "first_response_time": 300, "resource_count": 50, "page_size_kb": 1000},
                {"page_load_time": 3.0, "first_response_time": 400, "resource_count": 70, "page_size_kb": 1500},
                {"page_load_time": 3.5, "first_response_time": 600, "resource_count": 90, "page_size_kb": 2000},
                {"page_load_time": 4.0, "first_response_time": 700, "resource_count": 110, "page_size_kb": 2300},
                {"page_load_time": 4.5, "first_response_time": 800, "resource_count": 120, "page_size_kb": 2500}
            ]
            
            # Run analysis
            results = await predictor.analyze_and_predict(
                current_metrics=current_metrics,
                historical_metrics=historical_metrics
            )
            
            console.print(f"[cyan]Performance Score:[/cyan] {results['performance_score']}/100")
            console.print(f"[cyan]Trend:[/cyan] {results['trend_analysis']['trend']}")
            console.print(f"[cyan]Prediction Confidence:[/cyan] {results['predictions']['confidence']}")
            
            # Display current performance
            console.print("\n[bold]Current Performance:[/bold]")
            for metric, data in results["current_performance"].items():
                status_color = "green" if data["status"] == "EXCELLENT" else "yellow" if data["status"] == "GOOD" else "red"
                console.print(f"  {metric}: {data['value']} - [{status_color}]{data['status']}[/{status_color}]")
            
            # Display predictions
            console.print("\n[bold]30-Day Predictions:[/bold]")
            pred = results["predictions"]["next_30_days"]
            console.print(f"  Load Time: {pred['load_time']['predicted']}s (current: {pred['load_time']['current']}s)")
            console.print(f"  Change: {pred['load_time']['change']}%")
            console.print(f"  Risk Level: {pred['risk_level']}")
            
            # Display bottlenecks
            if results["bottlenecks"]:
                console.print("\n[bold red]Bottlenecks Identified:[/bold red]")
                for bottleneck in results["bottlenecks"]:
                    console.print(f"  • {bottleneck['type']} ({bottleneck['severity']})")
                    console.print(f"    Value: {bottleneck['value']}, Threshold: {bottleneck['threshold']}")
            
            # Display top recommendations
            console.print("\n[bold]Top Recommendations:[/bold]")
            for rec in results["optimization_recommendations"][:3]:
                console.print(f"\n  [{rec['priority']}] {rec['title']}")
                console.print(f"  Category: {rec['category']}")
                console.print(f"  Expected Improvement: {rec['expected_improvement']}")
                console.print(f"  Effort: {rec['effort']}")
            
            # Export report
            report_path = self.output_dir / "performance_prediction_report.json"
            with open(report_path, 'w') as f:
                json.dump(results, f, indent=2)
            console.print(f"\n[green]✓[/green] Report exported to {report_path}")
            
            self.test_results.append({
                "module": "Performance Predictor",
                "status": "PASSED",
                "details": f"Score: {results['performance_score']}, Trend: {results['trend_analysis']['trend']}"
            })
            
            return True
            
        except Exception as e:
            console.print(f"[red]✗[/red] Performance Predictor test failed: {e}")
            self.test_results.append({
                "module": "Performance Predictor",
                "status": "FAILED",
                "error": str(e)
            })
            return False
    
    async def run_all_tests(self):
        """Run all next-level feature tests"""
        console.print(Panel.fit(
            "[bold cyan]WebSentinel Next-Level Features Test Suite[/bold cyan]\n"
            "Testing: Visual Regression, Security, Accessibility, Performance",
            title="Test Suite",
            border_style="cyan"
        ))
        
        start_time = datetime.now()
        
        # Run all tests
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Running tests...", total=4)
            
            await self.test_visual_regression()
            progress.advance(task)
            
            await self.test_security_scanner()
            progress.advance(task)
            
            await self.test_accessibility_analyzer()
            progress.advance(task)
            
            await self.test_performance_predictor()
            progress.advance(task)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Display summary
        self.display_summary(duration)
        
        # Save summary report
        self.save_summary_report()
    
    def display_summary(self, duration: float):
        """Display test summary"""
        console.print("\n" + "="*80)
        
        # Create summary table
        table = Table(title="Test Results Summary", box=box.ROUNDED, show_lines=True)
        table.add_column("Module", style="cyan", width=25)
        table.add_column("Status", style="white", width=15)
        table.add_column("Details", style="white", width=35)
        
        passed_count = 0
        failed_count = 0
        
        for result in self.test_results:
            status = result["status"]
            if status == "PASSED":
                status_display = "[green]✓ PASSED[/green]"
                passed_count += 1
            else:
                status_display = "[red]✗ FAILED[/red]"
                failed_count += 1
            
            details = result.get("details", result.get("error", ""))
            table.add_row(result["module"], status_display, details)
        
        console.print(table)
        
        # Overall summary
        total_tests = len(self.test_results)
        success_rate = (passed_count / total_tests * 100) if total_tests > 0 else 0
        
        summary_panel = Panel(
            f"[bold]Total Tests:[/bold] {total_tests}\n"
            f"[green]Passed:[/green] {passed_count}\n"
            f"[red]Failed:[/red] {failed_count}\n"
            f"[cyan]Success Rate:[/cyan] {success_rate:.1f}%\n"
            f"[cyan]Duration:[/cyan] {duration:.2f}s",
            title="Summary",
            border_style="green" if failed_count == 0 else "yellow"
        )
        
        console.print(summary_panel)
        
        if failed_count == 0:
            console.print("\n[bold green]🎉 All tests passed! Next-level features are working perfectly![/bold green]")
        else:
            console.print(f"\n[bold yellow]⚠️  {failed_count} test(s) failed. Please review the errors above.[/bold yellow]")
    
    def save_summary_report(self):
        """Save detailed summary report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_suite": "Next-Level Features",
            "results": self.test_results,
            "summary": {
                "total": len(self.test_results),
                "passed": sum(1 for r in self.test_results if r["status"] == "PASSED"),
                "failed": sum(1 for r in self.test_results if r["status"] == "FAILED")
            }
        }
        
        report_path = self.output_dir / "test_summary.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        console.print(f"\n[cyan]Full report saved to:[/cyan] {report_path}")


async def main():
    """Main test execution"""
    tester = NextLevelFeatureTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
