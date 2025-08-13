import requests
from requests.exceptions import JSONDecodeError
from src.infrastructure.exceptions import ApiClientError
from src.logging_system import MarketDataLogger

class SentimentApiClient:
    """
    Клиент для получения данных об индексе страха и жадности с alternative.me.
    """
    def __init__(self, logger: MarketDataLogger):
        self.base_url = "https://api.alternative.me"
        self.logger = logger

    def get_fear_and_greed_index(self, trace_id: str = None) -> dict:
        """
        Получает последнее значение индекса страха и жадности.
        """
        endpoint = "/fng/"
        url = self.base_url + endpoint
        
        self.logger.log_operation_start(
            "get_fear_and_greed_index",
            context={"url": url},
            trace_id=trace_id
        )
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Вызовет исключение для 4xx/5xx ответов
            
            try:
                data = response.json()
            except JSONDecodeError as e:
                error_msg = f"Failed to decode JSON. Status: {response.status_code}. Content: {response.text[:200]}"
                self.logger.log_operation_error(
                    "get_fear_and_greed_index_json_decode",
                    error=error_msg,
                    context={"url": url},
                    trace_id=trace_id
                )
                raise ApiClientError(error_msg) from e

            self.logger.log_operation_complete(
                "get_fear_and_greed_index",
                context={"status_code": response.status_code, "data_name": data.get('name')},
                trace_id=trace_id
            )
            return data

        except requests.exceptions.RequestException as e:
            self.logger.log_operation_error(
                "get_fear_and_greed_index_network_error",
                error=str(e),
                context={"url": url},
                trace_id=trace_id
            )
            raise ApiClientError(f"Network error fetching Fear & Greed Index: {e}") from e