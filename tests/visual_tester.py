"""
Visual Regression Tester
=========================

Automated visual regression testing for web applications.
Compare screenshots, detect visual changes, manage baselines.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import hashlib

from playwright.async_api import Page
from PIL import Image, ImageChops, ImageDraw, ImageFilter
from rich.console import Console

console = Console()


class VisualTester:
    """Visual regression testing with screenshot comparison"""
    
    def __init__(self, page: Page, baseline_dir: str = 'visual_baselines'):
        self.page = page
        self.baseline_dir = Path(baseline_dir)
        self.baseline_dir.mkdir(exist_ok=True)
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'overall_status': 'PASS'
        }
    
    async def capture_screenshot(
        self, 
        name: str, 
        full_page: bool = True,
        viewport: Optional[Dict[str, int]] = None
    ) -> str:
        """Capture a screenshot"""
        console.print(f"[cyan]📸 Capturing screenshot: {name}[/cyan]")
        
        try:
            # Set viewport if specified
            if viewport:
                await self.page.set_viewport_size(viewport)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{name}_{timestamp}.png"
            filepath = self.baseline_dir / filename
            
            # Capture screenshot
            await self.page.screenshot(path=str(filepath), full_page=full_page)
            
            console.print(f"   [green]✓[/green] Screenshot saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            console.print(f"   [red]✗[/red] Screenshot capture failed: {e}")
            raise
    
    def get_baseline_path(self, name: str) -> Optional[Path]:
        """Get the baseline screenshot path for a given name"""
        # Look for the most recent baseline
        pattern = f"{name}_baseline_*.png"
        baselines = list(self.baseline_dir.glob(pattern))
        
        if baselines:
            return max(baselines, key=lambda p: p.stat().st_mtime)
        return None
    
    def save_baseline(self, screenshot_path: str, name: str) -> str:
        """Save a screenshot as a baseline"""
        console.print(f"[cyan]💾 Saving baseline: {name}[/cyan]")
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            baseline_filename = f"{name}_baseline_{timestamp}.png"
            baseline_path = self.baseline_dir / baseline_filename
            
            # Copy the screenshot to baseline
            img = Image.open(screenshot_path)
            img.save(str(baseline_path))
            
            console.print(f"   [green]✓[/green] Baseline saved: {baseline_path}")
            return str(baseline_path)
            
        except Exception as e:
            console.print(f"   [red]✗[/red] Baseline save failed: {e}")
            raise
    
    def compare_images(
        self, 
        baseline_path: str, 
        screenshot_path: str,
        threshold: float = 0.1
    ) -> Dict[str, Any]:
        """Compare two images and detect differences"""
        console.print(f"[cyan]🔍 Comparing images...[/cyan]")
        
        try:
            # Load images
            baseline_img = Image.open(baseline_path)
            screenshot_img = Image.open(screenshot_path)
            
            # Ensure same size
            if baseline_img.size != screenshot_img.size:
                console.print(f"   [yellow]⚠[/yellow] Resizing images to match")
                screenshot_img = screenshot_img.resize(baseline_img.size, Image.Resampling.LANCZOS)
            
            # Calculate difference
            diff_img = ImageChops.difference(baseline_img, screenshot_img)
            
            # Calculate percentage difference
            histogram = diff_img.histogram()
            total_pixels = sum(histogram)
            non_zero_pixels = sum(histogram[1:])  # Exclude zero differences
            diff_percentage = (non_zero_pixels / total_pixels) * 100 if total_pixels > 0 else 0
            
            # Determine status
            status = 'FAIL' if diff_percentage > threshold else 'PASS'
            
            # Save diff image if differences found
            diff_path = None
            if diff_percentage > 0:
                diff_path = self._save_diff_image(baseline_img, screenshot_img, diff_img)
            
            result = {
                'baseline': baseline_path,
                'screenshot': screenshot_path,
                'diff_percentage': round(diff_percentage, 4),
                'threshold': threshold,
                'status': status,
                'diff_image': diff_path,
                'message': f"Visual difference: {diff_percentage:.2f}% (threshold: {threshold}%)"
            }
            
            if status == 'PASS':
                console.print(f"   [green]✓[/green] Visual match: {diff_percentage:.2f}% difference")
            else:
                console.print(f"   [red]✗[/red] Visual mismatch: {diff_percentage:.2f}% difference (threshold: {threshold}%)")
            
            return result
            
        except Exception as e:
            console.print(f"   [red]✗[/red] Image comparison failed: {e}")
            return {
                'status': 'ERROR',
                'error': str(e),
                'message': f"Failed to compare images: {e}"
            }
    
    def _save_diff_image(
        self, 
        baseline_img: Image.Image,
        screenshot_img: Image.Image,
        diff_img: Image.Image
    ) -> str:
        """Save a composite image showing baseline, screenshot, and diff"""
        try:
            # Create a composite image
            width = baseline_img.width
            height = baseline_img.height
            
            composite = Image.new('RGB', (width * 3, height))
            
            # Place baseline, screenshot, and diff side by side
            composite.paste(baseline_img.convert('RGB'), (0, 0))
            composite.paste(screenshot_img.convert('RGB'), (width, 0))
            
            # Enhance diff visibility
            diff_enhanced = diff_img.convert('RGB')
            enhancer = Image.new('RGB', diff_enhanced.size, 'black')
            diff_enhanced = ImageChops.add(diff_enhanced, enhancer, scale=2.0)
            composite.paste(diff_enhanced, (width * 2, 0))
            
            # Add labels
            draw = ImageDraw.Draw(composite)
            draw.text((10, 10), "BASELINE", fill=(255, 0, 0))
            draw.text((width + 10, 10), "CURRENT", fill=(0, 255, 0))
            draw.text((width * 2 + 10, 10), "DIFF", fill=(255, 255, 0))
            
            # Save composite
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            diff_filename = f"diff_{timestamp}.png"
            diff_path = self.baseline_dir / diff_filename
            composite.save(str(diff_path))
            
            return str(diff_path)
            
        except Exception as e:
            console.print(f"   [yellow]⚠[/yellow] Failed to save diff image: {e}")
            return None
    
    async def test_viewport(
        self, 
        name: str, 
        viewport: Dict[str, int],
        baseline_exists: bool = True,
        threshold: float = 0.1
    ) -> Dict[str, Any]:
        """Test a specific viewport size"""
        console.print(f"\n[cyan]📱 Testing viewport: {viewport['width']}x{viewport['height']}[/cyan]")
        
        try:
            # Capture screenshot
            screenshot_path = await self.capture_screenshot(
                name=f"{name}_{viewport['width']}x{viewport['height']}",
                viewport=viewport,
                full_page=False
            )
            
            # If baseline doesn't exist, save this as baseline
            baseline_path = self.get_baseline_path(f"{name}_{viewport['width']}x{viewport['height']}")
            
            if not baseline_path or not baseline_exists:
                baseline_path = self.save_baseline(screenshot_path, f"{name}_{viewport['width']}x{viewport['height']}")
                result = {
                    'viewport': viewport,
                    'status': 'BASELINE_CREATED',
                    'screenshot': screenshot_path,
                    'baseline': baseline_path,
                    'message': 'Baseline created for future comparisons'
                }
            else:
                # Compare with baseline
                result = self.compare_images(str(baseline_path), screenshot_path, threshold)
                result['viewport'] = viewport
            
            self.results['tests'].append(result)
            return result
            
        except Exception as e:
            console.print(f"   [red]✗[/red] Viewport test failed: {e}")
            result = {
                'viewport': viewport,
                'status': 'ERROR',
                'error': str(e),
                'message': f"Failed to test viewport: {e}"
            }
            self.results['tests'].append(result)
            return result
    
    async def test_responsive_design(
        self,
        name: str = 'responsive',
        create_baseline: bool = False,
        threshold: float = 0.1
    ) -> Dict[str, Any]:
        """Test multiple viewport sizes for responsive design"""
        console.print("\n[bold cyan]📱 Testing Responsive Design[/bold cyan]\n")
        
        viewports = [
            {'width': 1920, 'height': 1080, 'name': 'desktop'},
            {'width': 1366, 'height': 768, 'name': 'laptop'},
            {'width': 768, 'height': 1024, 'name': 'tablet'},
            {'width': 375, 'height': 667, 'name': 'mobile'}
        ]
        
        results = []
        for viewport_config in viewports:
            viewport = {k: v for k, v in viewport_config.items() if k in ['width', 'height']}
            result = await self.test_viewport(
                name=f"{name}_{viewport_config['name']}",
                viewport=viewport,
                baseline_exists=not create_baseline,
                threshold=threshold
            )
            results.append(result)
        
        return {'viewports': results}
    
    async def test_element_screenshot(
        self,
        selector: str,
        name: str,
        create_baseline: bool = False,
        threshold: float = 0.1
    ) -> Dict[str, Any]:
        """Test a specific element screenshot"""
        console.print(f"\n[cyan]🎯 Testing element: {selector}[/cyan]")
        
        try:
            element = await self.page.query_selector(selector)
            if not element:
                raise ValueError(f"Element not found: {selector}")
            
            # Capture element screenshot
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{name}_{timestamp}.png"
            filepath = self.baseline_dir / filename
            
            await element.screenshot(path=str(filepath))
            console.print(f"   [green]✓[/green] Element screenshot saved: {filepath}")
            
            # Check for baseline
            baseline_path = self.get_baseline_path(name)
            
            if not baseline_path or create_baseline:
                baseline_path = self.save_baseline(str(filepath), name)
                result = {
                    'selector': selector,
                    'status': 'BASELINE_CREATED',
                    'screenshot': str(filepath),
                    'baseline': baseline_path,
                    'message': 'Baseline created for future comparisons'
                }
            else:
                result = self.compare_images(str(baseline_path), str(filepath), threshold)
                result['selector'] = selector
            
            self.results['tests'].append(result)
            return result
            
        except Exception as e:
            console.print(f"   [red]✗[/red] Element screenshot failed: {e}")
            result = {
                'selector': selector,
                'status': 'ERROR',
                'error': str(e),
                'message': f"Failed to capture element: {e}"
            }
            self.results['tests'].append(result)
            return result
    
    async def run_all_tests(
        self,
        name: str = 'visual_test',
        create_baseline: bool = False,
        threshold: float = 0.1,
        test_responsive: bool = True,
        test_elements: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Run all visual regression tests"""
        console.print("\n[bold cyan]👁️  Running Visual Regression Tests[/bold cyan]\n")
        
        # Test responsive design
        if test_responsive:
            await self.test_responsive_design(name, create_baseline, threshold)
        
        # Test specific elements
        if test_elements:
            for element in test_elements:
                await self.test_element_screenshot(
                    selector=element['selector'],
                    name=element['name'],
                    create_baseline=create_baseline,
                    threshold=threshold
                )
        
        # Calculate overall status
        statuses = [test.get('status') for test in self.results['tests']]
        
        if 'FAIL' in statuses or 'ERROR' in statuses:
            self.results['overall_status'] = 'FAIL'
        elif 'BASELINE_CREATED' in statuses:
            self.results['overall_status'] = 'BASELINE_CREATED'
        else:
            self.results['overall_status'] = 'PASS'
        
        return self.results
    
    def save_results(self, output_dir: str = 'visual_results'):
        """Save visual test results to JSON"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"visual_test_{timestamp}.json"
        
        filepath = output_path / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        
        console.print(f"\n[green]✓[/green] Visual test results saved to: {filepath}")
        return str(filepath)
