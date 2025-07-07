#!/usr/bin/env python3
"""
GPU Memory Monitor for Discord AI Bot
Monitors memory usage of TTS, STT, and overall GPU health
"""

import requests
import subprocess
import json
import time
import argparse

def get_nvidia_smi_info():
    """Get GPU memory info from nvidia-smi"""
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=memory.used,memory.total,utilization.gpu', '--format=csv,noheader,nounits'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            gpu_info = []
            for line in lines:
                used, total, util = line.split(', ')
                gpu_info.append({
                    'memory_used_mb': int(used),
                    'memory_total_mb': int(total),
                    'utilization_percent': int(util),
                    'memory_used_gb': round(int(used) / 1024, 2),
                    'memory_total_gb': round(int(total) / 1024, 2),
                    'memory_usage_percent': round((int(used) / int(total)) * 100, 1)
                })
            return gpu_info
        else:
            return None
    except Exception as e:
        print(f"Error getting nvidia-smi info: {e}")
        return None

def check_service_memory(service_name, port):
    """Check memory usage of a specific service"""
    try:
        response = requests.get(f'http://localhost:{port}/memory_status', timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def check_service_health(service_name, port):
    """Check if service is running"""
    try:
        response = requests.get(f'http://localhost:{port}/health', timeout=5)
        return response.status_code == 200
    except:
        return False

def print_memory_report():
    """Print comprehensive memory report"""
    print("\n" + "="*60)
    print("GPU Memory Report for Discord AI Bot")
    print("="*60)
    
    # GPU Overall Status
    gpu_info = get_nvidia_smi_info()
    if gpu_info:
        for i, gpu in enumerate(gpu_info):
            print(f"\nGPU {i} Overall Status:")
            print(f"  Memory: {gpu['memory_used_gb']:.2f} GB / {gpu['memory_total_gb']:.2f} GB ({gpu['memory_usage_percent']}%)")
            print(f"  Utilization: {gpu['utilization_percent']}%")
    else:
        print("\nGPU Status: Unable to get GPU information")
    
    # Service Status
    services = [
        ("STT (Whisper)", 5000),
        ("TTS (SpeechT5)", 5001),
        ("LLM (Ollama)", 11434)
    ]
    
    print("\nService Status:")
    for service_name, port in services:
        is_healthy = check_service_health(service_name, port)
        health_status = "✅ RUNNING" if is_healthy else "❌ DOWN"
        print(f"  {service_name:20} {health_status}")
        
        if is_healthy and port in [5000, 5001]:  # Only our custom services have memory endpoint
            memory_info = check_service_memory(service_name, port)
            if "gpu_memory" in memory_info and isinstance(memory_info["gpu_memory"], dict):
                mem = memory_info["gpu_memory"]
                print(f"    Memory: {mem.get('allocated_gb', 'N/A')} GB allocated ({mem.get('usage_percent', 'N/A')}%)")
    
    # Memory Recommendations
    if gpu_info:
        total_usage = gpu_info[0]['memory_usage_percent']
        print(f"\nMemory Recommendations:")
        if total_usage > 90:
            print("  🔴 CRITICAL: GPU memory usage is very high!")
            print("     - Restart services to free memory")
            print("     - Consider using smaller models")
        elif total_usage > 75:
            print("  🟡 WARNING: GPU memory usage is high")
            print("     - Monitor for potential OOM errors")
            print("     - Consider restarting services periodically")
        else:
            print("  🟢 GOOD: GPU memory usage is within safe limits")

def monitor_continuous(interval=10):
    """Continuously monitor memory usage"""
    print(f"Starting continuous monitoring (updating every {interval}s)")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            print_memory_report()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

def main():
    parser = argparse.ArgumentParser(description='Monitor GPU memory usage for Discord AI Bot')
    parser.add_argument('--continuous', '-c', action='store_true', help='Continuous monitoring mode')
    parser.add_argument('--interval', '-i', type=int, default=10, help='Update interval for continuous mode (seconds)')
    
    args = parser.parse_args()
    
    if args.continuous:
        monitor_continuous(args.interval)
    else:
        print_memory_report()

if __name__ == '__main__':
    main()
