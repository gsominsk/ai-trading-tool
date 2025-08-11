import requests
import requests
import logging
import time
import uuid
from typing import Optional

from .exceptions import ApiClientError, RateLimitError, APIResponseError, ErrorContext
from src.logging_system.json_formatter import StructuredLogger

class BinanceApiClient:
    """
    A client for interacting with the Binance API.
    Handles request signing, error handling, and rate limiting.
    """
    def __init__(self, logger: StructuredLogger, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """
        Initializes the Binance API client.

        Args:
            logger: A configured StructuredLogger instance.
            api_key: Your Binance API key.
            api_secret: Your Binance API secret.
        """
        self.logger = logger
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.binance.com/api/v3"
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"X-MBX-APIKEY": self.api_key})

        self.logger.info("BinanceApiClient initialized", operation="initialization")

    # --- Public Methods ---

    def get_server_time(self, trace_id: Optional[str] = None) -> int:
        """
        Tests connectivity to the Rest API and gets the current server time.

        Args:
            trace_id: The trace ID for logging correlation.

        Returns:
            The server time in milliseconds.
        """
        trace_id = trace_id or f"time_{uuid.uuid4().hex[:8]}"
        endpoint = f"{self.base_url}/time"
        self.logger.info(
            "Requesting server time from API",
            operation="get_server_time",
            context={"endpoint": endpoint},
            trace_id=trace_id,
        )

        start_time = time.time()
        try:
            response = self.session.get(endpoint, timeout=5)
            duration = time.time() - start_time
            self._handle_response(response, trace_id)
            
            data = response.json()
            server_time = data.get("serverTime")

            self.logger.info(
                "Server time request successful",
                operation="get_server_time",
                context={
                    "endpoint": endpoint,
                    "duration_ms": int(duration * 1000),
                    "server_time": server_time,
                },
                trace_id=trace_id,
            )
            return server_time

        except (requests.exceptions.RequestException, ApiClientError) as e:
            self.logger.error(
                "Failed to get server time",
                operation="get_server_time",
                context={"error": str(e)},
                trace_id=trace_id,
            )
            raise

    def _handle_response(self, response: requests.Response, trace_id: str):
        """
        Centralized handler for API responses. Checks for errors and raises
        appropriate exceptions.

        Args:
            response: The requests.Response object.
            trace_id: The trace ID for logging correlation.
        """
        if response.status_code == 200:
            return

        self.logger.error(
            "API request failed",
            operation="api_request",
            context={
                "status_code": response.status_code,
                "response_text": response.text,
            },
            trace_id=trace_id,
        )

        if response.status_code == 429:
            raise RateLimitError(
                "Rate limit exceeded",
                retry_after=response.headers.get("Retry-After"),
                context=ErrorContext(trace_id=trace_id, operation="api_request"),
            )

        try:
            error_data = response.json()
            error_code = error_data.get("code")
            error_msg = error_data.get("msg")
        except requests.exceptions.JSONDecodeError:
            error_code = None
            error_msg = response.text

        raise APIResponseError(
            f"Binance API Error: {error_msg} (code: {error_code})",
            status_code=response.status_code,
            response_data=error_data if 'error_data' in locals() else response.text,
            context=ErrorContext(trace_id=trace_id, operation="api_request"),
        )


    # --- Private Methods (Order Management) ---

    def create_order(self, symbol: str, side: str, type: str, quantity: float, price: Optional[float] = None, trace_id: Optional[str] = None):
        """
        Creates a new order.
        NOTE: This is a placeholder and is not yet implemented.
        """
        self.logger.warning("create_order is not yet implemented.", operation="create_order", trace_id=trace_id)
        raise NotImplementedError("Order creation functionality is not yet implemented.")

    def cancel_order(self, symbol: str, order_id: str, trace_id: Optional[str] = None):
        """
        Cancels an existing order.
        NOTE: This is a placeholder and is not yet implemented.
        """
        self.logger.warning("cancel_order is not yet implemented.", operation="cancel_order", trace_id=trace_id)
        raise NotImplementedError("Order cancellation functionality is not yet implemented.")

    def get_order_status(self, symbol: str, order_id: str, trace_id: Optional[str] = None):
        """
        Retrieves the status of an order.
        NOTE: This is a placeholder and is not yet implemented.
        """
        self.logger.warning("get_order_status is not yet implemented.", operation="get_order_status", trace_id=trace_id)
        raise NotImplementedError("Order status retrieval functionality is not yet implemented.")


    def get_klines(self, symbol: str, interval: str, limit: int, trace_id: Optional[str] = None) -> list:
        """
        Get candlestick/kline data.

        Args:
            symbol: The trading symbol (e.g., 'BTCUSDT').
            interval: The interval of candlestick ('1m', '1h', '1d', etc.).
            limit: The number of candles to retrieve (max 1000).
            trace_id: The trace ID for logging correlation.

        Returns:
            A list of kline data.
        """
        trace_id = trace_id or f"klines_{uuid.uuid4().hex[:8]}"
        endpoint = f"{self.base_url}/klines"
        params = {"symbol": symbol, "interval": interval, "limit": limit}

        self.logger.info(
            "Requesting klines from API",
            operation="get_klines",
            context={"endpoint": endpoint, "params": params},
            trace_id=trace_id,
        )

        start_time = time.time()
        try:
            response = self.session.get(endpoint, params=params, timeout=10)
            duration = time.time() - start_time
            self._handle_response(response, trace_id)

            data = response.json()

            self.logger.info(
                "Klines request successful",
                operation="get_klines",
                context={
                    "endpoint": endpoint,
                    "duration_ms": int(duration * 1000),
                    "records_returned": len(data),
                },
                trace_id=trace_id,
            )
            return data

        except (requests.exceptions.RequestException, ApiClientError) as e:
            self.logger.error(
                "Failed to get klines",
                operation="get_klines",
                context={"error": str(e), "params": params},
                trace_id=trace_id,
            )
            raise
