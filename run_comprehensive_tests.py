#!/usr/bin/env python3
"""
ANZX AI Platform - Comprehensive Testing Suite
Tests all functionality as a real customer would use it
"""

import asyncio
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ANZXComprehensiveTester:
    """Comprehensive testing suite for ANZX AI Platform"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = None
        self.test_results = []
        self.assistants = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name: str, success: bool, details: Dict[str, Any]):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
        if details.get("message"):
            logger.info(f"    {details['message']}")
    
    async def test_api_health(self):
        """Test 1: API Health Check"""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_result("API Health Check", True, {
                        "message": f"Service status: {data.get('status')}",
                        "version": data.get("version"),
                        "service": data.get("service")
                    })
                    return True
                else:
                    self.log_result("API Health Check", False, {
                        "message": f"HTTP {response.status}",
                        "status_code": response.status
                    })
                    return False
        except Exception as e:
            self.log_result("API Health Check", False, {"message": f"Error: {str(e)}"})
            return False
    
    async def test_assistants_discovery(self):
        """Test 2: Assistants Discovery"""
        try:
            async with self.session.get(f"{self.base_url}/assistants") as response:
                if response.status == 200:
                    data = await response.json()
                    self.assistants = data.get("assistants", [])
                    
                    self.log_result("Assistants Discovery", True, {
                        "message": f"Found {len(self.assistants)} assistants",
                        "assistant_count": len(self.assistants),
                        "assistant_types": [a.get("type") for a in self.assistants]
                    })
                    return True
                else:
                    self.log_result("Assistants Discovery", False, {
                        "message": f"HTTP {response.status}",
                        "status_code": response.status
                    })
                    return False
        except Exception as e:
            self.log_result("Assistants Discovery", False, {"message": f"Error: {str(e)}"})
            return False
    
    async def test_assistant_types(self):
        """Test 3: Validate All Assistant Types"""
        expected_types = ["support", "sales", "technical", "admin", "content", "insights"]
        found_types = [a.get("type") for a in self.assistants]
        
        missing_types = [t for t in expected_types if t not in found_types]
        extra_types = [t for t in found_types if t not in expected_types]
        
        success = len(missing_types) == 0
        
        self.log_result("Assistant Types Validation", success, {
            "message": f"Expected: {len(expected_types)}, Found: {len(set(found_types))}",
            "expected_types": expected_types,
            "found_types": list(set(found_types)),
            "missing_types": missing_types,
            "extra_types": extra_types
        })
        
        return success
    
    async def test_assistant_chat_simulation(self):
        """Test 4: Simulate Customer Conversations with Each Assistant Type"""
        if not self.assistants:
            self.log_result("Assistant Chat Simulation", False, {
                "message": "No assistants available for testing"
            })
            return False
        
        # Test scenarios for each assistant type
        test_scenarios = {
            "support": [
                "I'm having trouble logging into my account",
                "My payment failed, can you help?",
                "How do I reset my password?"
            ],
            "sales": [
                "I'm interested in your enterprise plan",
                "What's the pricing for 50 users?",
                "Can you schedule a demo?"
            ],
            "technical": [
                "How do I integrate your API?",
                "I'm getting a 401 error",
                "What's the rate limit for API calls?"
            ],
            "admin": [
                "Schedule a meeting for next Tuesday",
                "Cancel my 3pm appointment",
                "What's on my calendar today?"
            ],
            "content": [
                "Write a blog post about AI",
                "Create social media content",
                "Help me with email marketing"
            ],
            "insights": [
                "Show me last month's performance",
                "What are the trending topics?",
                "Generate a sales report"
            ]
        }
        
        successful_chats = 0
        total_chats = 0
        
        for assistant in self.assistants:
            assistant_type = assistant.get("type")
            assistant_id = assistant.get("id")
            assistant_name = assistant.get("name")
            
            if assistant_type in test_scenarios:
                scenarios = test_scenarios[assistant_type]
                
                for i, message in enumerate(scenarios):
                    total_chats += 1
                    
                    try:
                        # Simulate chat with assistant
                        chat_data = {
                            "message": message,
                            "channel": "api-test",
                            "context": {"test_scenario": True}
                        }
                        
                        async with self.session.post(
                            f"{self.base_url}/assistants/{assistant_id}/chat",
                            json=chat_data
                        ) as response:
                            
                            if response.status == 200:
                                response_data = await response.json()
                                successful_chats += 1
                                
                                logger.info(f"    ✅ {assistant_name} ({assistant_type}): '{message[:30]}...'")
                                
                            else:
                                logger.warning(f"    ⚠️  {assistant_name} chat failed: HTTP {response.status}")
                                
                    except Exception as e:
                        logger.warning(f"    ❌ {assistant_name} chat error: {str(e)}")
        
        success_rate = (successful_chats / total_chats * 100) if total_chats > 0 else 0
        
        self.log_result("Assistant Chat Simulation", success_rate >= 50, {
            "message": f"Success rate: {success_rate:.1f}% ({successful_chats}/{total_chats})",
            "successful_chats": successful_chats,
            "total_chats": total_chats,
            "success_rate": success_rate
        })
        
        return success_rate >= 50
    
    async def test_api_performance(self):
        """Test 5: API Performance Testing"""
        endpoints_to_test = [
            ("/health", "Health Check"),
            ("/assistants", "Assistants List"),
        ]
        
        performance_results = []
        
        for endpoint, name in endpoints_to_test:
            response_times = []
            
            # Test each endpoint 5 times
            for i in range(5):
                try:
                    start_time = time.time()
                    async with self.session.get(f"{self.base_url}{endpoint}") as response:
                        end_time = time.time()
                        response_time = (end_time - start_time) * 1000  # Convert to ms
                        
                        if response.status == 200:
                            response_times.append(response_time)
                        
                except Exception as e:
                    logger.warning(f"Performance test failed for {endpoint}: {e}")
            
            if response_times:
                avg_time = sum(response_times) / len(response_times)
                max_time = max(response_times)
                min_time = min(response_times)
                
                performance_results.append({
                    "endpoint": endpoint,
                    "name": name,
                    "avg_response_time_ms": round(avg_time, 2),
                    "max_response_time_ms": round(max_time, 2),
                    "min_response_time_ms": round(min_time, 2),
                    "samples": len(response_times)
                })
        
        # Check if performance meets targets (< 2000ms average)
        avg_performance = sum(r["avg_response_time_ms"] for r in performance_results) / len(performance_results)
        performance_good = avg_performance < 2000
        
        self.log_result("API Performance Testing", performance_good, {
            "message": f"Average response time: {avg_performance:.2f}ms",
            "performance_target_met": performance_good,
            "target_ms": 2000,
            "endpoint_results": performance_results
        })
        
        return performance_good
    
    async def test_error_handling(self):
        """Test 6: Error Handling and Edge Cases"""
        error_test_cases = [
            ("/nonexistent", "404 Not Found", 404),
            ("/assistants/invalid-uuid", "Invalid Assistant ID", [400, 404, 422]),
            ("/assistants/00000000-0000-0000-0000-000000000000", "Non-existent Assistant", 404)
        ]
        
        error_handling_results = []
        
        for endpoint, test_name, expected_status in error_test_cases:
            try:
                async with self.session.get(f"{self.base_url}{endpoint}") as response:
                    actual_status = response.status
                    
                    # Check if status is expected (can be single int or list)
                    if isinstance(expected_status, list):
                        status_correct = actual_status in expected_status
                    else:
                        status_correct = actual_status == expected_status
                    
                    error_handling_results.append({
                        "test": test_name,
                        "endpoint": endpoint,
                        "expected_status": expected_status,
                        "actual_status": actual_status,
                        "correct": status_correct
                    })
                    
            except Exception as e:
                error_handling_results.append({
                    "test": test_name,
                    "endpoint": endpoint,
                    "error": str(e),
                    "correct": False
                })
        
        correct_responses = sum(1 for r in error_handling_results if r.get("correct", False))
        total_tests = len(error_handling_results)
        
        self.log_result("Error Handling", correct_responses == total_tests, {
            "message": f"Correct error responses: {correct_responses}/{total_tests}",
            "error_test_results": error_handling_results
        })
        
        return correct_responses == total_tests
    
    async def test_api_documentation(self):
        """Test 7: API Documentation Accessibility"""
        doc_endpoints = [
            ("/docs", "Swagger UI"),
            ("/openapi.json", "OpenAPI Schema")
        ]
        
        doc_results = []
        
        for endpoint, name in doc_endpoints:
            try:
                async with self.session.get(f"{self.base_url}{endpoint}") as response:
                    if response.status == 200:
                        content = await response.text()
                        doc_results.append({
                            "endpoint": endpoint,
                            "name": name,
                            "accessible": True,
                            "content_length": len(content)
                        })
                    else:
                        doc_results.append({
                            "endpoint": endpoint,
                            "name": name,
                            "accessible": False,
                            "status_code": response.status
                        })
            except Exception as e:
                doc_results.append({
                    "endpoint": endpoint,
                    "name": name,
                    "accessible": False,
                    "error": str(e)
                })
        
        accessible_docs = sum(1 for r in doc_results if r.get("accessible", False))
        
        self.log_result("API Documentation", accessible_docs == len(doc_endpoints), {
            "message": f"Accessible documentation: {accessible_docs}/{len(doc_endpoints)}",
            "documentation_results": doc_results
        })
        
        return accessible_docs == len(doc_endpoints)
    
    async def run_all_tests(self):
        """Run all comprehensive tests"""
        logger.info("🚀 Starting ANZX AI Platform Comprehensive Testing")
        logger.info("=" * 60)
        
        # Run all tests in sequence
        test_methods = [
            self.test_api_health,
            self.test_assistants_discovery,
            self.test_assistant_types,
            self.test_assistant_chat_simulation,
            self.test_api_performance,
            self.test_error_handling,
            self.test_api_documentation
        ]
        
        for test_method in test_methods:
            await test_method()
            await asyncio.sleep(1)  # Brief pause between tests
        
        # Generate summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        logger.info("=" * 60)
        logger.info("📊 COMPREHENSIVE TESTING SUMMARY")
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {total_tests - passed_tests}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            logger.info("🎉 EXCELLENT - Platform is production ready!")
        elif success_rate >= 75:
            logger.info("✅ GOOD - Platform is functional with minor issues")
        elif success_rate >= 50:
            logger.info("⚠️  FAIR - Platform has some issues to address")
        else:
            logger.info("🔧 NEEDS WORK - Significant issues found")
        
        return {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "success_rate": success_rate,
                "timestamp": datetime.now().isoformat(),
                "platform_status": "production_ready" if success_rate >= 90 else "needs_work"
            },
            "detailed_results": self.test_results,
            "assistants_found": self.assistants
        }

async def main():
    """Main testing function"""
    base_url = "https://anzx-ai-platform-core-api-1088103632448.australia-southeast1.run.app"
    
    async with ANZXComprehensiveTester(base_url) as tester:
        results = await tester.run_all_tests()
        
        # Save results to file
        with open("comprehensive_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"📄 Detailed results saved to: comprehensive_test_results.json")
        
        return results["summary"]["success_rate"] >= 75

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)