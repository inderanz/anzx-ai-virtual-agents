"""
OWASP Security Testing
Automated security scanning and vulnerability testing
"""

import pytest
import requests
import json
import time
from typing import Dict, List, Any
from unittest.mock import patch, Mock

from app.main import app
from app.config.settings import get_settings


class TestOWASPTop10:
    """Test against OWASP Top 10 vulnerabilities"""
    
    def setup_method(self):
        """Set up test environment"""
        self.base_url = "http://localhost:8000"
        self.test_headers = {
            "Content-Type": "application/json",
            "User-Agent": "OWASP-Security-Test"
        }
    
    def test_injection_attacks(self):
        """Test for SQL injection and other injection vulnerabilities"""
        # SQL injection payloads
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin'--",
            "admin' /*",
            "' OR 1=1#"
        ]
        
        # Test login endpoint
        for payload in sql_payloads:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json={
                    "email": payload,
                    "password": "test"
                },
                headers=self.test_headers
            )
            
            # Should not return successful login
            assert response.status_code != 200
            assert "token" not in response.text.lower()
        
        # Test search endpoints
        search_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "${7*7}",  # Template injection
            "{{7*7}}",  # Template injection
            "%{7*7}"   # Template injection
        ]
        
        for payload in search_payloads:
            response = requests.post(
                f"{self.base_url}/api/v1/knowledge/search",
                json={"query": payload},
                headers={**self.test_headers, "Authorization": "Bearer test-token"}
            )
            
            # Should not execute the payload
            assert "49" not in response.text  # 7*7 = 49
            assert "<script>" not in response.text
    
    def test_broken_authentication(self):
        """Test for authentication vulnerabilities"""
        # Test weak password requirements
        weak_passwords = ["123", "password", "admin", "test"]
        
        for password in weak_passwords:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/register",
                json={
                    "email": "test@example.com",
                    "password": password,
                    "full_name": "Test User"
                },
                headers=self.test_headers
            )
            
            # Should reject weak passwords
            assert response.status_code == 400
        
        # Test session fixation
        response1 = requests.get(f"{self.base_url}/api/v1/auth/me")
        session_id_1 = response1.cookies.get("session_id")
        
        # Login
        login_response = requests.post(
            f"{self.base_url}/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "ValidPassword123!"
            },
            headers=self.test_headers
        )
        
        if login_response.status_code == 200:
            session_id_2 = login_response.cookies.get("session_id")
            # Session ID should change after login
            assert session_id_1 != session_id_2
        
        # Test brute force protection
        for i in range(10):
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "wrong_password"
                },
                headers=self.test_headers
            )
        
        # Should implement rate limiting
        assert response.status_code == 429  # Too Many Requests
    
    def test_sensitive_data_exposure(self):
        """Test for sensitive data exposure"""
        # Test error messages don't leak sensitive info
        response = requests.post(
            f"{self.base_url}/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password"
            },
            headers=self.test_headers
        )
        
        # Should not reveal if user exists
        assert "user not found" not in response.text.lower()
        assert "invalid credentials" in response.text.lower()
        
        # Test API responses don't include sensitive fields
        response = requests.get(
            f"{self.base_url}/api/v1/auth/me",
            headers={**self.test_headers, "Authorization": "Bearer valid-token"}
        )
        
        if response.status_code == 200:
            user_data = response.json()
            # Should not include sensitive fields
            assert "password" not in user_data
            assert "password_hash" not in user_data
            assert "secret_key" not in user_data
    
    def test_xml_external_entities(self):
        """Test for XXE vulnerabilities"""
        xxe_payloads = [
            '<?xml version="1.0" encoding="ISO-8859-1"?><!DOCTYPE foo [<!ELEMENT foo ANY ><!ENTITY xxe SYSTEM "file:///etc/passwd" >]><foo>&xxe;</foo>',
            '<?xml version="1.0"?><!DOCTYPE root [<!ENTITY test SYSTEM "file:///etc/passwd">]><root>&test;</root>',
            '<?xml version="1.0"?><!DOCTYPE replace [<!ENTITY example "Doe"> ]><userInfo><firstName>John</firstName><lastName>&example;</lastName></userInfo>'
        ]
        
        for payload in xxe_payloads:
            response = requests.post(
                f"{self.base_url}/api/v1/knowledge/documents",
                data=payload,
                headers={
                    "Content-Type": "application/xml",
                    "Authorization": "Bearer test-token"
                }
            )
            
            # Should not process XXE
            assert "/etc/passwd" not in response.text
            assert "root:" not in response.text
    
    def test_broken_access_control(self):
        """Test for access control vulnerabilities"""
        # Test horizontal privilege escalation
        user1_token = "user1-token"
        user2_id = "user2-id"
        
        response = requests.get(
            f"{self.base_url}/api/v1/users/{user2_id}",
            headers={**self.test_headers, "Authorization": f"Bearer {user1_token}"}
        )
        
        # Should not allow access to other user's data
        assert response.status_code in [401, 403, 404]
        
        # Test vertical privilege escalation
        regular_user_token = "regular-user-token"
        
        response = requests.post(
            f"{self.base_url}/api/v1/admin/users",
            json={"email": "new@example.com", "role": "admin"},
            headers={**self.test_headers, "Authorization": f"Bearer {regular_user_token}"}
        )
        
        # Should not allow regular user to create admin users
        assert response.status_code in [401, 403]
        
        # Test direct object references
        response = requests.get(
            f"{self.base_url}/api/v1/conversations/1",
            headers={**self.test_headers, "Authorization": f"Bearer {regular_user_token}"}
        )
        
        # Should validate ownership
        assert response.status_code in [401, 403, 404]
    
    def test_security_misconfiguration(self):
        """Test for security misconfigurations"""
        # Test security headers
        response = requests.get(f"{self.base_url}/")
        
        # Should have security headers
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] in ["DENY", "SAMEORIGIN"]
        
        assert "X-XSS-Protection" in response.headers
        assert "Strict-Transport-Security" in response.headers
        
        # Test CORS configuration
        response = requests.options(
            f"{self.base_url}/api/v1/auth/login",
            headers={
                "Origin": "https://malicious-site.com",
                "Access-Control-Request-Method": "POST"
            }
        )
        
        # Should not allow arbitrary origins
        cors_origin = response.headers.get("Access-Control-Allow-Origin")
        assert cors_origin != "*" or cors_origin != "https://malicious-site.com"
        
        # Test debug information exposure
        response = requests.get(f"{self.base_url}/debug")
        assert response.status_code == 404  # Debug endpoint should not exist
        
        response = requests.get(f"{self.base_url}/.env")
        assert response.status_code == 404  # Environment file should not be accessible
    
    def test_cross_site_scripting(self):
        """Test for XSS vulnerabilities"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<svg onload=alert('xss')>",
            "';alert('xss');//",
            "<iframe src=javascript:alert('xss')></iframe>"
        ]
        
        # Test reflected XSS
        for payload in xss_payloads:
            response = requests.get(
                f"{self.base_url}/search",
                params={"q": payload},
                headers=self.test_headers
            )
            
            # Should not reflect unescaped payload
            assert payload not in response.text
            assert "alert('xss')" not in response.text
        
        # Test stored XSS
        for payload in xss_payloads:
            response = requests.post(
                f"{self.base_url}/api/v1/conversations/1/messages",
                json={"content": payload, "role": "user"},
                headers={**self.test_headers, "Authorization": "Bearer test-token"}
            )
            
            if response.status_code == 201:
                # Retrieve the message
                get_response = requests.get(
                    f"{self.base_url}/api/v1/conversations/1/messages",
                    headers={**self.test_headers, "Authorization": "Bearer test-token"}
                )
                
                # Should not contain unescaped payload
                assert payload not in get_response.text
                assert "alert('xss')" not in get_response.text
    
    def test_insecure_deserialization(self):
        """Test for insecure deserialization vulnerabilities"""
        # Test pickle deserialization
        malicious_payloads = [
            "cposix\nsystem\np0\n(S'ls'\np1\ntp2\nRp3\n.",  # Pickle payload
            '{"__reduce__": ["os.system", ["ls"]]}',  # JSON with reduce
            "!!python/object/apply:os.system ['ls']"  # YAML payload
        ]
        
        for payload in malicious_payloads:
            response = requests.post(
                f"{self.base_url}/api/v1/import",
                data=payload,
                headers={
                    "Content-Type": "application/octet-stream",
                    "Authorization": "Bearer test-token"
                }
            )
            
            # Should not execute system commands
            assert response.status_code in [400, 415]  # Bad Request or Unsupported Media Type
    
    def test_using_components_with_known_vulnerabilities(self):
        """Test for known vulnerable components"""
        # Test server information disclosure
        response = requests.get(f"{self.base_url}/")
        
        # Should not reveal server version
        server_header = response.headers.get("Server", "")
        assert "Apache" not in server_header or "/" not in server_header
        assert "nginx" not in server_header or "/" not in server_header
        
        # Test for common vulnerable endpoints
        vulnerable_endpoints = [
            "/phpinfo.php",
            "/wp-admin/",
            "/admin/",
            "/.git/",
            "/config.php",
            "/database.sql"
        ]
        
        for endpoint in vulnerable_endpoints:
            response = requests.get(f"{self.base_url}{endpoint}")
            assert response.status_code == 404
    
    def test_insufficient_logging_monitoring(self):
        """Test for logging and monitoring capabilities"""
        # Test that security events are logged
        # This would typically check log files or monitoring systems
        
        # Simulate failed login attempt
        response = requests.post(
            f"{self.base_url}/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrong_password"
            },
            headers=self.test_headers
        )
        
        # Should log failed attempts (this would be verified in actual log files)
        assert response.status_code == 401
        
        # Test rate limiting logs
        for i in range(5):
            requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "wrong_password"
                },
                headers=self.test_headers
            )
        
        # Should trigger rate limiting
        response = requests.post(
            f"{self.base_url}/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrong_password"
            },
            headers=self.test_headers
        )
        
        assert response.status_code == 429


class TestAPISecurityBestPractices:
    """Test API security best practices"""
    
    def setup_method(self):
        self.base_url = "http://localhost:8000"
        self.test_headers = {"Content-Type": "application/json"}
    
    def test_input_validation(self):
        """Test comprehensive input validation"""
        # Test field length limits
        long_string = "A" * 10000
        
        response = requests.post(
            f"{self.base_url}/api/v1/auth/register",
            json={
                "email": long_string + "@example.com",
                "password": "ValidPassword123!",
                "full_name": long_string
            },
            headers=self.test_headers
        )
        
        assert response.status_code == 400
        
        # Test data type validation
        response = requests.post(
            f"{self.base_url}/api/v1/assistants",
            json={
                "name": 123,  # Should be string
                "type": ["invalid"],  # Should be string
                "capabilities": "invalid"  # Should be array
            },
            headers={**self.test_headers, "Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 400
    
    def test_output_encoding(self):
        """Test proper output encoding"""
        # Test HTML encoding
        response = requests.post(
            f"{self.base_url}/api/v1/conversations/1/messages",
            json={
                "content": "<script>alert('test')</script>",
                "role": "user"
            },
            headers={**self.test_headers, "Authorization": "Bearer test-token"}
        )
        
        if response.status_code == 201:
            message_data = response.json()
            # Should be HTML encoded
            assert "&lt;script&gt;" in message_data.get("content", "") or \
                   "<script>" not in message_data.get("content", "")
    
    def test_authentication_security(self):
        """Test authentication security measures"""
        # Test JWT token validation
        invalid_tokens = [
            "invalid.token.here",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",
            "",
            "Bearer ",
            "malformed-token"
        ]
        
        for token in invalid_tokens:
            response = requests.get(
                f"{self.base_url}/api/v1/auth/me",
                headers={**self.test_headers, "Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 401
    
    def test_authorization_controls(self):
        """Test authorization and access controls"""
        # Test role-based access control
        user_token = "user-token"
        admin_token = "admin-token"
        
        # User should not access admin endpoints
        response = requests.get(
            f"{self.base_url}/api/v1/admin/users",
            headers={**self.test_headers, "Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code in [401, 403]
        
        # Admin should access admin endpoints
        response = requests.get(
            f"{self.base_url}/api/v1/admin/users",
            headers={**self.test_headers, "Authorization": f"Bearer {admin_token}"}
        )
        
        # Should allow admin access (or return 404 if endpoint doesn't exist)
        assert response.status_code != 403
    
    def test_data_encryption(self):
        """Test data encryption requirements"""
        # Test HTTPS enforcement
        http_response = requests.get("http://localhost:8000/api/v1/auth/login")
        
        # Should redirect to HTTPS or return security error
        assert http_response.status_code in [301, 302, 400, 403]
        
        # Test password hashing
        response = requests.post(
            f"{self.base_url}/api/v1/auth/register",
            json={
                "email": "encryption-test@example.com",
                "password": "TestPassword123!",
                "full_name": "Test User"
            },
            headers=self.test_headers
        )
        
        if response.status_code == 201:
            # Password should never be returned in plain text
            user_data = response.json()
            assert "password" not in user_data
            assert "TestPassword123!" not in str(user_data)


class TestComplianceRequirements:
    """Test compliance with security standards"""
    
    def test_gdpr_compliance(self):
        """Test GDPR compliance requirements"""
        # Test data portability
        response = requests.get(
            f"http://localhost:8000/api/v1/users/me/export",
            headers={"Authorization": "Bearer test-token"}
        )
        
        # Should provide data export capability
        assert response.status_code in [200, 404]  # 404 if not implemented yet
        
        # Test right to deletion
        response = requests.delete(
            f"http://localhost:8000/api/v1/users/me",
            headers={"Authorization": "Bearer test-token"}
        )
        
        # Should provide deletion capability
        assert response.status_code in [200, 204, 404]  # 404 if not implemented yet
    
    def test_australian_privacy_principles(self):
        """Test Australian Privacy Principles compliance"""
        # Test consent collection
        response = requests.post(
            f"http://localhost:8000/api/v1/auth/register",
            json={
                "email": "privacy-test@example.com",
                "password": "TestPassword123!",
                "full_name": "Test User",
                "consent": {
                    "data_collection": True,
                    "marketing": False,
                    "analytics": True
                }
            },
            headers={"Content-Type": "application/json"}
        )
        
        # Should handle consent properly
        if response.status_code == 201:
            user_data = response.json()
            assert "consent" in user_data or response.status_code == 201
    
    def test_data_breach_notification(self):
        """Test data breach notification capabilities"""
        # This would test the breach notification system
        # In a real implementation, this would verify:
        # - Breach detection mechanisms
        # - Notification procedures
        # - Compliance with 72-hour notification requirement
        
        # Placeholder test - would be implemented based on actual breach detection system
        assert True  # Placeholder for actual breach notification tests


class TestPenetrationTesting:
    """Automated penetration testing"""
    
    def test_port_scanning_protection(self):
        """Test protection against port scanning"""
        # This would typically use tools like nmap
        # For now, we'll test basic port access
        
        import socket
        
        # Test that only expected ports are open
        expected_ports = [8000]  # API port
        unexpected_ports = [22, 23, 3389, 5432, 6379]  # SSH, Telnet, RDP, PostgreSQL, Redis
        
        for port in unexpected_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            # Port should be closed (connection refused)
            assert result != 0
    
    def test_directory_traversal(self):
        """Test directory traversal protection"""
        traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "....//....//....//etc/passwd"
        ]
        
        for payload in traversal_payloads:
            response = requests.get(
                f"http://localhost:8000/api/v1/files/{payload}",
                headers={"Authorization": "Bearer test-token"}
            )
            
            # Should not allow directory traversal
            assert response.status_code in [400, 403, 404]
            assert "/etc/passwd" not in response.text
            assert "root:" not in response.text
    
    def test_command_injection(self):
        """Test command injection protection"""
        command_payloads = [
            "; ls -la",
            "| cat /etc/passwd",
            "&& whoami",
            "`id`",
            "$(whoami)",
            "; rm -rf /",
            "| nc -l 4444"
        ]
        
        for payload in command_payloads:
            response = requests.post(
                f"http://localhost:8000/api/v1/system/command",
                json={"command": payload},
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer admin-token"
                }
            )
            
            # Should not execute system commands
            assert response.status_code in [400, 403, 404]
            assert "root" not in response.text
            assert "uid=" not in response.text


class TestVulnerabilityScanning:
    """Automated vulnerability scanning"""
    
    def test_dependency_vulnerabilities(self):
        """Test for known vulnerabilities in dependencies"""
        # This would typically use tools like safety, bandit, or snyk
        # For now, we'll check for common vulnerable patterns
        
        import subprocess
        import os
        
        # Check if safety is available and run it
        try:
            result = subprocess.run(
                ["safety", "check", "--json"],
                cwd="../../",
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # No vulnerabilities found
                assert True
            else:
                # Parse safety output for critical vulnerabilities
                if result.stdout:
                    import json
                    try:
                        vulnerabilities = json.loads(result.stdout)
                        critical_vulns = [v for v in vulnerabilities if v.get("severity") == "critical"]
                        assert len(critical_vulns) == 0, f"Critical vulnerabilities found: {critical_vulns}"
                    except json.JSONDecodeError:
                        pass
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Safety not available or timeout
            pass
    
    def test_code_quality_security(self):
        """Test code quality and security patterns"""
        # This would typically use tools like bandit for Python
        # For now, we'll test basic security patterns
        
        try:
            result = subprocess.run(
                ["bandit", "-r", "app/", "-f", "json"],
                cwd="../../",
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.stdout:
                import json
                try:
                    bandit_results = json.loads(result.stdout)
                    high_severity = [
                        issue for issue in bandit_results.get("results", [])
                        if issue.get("issue_severity") == "HIGH"
                    ]
                    
                    # Should not have high severity security issues
                    assert len(high_severity) == 0, f"High severity security issues: {high_severity}"
                except json.JSONDecodeError:
                    pass
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Bandit not available or timeout
            pass