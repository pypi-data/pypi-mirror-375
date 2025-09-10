"""
Health Check System for CausalLLM

Provides comprehensive health monitoring for system components,
dependencies, and operational status.
"""

import time
import asyncio
import threading
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum
import psutil
import requests
from datetime import datetime, timedelta


class HealthStatus(Enum):
    """Health check status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded" 
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    name: str
    status: HealthStatus
    message: str
    duration_ms: float
    timestamp: datetime
    details: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'status': self.status.value,
            'message': self.message,
            'duration_ms': self.duration_ms,
            'timestamp': self.timestamp.isoformat(),
            'details': self.details or {}
        }


class HealthCheck:
    """Base class for health checks."""
    
    def __init__(self, name: str, timeout: float = 30.0, interval: float = 60.0):
        self.name = name
        self.timeout = timeout
        self.interval = interval
    
    async def check(self) -> HealthCheckResult:
        """Perform the health check."""
        start_time = time.time()
        
        try:
            status, message, details = await asyncio.wait_for(
                self._perform_check(), 
                timeout=self.timeout
            )
            duration_ms = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                name=self.name,
                status=status,
                message=message,
                duration_ms=duration_ms,
                timestamp=datetime.now(),
                details=details
            )
        except asyncio.TimeoutError:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check timed out after {self.timeout}s",
                duration_ms=duration_ms,
                timestamp=datetime.now()
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                duration_ms=duration_ms,
                timestamp=datetime.now()
            )
    
    async def _perform_check(self) -> tuple[HealthStatus, str, Optional[Dict[str, Any]]]:
        """Override this method to implement the actual health check."""
        raise NotImplementedError("Subclasses must implement _perform_check")


class SystemResourcesHealthCheck(HealthCheck):
    """Health check for system resources (CPU, memory, disk)."""
    
    def __init__(self, cpu_threshold: float = 90.0, memory_threshold: float = 90.0, 
                 disk_threshold: float = 90.0, **kwargs):
        super().__init__("system_resources", **kwargs)
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.disk_threshold = disk_threshold
    
    async def _perform_check(self) -> tuple[HealthStatus, str, Optional[Dict[str, Any]]]:
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        details = {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'disk_percent': (disk.used / disk.total) * 100,
            'thresholds': {
                'cpu': self.cpu_threshold,
                'memory': self.memory_threshold,
                'disk': self.disk_threshold
            }
        }
        
        issues = []
        if cpu_percent > self.cpu_threshold:
            issues.append(f"CPU usage high: {cpu_percent:.1f}%")
        if memory.percent > self.memory_threshold:
            issues.append(f"Memory usage high: {memory.percent:.1f}%")
        if (disk.used / disk.total) * 100 > self.disk_threshold:
            issues.append(f"Disk usage high: {(disk.used / disk.total) * 100:.1f}%")
        
        if issues:
            return HealthStatus.DEGRADED, f"Resource issues: {'; '.join(issues)}", details
        else:
            return HealthStatus.HEALTHY, "System resources within normal ranges", details


class DatabaseHealthCheck(HealthCheck):
    """Health check for database connectivity."""
    
    def __init__(self, connection_string: str = None, **kwargs):
        super().__init__("database", **kwargs)
        self.connection_string = connection_string
    
    async def _perform_check(self) -> tuple[HealthStatus, str, Optional[Dict[str, Any]]]:
        if not self.connection_string:
            return HealthStatus.UNKNOWN, "No database connection configured", None
        
        # This is a placeholder implementation
        # In a real scenario, you'd connect to your actual database
        try:
            # Simulate database check
            await asyncio.sleep(0.1)  # Simulate connection time
            return HealthStatus.HEALTHY, "Database connection successful", {
                'connection_string': self.connection_string.split('@')[-1] if '@' in self.connection_string else 'localhost'
            }
        except Exception as e:
            return HealthStatus.UNHEALTHY, f"Database connection failed: {str(e)}", None


class LLMProviderHealthCheck(HealthCheck):
    """Health check for LLM provider APIs."""
    
    def __init__(self, provider: str = "openai", api_key: Optional[str] = None, **kwargs):
        super().__init__(f"llm_provider_{provider}", **kwargs)
        self.provider = provider
        self.api_key = api_key
    
    async def _perform_check(self) -> tuple[HealthStatus, str, Optional[Dict[str, Any]]]:
        if not self.api_key:
            return HealthStatus.UNKNOWN, f"No API key configured for {self.provider}", None
        
        try:
            # Test a minimal API call to check connectivity
            if self.provider == "openai":
                # This is a simplified check - in practice you'd make an actual API call
                await asyncio.sleep(0.2)  # Simulate API call
                return HealthStatus.HEALTHY, f"{self.provider} API accessible", {
                    'provider': self.provider,
                    'api_configured': True
                }
            else:
                return HealthStatus.UNKNOWN, f"Health check not implemented for {self.provider}", None
                
        except Exception as e:
            return HealthStatus.UNHEALTHY, f"{self.provider} API check failed: {str(e)}", None


class ComponentHealthCheck(HealthCheck):
    """Health check for internal CausalLLM components."""
    
    def __init__(self, component_name: str, check_function: Callable, **kwargs):
        super().__init__(f"component_{component_name}", **kwargs)
        self.component_name = component_name
        self.check_function = check_function
    
    async def _perform_check(self) -> tuple[HealthStatus, str, Optional[Dict[str, Any]]]:
        try:
            result = await asyncio.create_task(
                asyncio.to_thread(self.check_function)
            )
            
            if result is True:
                return HealthStatus.HEALTHY, f"Component {self.component_name} is healthy", None
            elif isinstance(result, tuple) and len(result) >= 2:
                status, message = result[:2]
                details = result[2] if len(result) > 2 else None
                return status, message, details
            else:
                return HealthStatus.DEGRADED, f"Component {self.component_name} returned unexpected result", {'result': str(result)}
                
        except Exception as e:
            return HealthStatus.UNHEALTHY, f"Component {self.component_name} check failed: {str(e)}", None


class HealthChecker:
    """Main health checking system for CausalLLM."""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.health_checks: List[HealthCheck] = []
        self.last_results: Dict[str, HealthCheckResult] = {}
        self._background_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        # Add default health checks
        self._add_default_health_checks()
    
    def _add_default_health_checks(self) -> None:
        """Add default health checks."""
        # System resources
        self.add_health_check(SystemResourcesHealthCheck())
        
        # Database (if configured)
        # self.add_health_check(DatabaseHealthCheck())
        
        # LLM Provider (if configured)
        # self.add_health_check(LLMProviderHealthCheck())
    
    def add_health_check(self, health_check: HealthCheck) -> None:
        """Add a health check to the system."""
        if self.enabled:
            self.health_checks.append(health_check)
    
    def remove_health_check(self, name: str) -> None:
        """Remove a health check by name."""
        self.health_checks = [hc for hc in self.health_checks if hc.name != name]
        self.last_results.pop(name, None)
    
    async def run_health_check(self, name: str) -> Optional[HealthCheckResult]:
        """Run a specific health check by name."""
        if not self.enabled:
            return None
            
        for health_check in self.health_checks:
            if health_check.name == name:
                result = await health_check.check()
                self.last_results[name] = result
                return result
        return None
    
    async def run_all_health_checks(self) -> Dict[str, HealthCheckResult]:
        """Run all health checks concurrently."""
        if not self.enabled:
            return {}
        
        tasks = [health_check.check() for health_check in self.health_checks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        health_results = {}
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Create a failed health check result
                health_check = self.health_checks[i]
                health_results[health_check.name] = HealthCheckResult(
                    name=health_check.name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Health check failed with exception: {str(result)}",
                    duration_ms=0,
                    timestamp=datetime.now()
                )
            else:
                health_results[result.name] = result
        
        self.last_results.update(health_results)
        return health_results
    
    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        if not self.enabled or not self.last_results:
            return {
                'status': HealthStatus.UNKNOWN.value,
                'message': 'Health checking disabled or no results available',
                'checks': {}
            }
        
        # Determine overall status
        statuses = [result.status for result in self.last_results.values()]
        
        if any(status == HealthStatus.UNHEALTHY for status in statuses):
            overall_status = HealthStatus.UNHEALTHY
            message = "One or more components are unhealthy"
        elif any(status == HealthStatus.DEGRADED for status in statuses):
            overall_status = HealthStatus.DEGRADED  
            message = "Some components are degraded"
        elif all(status == HealthStatus.HEALTHY for status in statuses):
            overall_status = HealthStatus.HEALTHY
            message = "All components are healthy"
        else:
            overall_status = HealthStatus.UNKNOWN
            message = "Health status unknown"
        
        return {
            'status': overall_status.value,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'checks': {name: result.to_dict() for name, result in self.last_results.items()}
        }
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get a summary of health check results."""
        overall = self.get_overall_health()
        
        summary = {
            'overall': overall,
            'summary': {
                'total_checks': len(self.health_checks),
                'healthy': len([r for r in self.last_results.values() if r.status == HealthStatus.HEALTHY]),
                'degraded': len([r for r in self.last_results.values() if r.status == HealthStatus.DEGRADED]),
                'unhealthy': len([r for r in self.last_results.values() if r.status == HealthStatus.UNHEALTHY]),
                'unknown': len([r for r in self.last_results.values() if r.status == HealthStatus.UNKNOWN])
            }
        }
        
        return summary
    
    async def start_background_monitoring(self, interval: float = 60.0) -> None:
        """Start background health monitoring."""
        if not self.enabled or self._background_task is not None:
            return
        
        async def background_monitor():
            while not self._shutdown_event.is_set():
                try:
                    await self.run_all_health_checks()
                except Exception:
                    pass  # Log error in production
                
                try:
                    await asyncio.wait_for(
                        self._shutdown_event.wait(), 
                        timeout=interval
                    )
                except asyncio.TimeoutError:
                    continue  # Continue monitoring
                break
        
        self._background_task = asyncio.create_task(background_monitor())
    
    async def stop_background_monitoring(self) -> None:
        """Stop background health monitoring."""
        if self._background_task is not None:
            self._shutdown_event.set()
            try:
                await asyncio.wait_for(self._background_task, timeout=5.0)
            except asyncio.TimeoutError:
                self._background_task.cancel()
            self._background_task = None
            self._shutdown_event.clear()


# Global health checker instance
_global_health_checker: Optional[HealthChecker] = None


def get_global_health_checker() -> HealthChecker:
    """Get the global health checker instance."""
    global _global_health_checker
    if _global_health_checker is None:
        _global_health_checker = HealthChecker()
    return _global_health_checker


def configure_health_checker(enabled: bool = True) -> HealthChecker:
    """Configure the global health checker."""
    global _global_health_checker
    _global_health_checker = HealthChecker(enabled=enabled)
    return _global_health_checker