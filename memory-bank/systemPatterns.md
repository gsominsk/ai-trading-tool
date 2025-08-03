# System Patterns - АРХИТЕКТУРНАЯ ОСНОВА ПРОЕКТА

**ВАЖНО: Данная архитектура является ПУТЕВОДНОЙ ОСНОВОЙ проекта - я должен помнить о ней и придерживаться этих принципов во время всей разработки.**

2025-08-02 18:52:43 - Создана фундаментальная архитектура LLM-торговой системы

---

## CORE ARCHITECTURAL PRINCIPLES (РУКОВОДЯЩИЕ ПРИНЦИПЫ)

### 1. МОДУЛЬНАЯ LLM-АРХИТЕКТУРА
```
Основной принцип: Система строится на модульных LLM компонентах с абстрагированными интерфейсами
```

### 2. УНИВЕРСАЛЬНОСТЬ ДАННЫХ
```
Принцип: Все LLM модели получают идентичные данные в стандартизированном формате
```

### 3. КОНФИГУРАЦИОННАЯ ГИБКОСТЬ
```
Принцип: Любая конфигурация LLM переключается через YAML без изменения кода
```

### 4. СТАБИЛЬНОЕ ЯДРО
```
Принцип: Четыре базовых компонента обеспечивают стабильность при развитии LLM слоя
```

---

## ARCHITECTURAL PATTERNS (АРХИТЕКТУРНЫЕ ПАТТЕРНЫ)

### A. CORE IMMUTABLE LAYER (НЕИЗМЕНЯЕМЫЙ СЛОЙ)

#### 1. DataPreparer - СБОРЩИК ДАННЫХ
```python
class DataPreparer:
    """БАЗОВЫЙ КОМПОНЕНТ - подготовка данных для LLM"""
    
    def get_market_data(self, symbol: str) -> MarketDataSet:
        # Уровень 1: 6 месяцев дневных свечей  
        # Уровень 2: 2 недели 4H свечей
        # Уровень 3: 48 часов 1H свечей
        # Технические индикаторы: RSI, MACD, MA(20/50)
        # Рыночный контекст: BTC корреляция, Fear & Greed
        pass
```

#### 2. PortfolioManager - УПРАВЛЕНИЕ ПОРТФЕЛЕМ
```python
class PortfolioManager:
    """БАЗОВЫЙ КОМПОНЕНТ - адаптированный из ChatGPT-Micro-Cap-Experiment"""
    
    def update_position(self, symbol: str, action: str, amount: float):
        # Логика из Trading_Script.py (проверена в реальной торговле)
        pass
        
    def calculate_pnl(self) -> float:
        # Расчеты PnL, Sharpe/Sortino ratios
        pass
```

#### 3. RiskManager - УПРАВЛЕНИЕ РИСКАМИ
```python
class RiskManager:
    """БАЗОВЫЙ КОМПОНЕНТ - риск-менеджмент"""
    
    def validate_trade(self, trade_signal: TradeSignal) -> bool:
        # Stop-loss автоматизация
        # Проверка максимальной просадки
        # Контроль размера позиции
        pass
```

#### 4. OrderExecutor - ИСПОЛНЕНИЕ ОРДЕРОВ
```python
import requests
import hmac
import hashlib
import time

class OrderExecutor:
    """БАЗОВЫЙ КОМПОНЕНТ - самописный Binance клиент с проверенными зависимостями"""
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.binance.com"
    
    def _create_signature(self, params: str) -> str:
        """HMAC подпись через стандартную библиотеку Python"""
        return hmac.new(
            self.api_secret.encode('utf-8'),
            params.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def execute_order(self, order: Order) -> ExecutionResult:
        # requests для HTTP (стандарт индустрии)
        # Самописная обработка Binance API
        pass
        
    def create_stop_loss_order(self, symbol: str, quantity: float, stop_price: float):
        # Прямая работа с Binance REST API
        # Полный контроль над торговой логикой
        pass
```

### B. MODULAR LLM LAYER (МОДУЛЬНЫЙ LLM СЛОЙ)

