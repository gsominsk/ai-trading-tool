"""
AI Trading System - Main Entry Point

Autonomous cryptocurrency trading system using LLM decision making.
Integrates MarketDataService, LLM providers, portfolio management, and order execution.
"""

import asyncio
import logging
import yaml
from datetime import datetime
from pathlib import Path

from src.market_data import MarketDataService


def load_config(config_path: str = "config/trading_config.yaml") -> dict:
    """Load trading system configuration."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML configuration: {e}")


def setup_logging(config: dict):
    """Setup logging configuration."""
    log_config = config.get('logging', {})
    
    # Create logs directory
    log_file = log_config.get('file', 'logs/trading_system.log')
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_config.get('level', 'INFO')),
        format=log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
        datefmt=log_config.get('date_format', '%Y-%m-%d %H:%M:%S'),
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


def create_data_directories():
    """Create necessary data directories."""
    directories = [
        "data/cache",
        "data", 
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


async def test_market_data_service(config: dict):
    """Test MarketDataService functionality."""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("=== Testing MarketDataService ===")
        
        # Initialize service
        cache_dir = config['market_data']['cache']['directory']
        service = MarketDataService(cache_dir=cache_dir)
        
        # Test with BTC
        logger.info("Fetching BTC market data...")
        btc_data = service.get_market_data("BTCUSDT")
        
        logger.info("=== BTC Market Data Retrieved ===")
        logger.info(f"Symbol: {btc_data.symbol}")
        logger.info(f"Timestamp: {btc_data.timestamp}")
        logger.info(f"RSI(14): {btc_data.rsi_14:.2f}")
        logger.info(f"MACD Signal: {btc_data.macd_signal}")
        logger.info(f"MA Trend: {btc_data.ma_trend}")
        logger.info(f"Volume Profile: {btc_data.volume_profile}")
        
        # Test LLM context generation
        logger.info("=== LLM Context Test ===")
        llm_context = btc_data.to_llm_context()
        logger.info("Generated LLM context successfully")
        logger.info(f"Context length: {len(llm_context)} characters")
        
        # Show first 500 characters of context
        logger.info("Context preview:")
        logger.info(llm_context[:500] + "..." if len(llm_context) > 500 else llm_context)
        
        return True
        
    except Exception as e:
        logger.error(f"MarketDataService test failed: {e}")
        return False


async def main():
    """Main application entry point."""
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        config = load_config()
        setup_logging(config)
        create_data_directories()
        
        logger.info("=== AI Trading System Starting ===")
        logger.info(f"Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        logger.info(f"Primary LLM Model: {config['llm']['primary_model']}")
        logger.info(f"Paper Trading Mode: {config['execution']['paper_trading']}")
        
        # Test MarketDataService
        market_data_success = await test_market_data_service(config)
        
        if not market_data_success:
            logger.error("MarketDataService test failed. Exiting.")
            return
        
        logger.info("=== All Systems Operational ===")
        logger.info("MarketDataService: ✅ READY")
        logger.info("LLM Provider: 🔄 TODO (Next Phase)")
        logger.info("Portfolio Manager: 🔄 TODO (Next Phase)")
        logger.info("Order Executor: 🔄 TODO (Next Phase)")
        
        # For now, just demonstrate the system is ready
        logger.info("=== Phase 1 Complete: MarketDataService Implemented ===")
        logger.info("Next: Implement Claude Provider for LLM integration")
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())