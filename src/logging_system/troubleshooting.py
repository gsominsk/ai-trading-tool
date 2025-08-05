"""
Troubleshooting utilities for logging system failures
Помощник для диагностики сбоев системы логирования
"""

import subprocess
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple


def check_service_status(service_name: str) -> Dict[str, str]:
    """
    Проверка статуса сервиса и причины остановки
    
    Args:
        service_name: Имя systemd сервиса (например: 'trading-service')
    
    Returns:
        Dictionary с информацией о статусе сервиса
    """
    result = {}
    
    try:
        # Статус сервиса
        status_cmd = f"systemctl status {service_name}"
        status_output = subprocess.run(status_cmd.split(), capture_output=True, text=True)
        result['status'] = status_output.stdout
        result['status_code'] = status_output.returncode
        
        # Время последней активности
        show_cmd = f"systemctl show {service_name} --property=ActiveEnterTimestamp,InactiveEnterTimestamp,ExecMainStatus"
        show_output = subprocess.run(show_cmd.split(), capture_output=True, text=True)
        result['timestamps'] = show_output.stdout
        
        # Последние критические ошибки
        since_week = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        journal_cmd = f"journalctl -u {service_name} -p err --since {since_week}"
        journal_output = subprocess.run(journal_cmd.split(), capture_output=True, text=True)
        result['critical_errors'] = journal_output.stdout
        
    except Exception as e:
        result['error'] = f"Failed to check service status: {e}"
    
    return result


def check_disk_space(log_path: str) -> Dict[str, any]:
    """
    Проверка места на диске для логов
    
    Args:
        log_path: Путь к директории с логами
    
    Returns:
        Dictionary с информацией о дисковом пространстве
    """
    result = {}
    
    try:
        # Общее место на диске
        df_output = subprocess.run(['df', '-h', log_path], capture_output=True, text=True)
        result['disk_usage'] = df_output.stdout
        
        # Размер файлов логов
        if os.path.exists(log_path):
            du_output = subprocess.run(['du', '-sh', f"{log_path}/*"], capture_output=True, text=True, shell=True)
            result['log_sizes'] = du_output.stdout
            
            # Проверка inodes
            df_inodes = subprocess.run(['df', '-i', log_path], capture_output=True, text=True)
            result['inodes'] = df_inodes.stdout
            
            # Поиск больших файлов
            find_cmd = f"find {log_path} -size +100M -ls"
            find_output = subprocess.run(find_cmd.split(), capture_output=True, text=True)
            result['large_files'] = find_output.stdout
        else:
            result['error'] = f"Log directory {log_path} does not exist"
            
    except Exception as e:
        result['error'] = f"Failed to check disk space: {e}"
    
    return result


def check_permissions(log_path: str, user: str = None) -> Dict[str, str]:
    """
    Проверка прав доступа к файлам логов
    
    Args:
        log_path: Путь к директории с логами
        user: Пользователь сервиса (опционально)
    
    Returns:
        Dictionary с информацией о правах доступа
    """
    result = {}
    
    try:
        if os.path.exists(log_path):
            # Права на директорию
            ls_output = subprocess.run(['ls', '-la', log_path], capture_output=True, text=True)
            result['permissions'] = ls_output.stdout
            
            # Проверка владельца файлов
            stat_output = subprocess.run(['stat', log_path], capture_output=True, text=True)
            result['ownership'] = stat_output.stdout
            
            if user:
                # Информация о пользователе
                id_output = subprocess.run(['id', user], capture_output=True, text=True)
                result['user_info'] = id_output.stdout
        else:
            result['error'] = f"Log directory {log_path} does not exist"
            
    except Exception as e:
        result['error'] = f"Failed to check permissions: {e}"
    
    return result


def analyze_log_errors(log_path: str, hours_back: int = 24) -> List[str]:
    """
    Анализ ошибок в логах за указанный период
    
    Args:
        log_path: Путь к директории с логами
        hours_back: Количество часов назад для анализа
    
    Returns:
        List критических ошибок системы логирования
    """
    critical_patterns = [
        "CRITICAL: Logging system failed",
        "CRITICAL: Failed to configure file logging", 
        "[Errno 28] No space left on device",
        "[Errno 13] Permission denied",
        "[Errno 30] Read-only file system",
        "[Errno 2] No such file or directory"
    ]
    
    errors = []
    
    try:
        if os.path.exists(log_path):
            # Поиск в основных логах
            for log_file in ['trading.log', 'logging_errors.log']:
                file_path = os.path.join(log_path, log_file)
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        lines = f.readlines()
                        for line in lines:
                            for pattern in critical_patterns:
                                if pattern in line:
                                    errors.append(f"{log_file}: {line.strip()}")
                                    
            # Поиск в ротированных логах
            for i in range(1, 8):  # Проверить последние 7 ротированных файлов
                rotated_file = os.path.join(log_path, f"trading.log.{i}")
                if os.path.exists(rotated_file):
                    try:
                        # Попытка прочитать сжатый файл
                        if rotated_file.endswith('.gz'):
                            import gzip
                            with gzip.open(rotated_file, 'rt') as f:
                                lines = f.readlines()
                        else:
                            with open(rotated_file, 'r') as f:
                                lines = f.readlines()
                                
                        for line in lines:
                            for pattern in critical_patterns:
                                if pattern in line:
                                    errors.append(f"trading.log.{i}: {line.strip()}")
                    except:
                        continue
                        
    except Exception as e:
        errors.append(f"Error analyzing logs: {e}")
    
    return errors