#### 1. Abstract LLM Interface
```python
class LLMProvider(ABC):
    """АБСТРАКТНЫЙ ИНТЕРФЕЙС - все LLM должны его реализовывать"""
    
    @abstractmethod
    def analyze_market(self, market_data: MarketDataSet) -> TradeSignal:
        pass
        
    @abstractmethod  
    def get_confidence_score(self) -> float:
        pass
```

#### 2. Concrete LLM Implementations
```python
class ClaudeProvider(LLMProvider):
    """Реализация для Claude 4"""
    
class GeminiProvider(LLMProvider):
    """Реализация для Gemini 2.5 Pro"""
    
class GPTProvider(LLMProvider):  
    """Реализация для GPT o3"""
```

### C. COMBINATORIAL CONFIGURATIONS (КОМБИНАТОРНЫЕ КОНФИГУРАЦИИ)

#### 1. Single Model Mode
```yaml
mode: single
provider: claude  # или gemini, gpt
```

#### 2. Duplicate Pairs Mode
```yaml
mode: duplicate_pairs
pairs:
  - [claude, claude]
  - [gemini, gemini]
  - [gpt, gpt]
```

#### 3. Specialized Roles Mode
```yaml
mode: specialized
roles:
  trend_analyst: claude
  risk_assessor: gemini  
  signal_generator: gpt
```

#### 4. Ensemble Mode
```yaml
mode: ensemble
providers: [claude, gemini, gpt]
voting_strategy: majority  # или weighted, unanimous
```

#### 5. Sequential Validation Mode
```yaml
mode: sequential
chain:
  - claude      # первичный анализ
  - gemini      # проверка
  - gpt         # финальное решение
```

---

## CODING PATTERNS (ПАТТЕРНЫ КОДИРОВАНИЯ)

### 1. FACTORY PATTERN для LLM
```python
class LLMFactory:
    """Создание LLM провайдеров по конфигурации"""
    
    @staticmethod
    def create_provider(config: Dict) -> LLMProvider:
        provider_map = {
            'claude': ClaudeProvider,
            'gemini': GeminiProvider, 
            'gpt': GPTProvider
        }
        return provider_map[config['type']](config['params'])
```

### 2. STRATEGY PATTERN для Trading Modes
```python
class TradingStrategy(ABC):
    """Абстрактная стратегия торговли"""
    
    @abstractmethod
    def make_decision(self, market_data: MarketDataSet) -> TradeSignal:
        pass

class SingleModelStrategy(TradingStrategy):
    """Стратегия одной модели"""
    
class EnsembleStrategy(TradingStrategy):
    """Стратегия ансамбля"""
```

### 3. CONFIGURATION DRIVEN APPROACH
```python
class ConfigManager:
    """Управление конфигурациями без изменения кода"""
    
    def load_config(self, config_path: str) -> Dict:
        # Загрузка YAML конфигурации
        pass
        
    def switch_mode(self, new_mode: str):
        # Переключение режима без перезапуска
        pass
```

---

## DATA PATTERNS (ПАТТЕРНЫ ДАННЫХ)

### 1. STANDARDIZED DATA STRUCTURE
```python
@dataclass
class MarketDataSet:
    """Стандартизированная структура данных для всех LLM"""
    
    # Уровень 1: Долгосрочный тренд
    daily_candles_6m: List[Candle]
    
    # Уровень 2: Среднесрочный анализ  
    four_hour_candles_2w: List[Candle]
    
    # Уровень 3: Краткосрочные сигналы
    hourly_candles_48h: List[Candle]
    
    # Технические индикаторы
    rsi: float
    macd: MACD
    moving_averages: MovingAverages
    
    # Рыночный контекст
    btc_correlation: float
    fear_greed_index: int
    market_sentiment: str
```

### 2. UNIFIED RESPONSE FORMAT
```python
@dataclass
class TradeSignal:
    """Единый формат ответа от всех LLM"""
    
    action: str  # BUY, SELL, HOLD
    confidence: float  # 0.0 - 1.0
    reasoning: str
    risk_level: str  # LOW, MEDIUM, HIGH
    target_price: Optional[float]
    stop_loss: Optional[float]
    timestamp: datetime
```

---

