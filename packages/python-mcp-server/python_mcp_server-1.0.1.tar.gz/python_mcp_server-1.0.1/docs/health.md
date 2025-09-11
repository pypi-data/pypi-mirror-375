# Health Monitoring

Comprehensive kernel health monitoring and diagnostics for reliable Python execution in Python MCP Server v0.6.0.

## Overview

The health monitoring system provides real-time insights into kernel performance, resource usage, and responsiveness. This enables proactive maintenance and automatic recovery from failures.

## Health Metrics

### System Resources
```python
health = await client.call_tool("get_kernel_health")

print(f"Status: {health.data['status']}")           # healthy/dead/zombie
print(f"PID: {health.data['pid']}")                 # Process ID
print(f"Memory: {health.data['memory_usage']} bytes") # RAM usage
print(f"CPU: {health.data['cpu_percent']}%")         # CPU utilization
print(f"Threads: {health.data['num_threads']}")      # Thread count
print(f"Uptime: {health.data['uptime']} seconds")    # Runtime
```

### Responsiveness Testing
```python
responsive = await client.call_tool("check_kernel_responsiveness")

if responsive.data['responsive']:
    print(f"Kernel responded in {responsive.data['response_time']:.3f}s")
else:
    print("Kernel is unresponsive - consider restarting")
```

## Health States

### Healthy Kernel
```json
{
    "status": "healthy",
    "pid": 12345,
    "memory_usage": 52428800,
    "cpu_percent": 2.5,
    "num_threads": 8,
    "uptime": 3600.0
}
```

### Dead Kernel
```json
{
    "status": "dead", 
    "pid": null,
    "memory_usage": null,
    "cpu_percent": null,
    "num_threads": null,
    "uptime": null
}
```

### Zombie Kernel
```json
{
    "status": "zombie",
    "pid": 12345,
    "memory_usage": null,
    "cpu_percent": null,
    "num_threads": null,
    "uptime": null
}
```

## Monitoring Workflows

### Automated Health Checks
```python
import asyncio

async def continuous_monitoring(client, interval=30):
    """Monitor kernel health every 30 seconds"""
    while True:
        try:
            # Check current session health
            health = await client.call_tool("get_kernel_health")
            responsive = await client.call_tool("check_kernel_responsiveness")
            
            if health.data['status'] != 'healthy':
                print(f"⚠️  Unhealthy kernel detected: {health.data['status']}")
                await handle_unhealthy_kernel(client, health.data)
            
            if not responsive.data['responsive']:
                print(f"⚠️  Unresponsive kernel (>{responsive.data['response_time']}s)")
                await handle_unresponsive_kernel(client)
                
            # Memory usage check
            memory_mb = health.data.get('memory_usage', 0) / (1024**2)
            if memory_mb > 1000:  # 1GB threshold
                print(f"⚠️  High memory usage: {memory_mb:.1f}MB")
                
        except Exception as e:
            print(f"Health check failed: {e}")
            
        await asyncio.sleep(interval)

async def handle_unhealthy_kernel(client, health_data):
    """Handle unhealthy kernel states"""
    if health_data['status'] in ['dead', 'zombie']:
        print("🔄 Restarting unhealthy kernel...")
        await client.call_tool("restart_kernel")
        
        # Verify restart
        await asyncio.sleep(2)
        new_health = await client.call_tool("get_kernel_health")
        if new_health.data['status'] == 'healthy':
            print("✅ Kernel restart successful")
        else:
            print("❌ Kernel restart failed")

async def handle_unresponsive_kernel(client):
    """Handle unresponsive kernel"""
    print("🔄 Restarting unresponsive kernel...")
    await client.call_tool("restart_kernel")
```

