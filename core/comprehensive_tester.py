"""
Comprehensive Web Testing Module
Performs detailed testing of web applications including functionality, security, performance, and accessibility
"""
import asyncio
from datetime import datetime
from typing import Dict, Any
from pathlib import Path
import json
import re
from urllib.parse import urlparse

from browser_use.browser.context import BrowserContext
from rich.console import Console

console = Console()


class ComprehensiveTester:
    """Performs comprehensive testing on web applications"""
    
    def __init__(self, url: str, browser_context: BrowserContext):
        self.url = url
        self.context = browser_context
        self.results = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }
    
    async def test_page_load(self) -> Dict[str, Any]:
        """Test page load performance and basic functionality"""
        console.print("[cyan]📊 Testing page load performance...[/cyan]")
        
        page = await self.context.get_current_page()
        
        try:
            start_time = datetime.now()
            response = await page.goto(self.url, wait_until='networkidle', timeout=30000)
            load_time = (datetime.now() - start_time).total_seconds()
            
            # Get page metrics
            title = await page.title()
            status_code = response.status if response else None
            
            result = {
                'status': 'PASS' if status_code and status_code < 400 else 'FAIL',
                'load_time': load_time,
                'status_code': status_code,
                'page_title': title,
                'message': f"Page loaded in {load_time:.2f}s with status {status_code}"
            }
            
            console.print(f"   [green]✓[/green] Load time: {load_time:.2f}s (Status: {status_code})")
            return result
            
        except Exception as e:
            console.print(f"   [red]✗[/red] Page load failed: {e}")
            return {
                'status': 'FAIL',
                'error': str(e),
                'message': f"Failed to load page: {e}"
            }
    
    async def test_links(self) -> Dict[str, Any]:
        """Test all links on the page"""
        console.print("[cyan]🔗 Testing links...[/cyan]")
        
        page = await self.context.get_current_page()
        
        try:
            # Get all links
            links = await page.evaluate("""() => {
                return Array.from(document.querySelectorAll('a[href]'))
                    .map(a => ({
                        href: a.href,
                        text: a.textContent.trim(),
                        target: a.target
                    }));
            }""")
            
            total_links = len(links)
            internal_links = [l for l in links if urlparse(l['href']).netloc == urlparse(self.url).netloc or not urlparse(l['href']).netloc]
            external_links = [l for l in links if l not in internal_links]
            broken_links = []
            
            # Test internal links (sample up to 10)
            for link in internal_links[:10]:
                try:
                    response = await page.request.get(link['href'], timeout=5000)
                    if response.status >= 400:
                        broken_links.append({'url': link['href'], 'status': response.status})
                except (asyncio.TimeoutError, RuntimeError, ValueError):
                    broken_links.append({'url': link['href'], 'status': 'timeout'})
            
            result = {
                'status': 'PASS' if len(broken_links) == 0 else 'WARNING',
                'total_links': total_links,
                'internal_links': len(internal_links),
                'external_links': len(external_links),
                'broken_links': broken_links,
                'message': f"Found {total_links} links ({len(broken_links)} broken)"
            }
            
            console.print(f"   [green]✓[/green] Total: {total_links}, Internal: {len(internal_links)}, External: {len(external_links)}")
            if broken_links:
                console.print(f"   [yellow]⚠[/yellow] {len(broken_links)} broken link(s) detected")
            
            return result
            
        except Exception as e:
            console.print(f"   [red]✗[/red] Link testing failed: {e}")
            return {
                'status': 'FAIL',
                'error': str(e),
                'message': f"Link testing failed: {e}"
            }
    
    async def test_forms(self) -> Dict[str, Any]:
        """Test forms on the page"""
        console.print("[cyan]📝 Testing forms...[/cyan]")
        
        page = await self.context.get_current_page()
        
        try:
            forms = await page.evaluate("""() => {
                return Array.from(document.querySelectorAll('form')).map(form => ({
                    action: form.action,
                    method: form.method,
                    inputs: Array.from(form.querySelectorAll('input, textarea, select')).length,
                    hasSubmit: form.querySelector('button[type="submit"], input[type="submit"]') !== null
                }));
            }""")
            
            result = {
                'status': 'PASS' if len(forms) >= 0 else 'FAIL',
                'total_forms': len(forms),
                'forms': forms,
                'message': f"Found {len(forms)} form(s) on the page"
            }
            
            console.print(f"   [green]✓[/green] Found {len(forms)} form(s)")
            return result
            
        except Exception as e:
            console.print(f"   [red]✗[/red] Form testing failed: {e}")
            return {
                'status': 'FAIL',
                'error': str(e),
                'message': f"Form testing failed: {e}"
            }
    
    async def test_responsive_design(self) -> Dict[str, Any]:
        """Test responsive design across different viewports"""
        console.print("[cyan]📱 Testing responsive design...[/cyan]")
        
        page = await self.context.get_current_page()
        
        viewports = [
            {'name': 'Mobile', 'width': 375, 'height': 667},
            {'name': 'Tablet', 'width': 768, 'height': 1024},
            {'name': 'Desktop', 'width': 1920, 'height': 1080}
        ]
        
        viewport_results = []
        
        try:
            for viewport in viewports:
                await page.set_viewport_size({'width': viewport['width'], 'height': viewport['height']})
                await asyncio.sleep(1)  # Wait for reflow
                
                # Check if page renders without horizontal scroll
                has_horizontal_scroll = await page.evaluate("""() => {
                    return document.documentElement.scrollWidth > window.innerWidth;
                }""")
                
                viewport_results.append({
                    'name': viewport['name'],
                    'width': viewport['width'],
                    'height': viewport['height'],
                    'has_horizontal_scroll': has_horizontal_scroll,
                    'status': 'PASS' if not has_horizontal_scroll else 'WARNING'
                })
                
                status_icon = "[green]✓[/green]" if not has_horizontal_scroll else "[yellow]⚠[/yellow]"
                console.print(f"   {status_icon} {viewport['name']}: {viewport['width']}x{viewport['height']}")
            
            # Reset to desktop
            await page.set_viewport_size({'width': 1920, 'height': 1080})
            
            result = {
                'status': 'PASS' if all(v['status'] == 'PASS' for v in viewport_results) else 'WARNING',
                'viewports': viewport_results,
                'message': f"Tested {len(viewports)} viewport sizes"
            }
            
            return result
            
        except Exception as e:
            console.print(f"   [red]✗[/red] Responsive testing failed: {e}")
            return {
                'status': 'FAIL',
                'error': str(e),
                'message': f"Responsive testing failed: {e}"
            }
    
    async def test_security_headers(self) -> Dict[str, Any]:
        """Test security headers"""
        console.print("[cyan]🔒 Testing security headers...[/cyan]")
        
        page = await self.context.get_current_page()
        
        try:
            response = await page.goto(self.url, wait_until='networkidle')
            headers = response.headers if response else {}
            
            security_headers = {
                'X-Frame-Options': headers.get('x-frame-options'),
                'X-Content-Type-Options': headers.get('x-content-type-options'),
                'Strict-Transport-Security': headers.get('strict-transport-security'),
                'Content-Security-Policy': headers.get('content-security-policy'),
                'X-XSS-Protection': headers.get('x-xss-protection'),
            }
            
            missing_headers = [k for k, v in security_headers.items() if not v]
            
            result = {
                'status': 'WARNING' if len(missing_headers) > 2 else 'PASS',
                'headers': security_headers,
                'missing_headers': missing_headers,
                'message': f"{len(missing_headers)} security header(s) missing"
            }
            
            if missing_headers:
                console.print(f"   [yellow]⚠[/yellow] Missing: {', '.join(missing_headers)}")
            else:
                console.print("   [green]✓[/green] All key security headers present")
            
            return result
            
        except Exception as e:
            console.print(f"   [red]✗[/red] Security header testing failed: {e}")
            return {
                'status': 'FAIL',
                'error': str(e),
                'message': f"Security testing failed: {e}"
            }
    
    async def test_accessibility(self) -> Dict[str, Any]:
        """Test basic accessibility features"""
        console.print("[cyan]♿ Testing accessibility...[/cyan]")
        
        page = await self.context.get_current_page()
        
        try:
            accessibility_checks = await page.evaluate("""() => {
                const results = {
                    has_lang_attr: document.documentElement.hasAttribute('lang'),
                    images_with_alt: 0,
                    images_without_alt: 0,
                    has_heading_structure: document.querySelector('h1') !== null,
                    has_skip_link: document.querySelector('a[href^="#"]') !== null,
                    form_labels: 0,
                    form_inputs_without_labels: 0
                };
                
                // Check images
                const images = document.querySelectorAll('img');
                images.forEach(img => {
                    if (img.hasAttribute('alt')) {
                        results.images_with_alt++;
                    } else {
                        results.images_without_alt++;
                    }
                });
                
                // Check form labels
                const inputs = document.querySelectorAll('input:not([type="hidden"]), textarea, select');
                inputs.forEach(input => {
                    const id = input.id;
                    if (id && document.querySelector(`label[for="${id}"]`)) {
                        results.form_labels++;
                    } else if (!input.closest('label')) {
                        results.form_inputs_without_labels++;
                    }
                });
                
                return results;
            }""")
            
            issues = []
            if not accessibility_checks['has_lang_attr']:
                issues.append('Missing lang attribute on html tag')
            if accessibility_checks['images_without_alt'] > 0:
                issues.append(f"{accessibility_checks['images_without_alt']} images without alt text")
            if not accessibility_checks['has_heading_structure']:
                issues.append('No h1 heading found')
            if accessibility_checks['form_inputs_without_labels'] > 0:
                issues.append(f"{accessibility_checks['form_inputs_without_labels']} form inputs without labels")
            
            result = {
                'status': 'WARNING' if len(issues) > 0 else 'PASS',
                'checks': accessibility_checks,
                'issues': issues,
                'message': f"Found {len(issues)} accessibility issue(s)"
            }
            
            if issues:
                console.print(f"   [yellow]⚠[/yellow] Issues: {len(issues)}")
                for issue in issues[:3]:  # Show first 3
                    console.print(f"      • {issue}")
            else:
                console.print("   [green]✓[/green] Basic accessibility checks passed")
            
            return result
            
        except Exception as e:
            console.print(f"   [red]✗[/red] Accessibility testing failed: {e}")
            return {
                'status': 'FAIL',
                'error': str(e),
                'message': f"Accessibility testing failed: {e}"
            }
    
    async def test_console_errors(self) -> Dict[str, Any]:
        """Check for JavaScript console errors"""
        console.print("[cyan]🐛 Checking console errors...[/cyan]")
        
        page = await self.context.get_current_page()
        
        console_messages = []
        errors = []
        warnings = []
        
        def on_console_msg(msg):
            console_messages.append({
                'type': msg.type,
                'text': msg.text
            })
            if msg.type == 'error':
                errors.append(msg.text)
            elif msg.type == 'warning':
                warnings.append(msg.text)
        
        try:
            page.on('console', on_console_msg)
            await page.reload(wait_until='networkidle')
            await asyncio.sleep(2)  # Wait for console messages
            
            result = {
                'status': 'WARNING' if len(errors) > 0 else 'PASS',
                'total_messages': len(console_messages),
                'errors': errors[:10],  # First 10 errors
                'warnings': warnings[:10],  # First 10 warnings
                'message': f"Found {len(errors)} error(s) and {len(warnings)} warning(s) in console"
            }
            
            if errors:
                console.print(f"   [red]✗[/red] {len(errors)} console error(s)")
            elif warnings:
                console.print(f"   [yellow]⚠[/yellow] {len(warnings)} console warning(s)")
            else:
                console.print("   [green]✓[/green] No console errors")
            
            return result
            
        except Exception as e:
            console.print(f"   [red]✗[/red] Console error checking failed: {e}")
            return {
                'status': 'FAIL',
                'error': str(e),
                'message': f"Console error checking failed: {e}"
            }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all comprehensive tests"""
        console.print("\n[bold cyan]🔬 Running Comprehensive Tests[/bold cyan]\n")
        
        self.results['tests']['page_load'] = await self.test_page_load()
        self.results['tests']['links'] = await self.test_links()
        self.results['tests']['forms'] = await self.test_forms()
        self.results['tests']['responsive'] = await self.test_responsive_design()
        self.results['tests']['security'] = await self.test_security_headers()
        self.results['tests']['accessibility'] = await self.test_accessibility()
        self.results['tests']['console_errors'] = await self.test_console_errors()
        
        # Calculate overall status
        statuses = [test['status'] for test in self.results['tests'].values()]
        if 'FAIL' in statuses:
            self.results['overall_status'] = 'FAIL'
        elif 'WARNING' in statuses:
            self.results['overall_status'] = 'WARNING'
        else:
            self.results['overall_status'] = 'PASS'
        
        return self.results
    
    def save_results(self, output_dir: str = 'test_results'):
        """Save test results to JSON"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Create filename from URL
        safe_url = re.sub(r'[^\w\-]', '_', urlparse(self.url).netloc)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_{safe_url}_{timestamp}.json"
        
        filepath = output_path / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        
        console.print(f"\n[green]✓[/green] Test results saved to: {filepath}")
        return str(filepath)
