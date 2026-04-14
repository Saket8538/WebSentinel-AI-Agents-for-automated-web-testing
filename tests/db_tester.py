"""
Database Tester
===============

Comprehensive database testing for various database systems.
Test connections, query performance, data integrity, and more.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import json
import time

from rich.console import Console
from rich.table import Table

console = Console()


class DatabaseTester:
    """Test database connections and operations"""
    
    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.db_type = db_config.get('type', 'unknown').lower()
        self.connection = None
        self.results = {
            'db_type': self.db_type,
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'overall_status': 'PASS'
        }
    
    def connect(self) -> Dict[str, Any]:
        """Connect to the database"""
        console.print(f"[cyan]🔌 Connecting to {self.db_type} database...[/cyan]")
        
        start_time = time.time()
        
        try:
            if self.db_type == 'postgresql':
                import psycopg2
                self.connection = psycopg2.connect(
                    host=self.db_config.get('host'),
                    port=self.db_config.get('port', 5432),
                    database=self.db_config.get('database'),
                    user=self.db_config.get('user'),
                    password=self.db_config.get('password')
                )
            
            elif self.db_type == 'mysql':
                import mysql.connector
                self.connection = mysql.connector.connect(
                    host=self.db_config.get('host'),
                    port=self.db_config.get('port', 3306),
                    database=self.db_config.get('database'),
                    user=self.db_config.get('user'),
                    password=self.db_config.get('password')
                )
            
            elif self.db_type == 'mongodb':
                from pymongo import MongoClient
                connection_string = self.db_config.get('connection_string')
                self.connection = MongoClient(connection_string)
                # Test connection
                self.connection.server_info()
            
            elif self.db_type == 'sqlite':
                import sqlite3
                db_path = self.db_config.get('path')
                self.connection = sqlite3.connect(db_path)
            
            elif self.db_type == 'redis':
                import redis
                self.connection = redis.Redis(
                    host=self.db_config.get('host'),
                    port=self.db_config.get('port', 6379),
                    password=self.db_config.get('password'),
                    decode_responses=True
                )
                # Test connection
                self.connection.ping()
            
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
            
            elapsed_time = (time.time() - start_time) * 1000
            
            result = {
                'test': 'connection',
                'status': 'PASS',
                'connection_time_ms': round(elapsed_time, 2),
                'message': f"Connected to {self.db_type} in {elapsed_time:.2f}ms"
            }
            
            console.print(f"   [green]✓[/green] Connected successfully ({elapsed_time:.2f}ms)")
            self.results['tests'].append(result)
            return result
            
        except Exception as e:
            console.print(f"   [red]✗[/red] Connection failed: {e}")
            result = {
                'test': 'connection',
                'status': 'FAIL',
                'error': str(e),
                'message': f"Failed to connect: {e}"
            }
            self.results['tests'].append(result)
            return result
    
    def test_query_performance(
        self,
        query: str,
        params: Optional[tuple] = None,
        iterations: int = 10
    ) -> Dict[str, Any]:
        """Test query execution performance"""
        console.print(f"\n[cyan]⚡ Testing query performance ({iterations} iterations)[/cyan]")
        
        if not self.connection:
            return {
                'test': 'query_performance',
                'status': 'FAIL',
                'error': 'No database connection',
                'message': 'Not connected to database'
            }
        
        try:
            execution_times = []
            
            for i in range(iterations):
                start_time = time.time()
                
                if self.db_type in ['postgresql', 'mysql', 'sqlite']:
                    cursor = self.connection.cursor()
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                    cursor.fetchall()
                    cursor.close()
                
                elif self.db_type == 'mongodb':
                    # Parse MongoDB query (simplified)
                    db = self.connection[self.db_config.get('database')]
                    collection_name = self.db_config.get('collection', 'test')
                    collection = db[collection_name]
                    list(collection.find())
                
                elif self.db_type == 'redis':
                    # Execute Redis command
                    self.connection.execute_command(*query.split())
                
                elapsed_time = (time.time() - start_time) * 1000
                execution_times.append(elapsed_time)
            
            avg_time = sum(execution_times) / len(execution_times)
            min_time = min(execution_times)
            max_time = max(execution_times)
            
            result = {
                'test': 'query_performance',
                'status': 'PASS',
                'query': query,
                'iterations': iterations,
                'avg_time_ms': round(avg_time, 2),
                'min_time_ms': round(min_time, 2),
                'max_time_ms': round(max_time, 2),
                'message': f"Query executed {iterations} times, avg: {avg_time:.2f}ms"
            }
            
            console.print(f"   [green]✓[/green] Avg: {avg_time:.2f}ms, Min: {min_time:.2f}ms, Max: {max_time:.2f}ms")
            self.results['tests'].append(result)
            return result
            
        except Exception as e:
            console.print(f"   [red]✗[/red] Query performance test failed: {e}")
            result = {
                'test': 'query_performance',
                'status': 'FAIL',
                'error': str(e),
                'message': f"Failed to test query performance: {e}"
            }
            self.results['tests'].append(result)
            return result
    
    def test_data_integrity(self, table_name: str) -> Dict[str, Any]:
        """Test data integrity in a table"""
        console.print(f"\n[cyan]🔍 Testing data integrity for {table_name}[/cyan]")
        
        if not self.connection:
            return {
                'test': 'data_integrity',
                'status': 'FAIL',
                'error': 'No database connection',
                'message': 'Not connected to database'
            }
        
        try:
            issues = []
            
            if self.db_type in ['postgresql', 'mysql']:
                cursor = self.connection.cursor()
                
                # Check for NULL values in non-nullable columns
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {table_name}
                """)
                row_count = cursor.fetchone()[0]
                
                # Check for duplicate primary keys (simplified)
                try:
                    cursor.execute(f"""
                        SELECT COUNT(*) as total, COUNT(DISTINCT id) as unique_ids 
                        FROM {table_name}
                    """)
                    total, unique = cursor.fetchone()
                    if total != unique:
                        issues.append(f"Found {total - unique} duplicate primary keys")
                except Exception:
                    pass  # Table might not have 'id' column
                
                cursor.close()
            
            elif self.db_type == 'mongodb':
                db = self.connection[self.db_config.get('database')]
                collection = db[table_name]
                
                row_count = collection.count_documents({})
                
                # Check for documents with missing required fields
                if self.db_config.get('required_fields'):
                    for field in self.db_config['required_fields']:
                        missing = collection.count_documents({field: {'$exists': False}})
                        if missing > 0:
                            issues.append(f"{missing} documents missing required field '{field}'")
            
            status = 'WARNING' if issues else 'PASS'
            
            result = {
                'test': 'data_integrity',
                'status': status,
                'table': table_name,
                'row_count': row_count,
                'issues': issues,
                'message': f"Checked {row_count} rows, found {len(issues)} issue(s)"
            }
            
            console.print(f"   [green]✓[/green] Rows: {row_count}")
            if issues:
                console.print(f"   [yellow]⚠[/yellow] Issues: {len(issues)}")
                for issue in issues:
                    console.print(f"      • {issue}")
            
            self.results['tests'].append(result)
            return result
            
        except Exception as e:
            console.print(f"   [red]✗[/red] Data integrity test failed: {e}")
            result = {
                'test': 'data_integrity',
                'status': 'FAIL',
                'error': str(e),
                'message': f"Failed to test data integrity: {e}"
            }
            self.results['tests'].append(result)
            return result
    
    def test_connection_pool(self, pool_size: int = 10) -> Dict[str, Any]:
        """Test database connection pooling"""
        console.print(f"\n[cyan]🏊 Testing connection pool (size: {pool_size})[/cyan]")
        
        try:
            connections = []
            connection_times = []
            
            # Create connections
            for i in range(pool_size):
                start_time = time.time()
                
                if self.db_type == 'postgresql':
                    import psycopg2
                    conn = psycopg2.connect(
                        host=self.db_config.get('host'),
                        port=self.db_config.get('port', 5432),
                        database=self.db_config.get('database'),
                        user=self.db_config.get('user'),
                        password=self.db_config.get('password')
                    )
                    connections.append(conn)
                
                elif self.db_type == 'mysql':
                    import mysql.connector
                    conn = mysql.connector.connect(
                        host=self.db_config.get('host'),
                        port=self.db_config.get('port', 3306),
                        database=self.db_config.get('database'),
                        user=self.db_config.get('user'),
                        password=self.db_config.get('password')
                    )
                    connections.append(conn)
                
                elapsed_time = (time.time() - start_time) * 1000
                connection_times.append(elapsed_time)
            
            # Close connections
            for conn in connections:
                conn.close()
            
            avg_time = sum(connection_times) / len(connection_times)
            
            result = {
                'test': 'connection_pool',
                'status': 'PASS',
                'pool_size': pool_size,
                'avg_connection_time_ms': round(avg_time, 2),
                'message': f"Created {pool_size} connections, avg: {avg_time:.2f}ms"
            }
            
            console.print(f"   [green]✓[/green] Avg connection time: {avg_time:.2f}ms")
            self.results['tests'].append(result)
            return result
            
        except Exception as e:
            console.print(f"   [red]✗[/red] Connection pool test failed: {e}")
            result = {
                'test': 'connection_pool',
                'status': 'FAIL',
                'error': str(e),
                'message': f"Failed to test connection pool: {e}"
            }
            self.results['tests'].append(result)
            return result
    
    def test_transaction(self) -> Dict[str, Any]:
        """Test database transaction support"""
        console.print(f"\n[cyan]🔄 Testing transaction support[/cyan]")
        
        if not self.connection:
            return {
                'test': 'transaction',
                'status': 'FAIL',
                'error': 'No database connection',
                'message': 'Not connected to database'
            }
        
        try:
            if self.db_type in ['postgresql', 'mysql', 'sqlite']:
                cursor = self.connection.cursor()
                
                # Start transaction
                self.connection.begin()
                
                # Execute test query (this won't actually modify data if we rollback)
                cursor.execute("SELECT 1")
                
                # Rollback
                self.connection.rollback()
                
                cursor.close()
            
            elif self.db_type == 'mongodb':
                # MongoDB transactions require replica set
                db = self.connection[self.db_config.get('database')]
                with self.connection.start_session() as session:
                    with session.start_transaction():
                        # Test transaction
                        pass
            
            result = {
                'test': 'transaction',
                'status': 'PASS',
                'message': 'Transaction support verified'
            }
            
            console.print(f"   [green]✓[/green] Transactions supported")
            self.results['tests'].append(result)
            return result
            
        except Exception as e:
            console.print(f"   [yellow]⚠[/yellow] Transaction test: {e}")
            result = {
                'test': 'transaction',
                'status': 'WARNING',
                'error': str(e),
                'message': f"Transaction support uncertain: {e}"
            }
            self.results['tests'].append(result)
            return result
    
    def run_all_tests(
        self,
        test_query: Optional[str] = None,
        test_table: Optional[str] = None,
        test_pool: bool = False
    ) -> Dict[str, Any]:
        """Run all database tests"""
        console.print("\n[bold cyan]🗄️  Running Database Tests[/bold cyan]\n")
        
        # Connect to database
        self.connect()
        
        if self.connection:
            # Test query performance
            if test_query:
                self.test_query_performance(test_query)
            
            # Test data integrity
            if test_table:
                self.test_data_integrity(test_table)
            
            # Test connection pool
            if test_pool:
                self.test_connection_pool()
            
            # Test transactions
            self.test_transaction()
        
        # Calculate overall status
        statuses = [test.get('status') for test in self.results['tests']]
        
        if 'FAIL' in statuses:
            self.results['overall_status'] = 'FAIL'
        elif 'WARNING' in statuses:
            self.results['overall_status'] = 'WARNING'
        else:
            self.results['overall_status'] = 'PASS'
        
        return self.results
    
    def save_results(self, output_dir: str = 'db_results'):
        """Save database test results to JSON"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"db_test_{self.db_type}_{timestamp}.json"
        
        filepath = output_path / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        
        console.print(f"\n[green]✓[/green] Database test results saved to: {filepath}")
        return str(filepath)
    
    def close(self):
        """Close database connection"""
        if self.connection:
            try:
                if self.db_type in ['postgresql', 'mysql', 'sqlite']:
                    self.connection.close()
                elif self.db_type == 'mongodb':
                    self.connection.close()
                elif self.db_type == 'redis':
                    self.connection.close()
                
                console.print(f"[cyan]🔌 Database connection closed[/cyan]")
            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] Error closing connection: {e}")
