import sqlite3
import os
from typing import Dict, Any

class OmsRepository:
    """
    Отвечает за сохранение и загрузку состояния ордеров (orders)
    в персистентное хранилище (база данных SQLite).
    """
    def __init__(self, db_path: str):
        """
        Инициализирует репозиторий с путем к файлу базы данных.

        Args:
            db_path (str): Путь к файлу .db, где хранится состояние OMS.
        """
        self._db_path = db_path
        # Убедимся, что директория для файла существует
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        self._create_table()

    def _create_table(self):
        """Создает таблицу orders в БД, если она не существует."""
        conn = None
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    order_id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    status TEXT NOT NULL,
                    order_type TEXT NOT NULL,
                    margin REAL NOT NULL,
                    leverage INTEGER NOT NULL,
                    entry_price REAL NOT NULL,
                    exit_price REAL,
                    stop_loss REAL,
                    take_profit REAL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
            """)
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error in _create_table: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def load(self) -> Dict[str, Dict[str, Any]]:
        """
        Загружает все ордера из базы данных SQLite.

        Returns:
            Словарь с состоянием ордеров, где ключ - order_id.
            Возвращает пустой словарь, если таблица пуста или произошла ошибка.
        """
        orders = {}
        conn = None
        try:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders")
            rows = cursor.fetchall()
            for row in rows:
                orders[row['order_id']] = dict(row)
        except sqlite3.Error as e:
            print(f"Database error in load: {e}")
            return {}
        finally:
            if conn:
                conn.close()
        return orders

    def save(self, order: Dict[str, Any]):
        """
        Сохраняет или обновляет один ордер в базе данных.
        Использует 'INSERT OR REPLACE' для атомарности.

        Args:
            order: Словарь, представляющий один ордер.
        """
        conn = None
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            
            # Определяем колонки и плейсхолдеры на основе ключей словаря
            columns = ', '.join(order.keys())
            placeholders = ', '.join('?' * len(order))
            sql = f"INSERT OR REPLACE INTO orders ({columns}) VALUES ({placeholders})"
            
            # Убедимся, что значения передаются в правильном порядке
            values = [order.get(key) for key in order.keys()]
            
            cursor.execute(sql, values)
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error in save: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    def delete(self, order_id: str):
        """
        Удаляет ордер из базы данных по его ID.

        Args:
            order_id: ID ордера для удаления.
        """
        conn = None
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error in delete: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()