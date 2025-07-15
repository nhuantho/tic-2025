import os
import json
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

class ReportGenerator:
    """Service to generate test reports with inter-service analysis"""
    
    @staticmethod
    def generate_test_report(service_name: str, results: List[Dict[str, Any]], execution_summary: Dict[str, Any]) -> str:
        """Generate a comprehensive test report with inter-service analysis"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"test_report_{service_name}_{timestamp}.md"
        
        # Create reports directory if it doesn't exist
        reports_dir = "logs/reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        filepath = os.path.join(reports_dir, filename)
        
        # Generate markdown content
        markdown_content = ReportGenerator._generate_markdown_content(service_name, results, execution_summary)
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return filepath
    
    @staticmethod
    def generate_multi_service_report(service_configs: Dict[str, Any], results: Dict[str, Any]) -> str:
        """Generate a comprehensive multi-service test report"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"multi_service_report_{timestamp}.md"
        
        # Create reports directory if it doesn't exist
        reports_dir = "logs/reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        filepath = os.path.join(reports_dir, filename)
        
        # Generate markdown content
        markdown_content = ReportGenerator._generate_multi_service_markdown_content(service_configs, results)
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return filepath
    
    @staticmethod
    def _generate_markdown_content(service_name: str, results: List[Dict[str, Any]], execution_summary: Dict[str, Any]) -> str:
        """Generate markdown content for single service report"""
        content = f"""# 🧪 Test Execution Report - {service_name}

## 📊 Executive Summary

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Service:** {service_name}  
**Total Tests:** {execution_summary.get('total_tests', 0)}  
**Success Rate:** {execution_summary.get('success_rate', 0):.1f}%  
**Average Response Time:** {execution_summary.get('average_response_time', 0):.0f}ms

### 📈 Test Results Overview

| Status | Count | Percentage |
|--------|-------|------------|
| ✅ Passed | {execution_summary.get('passed', 0)} | {(execution_summary.get('passed', 0) / execution_summary.get('total_tests', 1) * 100):.1f}% |
| ❌ Failed | {execution_summary.get('failed', 0)} | {(execution_summary.get('failed', 0) / execution_summary.get('total_tests', 1) * 100):.1f}% |
| ⚠️ Error | {execution_summary.get('errors', 0)} | {(execution_summary.get('errors', 0) / execution_summary.get('total_tests', 1) * 100):.1f}% |

## 🔍 Inter-Service Communication Analysis

"""
        
        # Add inter-service communication analysis
        service_calls = []
        for result in results:
            calls = result.get('service_calls', [])
            service_calls.extend(calls)
        
        if service_calls:
            content += f"""
### 🌐 Service Dependencies

**Total Inter-Service Calls:** {len(service_calls)}

#### Service Call Details:
"""
            for i, call in enumerate(service_calls, 1):
                content += f"""
**Call {i}:**
- **From:** {call.get('source_service', 'unknown')}
- **To:** {call.get('target_service', 'unknown')}
- **Endpoint:** {call.get('endpoint', 'unknown')}
- **Method:** {call.get('method', 'GET')}
- **Status:** {call.get('status', 'unknown')}
- **Response Time:** {call.get('response_time', 0)}ms
"""
        else:
            content += """
### 🌐 Service Dependencies

**No inter-service communication detected in this test run.**
"""
        
        content += f"""

## 📋 Detailed Test Results

"""
        
        # Add detailed results
        for i, result in enumerate(results, 1):
            test_case = result.get('test_case', {})
            status_emoji = "✅" if result.get('status') == 'passed' else "❌" if result.get('status') == 'failed' else "⚠️"
            
            content += f"""
### {status_emoji} Test {i}: {test_case.get('name', 'Unknown Test')}

**Status:** {result.get('status', 'unknown').upper()}  
**Response Code:** {result.get('response_status_code', 'N/A')}  
**Response Time:** {result.get('response_time', 0)}ms  
**Priority:** {test_case.get('priority', 'medium')}

**Endpoint:** {test_case.get('method', 'GET')} {test_case.get('path', '')}

"""
            
            if result.get('error_message'):
                content += f"**Error:** {result.get('error_message')}\n\n"
            
            if result.get('response_body'):
                content += f"**Response Body:**\n```json\n{result.get('response_body', '')}\n```\n\n"
            
            if result.get('execution_log'):
                content += f"**Execution Log:**\n```\n{result.get('execution_log', '')}\n```\n\n"
        
        content += f"""
## 🎯 Recommendations

"""
        
        # Add recommendations based on results
        failed_tests = [r for r in results if r.get('status') == 'failed']
        error_tests = [r for r in results if r.get('status') == 'error']
        
        if failed_tests:
            content += f"""
### ❌ Failed Tests ({len(failed_tests)})
- Review the {len(failed_tests)} failed test cases above
- Check if the expected status codes match the actual API behavior
- Verify that the test data is valid and up-to-date
"""
        
        if error_tests:
            content += f"""
### ⚠️ Error Tests ({len(error_tests)})
- Investigate the {len(error_tests)} tests that encountered errors
- Check network connectivity and service availability
- Verify that all required services are running
"""
        
        if service_calls:
            content += f"""
### 🌐 Inter-Service Communication
- Monitor the {len(service_calls)} inter-service calls for performance issues
- Consider implementing circuit breakers for critical service dependencies
- Review service dependency patterns for potential optimization
"""
        
        content += f"""
## 📝 Test Environment

- **Report Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Service:** {service_name}
- **Total Tests Executed:** {execution_summary.get('total_tests', 0)}
- **Execution Duration:** Calculated from individual test response times

---
*Report generated by APITestGen - Automated API Test Generation Tool*
"""
        
        return content
    
    @staticmethod
    def _generate_multi_service_markdown_content(service_configs: Dict[str, Any], results: Dict[str, Any]) -> str:
        """Generate markdown content for multi-service report"""
        content = f"""# 🏗️ Multi-Service Test Execution Report

## 📊 Executive Summary

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Services Tested:** {len(service_configs)}  
**Total Tests:** {len(results.get('results', []))}

### 🏢 Services Overview

"""
        
        # Add service overview
        for service_name, config in service_configs.items():
            service_results = results.get('service_results', {}).get(service_name, [])
            passed = len([r for r in service_results if r.get('status') == 'passed'])
            failed = len([r for r in service_results if r.get('status') == 'failed'])
            errors = len([r for r in service_results if r.get('status') == 'error'])
            total = len(service_results)
            success_rate = (passed / total * 100) if total > 0 else 0
            
            content += f"""
#### {service_name}
- **Base URL:** {config.get('base_url', 'N/A')}
- **Tests:** {total} (✅ {passed} | ❌ {failed} | ⚠️ {errors})
- **Success Rate:** {success_rate:.1f}%
"""
        
        # Add inter-service communication analysis
        inter_service_report = results.get('inter_service_report', {})
        
        content += f"""

## 🌐 Inter-Service Communication Analysis

### 📊 Communication Overview

**Total Service Calls:** {inter_service_report.get('total_service_calls', 0)}  
**Services Involved:** {len(service_configs)}

### 🔗 Service Dependencies

"""
        
        service_dependencies = inter_service_report.get('service_dependencies', {})
        for service, dependencies in service_dependencies.items():
            if dependencies:
                content += f"""
**{service}** depends on:
"""
                for dep in dependencies:
                    content += f"- {dep}\n"
            else:
                content += f"**{service}** has no external dependencies\n"
        
        # Add communication patterns
        patterns = inter_service_report.get('communication_patterns', {})
        content += f"""

### 📈 Communication Patterns

- **Synchronous Calls:** {patterns.get('synchronous_calls', 0)}
- **Asynchronous Calls:** {patterns.get('asynchronous_calls', 0)}
- **Error Propagation:** {patterns.get('error_propagation', 0)}

### 🔍 Detailed Service Calls

"""
        
        service_calls = inter_service_report.get('service_calls', [])
        for i, call in enumerate(service_calls, 1):
            content += f"""
**Call {i}:**
- **Source:** {call.get('source_service', 'unknown')}
- **Target:** {call.get('target_service', 'unknown')}
- **Endpoint:** {call.get('endpoint', 'unknown')}
- **Method:** {call.get('method', 'GET')}
- **Status:** {call.get('status', 'unknown')}
- **Response Time:** {call.get('response_time', 0)}ms
"""
        
        content += f"""

## 📋 Detailed Test Results by Service

"""
        
        # Add detailed results by service
        for service_name, service_results in results.get('service_results', {}).items():
            content += f"""
### 🏢 {service_name}

"""
            
            for i, result in enumerate(service_results, 1):
                test_case = result.get('test_case', {})
                status_emoji = "✅" if result.get('status') == 'passed' else "❌" if result.get('status') == 'failed' else "⚠️"
                
                content += f"""
#### {status_emoji} Test {i}: {test_case.get('name', 'Unknown Test')}

**Status:** {result.get('status', 'unknown').upper()}  
**Response Code:** {result.get('response_status_code', 'N/A')}  
**Response Time:** {result.get('response_time', 0)}ms

**Endpoint:** {test_case.get('method', 'GET')} {test_case.get('path', '')}

"""
                
                if result.get('error_message'):
                    content += f"**Error:** {result.get('error_message')}\n\n"
        
        content += f"""

## 🎯 Multi-Service Recommendations

### 🔧 Architecture Recommendations

"""
        
        if service_dependencies:
            content += """
- **Service Coupling:** Review service dependencies to minimize tight coupling
- **Circuit Breakers:** Implement circuit breakers for critical service dependencies
- **Monitoring:** Add comprehensive monitoring for inter-service communication
"""
        
        if patterns.get('synchronous_calls', 0) > patterns.get('asynchronous_calls', 0):
            content += """
- **Async Communication:** Consider using asynchronous communication patterns where appropriate
- **Performance:** Synchronous calls may impact overall system performance
"""
        
        content += f"""

### 🚀 Performance Recommendations

- **Load Testing:** Conduct load testing across all services simultaneously
- **Dependency Mapping:** Create a visual dependency map for better understanding
- **Error Handling:** Implement robust error handling for inter-service failures

## 📝 Test Environment

- **Report Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Services Tested:** {', '.join(service_configs.keys())}
- **Total Tests:** {len(results.get('results', []))}

---
*Report generated by APITestGen - Multi-Service Test Generation Tool*
"""
        
        return content 