# Trading Service Logging Troubleshooting Guide

## Archive Reference
Complete troubleshooting guide (312 lines) archived in [`memory-bank/archive/logging_troubleshooting_guide.md`](memory-bank/archive/logging_troubleshooting_guide.md).

## Quick Diagnostics (30 seconds)

### **Step 1: Check Service Status**
```bash
# Show exact failure reason
sudo journalctl -u your-trading-service -p err --since "1 week ago" | tail -5
systemctl status your-trading-service
```

### **Step 2: Common Issues & Solutions**
| Error Message | Cause | Quick Fix |
|--------------|-------|-----------|
| `[Errno 28] No space left on device` | Disk full | `sudo rm /path/to/logs/*.gz` |
| `[Errno 13] Permission denied` | Wrong permissions | `sudo chown trading-user /path/to/logs/` |
| `[Errno 30] Read-only file system` | FS mounted read-only | `sudo mount -o remount,rw /path/to/logs` |

### **Step 3: Quick Recovery**
```bash
# 1. Fix the problem (space/permissions)
# 2. Test logging: python3 -c "import logging; logging.basicConfig(filename='/path/to/logs/test.log')"
# 3. Restart: sudo systemctl start your-trading-service
```

---
*Optimized 2025-08-05: Reduced from 312 lines to essential diagnostics + archive reference*