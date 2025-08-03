# AI Trading System - Сокращенный Roadmap

## 📋 Проект
**Цель**: Автономная LLM-торговая система для криптовалют (Binance API, 1H таймфрейм)  
**Архитектура**: [`systemPatterns.md`](memory-bank/systemPatterns.md) - модульная система с 4 базовыми компонентами + LLM слой  
**База**: Адаптация [`ChatGPT-Micro-Cap-Experiment`](ChatGPT-Micro-Cap-Experiment/) (проверено: $100→$121.82 за месяц)

## 🎯 Ключевые решения
✅ **LLM вместо ML**: Claude 4, Gemini 2.5 Pro, GPT o3  
✅ **Архитектура создана**: 4 базовых компонента + 5 конфигураций LLM  
✅ **Готовый код**: 85% переиспользование из проверенной системы  
✅ **Улучшение**: Реальные стоп-лоссы через Binance API (не эмуляция)

## 🏗️ Архитектурные компоненты
**Базовые (стабильные):**
## 🏗️ Архитектурная диаграмма системы

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              🎯 LLM TRADING SYSTEM                              │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                          📊 DATA PREPARATION LAYER                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ✅ DataPreparer                                                               │
│     ├── Level 1: 6 месяцев дневных свечей (глобальный тренд)                   │
│     ├── Level 2: 2 недели 4H свечей (среднесрочный анализ)                     │
│     ├── Level 3: 48 часов 1H свечей (краткосрочные сигналы)                    │
│     ├── Технические индикаторы: RSI, MACD, MA(20/50)                          │
│     └── Рыночный контекст: BTC корреляция, Fear & Greed Index                  │
│                                                                                 │
│  📤 Output: MarketDataSet (стандартизированный формат)                         │
└─────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                             🤖 LLM DECISION LAYER                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ✅ Abstract LLMProvider Interface                                             │
│     ├── ✅ ClaudeProvider    (ВЫБРАНО для MVP - Sonnet 4)                      │
│     ├── 🔄 GeminiProvider    (A/B тестирование - 2.5 Pro)                      │
│     └── 🔄 GPTProvider       (A/B тестирование - 4.1)                          │
│                                                                                 │
│  ❓ 5 КОНФИГУРАЦИЙ (ЧТО ОБСУДИТЬ):                                             │
│     ├── ✅ single           - одна модель работает                             │
│     ├── ❓ duplicate_pairs  - параллельные одинаковые модели                   │
│     ├── ❓ specialized      - разделение ролей между моделями                  │
│     ├── ❓ ensemble         - голосование всех трех                            │
│     └── ❓ sequential       - цепочка проверок                                 │
│                                                                                 │
│  🔧 LLMFactory + Configuration Manager (YAML-конфиги)                          │
│  📤 Output: TradeSignal (action, confidence, reasoning, stop_loss)             │
└─────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           📈 PORTFOLIO MANAGEMENT LAYER                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ✅ PortfolioManager (адаптация Trading_Script.py)                            │
│     ├── DataFrame структура портфеля                                           │
│     ├── PnL расчеты и производительность                                       │
│     ├── CSV логирование (portfolio_update.csv, trade_log.csv)                  │
│     └── Sharpe/Sortino ratio расчеты                                          │
│                                                                                 │
│  ✅ RiskManager                                                                │
│     ├── Проверка размера позиций                                               │
│     ├── Контроль максимальной просадки                                         │
│     └── Валидация торговых сигналов                                            │
└─────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                             💰 ORDER EXECUTION LAYER                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ✅ OrderExecutor (самописный Binance клиент)                                  │
│     ├── HTTP запросы через requests                                            │
│     ├── HMAC подпись через hmac + hashlib (stdlib)                             │
│     ├── Market orders исполнение                                               │
│     ├── 🔥 АВТОМАТИЧЕСКИЕ СТОП-ЛОСС ОРДЕРА (улучшение vs репозитория)          │
│     └── WebSocket real-time данные (через websockets)                          │
│                                                                                 │
│  🎯 Binance API Integration:                                                    │
│     ├── REST API для ордеров                                                   │
│     ├── WebSocket для real-time цен                                            │
│     └── 🔒 Security: API keys, rate limits, error handling                     │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              📊 MONITORING & ANALYTICS                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ✅ Performance Tracking (адаптация Generate_Graph.py)                         │
│     ├── Portfolio vs Bitcoin benchmark сравнение                              │
│     ├── Multi-LLM performance comparison                                       │
│     └── Визуализация через matplotlib                                          │
│                                                                                 │
│  ❓ 24/7 Monitoring (ЧТО ОБСУДИТЬ):                                            │
│     ├── ❓ Система алертов и уведомлений                                        │
│     ├── ❓ Error handling и restart logic                                       │
│     └── ❓ Logging и audit trail                                               │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                🔧 TECH STACK                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ✅ ОПРЕДЕЛЕНО:                                                                │
│  📦 Зависимости: requests, websockets, pandas + LLM APIs                       │
│  🐍 Python stdlib: hmac, hashlib, json, time, asyncio                         │
│  💾 Storage: CSV файлы (MVP) → PostgreSQL (production)                         │
│  🐳 Infrastructure: Docker контейнеризация                                     │
│                                                                                 │
│  ❓ ЧТО ОБСУДИТЬ:                                                               │
│  ❓ Deployment стратегия (VPS, cloud, local)                                   │
│  ❓ Backup и recovery процедуры                                                 │
│  ❓ Configuration management                                                     │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 📋 Статус компонентов