## TESTING PATTERNS (ПАТТЕРНЫ ТЕСТИРОВАНИЯ)

### 1. LLM MOCK PATTERN
```python
class MockLLMProvider(LLMProvider):
    """Мок для тестирования без реальных LLM вызовов"""
    
    def analyze_market(self, market_data: MarketDataSet) -> TradeSignal:
        return TradeSignal(action="HOLD", confidence=0.5, ...)
```

### 2. BACKTESTING PATTERN
```python
class BacktestEngine:
    """Тестирование стратегий на исторических данных"""
    
    def run_backtest(self, strategy: TradingStrategy, 
                     data: HistoricalData) -> BacktestResults:
        pass
```

---

## DEPLOYMENT PATTERNS (ПАТТЕРНЫ РАЗВЕРТЫВАНИЯ)

### 1. CONTAINERIZATION
```dockerfile
# Каждый LLM провайдер - отдельный контейнер
# Неизменяемое ядро - базовый контейнер
# Конфигурации - через volume mounts
```

### 2. MONITORING PATTERN
```python
class PerformanceMonitor:
    """Мониторинг производительности всех конфигураций"""
    
    def track_performance(self, provider: str, signal: TradeSignal, 
                         result: TradeResult):
        pass
```

---

## SCALABILITY PATTERNS (ПАТТЕРНЫ МАСШТАБИРУЕМОСТИ)

### 1. HORIZONTAL SCALING
```
- Каждая LLM конфигурация может работать параллельно
- Load balancing между несколькими инстансами
- Distributed processing для multiple assets
```

### 2. VERTICAL SCALING  
```
- Увеличение вычислительных ресурсов
- Оптимизация промптов для LLM
- Кеширование частых запросов
```

---

## IMPLEMENTATION INVARIANTS (НЕИЗМЕНЯЕМЫЕ ПРАВИЛА РЕАЛИЗАЦИИ)

### 1. CORE COMPONENTS
```
DataPreparer, PortfolioManager, RiskManager, OrderExecutor 
НЕ ДОЛЖНЫ ИЗМЕНЯТЬСЯ при смене LLM конфигурации
```

### 2. DATA FORMAT
```
MarketDataSet и TradeSignal форматы НЕИЗМЕННЫ
Все LLM получают одинаковые данные
```

### 3. CONFIGURATION SWITCHING
```
Смена режимов ТОЛЬКО через YAML конфигурации
Никаких изменений кода при переключении
```

### 4. BACKWARD COMPATIBILITY
```
Новые LLM провайдеры ДОЛЖНЫ реализовывать LLMProvider интерфейс
Старые конфигурации ДОЛЖНЫ продолжать работать
```

---

**АРХИТЕКТУРНАЯ ОСНОВА ЗАВЕРШЕНА - ПОДЛЕЖИТ СТРОГОМУ СОБЛЮДЕНИЮ**

[2025-08-02 23:51:20] - MarketDataService Enhanced Candlestick Analysis Pattern

## Enhanced Data Preparation Pattern

### MarketDataService Candlestick Analysis
```python
class MarketDataService:
    """БАЗОВЫЙ КОМПОНЕНТ с enhanced candlestick analysis capabilities"""
    
    def get_enhanced_context(self, symbol: str) -> str:
        """Умный анализ свечных паттернов для LLM"""
        
        # 7-Algorithm Smart Selection
        key_candles = self._select_key_candles()
        patterns = self._identify_patterns(key_candles)
        
        # Enhanced Analysis Components:
        # 1. Recent Trend Analysis (последние 5 свечей)
        # 2. Pattern Recognition (Doji, Hammer, Shooting Star, Strong Bull/Bear)
        # 3. S/R Level Interaction (поддержка/сопротивление)
        # 4. Volume-Price Relationship (подтверждение трендов)
        
        return enhanced_context  # ~300-400 токенов
        
    def _select_key_candles(self) -> list:
        """7-алгоритмический отбор значимых свечей"""
        # 1. Recent 5 (текущий контекст)
        # 2. Extremes (max/min за 30 дней)
        # 3. High volume (топ 10% за 20 дней)  
        # 4. Big moves (>3% изменение)
        # 5. Patterns (технические фигуры)
        # 6. S/R tests (взаимодействие с уровнями)
        # 7. Deduplication (15 финальных свечей)
        
    def _identify_patterns(self, candles: list) -> list:
        """Распознавание свечных паттернов"""
        # Doji: body/range < 0.1
        # Hammer: lower_shadow/range > 0.6
        # Shooting Star: upper_shadow/range > 0.6
        # Strong Bull/Bear: body/range > 0.7
```

