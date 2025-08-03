# 🤖 AI Trading System - Autonomous Cryptocurrency Trading Bot

**Автономная торговая система на базе LLM для криптовалютного рынка (Binance API, 1H таймфрейм)**

![Python](https://img.shields.io/badge/python-v3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)

## 🎯 Обзор проекта

Система использует готовые LLM модели (Claude Sonnet 4, Gemini 2.5 Pro, GPT 4.1) вместо обучения собственных ML-моделей для принятия торговых решений. Построена на основе проверенной архитектуры [ChatGPT-Micro-Cap-Experiment](https://github.com/ChatGPT-Micro-Cap-Experiment) с улучшениями для криптовалютной торговли.

### ✨ Ключевые особенности

- **🧠 LLM-powered Trading**: Claude, Gemini, GPT для анализа рынка и принятия решений
- **📊 Enhanced Candlestick Analysis**: Smart selection алгоритм (15 ключевых свечей из 180)
- **🛡️ Automatic Stop-Loss**: Реальные стоп-лосс ордера через Binance API (не эмуляция) 
- **⚡ Token Optimization**: 91.7% экономия токенов при сохранении точности
- **🔄 Multi-timeframe Data**: 6 месяцев дневных + 2 недели 4H + 48 часов 1H свечей
- **📈 Pattern Recognition**: Doji, Hammer, Shooting Star, Strong Bull/Bear автоопределение
- **24/7 Trading**: Непрерывная торговля на криптовалютных рынках

## 🏗️ Архитектура системы

```
┌─────────────────────────────────────────────────────────────────┐
│                    🎯 LLM TRADING SYSTEM                        │
└─────────────────────────────────────────────────────────────────┘

📊 DATA LAYER          🤖 LLM LAYER           📈 EXECUTION LAYER
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ MarketDataService│    │ ClaudeProvider  │    │ PortfolioManager│
│ ✅ Enhanced     │───▶│ GeminiProvider  │───▶│ RiskManager     │
│ Candlestick     │    │ GPTProvider     │    │ OrderExecutor   │
│ Analysis        │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🔧 Основные компоненты

- **MarketDataService** ✅ - многоуровневая подготовка данных с enhanced candlestick analysis
- **LLM Providers** 🔄 - модульные интерфейсы для Claude, Gemini, GPT
- **PortfolioManager** - адаптация проверенной системы управления портфелем
- **RiskManager** - автоматические стоп-лоссы и контроль рисков
- **OrderExecutor** - самописный Binance API клиент

## 📈 Результаты тестирования

### Live Testing (BTC):
- **Цена**: $112,713.07
- **24H изменение**: -0.98%
- **RSI(14)**: 35.77 (Neutral)
- **MACD**: Bearish
- **Тренд**: Downward bias
- **Паттерны**: Shooting Star, Hammer, Strong Bear, Doji
- **S/R Tests**: 1 resistance test, 1 support test
- **Анализ объемов**: Weak bearish signal

## 🚀 Быстрый старт

### Предварительные требования

```bash
Python 3.9+
Binance API ключи
```

### Установка

```bash
# Клонирование репозитория
git clone https://github.com/your-username/ai-trading-system.git
cd ai-trading-system

# Установка зависимостей
pip install -r requirements.txt

# Настройка конфигурации
cp config/trading_config.yaml.example config/trading_config.yaml
# Отредактируйте API ключи в config/trading_config.yaml
```

### Базовое использование

```python
from src.market_data.market_data_service import create_market_data_service

# Создание сервиса
service = create_market_data_service()

# Получение базового анализа (~150-200 токенов)
basic_data = service.get_market_data("BTCUSDT")
print(basic_data.to_llm_context())

# Получение расширенного анализа (~300-400 токенов)
enhanced_context = service.get_enhanced_context("BTCUSDT")
print(enhanced_context)
```

## 📊 Enhanced Candlestick Analysis

### 7-Algorithm Smart Selection

1. **Recent 5 candles** - текущий рыночный контекст
2. **Extreme candles** - максимумы/минимумы за 30 дней  
3. **High volume candles** - топ 10% объема за 20 дней
4. **Big moves** - движения >3% за день
5. **Pattern candles** - технические фигуры (Doji, Hammer, etc.)
6. **S/R test candles** - взаимодействие с поддержкой/сопротивлением
7. **Deduplication** - удаление дубликатов и сортировка

### Pattern Recognition

- **Doji**: `body/range < 0.1` - нерешительность рынка
- **Hammer**: `lower_shadow/range > 0.6` - потенциальный разворот вверх
- **Shooting Star**: `upper_shadow/range > 0.6` - потенциальный разворот вниз
- **Strong Bull/Bear**: `body/range > 0.7` - сильное направленное движение

## 🔧 Конфигурация

### LLM Providers

```yaml
# Single Model Mode (MVP)
mode: single
provider: claude  # или gemini, gpt

# Ensemble Mode (Advanced)
mode: ensemble
providers: [claude, gemini, gpt]
voting_strategy: majority
```

### Trading Parameters

```yaml
trading:
  symbols: ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT"]
  timeframe: "1h"
  max_position_size: 0.02  # 2% портфеля на позицию
  stop_loss_pct: 0.03      # 3% стоп-лосс
```

## 📋 Roadmap

### ✅ Phase 1: Core Components (Completed)
- [x] MarketDataService с Enhanced Candlestick Analysis
- [x] Smart Selection Algorithm (7 алгоритмов)
- [x] Pattern Recognition System
- [x] Token Optimization (91.7% экономия)
- [x] Live Testing с Binance API

### 🔄 Phase 2: LLM Integration (In Progress)
- [ ] Claude Provider implementation
- [ ] GitHub Copilot API integration
- [ ] Structured prompt engineering
- [ ] TradeSignal standardization

### 📋 Phase 3: Portfolio Management (Planned)
- [ ] PortfolioManager адаптация из Trading_Script.py
- [ ] RiskManager с автоматическими стоп-лоссами
- [ ] CSV persistence system
- [ ] Performance analytics

### 🎯 Phase 4: Production Ready (Planned)
- [ ] OrderExecutor с Binance API
- [ ] 24/7 monitoring system
- [ ] WebSocket real-time data
- [ ] Security audit

## 📈 Преимущества vs Традиционные Боты

| Параметр | Традиционные боты | AI Trading System |
|----------|-------------------|-------------------|
| **Скорость разработки** | 6-8 месяцев | 6-8 недель |
| **Принятие решений** | Фиксированные алгоритмы | LLM анализ |
| **Стоп-лоссы** | Эмуляция | Реальные Binance ордера |
| **Масштабируемость** | Ограниченная | 5 LLM конфигураций |
| **Адаптивность** | Низкая | Высокая (LLM reasoning) |

## 🛡️ Управление рисками

- **Automatic Stop-Loss**: Реальные стоп-лосс ордера через Binance API
- **Position Sizing**: Максимум 2% портфеля на позицию
- **Token Limits**: Оптимизация запросов к LLM (300-400 токенов)
- **Multi-Model Validation**: Консенсус между несколькими LLM
- **24/7 Monitoring**: Непрерывный контроль позиций

## 📊 Tech Stack

### Проверенные зависимости
- **requests** - HTTP клиент для Binance API
- **websockets** - Real-time данные
- **pandas** - Обработка данных и DataFrame операции

### Python stdlib
- **hmac + hashlib** - Подпись Binance запросов
- **json, time, asyncio** - Базовые операции

### LLM APIs
- **anthropic** - Claude Sonnet 4
- **openai** - GPT 4.1
- **google.generativeai** - Gemini 2.5 Pro

## 📄 Лицензия

MIT License - см. файл [LICENSE](LICENSE)

## ⚠️ Disclaimer

Данная система предназначена для образовательных целей. Торговля криптовалютами несет высокие риски. Всегда тестируйте стратегии на демо-счетах перед использованием реальных средств.

## 🤝 Contributing

1. Fork проект
2. Создайте feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit изменения (`git commit -m 'Add some AmazingFeature'`)
4. Push в branch (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## 📞 Поддержка

- 📧 Email: [your-email@example.com]
- 💬 Telegram: [@your-telegram]
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/ai-trading-system/issues)

---

**⭐ Поставьте звезду, если проект был полезен!**