**✅ ОБСУЖДЕНО И РЕШЕНО:**
- Архитектурная основа (4 базовых компонента)
- Технологический стек и зависимости
- Структура данных для LLM (многоуровневая)
- Адаптация готового кода из ChatGPT-Micro-Cap-Experiment
- Автоматические стоп-лоссы (улучшение vs эмуляции)
- **Claude Sonnet 4 как стартовая LLM для MVP** (через GitHub Copilot)

**🔄 A/B ТЕСТИРОВАНИЕ:**
- GPT 4.1 и Gemini 2.5 Pro для сравнения производительности

**❓ НУЖНО ОБСУДИТЬ:**
- Детали конфигураций LLM (duplicate_pairs, specialized, ensemble, sequential)
- 24/7 monitoring и error handling стратегии
- Deployment и infrastructure решения
- Security best practices для production
- Testing стратегия (paper trading → live trading)

- **DataPreparer**: многоуровневые данные для LLM (6м + 2нед + 48ч)
- **PortfolioManager**: адаптация [`Trading_Script.py`](ChatGPT-Micro-Cap-Experiment/Scripts%20and%20CSV%20Files/Trading_Script.py)
- **RiskManager**: автоматические стоп-лосс ордера  
- **OrderExecutor**: Binance API интеграция

**LLM слой (модульный):**
- Abstract `LLMProvider` → `ClaudeProvider`, `GeminiProvider`, `GPTProvider`
- 5 конфигураций: single, duplicate_pairs, specialized, ensemble, sequential
- YAML-конфигурации для переключения без изменения кода

## 🗺️ Фазы разработки


### **🎯 PHASE 1 UPDATE: MarketDataService Complete**
**✅ ЗАВЕРШЕНО:**
- **DataPreparer Enhanced** - реализован MarketDataService с enhanced candlestick analysis
- **Smart Candlestick Selection** - 7-алгоритмический подход к отбору ключевых свечей
- **Token Optimization** - 15 ключевых свечей из 180 (экономия 91.7% токенов)
- **Pattern Recognition** - автоматическое определение Doji, Hammer, Shooting Star, Strong Bull/Bear
- **Live Testing** - успешное тестирование с BTC: "Downward bias", паттерны обнаружены
- **Dual Context API** - basic (~150-200 токенов) и enhanced (~300-400 токенов) режимы

**🔄 В РАБОТЕ:**
- **DataPreparer** ✅ MarketDataService with Enhanced Candlestick Analysis
### **Phase 1: Архитектурная реализация**
**Core Components:**
- [x] **DataPreparer** с многоуровневой структурой ✅ **MarketDataService Complete**
  - [x] Enhanced Candlestick Analysis (7-алгоритмический отбор ключевых свечей)
  - [x] Pattern Recognition (Doji, Hammer, Shooting Star, Strong Bull/Bear)
  - [x] Token Optimization (15 из 180 свечей, экономия 91.7% токенов)
  - [x] Dual Context API (basic ~150-200, enhanced ~300-400 токенов)
  - [x] Live Testing Success (BTC реальные данные с Binance API)