### Token Optimization Strategy
```python
# BASIC CONTEXT: ~150-200 tokens
basic_context = market_data.to_llm_context()

# ENHANCED CONTEXT: ~300-400 tokens  
enhanced_context = service.get_enhanced_context(symbol)

# Smart Selection Efficiency:
# 180 daily candles → 15 key candles (91.7% reduction)
# Maximum information retention with minimal token usage
```

### Live Testing Results Pattern
```python
# BTC Example Output:
enhanced_analysis = {
    "recent_trend": "Downward bias",
    "patterns": ["Shooting Star", "Hammer", "Strong Bear", "Doji"],
    "sr_tests": "R:1 tests, S:1 tests", 
    "volume_analysis": "Weak bearish signal",
    "efficiency": "11 key candles from 180 total"
}
```

### Integration with LLM Provider Pattern
```python
class ClaudeProvider(LLMProvider):
    """Enhanced context integration ready"""
    
    def analyze_market(self, symbol: str) -> TradeSignal:
        # Option 1: Basic context (speed)
        basic_data = self.market_service.get_market_data(symbol)
        
        # Option 2: Enhanced context (accuracy)  
        enhanced_data = self.market_service.get_enhanced_context(symbol)
        
        return self._process_llm_request(enhanced_data)
```


[2025-08-03 04:27:30] - Comprehensive Testing Strategy Patterns Added

## TESTING PATTERNS FOR AI TRADING SYSTEM

### Financial Safety Testing Pattern
```python
class FinancialPrecisionTests:
    """Критически важное тестирование для money operations"""
    
    def test_decimal_precision(self):
        # Crypto amounts до 8 decimal places
        assert calculate_pnl(100.12345678, 99.87654321) == Decimal('0.24691357')
        
    def test_large_amounts(self):
        # Edge cases для больших сумм
        pass
        
    def test_rounding_consistency(self):
        # Консистентность округления
        pass
```

### LLM Response Validation Pattern
```python
class LLMResponseValidator:
    """Validation AI-generated trading signals"""
    
    def validate_trading_signal(self, signal: dict) -> bool:
        required_fields = ['action', 'confidence', 'reasoning', 'risk_level']
        return all(field in signal for field in required_fields)
        
    def validate_signal_consistency(self, signals: List[dict]) -> float:
        # Consistency score между разными LLM на одинаковых данных
        pass
```

### Multi-LLM Testing Pattern
```python
class LLMComparisonFramework:
    """A/B testing framework для сравнения моделей"""
    
    def run_comparative_test(self, market_data: dict, providers: List[str]):
        results = {}
        for provider in providers:
            signal = self.llm_factory.create(provider).analyze_market(market_data)
            results[provider] = signal
        return self.compare_signals(results)
        
    def backtest_performance(self, provider: str, historical_data: dict):
        # Performance comparison на исторических данных
        pass
```

### Configuration Testing Pattern
```python
class ConfigurationTests:
    """Тестирование всех 5 архитектурных режимов"""
    
    @pytest.mark.parametrize("mode", ["single", "duplicate_pairs", "specialized", "ensemble", "sequential"])
    def test_configuration_switching(self, mode: str):
        config = self.load_config(mode)
        trading_system = TradingSystem(config)
        assert trading_system.validate_configuration()
        
    def test_mode_consistency(self):
        # Один и тот же market data должен обрабатываться без ошибок во всех режимах
        pass
```

### Risk Management Testing Pattern
```python
class RiskManagementTests:
    """Critical risk control validation"""
    
    def test_stop_loss_precision(self):
        # Stop-loss должен срабатывать точно на заданном уровне
        pass
        
    def test_position_size_limits(self):
        # Максимальный размер позиции не должен превышаться
        pass
        
    def test_drawdown_protection(self):
        # Maximum drawdown controls
        pass
```

