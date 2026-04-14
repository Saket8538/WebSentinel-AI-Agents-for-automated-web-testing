"""
API Tester
==========

Comprehensive API testing for REST endpoints.
Validate responses, test authentication, measure performance.
"""

import asyncio
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import json
import time

from rich.console import Console
from rich.table import Table

console = Console()


class APITester:
    """Test REST API endpoints with comprehensive validation"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.results = {
            'base_url': base_url,
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'overall_status': 'PASS'
        }
    
    def set_auth(self, auth_type: str, **kwargs):
        """Set authentication for API requests"""
        console.print(f"[cyan]🔐 Setting {auth_type} authentication[/cyan]")
        
        if auth_type == 'bearer':
            token = kwargs.get('token')
            self.session.headers.update({'Authorization': f'Bearer {token}'})
        elif auth_type == 'basic':
            username = kwargs.get('username')
            password = kwargs.get('password')
            self.session.auth = (username, password)
        elif auth_type == 'api_key':
            key = kwargs.get('key')
            header_name = kwargs.get('header_name', 'X-API-Key')
            self.session.headers.update({header_name: key})
        elif auth_type == 'custom_header':
            headers = kwargs.get('headers', {})
            self.session.headers.update(headers)
        
        console.print(f"   [green]✓[/green] Authentication configured")
    
    def test_endpoint(
        self,
        endpoint: str,
        method: str = 'GET',
        expected_status: int = 200,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Union[Dict, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
        validate_json: bool = True,
        validate_schema: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Test a single API endpoint"""
        console.print(f"\n[cyan]🌐 Testing {method} {endpoint}[/cyan]")
        
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            # Make request
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=data if isinstance(data, dict) else None,
                data=data if isinstance(data, str) else None,
                params=params,
                timeout=timeout
            )
            
            elapsed_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Validate status code
            status_match = response.status_code == expected_status
            
            # Parse response
            response_data = None
            is_json = False
            if validate_json:
                try:
                    response_data = response.json()
                    is_json = True
                except Exception:
                    pass
            
            # Validate schema if provided
            schema_valid = None
            if validate_schema and is_json:
                schema_valid = self._validate_schema(response_data, validate_schema)
            
            # Determine status
            status = 'PASS' if status_match and (schema_valid is None or schema_valid) else 'FAIL'
            
            result = {
                'endpoint': endpoint,
                'method': method,
                'url': url,
                'status': status,
                'status_code': response.status_code,
                'expected_status': expected_status,
                'status_match': status_match,
                'response_time_ms': round(elapsed_time, 2),
                'is_json': is_json,
                'response_size': len(response.content),
                'headers': dict(response.headers),
                'message': f"{method} {endpoint} - {response.status_code} ({elapsed_time:.2f}ms)"
            }
            
            if is_json:
                result['response_data'] = response_data
            
            if schema_valid is not None:
                result['schema_valid'] = schema_valid
            
            # Log result
            if status == 'PASS':
                console.print(f"   [green]✓[/green] Status: {response.status_code}, Time: {elapsed_time:.2f}ms")
            else:
                console.print(f"   [red]✗[/red] Expected {expected_status}, got {response.status_code}")
            
            self.results['tests'].append(result)
            return result
            
        except requests.exceptions.Timeout:
            console.print(f"   [red]✗[/red] Request timeout after {timeout}s")
            result = {
                'endpoint': endpoint,
                'method': method,
                'url': url,
                'status': 'FAIL',
                'error': 'Timeout',
                'message': f"Request timeout after {timeout}s"
            }
            self.results['tests'].append(result)
            return result
            
        except Exception as e:
            console.print(f"   [red]✗[/red] Request failed: {e}")
            result = {
                'endpoint': endpoint,
                'method': method,
                'url': url,
                'status': 'FAIL',
                'error': str(e),
                'message': f"Request failed: {e}"
            }
            self.results['tests'].append(result)
            return result
    
    def _validate_schema(self, data: Any, schema: Dict) -> bool:
        """Simple schema validation"""
        try:
            if 'type' in schema:
                expected_type = schema['type']
                
                if expected_type == 'object' and not isinstance(data, dict):
                    return False
                elif expected_type == 'array' and not isinstance(data, list):
                    return False
                elif expected_type == 'string' and not isinstance(data, str):
                    return False
                elif expected_type == 'number' and not isinstance(data, (int, float)):
                    return False
                elif expected_type == 'boolean' and not isinstance(data, bool):
                    return False
            
            if 'properties' in schema and isinstance(data, dict):
                for key, value_schema in schema['properties'].items():
                    if 'required' in schema and key in schema['required']:
                        if key not in data:
                            return False
                    if key in data:
                        if not self._validate_schema(data[key], value_schema):
                            return False
            
            if 'items' in schema and isinstance(data, list):
                for item in data:
                    if not self._validate_schema(item, schema['items']):
                        return False
            
            return True
            
        except Exception:
            return False
    
    def test_crud_operations(
        self,
        resource_endpoint: str,
        create_data: Dict,
        update_data: Dict,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """Test CRUD operations on a resource"""
        console.print(f"\n[bold cyan]🔄 Testing CRUD operations on {resource_endpoint}[/bold cyan]")
        
        results = {
            'resource': resource_endpoint,
            'operations': []
        }
        
        # CREATE
        create_result = self.test_endpoint(
            endpoint=resource_endpoint,
            method='POST',
            expected_status=201,
            data=create_data,
            timeout=timeout
        )
        results['operations'].append(create_result)
        
        # Extract resource ID if available
        resource_id = None
        if create_result.get('is_json') and create_result.get('response_data'):
            response_data = create_result['response_data']
            resource_id = response_data.get('id') or response_data.get('_id')
        
        if resource_id:
            # READ
            read_result = self.test_endpoint(
                endpoint=f"{resource_endpoint}/{resource_id}",
                method='GET',
                expected_status=200,
                timeout=timeout
            )
            results['operations'].append(read_result)
            
            # UPDATE
            update_result = self.test_endpoint(
                endpoint=f"{resource_endpoint}/{resource_id}",
                method='PUT',
                expected_status=200,
                data=update_data,
                timeout=timeout
            )
            results['operations'].append(update_result)
            
            # DELETE
            delete_result = self.test_endpoint(
                endpoint=f"{resource_endpoint}/{resource_id}",
                method='DELETE',
                expected_status=204,
                timeout=timeout
            )
            results['operations'].append(delete_result)
        else:
            console.print(f"   [yellow]⚠[/yellow] Could not extract resource ID, skipping READ, UPDATE, DELETE")
        
        return results
    
    def test_pagination(
        self,
        endpoint: str,
        page_param: str = 'page',
        limit_param: str = 'limit',
        max_pages: int = 3
    ) -> Dict[str, Any]:
        """Test API pagination"""
        console.print(f"\n[cyan]📄 Testing pagination on {endpoint}[/cyan]")
        
        results = {
            'endpoint': endpoint,
            'pages_tested': 0,
            'page_results': []
        }
        
        for page in range(1, max_pages + 1):
            params = {page_param: page, limit_param: 10}
            result = self.test_endpoint(
                endpoint=endpoint,
                method='GET',
                params=params
            )
            
            results['page_results'].append(result)
            results['pages_tested'] += 1
            
            # Check if we got data
            if not result.get('is_json') or not result.get('response_data'):
                break
        
        console.print(f"   [green]✓[/green] Tested {results['pages_tested']} page(s)")
        return results
    
    def test_rate_limiting(
        self,
        endpoint: str,
        requests_count: int = 10,
        delay_ms: int = 100
    ) -> Dict[str, Any]:
        """Test API rate limiting"""
        console.print(f"\n[cyan]⏱️  Testing rate limiting on {endpoint}[/cyan]")
        
        results = {
            'endpoint': endpoint,
            'requests_sent': 0,
            'successful_requests': 0,
            'rate_limited_requests': 0,
            'response_times': []
        }
        
        for i in range(requests_count):
            result = self.test_endpoint(endpoint=endpoint, method='GET')
            results['requests_sent'] += 1
            
            if result.get('status') == 'PASS':
                results['successful_requests'] += 1
            elif result.get('status_code') == 429:
                results['rate_limited_requests'] += 1
            
            if result.get('response_time_ms'):
                results['response_times'].append(result['response_time_ms'])
            
            time.sleep(delay_ms / 1000)
        
        if results['response_times']:
            results['avg_response_time_ms'] = round(sum(results['response_times']) / len(results['response_times']), 2)
            results['min_response_time_ms'] = min(results['response_times'])
            results['max_response_time_ms'] = max(results['response_times'])
        
        console.print(f"   [green]✓[/green] Sent {results['requests_sent']} requests")
        console.print(f"   [green]✓[/green] Successful: {results['successful_requests']}, Rate limited: {results['rate_limited_requests']}")
        
        return results
    
    def generate_report(self) -> Table:
        """Generate a Rich table report"""
        table = Table(title="API Test Results")
        
        table.add_column("Method", style="cyan")
        table.add_column("Endpoint", style="magenta")
        table.add_column("Status Code", style="yellow")
        table.add_column("Time (ms)", style="green")
        table.add_column("Result", style="bold")
        
        for test in self.results['tests']:
            result_style = "green" if test.get('status') == 'PASS' else "red"
            table.add_row(
                test.get('method', 'N/A'),
                test.get('endpoint', 'N/A'),
                str(test.get('status_code', 'N/A')),
                str(test.get('response_time_ms', 'N/A')),
                f"[{result_style}]{test.get('status', 'UNKNOWN')}[/{result_style}]"
            )
        
        return table
    
    def run_all_tests(
        self,
        endpoints: List[Dict[str, Any]],
        test_crud: Optional[Dict[str, Any]] = None,
        test_pagination: Optional[str] = None,
        test_rate_limit: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run all API tests"""
        console.print("\n[bold cyan]🔌 Running API Tests[/bold cyan]\n")
        
        # Test individual endpoints
        for endpoint_config in endpoints:
            self.test_endpoint(**endpoint_config)
        
        # Test CRUD operations
        if test_crud:
            self.test_crud_operations(**test_crud)
        
        # Test pagination
        if test_pagination:
            self.test_pagination(endpoint=test_pagination)
        
        # Test rate limiting
        if test_rate_limit:
            self.test_rate_limiting(endpoint=test_rate_limit)
        
        # Calculate overall status
        statuses = [test.get('status') for test in self.results['tests']]
        
        if 'FAIL' in statuses:
            self.results['overall_status'] = 'FAIL'
        else:
            self.results['overall_status'] = 'PASS'
        
        # Display report
        console.print("\n")
        console.print(self.generate_report())
        
        return self.results
    
    def save_results(self, output_dir: str = 'api_results'):
        """Save API test results to JSON"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"api_test_{timestamp}.json"
        
        filepath = output_path / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        
        console.print(f"\n[green]✓[/green] API test results saved to: {filepath}")
        return str(filepath)
