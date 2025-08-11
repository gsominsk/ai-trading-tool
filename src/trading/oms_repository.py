import sqlite3
import os
from typing import Dict, Any, Optional
from src.infrastructure.exceptions import RepositoryError
from src.logging_system.logger_config import MarketDataLogger

class OmsRepository:
    """
    Отвечает за сохранение и загрузку состояния ордеров (orders)
    в персистентное хранилище (база данных SQLite).
    """
    def __init__(self, db_path: str, logger: Optional[MarketDataLogger] = None):
        """
        Инициализирует репозиторий. Для :memory: создает постоянное соединение.

        Args:
            db_path (str): Путь к файлу .db или ':memory:'.
            logger (Optional[MarketDataLogger]): Экземпляр логгера.
        """
        self._db_path = db_path
        self.logger = logger
        self._conn = None

        if self._db_path == ":memory:":
            self._conn = sqlite3.connect(":memory:", check_same_thread=False)
        else:
            # Убедимся, что директория для файла существует
            os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        
        self._create_table()

    def _get_connection(self):
        """Возвращает существующее соединение или создает новое."""
        if self._conn:
            return self._conn
        return sqlite3.connect(self._db_path)

    def close(self):
        """Закрывает постоянное соединение, если оно существует."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def _create_table(self):
        """Создает таблицу orders в БД, если она не существует."""
        conn = self._get_connection()
        try:
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
            raise RepositoryError(
                message=f"Failed to create 'orders' table: {e}",
                repository_type="sqlite",
                db_operation="create_table",
                original_exception=e
            )
        finally:
            if not self._conn: # Закрываем только если соединение не постоянное
                conn.close()

    def load(self, trace_id: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Загружает все ордера из базы данных SQLite.

        Returns:
            Словарь с состоянием ордеров, где ключ - order_id.
            Возвращает пустой словарь, если таблица пуста или произошла ошибка.
        """
        if self.logger:
            self.logger.log_operation_start("repo_load", trace_id=trace_id)
        
        orders = {}
        conn = self._get_connection()
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders")
            rows = cursor.fetchall()
            for row in rows:
                orders[row['order_id']] = dict(row)
            
            if self.logger:
                self.logger.log_operation_complete("repo_load", trace_id=trace_id, context={"orders_loaded": len(orders)})
                
        except sqlite3.Error as e:
            if self.logger:
                self.logger.log_operation_error("repo_load", trace_id=trace_id, error=str(e))
            raise RepositoryError(
                message=f"Failed to load orders from OMS database: {e}",
                repository_type="sqlite",
                db_operation="load",
                original_exception=e
            )
        finally:
            if not self._conn:
                conn.close()
        return orders

    def save(self, order: Dict[str, Any], trace_id: Optional[str] = None):
        """
        Сохраняет или обновляет один ордер в базе данных.
        Использует 'INSERT OR REPLACE' для атомарности.

        Args:
            order: Словарь, представляющий один ордер.
        """
        if self.logger:
            self.logger.log_operation_start("repo_save", trace_id=trace_id, context={"order_id": order.get("order_id")})
            
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            columns = ', '.join(order.keys())
            placeholders = ', '.join('?' * len(order))
            sql = f"INSERT OR REPLACE INTO orders ({columns}) VALUES ({placeholders})"
            
            values = [order.get(key) for key in order.keys()]
            
            cursor.execute(sql, values)
            conn.commit()

            if self.logger:
                self.logger.log_operation_complete("repo_save", trace_id=trace_id, context={"order_id": order.get("order_id")})

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            if self.logger:
                self.logger.log_operation_error("repo_save", trace_id=trace_id, error=str(e), context={"order_id": order.get("order_id")})
            raise RepositoryError(
                message=f"Failed to save order to OMS database: {e}",
                repository_type="sqlite",
                db_operation="save",
                original_exception=e
            )
        finally:
            if not self._conn:
                conn.close()

    def delete(self, order_id: str, trace_id: Optional[str] = None):
        """
        Удаляет ордер из базы данных по его ID.

        Args:
            order_id: ID ордера для удаления.
        """
        if self.logger:
            self.logger.log_operation_start("repo_delete", trace_id=trace_id, context={"order_id": order_id})

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
            conn.commit()

            if self.logger:
                self.logger.log_operation_complete("repo_delete", trace_id=trace_id, context={"order_id": order_id})

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            if self.logger:
                self.logger.log_operation_error("repo_delete", trace_id=trace_id, error=str(e), context={"order_id": order_id})
            raise RepositoryError(
                message=f"Failed to delete order from OMS database: {e}",
                repository_type="sqlite",
                db_operation="delete",
                original_exception=e
            )
        finally:
            if not self._conn:
                conn.close()