### Multi-Session Health Monitoring
```python
async def monitor_all_sessions(client):
    """Check health of all active sessions"""
    sessions = await client.call_tool("list_sessions")
    current_session = sessions.data['active_session']
    
    health_report = {}
    
    for session_id in sessions.data['sessions'].keys():
        # Switch to each session for health check
        await client.call_tool("switch_session", {"session_id": session_id})
        
        health = await client.call_tool("get_kernel_health")
        responsive = await client.call_tool("check_kernel_responsiveness")
        
        health_report[session_id] = {
            'status': health.data['status'],
            'responsive': responsive.data['responsive'],
            'memory_mb': health.data.get('memory_usage', 0) / (1024**2),
            'cpu_percent': health.data.get('cpu_percent', 0),
            'uptime_hours': health.data.get('uptime', 0) / 3600
        }
    
    # Switch back to original session
    await client.call_tool("switch_session", {"session_id": current_session})
    
    # Print report
    print("\n📊 Session Health Report")
    print("-" * 50)
    for session_id, metrics in health_report.items():
        status_emoji = "✅" if metrics['status'] == 'healthy' else "❌"
        responsive_emoji = "🟢" if metrics['responsive'] else "🔴"
        
        print(f"{status_emoji} {session_id}")
        print(f"   Status: {metrics['status']}")
        print(f"   Responsive: {responsive_emoji}")
        print(f"   Memory: {metrics['memory_mb']:.1f} MB")
        print(f"   CPU: {metrics['cpu_percent']:.1f}%")
        print(f"   Uptime: {metrics['uptime_hours']:.1f} hours")
        print()
    
    return health_report
```

## Performance Optimization

### Memory Management
```python
async def optimize_memory_usage(client):
    """Optimize memory usage in current session"""
    
    # Check current memory usage
    health = await client.call_tool("get_kernel_health")
    initial_memory = health.data.get('memory_usage', 0)
    
    print(f"Initial memory usage: {initial_memory / (1024**2):.1f} MB")
    
    # Run garbage collection
    await client.call_tool("run_python_code", {
        "code": """
import gc
import sys

# Force garbage collection
collected = gc.collect()
print(f"Garbage collected: {collected} objects")

# Get memory info
import psutil
import os
process = psutil.Process(os.getpid())
print(f"Memory usage: {process.memory_info().rss / (1024**2):.1f} MB")

# Clear large variables (example)
# del large_dataframe, big_array  # Uncomment as needed
"""
    })
    
    # Check memory after optimization
    health = await client.call_tool("get_kernel_health")
    final_memory = health.data.get('memory_usage', 0)
    
    saved_mb = (initial_memory - final_memory) / (1024**2)
    print(f"Final memory usage: {final_memory / (1024**2):.1f} MB")
    print(f"Memory saved: {saved_mb:.1f} MB")
```

### CPU Monitoring
```python
async def monitor_cpu_usage(client, duration=60):
    """Monitor CPU usage over time"""
    samples = []
    
    for i in range(duration):
        health = await client.call_tool("get_kernel_health")
        cpu_percent = health.data.get('cpu_percent', 0)
        samples.append(cpu_percent)
        
        print(f"CPU Usage: {cpu_percent:.1f}%", end='\r')
        await asyncio.sleep(1)
    
    # Analyze CPU usage
    avg_cpu = sum(samples) / len(samples)
    max_cpu = max(samples)
    
    print(f"\n📈 CPU Analysis ({duration}s)")
    print(f"Average CPU: {avg_cpu:.1f}%")
    print(f"Peak CPU: {max_cpu:.1f}%")
    
    if avg_cpu > 50:
        print("⚠️  High average CPU usage detected")
    if max_cpu > 90:
        print("⚠️  CPU spikes detected")
```

## Alerting System

