import csv
import os
from datetime import datetime
from typing import Optional, Dict, List

class TradeLogRepository:
    """
    Репозиторий для управления персистентностью лога сделок (trade_log.csv).
    Инкапсулирует всю логику чтения и записи, следуя паттерну Repository.
    """
    def __init__(self, file_path: str = 'data/trade_log.csv'):
        self.file_path = file_path
        self.header = ['timestamp', 'order_id', 'symbol', 'order_type', 'price', 'quantity', 'status']
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """
        Убеждается, что файл лога и директория существуют.
        Если файл не существует, создает его и записывает заголовок.
        """
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self.header)

    def get_last_record(self) -> Optional[Dict[str, str]]:
        """
        Читает последнюю значащую запись из CSV-лога.
        Пропускает пустые строки.
        """
        try:
            with open(self.file_path, 'r', newline='') as f:
                reader = csv.DictReader(f)
                last_record = None
                for row in reader:
                    # Проверяем, что строка не пустая и содержит значения
                    if any(field for field in row.values()):
                        last_record = row
                return last_record
        except FileNotFoundError:
            # Этот случай обрабатывается в _ensure_file_exists, но для надежности
            return None
        except Exception as e:
            # В будущем здесь будет логирование
            print(f"Error reading trade log: {e}")
            return None

    def add_record(self, record_data: Dict[str, any]):
        """
        Добавляет новую запись в конец CSV-файла.
        
        Args:
            record_data: Словарь с данными для записи. 
                         Ключи должны соответствовать self.header.
        """
        # Устанавливаем timestamp, если он не предоставлен
        if 'timestamp' not in record_data:
            record_data['timestamp'] = datetime.utcnow().isoformat()

        try:
            with open(self.file_path, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.header)
                writer.writerow(record_data)
        except Exception as e:
            # В будущем здесь будет логирование
            print(f"Error writing to trade log: {e}")
