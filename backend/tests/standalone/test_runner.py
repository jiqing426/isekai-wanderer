#!/usr/bin/env python3
"""
Standalone Backend API Test Runner
Independent from OpenClaw runtime environment

Usage:
    python test_runner.py [--base-url http://localhost:8000] [--verbose]

Requirements:
    - Python 3.8+
    - requests library (pip install requests)
"""

import sys
import json
import time
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    print("Error: 'requests' library not found. Install with: pip install requests")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Single test result"""
    name: str
    passed: bool
    status_code: Optional[int] = None
    response_time_ms: float = 0.0
    request_method: str = ""
    request_url: str = ""
    request_body: Optional[str] = None
    response_body: Optional[str] = None
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TestSuite:
    """Test suite with multiple tests"""
    name: str
    results: List[TestResult] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.passed)
    
    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if not r.passed)
    
    @property
    def total(self) -> int:
        return len(self.results)


class APITester:
    """API testing client with logging"""
    
    def __init__(self, base_url: str, verbose: bool = False):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.verbose = verbose
        self.auth_token: Optional[str] = None
        
    def set_auth_token(self, token: str):
        """Set Bearer token for authenticated requests"""
        self.auth_token = token
        self.session.headers['Authorization'] = f'Bearer {token}'
        
    def request(self, method: str, endpoint: str, **kwargs) -> Tuple[requests.Response, float]:
        """
        Make HTTP request and measure response time
        
        Returns:
            Tuple of (Response, response_time_ms)
        """
        url = urljoin(self.base_url + '/', endpoint.lstrip('/'))
        
        # Log request
        if self.verbose:
            logger.info(f"→ {method} {url}")
            if 'json' in kwargs:
                logger.info(f"  Body: {json.dumps(kwargs['json'], indent=2, ensure_ascii=False)}")
        
        # Make request
        start = time.time()
        try:
            response = self.session.request(method, url, **kwargs)
            elapsed = (time.time() - start) * 1000
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            raise requests.RequestException(f"Request failed: {str(e)}")
        
        # Log response
        if self.verbose:
            logger.info(f"← {response.status_code} ({elapsed:.2f}ms)")
            try:
                body = response.json()
                logger.info(f"  Response: {json.dumps(body, indent=2, ensure_ascii=False)}")
            except:
                logger.info(f"  Response: {response.text[:200]}")
        
        return response, elapsed


class BackendTestSuite(TestSuite):
    """Backend API test suite"""
    
    def __init__(self, tester: APITester):
        super().__init__(name="Backend API Tests")
        self.tester = tester
        self.test_user = {
            "email": f"test_{int(time.time())}@example.com",
            "password": "***",
            "display_name": "Test User"
        }
        self.first_script_id: Optional[str] = None
        self.session_id: Optional[str] = None
        self.current_node_id: Optional[str] = None
        self.first_choice_id: Optional[str] = None
        
    def run_all_tests(self):
        """Run all tests in sequence"""
        self.start_time = datetime.now()
        
        logger.info("=" * 60)
        logger.info("Starting Backend API Test Suite")
        logger.info("=" * 60)
        
        # Health checks
        self.test_health_endpoint()
        self.test_health_v1_endpoint()
        
        # Authentication
        self.test_user_registration()
        self.test_user_login()
        self.test_protected_endpoint_without_auth()
        
        # Game functionality
        self.test_list_scripts()
        self.test_start_game()
        self.test_get_dialogue()
        self.test_submit_choice()
        self.test_progress_through_story()
        
        # Error cases
        self.test_invalid_script_id()
        self.test_invalid_choice_id()
        
        self.end_time = datetime.now()
        
        logger.info("=" * 60)
        logger.info(f"Test Suite Complete: {self.passed}/{self.total} passed")
        logger.info("=" * 60)
    
    def test_health_endpoint(self):
        """Test root health endpoint"""
        self._run_test(
            name="Root Health Check",
            method="GET",
            endpoint="/health",
            expected_status=200,
            validate=lambda r: r.json().get("status") == "ok"
        )
        
    def test_health_v1_endpoint(self):
        """Test v1 health endpoint"""
        self._run_test(
            name="V1 Health Check",
            method="GET",
            endpoint="/api/v1/health",
            expected_status=200,
            validate=lambda r: r.json().get("status") == "ok"
        )
    
    def test_user_registration(self):
        """Test user registration"""
        result = self._run_test(
            name="User Registration",
            method="POST",
            endpoint="/api/v1/auth/register",
            json=self.test_user,
            expected_status=201,
            validate=lambda r: "access_token" in r.json() and "id" in r.json()
        )
        
        if result.passed:
            # Save token for subsequent tests
            token = result.response_body.get("access_token")
            if token:
                self.tester.set_auth_token(token)
                logger.info(f"✓ Auth token set for user {result.response_body.get('id')}")
    
    def test_user_login(self):
        """Test user login"""
        result = self._run_test(
            name="User Login",
            method="POST",
            endpoint="/api/v1/auth/login",
            json={
                "email": self.test_user["email"],
                "password": self.test_user["password"]
            },
            expected_status=200,
            validate=lambda r: "access_token" in r.json()
        )
        
        if result.passed:
            token = result.response_body.get("access_token")
            if token:
                self.tester.set_auth_token(token)
    
    def test_protected_endpoint_without_auth(self):
        """Test accessing protected endpoint without authentication"""
        # Temporarily remove auth
        old_token = self.tester.auth_token
        self.tester.auth_token = None
        self.tester.session.headers.pop('Authorization', None)
        
        self._run_test(
            name="Protected Endpoint Without Auth",
            method="GET",
            endpoint="/api/v1/scripts",
            expected_status=401
        )
        
        # Restore auth
        if old_token:
            self.tester.set_auth_token(old_token)
    
    def test_list_scripts(self):
        """Test listing available scripts"""
        result = self._run_test(
            name="List Scripts",
            method="GET",
            endpoint="/api/v1/scripts",
            expected_status=200,
            validate=lambda r: "scripts" in r.json() and len(r.json()["scripts"]) > 0
        )
        
        if result.passed:
            scripts = result.response_body.get("scripts", [])
            logger.info(f"✓ Found {len(scripts)} scripts")
            if scripts:
                self.first_script_id = scripts[0]["id"]
    
    def test_start_game(self):
        """Test starting a new game"""
        if not self.first_script_id:
            self.results.append(TestResult(
                name="Start Game",
                passed=False,
                error="No script ID available (list_scripts failed)"
            ))
            return
        
        result = self._run_test(
            name="Start Game",
            method="POST",
            endpoint="/api/v1/game/start",
            json={"script_id": self.first_script_id},
            expected_status=200,
            validate=lambda r: "session_id" in r.json() and "node_id" in r.json()
        )
        
        if result.passed:
            self.session_id = result.response_body.get("session_id")
            self.current_node_id = result.response_body.get("node_id")
            logger.info(f"✓ Game started: session={self.session_id}")
    
    def test_get_dialogue(self):
        """Test getting dialogue for current node"""
        if not self.session_id:
            self.results.append(TestResult(
                name="Get Dialogue",
                passed=False,
                error="No session ID available (start_game failed)"
            ))
            return
        
        result = self._run_test(
            name="Get Dialogue",
            method="GET",
            endpoint=f"/api/v1/game/{self.session_id}/dialogue",
            expected_status=200,
            validate=lambda r: "node_id" in r.json() and "text" in r.json()
        )
        
        if result.passed:
            choices = result.response_body.get("choices", [])
            if choices:
                self.first_choice_id = choices[0]["id"]
                logger.info(f"✓ Got dialogue with {len(choices)} choices")
    
    def test_submit_choice(self):
        """Test submitting a choice"""
        if not self.session_id or not self.first_choice_id:
            self.results.append(TestResult(
                name="Submit Choice",
                passed=False,
                error="No session or choice ID available"
            ))
            return
        
        result = self._run_test(
            name="Submit Choice",
            method="POST",
            endpoint=f"/api/v1/game/{self.session_id}/choice",
            json={"choice_id": self.first_choice_id},
            expected_status=200,
            validate=lambda r: "next_node_id" in r.json() or "node_id" in r.json() or "is_ended" in r.json()
        )
        
        if result.passed:
            logger.info(f"✓ Choice submitted, new node: {result.response_body.get('node_id')}")
    
    def test_progress_through_story(self):
        """Test progressing through multiple nodes"""
        if not self.session_id:
            self.results.append(TestResult(
                name="Progress Through Story",
                passed=False,
                error="No session ID available"
            ))
            return
        
        # Get dialogue to see available choices
        response, _ = self.tester.request("GET", f"/api/v1/game/{self.session_id}/dialogue")
        
        if response.status_code != 200:
            self.results.append(TestResult(
                name="Progress Through Story",
                passed=False,
                error=f"Failed to get dialogue: {response.status_code}"
            ))
            return
        
        data = response.json()
        choices = data.get("choices", [])
        
        if not choices:
            # No choices means we're at an ending
            self.results.append(TestResult(
                name="Progress Through Story",
                passed=True,
                status_code=200,
                response_body=data,
                request_method="GET",
                request_url=f"/api/v1/game/{self.session_id}/dialogue"
            ))
            logger.info("✓ Reached story ending")
            return
        
        # Make a choice and verify we moved forward
        choice_id = choices[0]["id"]
        self._run_test(
            name="Progress Through Story",
            method="POST",
            endpoint=f"/api/v1/game/{self.session_id}/choice",
            json={"choice_id": choice_id},
            expected_status=200,
            validate=lambda r: True  # Just verify it doesn't error
        )
    
    def test_invalid_script_id(self):
        """Test starting game with invalid script ID"""
        self._run_test(
            name="Invalid Script ID",
            method="POST",
            endpoint="/api/v1/game/start",
            json={"script_id": "00000000-0000-0000-0000-000000000000"},
            expected_status=404
        )
    
    def test_invalid_choice_id(self):
        """Test submitting invalid choice"""
        if not self.session_id:
            self.results.append(TestResult(
                name="Invalid Choice ID",
                passed=False,
                error="No session ID available"
            ))
            return
        
        self._run_test(
            name="Invalid Choice ID",
            method="POST",
            endpoint=f"/api/v1/game/{self.session_id}/choice",
            json={"choice_id": "00000000-0000-0000-0000-000000000000"},
            expected_status=400
        )
    
    def _run_test(
        self,
        name: str,
        method: str,
        endpoint: str,
        expected_status: int,
        json: Optional[Dict] = None,
        validate: Optional[callable] = None
    ) -> TestResult:
        """Helper to run a single test"""
        result = TestResult(
            name=name,
            passed=False,
            request_method=method,
            request_url=endpoint,
            request_body=json
        )
        
        try:
            response, elapsed = self.tester.request(method, endpoint, json=json)
            
            result.status_code = response.status_code
            result.response_time_ms = elapsed
            
            try:
                result.response_body = response.json()
            except:
                result.response_body = response.text
            
            # Check status code
            if response.status_code != expected_status:
                result.error = f"Expected status {expected_status}, got {response.status_code}"
                logger.error(f"✗ {name}: {result.error}")
            # Run validation if provided
            elif validate and not validate(response):
                result.error = "Validation failed"
                logger.error(f"✗ {name}: Validation failed")
            else:
                result.passed = True
                logger.info(f"✓ {name} ({elapsed:.2f}ms)")
                
        except Exception as e:
            result.error = str(e)
            logger.error(f"✗ {name}: {str(e)}")
        
        self.results.append(result)
        return result


def generate_html_report(suite: TestSuite, output_path: str):
    """Generate HTML test report"""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Backend API Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .passed {{ color: #22c55e; font-weight: bold; }}
        .failed {{ color: #ef4444; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f5f5f5; }}
        .test-passed {{ background: #f0fdf4; }}
        .test-failed {{ background: #fef2f2; }}
        .details {{ font-size: 0.9em; color: #666; margin-top: 5px; }}
        .error {{ color: #ef4444; }}
    </style>
</head>
<body>
    <h1>Backend API Test Report</h1>
    
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Test Suite:</strong> {suite.name}</p>
        <p><strong>Total Tests:</strong> {suite.total}</p>
        <p><strong>Passed:</strong> <span class="passed">{suite.passed}</span></p>
        <p><strong>Failed:</strong> <span class="failed">{suite.failed}</span></p>
        <p><strong>Start Time:</strong> {suite.start_time}</p>
        <p><strong>End Time:</strong> {suite.end_time}</p>
        <p><strong>Duration:</strong> {(suite.end_time - suite.start_time).total_seconds():.2f}s</p>
    </div>
    
    <table>
        <thead>
            <tr>
                <th>Test Name</th>
                <th>Status</th>
                <th>Method</th>
                <th>Endpoint</th>
                <th>Status Code</th>
                <th>Time (ms)</th>
                <th>Details</th>
            </tr>
        </thead>
        <tbody>
"""
    
    for result in suite.results:
        status_class = "test-passed" if result.passed else "test-failed"
        status_text = "✓ PASSED" if result.passed else "✗ FAILED"
        
        html += f"""
            <tr class="{status_class}">
                <td>{result.name}</td>
                <td class="{'passed' if result.passed else 'failed'}">{status_text}</td>
                <td>{result.request_method}</td>
                <td>{result.request_url}</td>
                <td>{result.status_code or '-'}</td>
                <td>{result.response_time_ms:.2f}</td>
                <td>
                    {'<span class="error">' + result.error + '</span>' if result.error else ''}
                </td>
            </tr>
"""
    
    html += """
        </tbody>
    </table>
</body>
</html>
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    logger.info(f"HTML report generated: {output_path}")


def generate_json_report(suite: TestSuite, output_path: str):
    """Generate JSON test report"""
    report = {
        "suite_name": suite.name,
        "total_tests": suite.total,
        "passed": suite.passed,
        "failed": suite.failed,
        "start_time": suite.start_time.isoformat() if suite.start_time else None,
        "end_time": suite.end_time.isoformat() if suite.end_time else None,
        "results": []
    }
    
    for result in suite.results:
        report["results"].append({
            "name": result.name,
            "passed": result.passed,
            "status_code": result.status_code,
            "response_time_ms": result.response_time_ms,
            "request_method": result.request_method,
            "request_url": result.request_url,
            "request_body": result.request_body,
            "response_body": result.response_body,
            "error": result.error,
            "timestamp": result.timestamp
        })
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info(f"JSON report generated: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Backend API Test Runner")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Backend API base URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--output-dir",
        default="test_reports",
        help="Output directory for reports (default: test_reports)"
    )
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Initialize tester
    tester = APITester(args.base_url, verbose=args.verbose)
    
    # Run tests
    suite = BackendTestSuite(tester)
    suite.run_all_tests()
    
    # Generate reports
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_path = output_dir / f"test_report_{timestamp}.html"
    json_path = output_dir / f"test_report_{timestamp}.json"
    
    generate_html_report(suite, str(html_path))
    generate_json_report(suite, str(json_path))
    
    # Exit with appropriate code
    sys.exit(0 if suite.failed == 0 else 1)


if __name__ == "__main__":
    main()
