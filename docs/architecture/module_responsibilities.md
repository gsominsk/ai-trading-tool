# Module Responsibilities (Simplified MVP Architecture)

This document outlines the responsibilities of each core module in the simplified 4-module architecture for the AI Trading System MVP.

---

### 1. `Scheduler`
-   **File:** `main.py`
-   **Core Responsibility:** Acts as the system's heartbeat and entry point.
-   **Tasks:**
    -   Initiates the main application loop based on a defined schedule (e.g., every 15 minutes).
    -   Reads the list of trading pairs to be processed from a configuration file (e.g., `config/trading_config.yaml`).
    -   For each trading pair, it instantiates and triggers the `TradingCycle`.
    -   Handles top-level application lifecycle and graceful shutdown.

---

### 2. `MarketDataService`
-   **File:** `src/market_data/market_data_service.py`
-   **Core Responsibility:** Acts as the single source of truth for all market-related data.
-   **Status:** **Implemented and Stable.**
-   **Tasks:**
    -   Provides historical and current market data (klines).
    -   Calculates and provides a rich set of technical indicators (RSI, MACD, etc.).
    -   Provides contextual analysis (candlestick patterns, volume analysis).
    -   Encapsulates all direct communication with the data provider's API (e.g., Binance).

---

### 3. `OrderManagementSystem` (OMS)
-   **File:** `src/trading/oms.py`
-   **Core Responsibility:** Encapsulates all logic for interacting with the exchange's trading API. It is the only module authorized to place, check, or cancel orders.
-   **Tasks:**
    -   Provides clear methods for execution: `check_order_status(order_id)`, `place_new_order(plan)`, `cancel_order(order_id)`.
    -   Contains a "Sanity Filter" to perform basic validation on trade plans received from the `TradingCycle` before execution (e.g., ensure stop-loss is below entry for a long position).
    -   Manages API credentials and connection details securely.
    -   Incorporates `CircuitBreaker` logic to handle repeated API failures gracefully (e.g., stop trading for a specific pair after 5 consecutive API errors).

---

### 4. `TradingCycle`
-   **File:** `src/trading/trading_cycle.py`
-   **Core Responsibility:** The central "super-module" that orchestrates the entire decision-making and execution flow for a single asset in a single cycle.
-   **Tasks:**
    -   **State Synchronization:** At the start of each cycle, it checks the local `trade_log.csv`. If a `PENDING` order is found, it immediately calls the `OMS` to get the real-time status from the exchange and updates the log accordingly.
    -   **Trade Logging:** Manages all read/write operations for the `data/trade_log.csv` file. This includes logging new pending trades and updating the status of existing ones (`ACTIVE`, `CLOSED`, `CANCELLED`).
    -   **AI Strategy & Prompt Engineering:**
        -   Gathers all necessary data from the `MarketDataService`.
        -   Constructs a detailed, structured prompt for the LLM, including market data and the current position status (if any).
        -   Sends the request to the LLM API.
        -   Parses and validates the JSON response from the LLM.
    -   **Orchestration:** Based on the AI's response and the current state, it calls the appropriate methods on the `OMS` to execute the trading plan (place, cancel, or modify an order).