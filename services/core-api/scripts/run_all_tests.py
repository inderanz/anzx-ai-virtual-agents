#!/usr/bin/env python3
"""
Comprehensive Test Runner
Executes all test suites: unit, integration, e2e, security, and compliance
"""

import os
import sys
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path


class TestRunner:
    """Comprehensive test runner for all test suites"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {
            "start_time": datetime.now().isoformat(),
            "test_suites": {},
            "summary": {}
        }
    
    def run_unit_tests(self):
        """Run unit tests with coverage"""
        print("🧪 Running Unit Tests...")
        
        cmd = [
            "python", "-m", "pytest",
            "tests/",
            "--cov=app",
            "--cov-report=html:htmlcov",
            "--cov-report=xml:coverage.xml",
            "--cov-report=term-missing",
            "--cov-fail-under=70",
            "--junit-xml=test-results/unit-tests.xml",
            "-v"
        ]
        
        result = self._run_command(cmd, "Unit Tests")
        self.results["test_suites"]["unit"] = result
        return result["success"]
    
    def run_integration_tests(self):
        """Run integration tests with TestContainers"""
        print("🔗 Running Integration Tests...")
        
        # Start test containers
        print("  Starting test containers...")
        
        cmd = [
            "python", "-m", "pytest",
            "tests/integration/",
            "--junit-xml=test-results/integration-tests.xml",
            "-v", "-s"
        ]
        
        result = self._run_command(cmd, "Integration Tests")
        self.results["test_suites"]["integration"] = result
        return result["success"]
    
    def run_e2e_tests(self):
        """Run end-to-end tests with Playwright"""
        print("🎭 Running End-to-End Tests...")
        
        # Install Playwright browsers if needed
        subprocess.run(["npx", "playwright", "install"], 
                      cwd=self.project_root / "tests/e2e", 
                      capture_output=True)
        
        cmd = [
            "npx", "playwright", "test",
            "--reporter=html,junit",
            "--output-dir=test-results/e2e"
        ]
        
        result = self._run_command(cmd, "E2E Tests", cwd=self.project_root / "tests/e2e")
        self.results["test_suites"]["e2e"] = result
        return result["success"]
    
    def run_security_tests(self):
        """Run security and penetration tests"""
        print("🔒 Running Security Tests...")
        
        cmd = [
            "python", "-m", "pytest",
            "tests/security/",
            "--junit-xml=test-results/security-tests.xml",
            "-v", "-x"  # Stop on first failure for security tests
        ]
        
        result = self._run_command(cmd, "Security Tests")
        self.results["test_suites"]["security"] = result
        return result["success"]
    
    def run_compliance_tests(self):
        """Run privacy and compliance tests"""
        print("📋 Running Compliance Tests...")
        
        cmd = [
            "python", "-m", "pytest",
            "tests/security/test_privacy_compliance.py",
            "--junit-xml=test-results/compliance-tests.xml",
            "-v"
        ]
        
        result = self._run_command(cmd, "Compliance Tests")
        self.results["test_suites"]["compliance"] = result
        return result["success"]
    
    def run_performance_tests(self):
        """Run performance tests"""
        print("⚡ Running Performance Tests...")
        
        cmd = [
            "npx", "playwright", "test",
            "tests/performance.spec.js",
            "--reporter=html,junit",
            "--output-dir=test-results/performance"
        ]
        
        result = self._run_command(cmd, "Performance Tests", cwd=self.project_root / "tests/e2e")
        self.results["test_suites"]["performance"] = result
        return result["success"]
    
    def run_vulnerability_scan(self):
        """Run vulnerability scanning"""
        print("🛡️ Running Vulnerability Scan...")
        
        results = {}
        
        # Safety check for Python dependencies
        try:
            safety_result = subprocess.run(
                ["safety", "check", "--json"],
                capture_output=True,
                text=True,
                timeout=60
            )
            results["safety"] = {
                "success": safety_result.returncode == 0,
                "output": safety_result.stdout
            }
        except (subprocess.TimeoutExpired, FileNotFoundError):
            results["safety"] = {"success": False, "error": "Safety not available"}
        
        # Bandit security linting
        try:
            bandit_result = subprocess.run(
                ["bandit", "-r", "app/", "-f", "json"],
                capture_output=True,
                text=True,
                timeout=120
            )
            results["bandit"] = {
                "success": bandit_result.returncode == 0,
                "output": bandit_result.stdout
            }
        except (subprocess.TimeoutExpired, FileNotFoundError):
            results["bandit"] = {"success": False, "error": "Bandit not available"}
        
        # npm audit for JavaScript dependencies
        try:
            npm_audit_result = subprocess.run(
                ["npm", "audit", "--json"],
                cwd=self.project_root / "../chat-widget",
                capture_output=True,
                text=True,
                timeout=60
            )
            results["npm_audit"] = {
                "success": npm_audit_result.returncode == 0,
                "output": npm_audit_result.stdout
            }
        except (subprocess.TimeoutExpired, FileNotFoundError):
            results["npm_audit"] = {"success": False, "error": "npm audit not available"}
        
        self.results["test_suites"]["vulnerability_scan"] = results
        return all(result.get("success", False) for result in results.values())
    
    def _run_command(self, cmd, test_name, cwd=None):
        """Run a command and capture results"""
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout
            )
            
            duration = time.time() - start_time
            
            return {
                "success": result.returncode == 0,
                "duration": duration,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(cmd)
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "duration": time.time() - start_time,
                "error": "Test suite timed out",
                "command": " ".join(cmd)
            }
        except Exception as e:
            return {
                "success": False,
                "duration": time.time() - start_time,
                "error": str(e),
                "command": " ".join(cmd)
            }
    
    def generate_report(self):
        """Generate comprehensive test report"""
        self.results["end_time"] = datetime.now().isoformat()
        
        # Calculate summary
        total_suites = len(self.results["test_suites"])
        passed_suites = sum(1 for suite in self.results["test_suites"].values() 
                           if isinstance(suite, dict) and suite.get("success", False))
        
        self.results["summary"] = {
            "total_suites": total_suites,
            "passed_suites": passed_suites,
            "failed_suites": total_suites - passed_suites,
            "success_rate": (passed_suites / total_suites * 100) if total_suites > 0 else 0
        }
        
        # Save detailed results
        os.makedirs("test-results", exist_ok=True)
        with open("test-results/comprehensive-test-report.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("="*60)
        
        for suite_name, suite_result in self.results["test_suites"].items():
            if isinstance(suite_result, dict):
                status = "✅ PASS" if suite_result.get("success", False) else "❌ FAIL"
                duration = suite_result.get("duration", 0)
                print(f"{suite_name.upper():20} {status:10} ({duration:.1f}s)")
            else:
                print(f"{suite_name.upper():20} {'❓ MIXED':10}")
        
        print("-" * 60)
        print(f"TOTAL SUITES: {total_suites}")
        print(f"PASSED: {passed_suites}")
        print(f"FAILED: {total_suites - passed_suites}")
        print(f"SUCCESS RATE: {self.results['summary']['success_rate']:.1f}%")
        print("="*60)
        
        return self.results["summary"]["success_rate"] == 100.0
    
    def run_all(self):
        """Run all test suites"""
        print("🚀 Starting Comprehensive Test Suite")
        print("="*60)
        
        # Ensure test results directory exists
        os.makedirs("test-results", exist_ok=True)
        
        # Run all test suites
        test_suites = [
            ("Unit Tests", self.run_unit_tests),
            ("Integration Tests", self.run_integration_tests),
            ("Security Tests", self.run_security_tests),
            ("Compliance Tests", self.run_compliance_tests),
            ("E2E Tests", self.run_e2e_tests),
            ("Performance Tests", self.run_performance_tests),
            ("Vulnerability Scan", self.run_vulnerability_scan)
        ]
        
        for suite_name, suite_func in test_suites:
            try:
                success = suite_func()
                status = "✅" if success else "❌"
                print(f"{status} {suite_name} completed")
            except Exception as e:
                print(f"❌ {suite_name} failed with error: {e}")
                self.results["test_suites"][suite_name.lower().replace(" ", "_")] = {
                    "success": False,
                    "error": str(e)
                }
        
        # Generate final report
        all_passed = self.generate_report()
        
        if all_passed:
            print("\n🎉 All tests passed! System is ready for deployment.")
            return 0
        else:
            print("\n⚠️  Some tests failed. Please review the results before deployment.")
            return 1


def main():
    """Main entry point"""
    runner = TestRunner()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        suite = sys.argv[1].lower()
        
        if suite == "unit":
            success = runner.run_unit_tests()
        elif suite == "integration":
            success = runner.run_integration_tests()
        elif suite == "e2e":
            success = runner.run_e2e_tests()
        elif suite == "security":
            success = runner.run_security_tests()
        elif suite == "compliance":
            success = runner.run_compliance_tests()
        elif suite == "performance":
            success = runner.run_performance_tests()
        elif suite == "vulnerability":
            success = runner.run_vulnerability_scan()
        else:
            print(f"Unknown test suite: {suite}")
            print("Available suites: unit, integration, e2e, security, compliance, performance, vulnerability")
            return 1
        
        return 0 if success else 1
    else:
        # Run all tests
        return runner.run_all()


if __name__ == "__main__":
    sys.exit(main())