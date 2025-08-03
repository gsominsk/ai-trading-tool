# Product Context

This file provides a high-level overview of the project and the expected product that will be created. Initially it is based upon projectBrief.md (if provided) and all other available project-related information in the working directory. This file is intended to be updated as the project evolves, and should be used to inform all other modes of the project's goals and context.
2025-08-01 23:45:57 - Log of updates made will be appended as footnotes to the end of this file.

*

## Project Goal

*   

## Key Features

*   

## Overall Architecture

*   

2025-08-01 22:13:06 - PDF план анализирован: "Пошаговый план создания автономной торговой системы на базе ИИ". Обнаружен детальный 9-этапный план создания AI-бота для торговли криптовалютами на Binance с часовым таймфреймом.

## Project Goal

Создание автономной AI-торговой системы для криптовалют на бирже Binance с использованием часового таймфрейма (1H) для среднесрочной торговли до 100 топовых криптовалют.

## Key Features

- Автономное принятие торговых решений на базе ИИ
- Торговля на таймфрейме 1H (среднесрочные позиции)
- Поддержка до 100 криптовалют одновременно
- Двухуровневая система анализа: числовые данные + компьютерное зрение
- Встроенный риск-менеджмент и контроль просадки
- 24/7 мониторинг и уведомления
- Модульная архитектура с возможностью масштабирования

## Overall Architecture

**ОБНОВЛЕНО:** Модульная LLM-система включает:
- Модуль сбора данных (Binance API с многоуровневой структурой)
- **LLM-движок** (Claude 4, Gemini 2.5 Pro, GPT o3 вместо собственных ML-моделей)
- Модуль исполнения ордеров (адаптированный из ChatGPT-Micro-Cap-Experiment)
- Система риск-менеджмента
- Интерфейс мониторинга и сравнения производительности моделей
- Хранилище данных (PostgreSQL/InfluxDB)
- Контейнеризация через Docker

**Структура данных для LLM:**
- Уровень 1: 6 месяцев дневных свечей (глобальный тренд)
- Уровень 2: 2 недели 4H свечей (среднесрочный анализ)
- Уровень 3: 48 часов 1H свечей (краткосрочные сигналы)
- Технические индикаторы: RSI, MACD, MA(20/50)
- Рыночный контекст: корреляция с BTC, Fear & Greed Index

[2025-08-03 23:25:00] - **RooCode Memory Bank Enforcement System - Complete Implementation**

The AI trader project now includes a comprehensive Memory Bank workflow enforcement system using RooCode native capabilities. This represents a major architectural achievement that solves the fundamental problem of AI workflow discipline through external system controls rather than impossible AI self-blocking.

**Key Components Added:**
- External enforcement via fileRegex restrictions and XML blocking rules
- Mode-specific specialization with proper responsibility separation  
- Comprehensive documentation and validation testing
- Long-term maintainable configuration-as-code approach

**Impact:** The AI trader project now has robust workflow infrastructure that ensures consistent Memory Bank discipline across all development sessions, providing reliable project context preservation for complex algorithmic trading system development.