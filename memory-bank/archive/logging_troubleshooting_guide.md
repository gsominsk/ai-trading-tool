# Диагностика остановки торгового сервиса - Пошаговое руководство

## 🎯 Ситуация: Сервис не работает после недели отсутствия

### **STEP 1: Быстрая диагностика (30 секунд)**

```bash
# Одна команда покажет точную причину остановки
sudo journalctl -u your-trading-service -p err --since "1 week ago" | tail -5

# Проверка статуса сервиса
systemctl status your-trading-service
```

**Ожидаемый результат:**
```
Jan 12 14:23:15 server trading_bot[1234]: CRITICAL: Failed to configure file logging - shutting down service: [Errno 28] No space left on device
● trading-service.service - AI Trading Bot
   Active: failed (Result: exit-code)
   Main PID: 1234 (code=exited, status=1)
```

---

### **STEP 2: Анализ причины остановки**

#### **2.1 Проверка системных логов**
```bash
# Подробные логи за период
sudo journalctl -u your-trading-service --since "1 week ago" --until now

# Только критические ошибки
sudo journalctl -u your-trading-service -p err --since "1 week ago"

# Последние 50 записей с timestamp
sudo journalctl -u your-trading-service -n 50 --no-pager
```

#### **2.2 Проверка времени остановки**
```bash
# Точное время последнего запуска/остановки
systemctl show your-trading-service --property=ActiveEnterTimestamp,InactiveEnterTimestamp

# Exit code процесса (должен быть 1 для logging halt)
systemctl show your-trading-service --property=ExecMainStatus
```

---

### **STEP 3: Определение конкретной проблемы**

#### **3.1 Нехватка места на диске (90% случаев)**
```bash
# Проверка свободного места
df -h

# Размер файлов логов
du -sh /path/to/logs/*

# Поиск больших файлов
find /path/to/logs -size +100M -ls

# Проверка inodes (может закончиться место под файлы)
df -i
```

**Если видите в логах:**
```
CRITICAL: Failed to configure file logging - shutting down service: [Errno 28] No space left on device
```

**Решение:**
```bash
# Удалить старые ротированные логи
sudo rm /path/to/logs/trading.log.*.gz

# Очистить текущий лог (осторожно!)
sudo truncate -s 0 /path/to/logs/trading.log

# Настроить более агрессивную ротацию
sudo nano /etc/logrotate.d/trading-service
```

#### **3.2 Проблемы с правами доступа**
```bash
# Проверка прав на директорию и файлы
ls -la /path/to/logs/

# Владелец процесса vs владелец файлов
ps aux | grep trading
id trading-user
```

**Если видите в логах:**
```
CRITICAL: Failed to configure file logging - shutting down service: [Errno 13] Permission denied
```

**Решение:**
```bash
# Исправить владельца
sudo chown -R trading-user:trading-group /path/to/logs/

# Исправить права
sudo chmod 755 /path/to/logs/
sudo chmod 644 /path/to/logs/*.log
```

#### **3.3 Файловая система read-only**
```bash
# Проверка монтирования
mount | grep /path/to/logs

# Проверка ошибок файловой системы
dmesg | grep -i "remounted.*read-only"
```

**Если видите в логах:**
```
CRITICAL: Failed to configure file logging - shutting down service: [Errno 30] Read-only file system
```

**Решение:**
```bash
# Перемонтировать в read-write
sudo mount -o remount,rw /path/to/logs

# Проверить целостность файловой системы
sudo fsck /dev/sdX
```

---

### **STEP 4: Проверка файлов логов приложения**

```bash
# Основные логи торговли (последние записи перед остановкой)
tail -100 /path/to/logs/trading.log

# Логи ошибок системы логирования (fallback)
tail -100 /path/to/logs/logging_errors.log

# Поиск по времени остановки
grep "Jan 12 14:23" /path/to/logs/*.log

# Ротированные логи
ls -la /path/to/logs/trading.log.*
zcat /path/to/logs/trading.log.1.gz | tail -100
```

---

### **STEP 5: Дополнительная диагностика системы**

#### **5.1 Проверка памяти и ресурсов**
```bash
# OOM killer (нехватка памяти)
dmesg | grep -i "killed process"
grep -i "out of memory" /var/log/syslog

# Системные события в момент падения
dmesg | grep -A5 -B5 "Jan 12 14:23"
```

