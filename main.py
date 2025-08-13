"""
AI Trading System - Main Entry Point

Autonomous cryptocurrency trading system using LLM decision making.
Integrates MarketDataService, LLM providers, portfolio management, and order execution.
"""

import logging
import yaml
import os
from datetime import datetime, timezone
from pathlib import Path

# Imports for the refactored architecture
from src.infrastructure.binance_client import BinanceApiClient
from src.infrastructure.sentiment_client import SentimentApiClient
from src.market_data.market_data_service import MarketDataService
from src.logging_system.logger_config import configure_ai_logging, get_ai_logger, MarketDataLogger
from src.trading.oms import OrderManagementSystem
from src.trading.oms_repository import OmsRepository
from src.trading.trading_cycle import TradingCycle


def load_config(config_path: str = "config/trading_config.yaml") -> dict:
    """Load trading system configuration."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML configuration: {e}")


def create_data_directories():
    """Create necessary data directories."""
    directories = [
        "data/cache",
        "data",
        "logs"
    ]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def main():
    """Main application entry point."""
    try:
        # Load configuration
        config = load_config()
        
        # Setup advanced logging
        log_config = config.get('logging', {})
        configure_ai_logging(
            log_level="DEBUG",  # Always use DEBUG for demo and development
            log_file=log_config.get('file', 'logs/trading_system.log'),
            console_output=True
        )

        # Create a dedicated logger for the main application
        main_logger = logging.getLogger(__name__)

        create_data_directories()

        print("=== AI Trading System Demo ===")
        print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
        print(f"Primary LLM Model: {config['llm']['primary_model']}")
        print(f"Paper Trading Mode: {config['execution']['paper_trading']}")
        print("-" * 30)

        # --- Initialize Core Services ---
        print("🏭 Initializing System Components...")
        
        # 1. API Client
        api_key = os.getenv("BINANCE_API_KEY")
        api_secret = os.getenv("BINANCE_SECRET_KEY")
        if not api_key or not api_secret:
            main_logger.warning("API keys not set. Market data will be fetched without authentication.")
        api_client_logger = get_ai_logger("BinanceApiClient", service_name="BinanceApiClient")
        api_client = BinanceApiClient(logger=api_client_logger, api_key=api_key, api_secret=api_secret)
        print("   - BinanceApiClient initialized.")

        # 2. Sentiment API Client
        sentiment_logger = MarketDataLogger("SentimentApiClient", service_name="SentimentApiClient")
        sentiment_client = SentimentApiClient(logger=sentiment_logger)
        print("   - SentimentApiClient initialized.")

        # 3. Market Data Service
        market_data_logger = MarketDataLogger("MarketDataService", service_name="MarketDataService")
        market_data_service = MarketDataService(
            api_client=api_client,
            logger=market_data_logger,
            sentiment_client=sentiment_client
        )
        print("   - MarketDataService initialized.")

        # 4. OMS Repository (In-memory DB for demo)
        repo_logger = MarketDataLogger("OmsRepository", service_name="OmsRepository")
        oms_repository = OmsRepository(db_path=":memory:", logger=repo_logger)
        print("   - OmsRepository (in-memory) initialized.")

        # 5. Order Management System
        oms_logger = MarketDataLogger("OMS", service_name="OMS")
        oms = OrderManagementSystem(repository=oms_repository, logger=oms_logger)
        print("   - OrderManagementSystem initialized.")

        # 6. Trading Cycle
        trading_cycle = TradingCycle(oms=oms, market_data_service=market_data_service)
        print("   - TradingCycle initialized.")
        print("✅ All components are ready.")
        print("-" * 30)

        # --- Run a Single Trading Cycle ---
        print("\n▶️  Запускаем торговый цикл для ETHUSDT...")
        trading_cycle.run_cycle(symbol="ETHUSDT")
        print("\n🏁 Демонстрация завершена.")

    except Exception as e:
        logging.getLogger(__name__).critical(f"Application startup failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()