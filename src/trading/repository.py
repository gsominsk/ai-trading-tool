import json
import os
from typing import Dict, Any

class OrderRepository:
    """
    Отвечает за сохранение и загрузку состояния ордеров (orders)
    в персистентное хранилище (JSON-файл).
    """
    def __init__(self, file_path: str):
        """
        Инициализирует репозиторий с путем к файлу состояния.

        Args:
            file_path (str): Путь к файлу, где хранится состояние OMS.
        """
        self._file_path = file_path
        # Убедимся, что директория для файла существует
        os.makedirs(os.path.dirname(self._file_path), exist_ok=True)

    def load(self) -> Dict[str, Any]:
        """
        Загружает состояние ордеров из JSON-файла.

        Returns:
            Dict[str, Any]: Словарь с состоянием ордеров.
                            Возвращает пустой словарь, если файл не найден.
        """
        try:
            with open(self._file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            # В случае, если файл пуст или поврежден
            return {}

    def save(self, orders: Dict[str, Any]):
        """
        Сохраняет текущее состояние ордеров в JSON-файл.

        Args:
            orders (Dict[str, Any]): Словарь с состоянием ордеров для сохранения.
        """
        with open(self._file_path, 'w', encoding='utf-8') as f:
            json.dump(orders, f, indent=4, ensure_ascii=False)