- [ ] PortfolioManager адаптация (yfinance → самописный Binance клиент)
- [ ] RiskManager с реальными стоп-лосс ордерами
- [ ] OrderExecutor - самописный клиент через requests + hmac подпись
- [ ] Abstract LLMProvider интерфейс

**Single Configuration:**
- [x] Выбор стартовой LLM ✅ **Claude Sonnet 4** (GitHub Copilot доступ)
- [ ] Concrete LLM Implementation (ClaudeProvider)
- [ ] YAML Configuration System
- [ ] Single Mode тестирование
- [ ] MarketDataSet/TradeSignal стандартизация

### **Phase 2: Multi-LLM масштабирование**
**Multiple Providers:**
- [ ] Все 3 LLM провайдера (Claude + Gemini + GPT)
- [ ] LLMFactory Pattern
- [ ] Configuration Manager
- [ ] Duplicate Pairs Mode

**Advanced Configurations:**
- [ ] Specialized Roles Mode
- [ ] Ensemble Strategy с голосованием
- [ ] Sequential Validation цепочка
- [ ] Performance Monitor для всех конфигураций

### **Phase 3: Production**
- [ ] WebSocket клиент через websockets библиотеку
- [ ] 24/7 scheduler и error handling
- [ ] Security audit
- [ ] Monitoring dashboard
- [ ] Testing с минимальным капиталом

## 📊 Технический стек
**Обоснованные зависимости**: requests, websockets, pandas
**Python stdlib**: hmac + hashlib (подпись), json, time, asyncio
**LLM APIs**: anthropic (Claude), openai (GPT), google.generativeai (Gemini)
**Самописное**: вся торговая логика и архитектурные компоненты

## 🎯 MVP Scope
- **5 криптопар**: BTC, ETH, BNB, ADA, SOL
- **Single LLM**: Claude/Gemini/GPT (выбрать)
- **1H таймфрейм**: среднесрочная торговля
- **Автоматические стоп-лоссы**: через Binance API
- **Paper trading**: безопасное тестирование

## ⚡ Преимущества vs оригинал
**Скорость**: 6-8 недель вместо 6-8 месяцев (отказ от ML обучения)  
**Автоматизация**: Полная автоматизация решений (не полуавтомат)  
**Риск-менеджмент**: Реальные стоп-лоссы (не эмуляция)  
**Масштабируемость**: 5 конфигураций LLM из коробки  
**24/7**: Криптовалютный рынок (не ограничен торговыми часами)

## 🚨 Риски и решения
**Token limits** → многоуровневая структура данных (300-400 свечей вместо 4320)  
**API costs** → мониторинг и лимиты запросов  
**Model hallucinations** → multi-model consensus и валидация  
**Market volatility** → автоматические стоп-лоссы и позиционное управление

## 📈 Ожидаемые результаты
**Phase 1**: MVP с автоматизацией LLM решений  
**Phase 2**: Сравнение производительности всех конфигураций  
**Phase 3**: Production-ready система 24/7

---

## 📋 **ТЕКУЩИЙ СТАТУС**

**✅ ЗАВЕРШЕНО:**
- Архитектурная основа в [`systemPatterns.md`](memory-bank/systemPatterns.md)
- Детальный анализ базового репозитория  
- Roadmap интегрирован с архитектурой
- Понимание готовых компонентов для адаптации

**🔄 В РАБОТЕ:**
- Выбор стартовой LLM для MVP

**📋 СЛЕДУЮЩИЕ ШАГИ:**
1. Определить стартовую LLM (Claude/Gemini/GPT)
2. Начать Phase 1: реализация базовых компонентов
3. Адаптация [`Trading_Script.py`](ChatGPT-Micro-Cap-Experiment/Scripts%20and%20CSV%20Files/Trading_Script.py) под архитектуру

**Дата обновления**: 2025-08-02  
**Статус**: Готов к практической реализации ✅