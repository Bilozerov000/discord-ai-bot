#!/bin/bash

# Discord AI Bot Service Manager
# Manages TTS, STT services with memory optimization

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

check_gpu_memory() {
    if command -v nvidia-smi &> /dev/null; then
        local memory_usage=$(nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits | awk -F', ' '{print int(($1/$2)*100)}')
        echo $memory_usage
    else
        echo "0"
    fi
}

cleanup_gpu_memory() {
    log "Cleaning up GPU memory..."
    if command -v nvidia-smi &> /dev/null; then
        # Force cleanup of any hanging GPU processes
        nvidia-smi --gpu-reset &>/dev/null || true
    fi
    # Give some time for cleanup
    sleep 2
}

stop_service() {
    local service_name=$1
    local port=$2
    
    log "Stopping $service_name service..."
    
    # Kill processes using the port
    local pids=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pids" ]; then
        kill -TERM $pids 2>/dev/null
        sleep 3
        # Force kill if still running
        local remaining_pids=$(lsof -ti:$port 2>/dev/null)
        if [ ! -z "$remaining_pids" ]; then
            kill -KILL $remaining_pids 2>/dev/null
        fi
        success "$service_name stopped"
    else
        warning "$service_name was not running"
    fi
}

start_stt_service() {
    log "Starting optimized STT service..."
    
    # Check if port is free
    if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null; then
        error "Port 5000 is already in use"
        return 1
    fi
    
    cd "$SCRIPT_DIR"
    nohup python3 local_stt_server_optimized.py > "$LOG_DIR/stt.log" 2>&1 &
    local pid=$!
    
    # Wait a moment and check if it's still running
    sleep 3
    if kill -0 $pid 2>/dev/null; then
        success "STT service started (PID: $pid)"
        echo $pid > "$LOG_DIR/stt.pid"
        return 0
    else
        error "STT service failed to start. Check $LOG_DIR/stt.log"
        return 1
    fi
}

start_tts_service() {
    log "Starting optimized TTS service..."
    
    # Check if port is free
    if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null; then
        error "Port 5001 is already in use"
        return 1
    fi
    
    cd "$SCRIPT_DIR"
    nohup python3 local_tts_server_optimized.py > "$LOG_DIR/tts.log" 2>&1 &
    local pid=$!
    
    # Wait a moment and check if it's still running
    sleep 3
    if kill -0 $pid 2>/dev/null; then
        success "TTS service started (PID: $pid)"
        echo $pid > "$LOG_DIR/tts.pid"
        return 0
    else
        error "TTS service failed to start. Check $LOG_DIR/tts.log"
        return 1
    fi
}

check_service_health() {
    local service_name=$1
    local port=$2
    local max_attempts=10
    local attempt=1
    
    log "Checking $service_name health..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:$port/health >/dev/null 2>&1; then
            success "$service_name is healthy"
            return 0
        fi
        
        warning "Attempt $attempt/$max_attempts: $service_name not ready yet"
        sleep 2
        ((attempt++))
    done
    
    error "$service_name failed health check"
    return 1
}

restart_services() {
    log "Restarting AI services with memory optimization..."
    
    # Check initial GPU memory
    local initial_memory=$(check_gpu_memory)
    log "Initial GPU memory usage: ${initial_memory}%"
    
    # Stop services
    stop_service "TTS" 5001
    stop_service "STT" 5000
    
    # Cleanup GPU memory
    cleanup_gpu_memory
    
    # Check memory after cleanup
    local after_cleanup_memory=$(check_gpu_memory)
    log "GPU memory after cleanup: ${after_cleanup_memory}%"
    
    # Start services
    if start_stt_service && start_tts_service; then
        # Wait for services to be ready
        sleep 5
        
        # Health checks
        if check_service_health "STT" 5000 && check_service_health "TTS" 5001; then
            local final_memory=$(check_gpu_memory)
            success "All services restarted successfully!"
            log "Final GPU memory usage: ${final_memory}%"
            
            # Show memory status
            python3 "$SCRIPT_DIR/memory_monitor.py"
        else
            error "Some services failed health checks"
            return 1
        fi
    else
        error "Failed to start services"
        return 1
    fi
}

show_status() {
    log "Service Status:"
    
    # Check each service
    for service_port in "STT:5000" "TTS:5001"; do
        IFS=':' read -r name port <<< "$service_port"
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null; then
            if curl -s http://localhost:$port/health >/dev/null 2>&1; then
                success "$name is running and healthy on port $port"
            else
                warning "$name is running on port $port but not responding to health checks"
            fi
        else
            error "$name is not running on port $port"
        fi
    done
    
    # Show memory status
    echo ""
    python3 "$SCRIPT_DIR/memory_monitor.py"
}

show_logs() {
    local service=$1
    local lines=${2:-50}
    
    case $service in
        "stt")
            if [ -f "$LOG_DIR/stt.log" ]; then
                log "Last $lines lines of STT log:"
                tail -n $lines "$LOG_DIR/stt.log"
            else
                error "STT log file not found"
            fi
            ;;
        "tts")
            if [ -f "$LOG_DIR/tts.log" ]; then
                log "Last $lines lines of TTS log:"
                tail -n $lines "$LOG_DIR/tts.log"
            else
                error "TTS log file not found"
            fi
            ;;
        *)
            error "Unknown service. Use 'stt' or 'tts'"
            ;;
    esac
}

case "$1" in
    "restart")
        restart_services
        ;;
    "start")
        case "$2" in
            "stt")
                start_stt_service
                ;;
            "tts")
                start_tts_service
                ;;
            *)
                start_stt_service && start_tts_service
                ;;
        esac
        ;;
    "stop")
        case "$2" in
            "stt")
                stop_service "STT" 5000
                ;;
            "tts")
                stop_service "TTS" 5001
                ;;
            *)
                stop_service "TTS" 5001
                stop_service "STT" 5000
                ;;
        esac
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs "$2" "$3"
        ;;
    "memory")
        python3 "$SCRIPT_DIR/memory_monitor.py" "$2"
        ;;
    "monitor")
        python3 "$SCRIPT_DIR/memory_monitor.py" --continuous
        ;;
    *)
        echo "Usage: $0 {restart|start|stop|status|logs|memory|monitor} [service] [options]"
        echo ""
        echo "Commands:"
        echo "  restart              - Restart all services with memory cleanup"
        echo "  start [stt|tts]      - Start service(s)"
        echo "  stop [stt|tts]       - Stop service(s)"
        echo "  status               - Show service status and memory usage"
        echo "  logs <stt|tts> [num] - Show service logs (default: 50 lines)"
        echo "  memory               - Show current memory status"
        echo "  monitor              - Continuous memory monitoring"
        echo ""
        echo "Examples:"
        echo "  $0 restart           - Restart all services"
        echo "  $0 start stt         - Start only STT service"
        echo "  $0 logs tts 100      - Show last 100 lines of TTS logs"
        echo "  $0 monitor           - Start continuous memory monitoring"
        exit 1
        ;;
esac