#### **5.2 Проверка дисковых ошибок**
```bash
# I/O ошибки диска
dmesg | grep -i "i/o error"

# SMART статус диска
sudo smartctl -a /dev/sdX
```

#### **5.3 Проверка SELinux/AppArmor**
```bash
# SELinux блокировки
sudo ausearch -m avc -ts recent

# AppArmor блокировки
sudo dmesg | grep -i apparmor
```

---

### **STEP 6: Восстановление сервиса**

#### **6.1 Быстрое восстановление**
```bash
# 1. Решить проблему (освободить место/исправить права)
sudo rm /path/to/logs/trading.log.*.gz  # если место
sudo chown trading-user:trading-group /path/to/logs/  # если права

# 2. Проверить конфигурацию
sudo -u trading-user python3 -c "
import logging
logging.basicConfig(filename='/path/to/logs/test.log', level=logging.INFO)
logging.info('Test log entry')
print('Logging test successful')
"

# 3. Перезапустить сервис
sudo systemctl start your-trading-service

# 4. Проверить статус
sudo systemctl status your-trading-service
```

#### **6.2 Мониторинг восстановления**
```bash
# Следить за логами в реальном времени
sudo journalctl -u your-trading-service -f

# Проверить что логи создаются
tail -f /path/to/logs/trading.log

# Убедиться что торговля работает
grep "Trading operation" /path/to/logs/trading.log | tail -5
```

---

### **STEP 7: Предотвращение повторных проблем**

#### **7.1 Настройка мониторинга**
```bash
# Создать скрипт мониторинга места на диске
cat > /usr/local/bin/check-disk-space.sh << 'EOF'
#!/bin/bash
USAGE=$(df /path/to/logs | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $USAGE -gt 85 ]; then
    echo "ALERT: Disk usage ${USAGE}% on /path/to/logs"
    # Можно отправить email/slack уведомление
fi
EOF

# Добавить в crontab
echo "*/15 * * * * /usr/local/bin/check-disk-space.sh" | sudo crontab -
```

#### **7.2 Улучшение ротации логов**
```bash
# Более агрессивная ротация
sudo tee /etc/logrotate.d/trading-service << 'EOF'
/path/to/logs/trading.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 trading-user trading-group
    maxsize 50M
}
EOF
```

#### **7.3 Настройка алертов**
```bash
# Мониторинг статуса сервиса
cat > /usr/local/bin/check-trading-service.sh << 'EOF'
#!/bin/bash
if ! systemctl is-active --quiet your-trading-service; then
    echo "CRITICAL: Trading service is down!"
    # Отправить уведомление
fi
EOF
```

---

## 📊 **Частые причины и их признаки**

| Ошибка | Сообщение в логах | Решение |
|--------|-------------------|---------|
| **Нет места** | `[Errno 28] No space left on device` | Очистить старые логи, настроить ротацию |
| **Нет прав** | `[Errno 13] Permission denied` | Исправить владельца/права файлов |
| **Read-only FS** | `[Errno 30] Read-only file system` | Перемонтировать, проверить fsck |
| **Директория не существует** | `[Errno 2] No such file or directory` | Создать директорию с правильными правами |
| **Нет inodes** | `[Errno 28] No space left on device` (при df -h есть место) | Удалить лишние файлы, проверить df -i |

---

## 🚨 **Критическая диагностика (если ничего не помогает)**

```bash
# Полный дамп информации о сервисе
sudo systemctl show your-trading-service > service-debug.txt

# Трассировка системных вызовов (если сервис запускается но сразу падает)
sudo strace -f -o strace.log systemctl start your-trading-service

# Проверка всех процессов и открытых файлов
sudo lsof | grep trading
sudo netstat -tulpn | grep trading
```

---

## ✅ **Чеклист успешной диагностики**

- [ ] Найдено точное время остановки
- [ ] Определена причина из CRITICAL сообщения  
- [ ] Проверено место на диске и права доступа
- [ ] Устранена основная проблема
- [ ] Сервис успешно перезапущен
- [ ] Логи снова создаются
- [ ] Торговые операции работают
- [ ] Настроен мониторинг для предотвращения повторения

---

**💡 Главное преимущество простой системы:** Одна команда `journalctl` покажет точную причину остановки без изучения сложных логов!

--- Appended on Thu Aug  7 00:03:19 EEST 2025 ---


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

--- Appended on Thu Aug  7 00:03:27 EEST 2025 ---


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