### Custom Health Alerts
```python
class HealthAlert:
    def __init__(self, client):
        self.client = client
        self.alerts = []
    
    async def check_alerts(self):
        """Check for alert conditions"""
        health = await self.client.call_tool("get_kernel_health")
        responsive = await self.client.call_tool("check_kernel_responsiveness")
        
        # Memory alert
        memory_mb = health.data.get('memory_usage', 0) / (1024**2)
        if memory_mb > 500:
            self.alerts.append(f"High memory usage: {memory_mb:.1f}MB")
        
        # CPU alert  
        cpu_percent = health.data.get('cpu_percent', 0)
        if cpu_percent > 80:
            self.alerts.append(f"High CPU usage: {cpu_percent:.1f}%")
        
        # Responsiveness alert
        if not responsive.data['responsive']:
            response_time = responsive.data['response_time']
            self.alerts.append(f"Slow response: {response_time:.2f}s")
        
        # Status alert
        if health.data['status'] != 'healthy':
            self.alerts.append(f"Unhealthy kernel: {health.data['status']}")
        
        return self.alerts
    
    async def send_alerts(self):
        """Send alerts (customize for your notification system)"""
        if self.alerts:
            print("🚨 HEALTH ALERTS:")
            for alert in self.alerts:
                print(f"   • {alert}")
            
            # Clear alerts after sending
            self.alerts.clear()

# Usage
alert_system = HealthAlert(client)
alerts = await alert_system.check_alerts()
await alert_system.send_alerts()
```

## Recovery Strategies

### Automatic Recovery
```python
async def smart_recovery(client):
    """Intelligent kernel recovery based on health status"""
    
    health = await client.call_tool("get_kernel_health")
    responsive = await client.call_tool("check_kernel_responsiveness")
    
    if health.data['status'] == 'dead':
        print("💀 Dead kernel detected - restarting...")
        await client.call_tool("restart_kernel")
        return "restarted"
    
    elif health.data['status'] == 'zombie':
        print("🧟 Zombie kernel detected - force restart...")
        await client.call_tool("restart_kernel") 
        return "force_restarted"
    
    elif not responsive.data['responsive']:
        print("🐌 Unresponsive kernel - attempting restart...")
        await client.call_tool("restart_kernel")
        return "responsiveness_restart"
    
    else:
        memory_mb = health.data.get('memory_usage', 0) / (1024**2)
        if memory_mb > 1000:  # 1GB
            print("🗄️ High memory usage - performing cleanup...")
            await optimize_memory_usage(client)
            return "memory_cleanup"
    
    return "healthy"
```

### Progressive Recovery
```python
async def progressive_recovery(client, max_attempts=3):
    """Progressive recovery with escalating interventions"""
    
    for attempt in range(max_attempts):
        health = await client.call_tool("get_kernel_health")
        
        if health.data['status'] == 'healthy':
            print("✅ Kernel is healthy")
            return True
        
        print(f"🔄 Recovery attempt {attempt + 1}/{max_attempts}")
        
        if attempt == 0:
            # First attempt: gentle cleanup
            await optimize_memory_usage(client)
            
        elif attempt == 1:
            # Second attempt: restart kernel
            await client.call_tool("restart_kernel")
            
        else:
            # Final attempt: recreate session
            sessions = await client.call_tool("list_sessions")
            current_session = sessions.data['active_session']
            
            if current_session != 'default':
                await client.call_tool("delete_session", {"session_id": current_session})
                await client.call_tool("create_session", {"session_id": current_session})
        
        # Wait before next check
        await asyncio.sleep(5)
    
    print("❌ Recovery failed after all attempts")
    return False
```

## Best Practices

1. **Regular Monitoring**: Check health every 30-60 seconds
2. **Memory Thresholds**: Alert at 500MB, cleanup at 1GB  
3. **Response Time Limits**: Restart if >5 seconds unresponsive
4. **Progressive Recovery**: Try gentle fixes before drastic measures
5. **Session Isolation**: Use separate sessions for critical workflows
6. **Cleanup Automation**: Implement automatic resource cleanup

The health monitoring system ensures reliable, production-ready Python execution with proactive issue detection and automatic recovery.