def get_quick_diagnosis(service_name: str, log_path: str) -> str:
    """
    Быстрая диагностика проблемы (30 секунд)
    
    Args:
        service_name: Имя systemd сервиса
        log_path: Путь к директории с логами
    
    Returns:
        Строка с быстрым диагнозом проблемы
    """
    diagnosis = []
    
    # 1. Проверка статуса сервиса
    service_status = check_service_status(service_name)
    if 'critical_errors' in service_status and service_status['critical_errors']:
        last_error = service_status['critical_errors'].split('\n')[-2] if service_status['critical_errors'].split('\n')[-1] == '' else service_status['critical_errors'].split('\n')[-1]
        diagnosis.append(f"🚨 ПОСЛЕДНЯЯ ОШИБКА: {last_error}")
    
    # 2. Проверка места на диске
    disk_info = check_disk_space(log_path)
    if 'disk_usage' in disk_info:
        lines = disk_info['disk_usage'].split('\n')
        if len(lines) > 1:
            usage_line = lines[1]
            if 'Use%' in lines[0]:  # Header line
                usage_percent = usage_line.split()[-2]  # Last column before mount point
                if usage_percent.rstrip('%').isdigit() and int(usage_percent.rstrip('%')) > 90:
                    diagnosis.append(f"💾 КРИТИЧНО: Диск заполнен на {usage_percent}")
    
    # 3. Проверка прав доступа
    perm_info = check_permissions(log_path)
    if 'error' in perm_info:
        diagnosis.append(f"🔒 ПРАВА: {perm_info['error']}")
    
    # 4. Анализ логов
    log_errors = analyze_log_errors(log_path, 24)
    if log_errors:
        diagnosis.append(f"📝 НАЙДЕНО ОШИБОК В ЛОГАХ: {len(log_errors)}")
        diagnosis.append(f"   Последняя: {log_errors[-1]}")
    
    if not diagnosis:
        diagnosis.append("✅ Явных проблем не обнаружено - требуется детальная диагностика")
    
    return '\n'.join(diagnosis)


def suggest_fix(service_name: str, log_path: str) -> List[str]:
    """
    Предложение решений на основе диагностики
    
    Args:
        service_name: Имя systemd сервиса
        log_path: Путь к директории с логами
    
    Returns:
        List команд для исправления проблемы
    """
    fixes = []
    
    # Анализ ошибок
    log_errors = analyze_log_errors(log_path, 24)
    disk_info = check_disk_space(log_path)
    
    for error in log_errors:
        if "No space left on device" in error:
            fixes.extend([
                "# Освобождение места на диске:",
                f"sudo rm {log_path}/trading.log.*.gz",
                f"sudo truncate -s 0 {log_path}/trading.log",
                "# Проверка результата:",
                f"df -h {log_path}"
            ])
            
        elif "Permission denied" in error:
            fixes.extend([
                "# Исправление прав доступа:",
                f"sudo chown -R $(whoami):$(whoami) {log_path}",
                f"sudo chmod 755 {log_path}",
                f"sudo chmod 644 {log_path}/*.log",
                "# Проверка результата:",
                f"ls -la {log_path}"
            ])
            
        elif "Read-only file system" in error:
            fixes.extend([
                "# Перемонтирование в read-write:",
                f"sudo mount -o remount,rw {log_path}",
                "# Проверка файловой системы:",
                "sudo fsck -f /dev/sdX  # замените X на нужный диск"
            ])
            
        elif "No such file or directory" in error:
            fixes.extend([
                "# Создание директории логов:",
                f"sudo mkdir -p {log_path}",
                f"sudo chown $(whoami):$(whoami) {log_path}",
                f"sudo chmod 755 {log_path}"
            ])
    
    # Общие команды восстановления
    fixes.extend([
        "",
        "# Перезапуск сервиса:",
        f"sudo systemctl start {service_name}",
        f"sudo systemctl status {service_name}",
        "",
        "# Проверка логов:",
        f"tail -f {log_path}/trading.log"
    ])
    
    return fixes


def main():
    """Интерактивная диагностика из командной строки"""
    if len(sys.argv) < 3:
        print("Usage: python troubleshooting.py <service_name> <log_path>")
        print("Example: python troubleshooting.py trading-service /var/log/trading")
        sys.exit(1)
    
    service_name = sys.argv[1]
    log_path = sys.argv[2]
    
    print("🔍 ДИАГНОСТИКА ТОРГОВОГО СЕРВИСА")
    print("=" * 50)
    
    # Быстрая диагностика
    print("\n📋 БЫСТРАЯ ДИАГНОСТИКА:")
    quick_diagnosis = get_quick_diagnosis(service_name, log_path)
    print(quick_diagnosis)
    
    # Предложения по исправлению
    print("\n🔧 ПРЕДЛАГАЕМЫЕ ИСПРАВЛЕНИЯ:")
    fixes = suggest_fix(service_name, log_path)
    for fix in fixes:
        print(fix)
    
    print("\n📚 Полное руководство: memory-bank/logging_troubleshooting_guide.md")


if __name__ == "__main__":
    main()