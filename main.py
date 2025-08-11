"""
AI Trading System - Main Entry Point

Autonomous cryptocurrency trading system using LLM decision making.
Integrates MarketDataService, LLM providers, portfolio management, and order execution.
"""

import asyncio
import logging
import yaml
import os
from datetime import datetime
from pathlib import Path

# Imports for the refactored architecture
from src.infrastructure.binance_client import BinanceApiClient
from src.market_data.market_data_service import MarketDataService
from src.logging_system.logger_config import configure_ai_logging, MarketDataLogger
from src.logging_system.trace_generator import get_trace_id


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


async def test_market_data_service(service: MarketDataService, logger: MarketDataLogger):
    """Test MarketDataService functionality using the new architecture."""
    root_trace_id = get_trace_id()
    logger.log_operation_start("market_data_demo", trace_id=root_trace_id)

    try:
        # Corrected logging calls
        logger.logger.info("Fetching BTC market data...", trace_id=root_trace_id)
        # Pass the trace_id to the service method
        btc_data = service.get_market_data("BTCUSDT", trace_id=root_trace_id)

        logger.logger.info(f"Symbol: {btc_data.symbol}", trace_id=root_trace_id)
        logger.logger.info(f"Timestamp: {btc_data.timestamp}", trace_id=root_trace_id)
        logger.logger.info(f"RSI(14): {btc_data.rsi_14:.2f}", trace_id=root_trace_id)
        logger.logger.info(f"MACD Signal: {btc_data.macd_signal}", trace_id=root_trace_id)
        logger.logger.info(f"MA Trend: {btc_data.ma_trend}", trace_id=root_trace_id)
        logger.logger.info(f"Volume Profile: {btc_data.volume_profile}", trace_id=root_trace_id)

        # Test LLM context generation
        llm_context = btc_data.to_llm_context()
        logger.logger.info("Generated LLM context successfully", trace_id=root_trace_id)
        logger.logger.info(
            "LLM context preview",
            operation="llm_context_preview",
            context={
                "length": len(llm_context),
                "preview": llm_context[:500] + "..." if len(llm_context) > 500 else llm_context
            },
            trace_id=root_trace_id
        )

        logger.log_operation_complete("market_data_demo", trace_id=root_trace_id, context={"status": "success"})
        return True

    except Exception as e:
        # Corrected error logging call
        logger.logger.error(
            f"MarketDataService test failed: {e}",
            trace_id=root_trace_id,
            exc_info=True
        )
        logger.log_operation_error("market_data_demo", error=str(e), trace_id=root_trace_id)
        return False


async def main():
    """Main application entry point."""
    try:
        # Load configuration
        config = load_config()
        
        # Setup advanced logging
        log_config = config.get('logging', {})
        configure_ai_logging(
            log_level=log_config.get('level', 'INFO'),
            log_file=log_config.get('file', 'logs/trading_system.log'),
            console_output=True
        )

        # Create a dedicated logger for the main application
        main_logger = logging.getLogger(__name__)

        create_data_directories()

        main_logger.info("=== AI Trading System Starting ===")
        main_logger.info(f"Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        main_logger.info(f"Primary LLM Model: {config['llm']['primary_model']}")
        main_logger.info(f"Paper Trading Mode: {config['execution']['paper_trading']}")

        # --- Initialize Core Services ---
        # 1. Create specialized logger for MarketDataService
        market_data_logger = MarketDataLogger(__name__, service_name="MarketDataService")

        # 2. Get API keys from environment variables
        api_key = os.getenv("BINANCE_API_KEY")
        api_secret = os.getenv("BINANCE_SECRET_KEY")
        if not api_key or not api_secret:
            main_logger.warning("BINANCE_API_KEY or BINANCE_SECRET_KEY not set. Market data will be fetched without authentication.")

        # 3. Create Binance API Client
        from src.logging_system.logger_config import get_ai_logger
        api_client_logger = get_ai_logger("BinanceApiClient", service_name="BinanceApiClient")
        api_client = BinanceApiClient(logger=api_client_logger, api_key=api_key, api_secret=api_secret)

        # 4. Create MarketDataService with dependencies
        market_data_service = MarketDataService(api_client=api_client, logger=market_data_logger)

        # Test MarketDataService
        market_data_success = await test_market_data_service(market_data_service, market_data_logger)

        if not market_data_success:
            main_logger.error("MarketDataService test failed. Exiting.")
            return

        main_logger.info("=== All Systems Operational ===")
        main_logger.info("MarketDataService: ✅ READY")
        main_logger.info("LLM Provider: 🔄 TODO (Next Phase)")
        main_logger.info("Portfolio Manager: 🔄 TODO (Next Phase)")
        main_logger.info("Order Executor: 🔄 TODO (Next Phase)")

        main_logger.info("=== Phase 1 Complete: MarketDataService Implemented and Integrated ===")
        main_logger.info("Next: Implement Claude Provider for LLM integration")

    except Exception as e:
        logging.getLogger(__name__).critical(f"Application startup failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())