### Mock Patterns for External Dependencies
```python
class BinanceMockProvider:
    """Mock Binance API для предсказуемого тестирования"""
    
    def mock_market_data(self) -> dict:
        return load_fixture('btc_market_data_sample.json')
        
    def mock_order_execution(self, order: dict) -> dict:
        return {'status': 'FILLED', 'executedQty': order['quantity']}

class LLMMockProvider:
    """Mock LLM responses для reproducible tests"""
    
    def mock_claude_response(self) -> dict:
        return load_fixture('claude_trading_signal_sample.json')
```

### Backtesting Pattern
```python
class BacktestingFramework:
    """Historical data validation"""
    
    def run_strategy_backtest(self, strategy: str, timeframe: str, symbols: List[str]):
        historical_data = self.load_historical_data(timeframe, symbols)
        results = []
        
        for data_point in historical_data:
            signal = self.generate_signal(strategy, data_point)
            result = self.simulate_trade(signal, data_point)
            results.append(result)
            
        return self.calculate_metrics(results)
```

### Testing Pipeline Integration
```python
# pytest.ini configuration
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Unit tests
    integration: Integration tests  
    financial: Financial precision tests
    llm: LLM-related tests
    slow: Slow-running tests (backtesting)
```

**TESTING PRINCIPLES ESTABLISHED FOR AI TRADING SYSTEM**


[2025-01-03 12:54:45] - НОВЫЕ КРИТИЧЕСКИЕ ПАТТЕРНЫ для финансовых систем

## Financial Safety Pattern
- ВСЕ финансовые операции ТОЛЬКО через Decimal
- float категорически запрещен для денежных расчетов
- Mandatory rounding with ROUND_HALF_UP для консистентности
- Validation bounds для всех финансовых значений

## Real TDD Pattern  
- Импорт реального модуля в тестах (не закомментированный)
- Тесты должны проверять настоящий код, не только моки
- Mock только внешние зависимости (API), тестировать внутреннюю логику
- Каждый тест должен fail при поломке реального кода

## Comprehensive Validation Pattern
- Input validation на входе в каждый публичный метод
- Post-init validation в dataclasses для целостности данных  
- Error boundary testing для всех возможных edge cases
- Clear error messages с указанием ожидаемого формата

## Financial Data Structure Pattern
- MarketDataSet как строго типизированная структура
- Decimal для всех цен, объемов, процентов
- Validation в __post_init__ для проверки корректности
- Immutable data где возможно для предотвращения случайных изменений

УРОК: Финансовые системы требуют ОСОБОГО подхода к тестированию и типам данных


[2025-01-03 12:56:30] - WORKFLOW PATTERN для работы с Memory Bank и Git

## Memory Bank First Pattern
ПРАВИЛО: ВСЕГДА обновлять Memory Bank ПЕРЕД git commit
1. Завершить работу над задачей
2. Обновить все релевантные файлы Memory Bank:
   - decisionLog.md (решения и уроки)
   - activeContext.md (текущий статус)
   - progress.md (прогресс и планы)
   - systemPatterns.md (новые паттерны)
3. УТОЧНИТЬ у пользователя готовность к commit
4. Только после подтверждения делать git add + commit

ВАЖНО: Memory Bank должен содержать полный контекст ПЕРЕД фиксацией в git
Это обеспечивает преемственность для следующих сессий работы


[2025-01-03 12:58:35] - GIT COMMIT LANGUAGE PATTERN

## Git Commit Language Pattern
ПРАВИЛО: ВСЕ git commit сообщения ТОЛЬКО на английском языке
- Заголовок: "feat:", "fix:", "docs:", "refactor:", etc.
- Описание: полностью на английском
- Причина: международные стандарты разработки
- Исключений НЕТ - всегда английский

Пример правильного commit:
```
feat: critical MarketDataService fixes + real TDD implementation

- Replace all float → Decimal for financial precision safety
- Add comprehensive input data validation
- Fix critical issue: tests now actually test real code
```

ВАЖНО: Это правило дополняет Memory Bank First Pattern
