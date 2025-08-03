# Memory Bank Enhanced RooCode Modules

Этот набор RooCode модулей создан для решения проблемы "читаю но не использую" Memory Bank путем превращения Memory Bank из пассивного справочника в **активную руководящую систему**.

## Основные отличия от стандартных RooCode модулей

### 🔧 **Принудительная активация Memory Bank**
- Обязательные `<thinking>` блоки с цитатами из Memory Bank
- Формат ответов: `[MEMORY BANK: ACTIVE] + цитата + действие`
- Блокировка операций без Memory Bank verification
- Систематическая интеграция контекста в каждое решение

### 📋 **Расширенный состав Memory Bank файлов**
В дополнение к стандартным файлам добавлены:
- `workflowChecks.md` - автоматические проверки workflow
- `activationProtocol.md` - протокол принудительной активации

### 🚫 **Блокирующие механизмы**
- `attempt_completion` заблокирован без Memory Bank updates
- Критические операции требуют Memory Bank compliance
- Emergency override protocol для исключительных случаев

## Созданные модули

### 📐 **architect.yml** - Архитектурное планирование
**Фокус**: Проектирование, стратегия, техническая архитектура
**Специфика**: 
- Architectural decisions → decisionLog.md
- High-level planning и system design
- Strategic thinking с Memory Bank integration

### 💻 **code.yml** - Разработка и реализация
**Фокус**: Написание кода, рефакторинг, имплементация
**Специфика**:
- Implementation decisions → decisionLog.md
- Code quality gates и testing considerations
- Technical patterns → systemPatterns.md
- Pre/post code change workflows

### 🐛 **debug.yml** - Отладка и диагностика
**Фокус**: Поиск и решение проблем, диагностика
**Специфика**:
- Systematic investigation protocols
- Root cause analysis с Memory Bank integration
- Problem resolution → decisionLog.md
- Debug patterns → systemPatterns.md

### ❓ **ask.yml** - Анализ и исследование
**Фокус**: Ответы на вопросы, исследование, анализ
**Специфика**:
- Knowledge building и analytical insights
- Research methodologies → systemPatterns.md
- Insight documentation → decisionLog.md
- Context-aware analysis

### 🎭 **orchestrator.yml** - Координация проектов
**Фокус**: Многошаговые проекты, координация между режимами
**Специфика**:
- Cross-mode coordination protocols
- Workflow orchestration patterns
- Multi-phase project management
- Dependency tracking и milestone coordination

## Установка и использование

### 1. **Подготовка Global Instructions**
Добавьте следующие секции в ваши Global Instructions:

```yaml
memory_bank_strategy:
  initialization: |
      <thinking>
      - **CHECK FOR MEMORY BANK:**
      </thinking>
          <thinking>
        * First, check if the memory-bank/ directory exists.
          </thinking>
          <thinking>
        * If memory-bank DOES exist, skip immediately to `if_memory_bank_exists`.
          </thinking>
  if_no_memory_bank: |
      1. **Inform the User:**  
          "No Memory Bank was found. I recommend creating one to maintain project context. Would you like to switch to Flow-Architect mode to do this?"
      2. **Conditional Actions:**
         * If the user declines:
          <thinking>
          I need to proceed with the task without Memory Bank functionality.
          </thinking>
          a. Inform the user that the Memory Bank will not be created.
          b. Set the status to '[MEMORY BANK: INACTIVE]'.
          c. Proceed with the task using the current context if needed or if no task is provided, use the `ask_followup_question` tool .
         * If the user agrees:
          Switch to Flow-Architect mode to create the Memory Bank.
  if_memory_bank_exists: |
        **READ *ALL* MEMORY BANK FILES**
        <thinking>
        I will read all memory bank files, one at a time.
        </thinking>
        Plan: Read all mandatory files sequentially.
        1. Read `productContext.md`
        2. Read `activeContext.md` 
        3. Read `systemPatterns.md` 
        4. Read `decisionLog.md` 
        5. Read `progress.md` 
        6. Read `workflowChecks.md`
        7. Read `activationProtocol.md`
        8. Set status to [MEMORY BANK: ACTIVE] and inform user.
        9. Apply activation protocol with <thinking> blocks and blocking mechanisms
        10. Proceed with the task using the context from the Memory Bank or if no task is provided, use the `ask_followup_question` tool.
      
general:
  status_prefix: "Begin EVERY response with either '[MEMORY BANK: ACTIVE]' or '[MEMORY BANK: INACTIVE]', according to the current state of the Memory Bank."

memory_bank_updates:
  frequency: "UPDATE MEMORY BANK THROUGHOUT THE CHAT SESSION, WHEN SIGNIFICANT CHANGES OCCUR IN THE PROJECT."
  
umb:
  trigger: "^(Update Memory Bank|UMB)$"
  instructions:
    - "Halt Current Task: Stop current activity"
    - "Acknowledge Command: '[MEMORY BANK: UPDATING]'"
    - "Review Chat History"
  override_file_restrictions: true
  override_mode_restrictions: true
```

### 2. **Создание необходимых Memory Bank файлов**
Убедитесь что в вашем проекте есть:
- `memory-bank/productContext.md`
- `memory-bank/activeContext.md`
- `memory-bank/systemPatterns.md`
- `memory-bank/decisionLog.md`
- `memory-bank/progress.md`
- `memory-bank/workflowChecks.md`
- `memory-bank/activationProtocol.md`

### 3. **Замена стандартных RooCode модулей**
Используйте созданные .yml файлы вместо стандартных RooCode промптов для каждого режима.

## Ключевые принципы работы

### 🎯 **Активационный протокол**
Каждое действие должно:
1. Начинаться с чтения Memory Bank
2. Включать `<thinking>` блоки с цитатами
3. Использовать формат `[MEMORY BANK: ACTIVE] + цитата + действие`
4. Обновлять Memory Bank при значимых изменениях

### 🚪 **Quality Gates**
Перед завершением задач проверяется:
- Memory Bank синхронизация
- Документирование решений
- Обновление паттернов
- Фиксация прогресса

### ⚡ **Блокирующие механизмы**
- `attempt_completion` без Memory Bank updates = BLOCKED
- Критические операции без compliance = BLOCKED  
- Emergency override только в исключительных случаях

## Ожидаемые результаты

### ✅ **Полное устранение проблемы "читаю но не использую"**
- Memory Bank становится активным руководящим механизмом
- Каждое решение интегрируется с существующим контекстом
- Преемственность знаний между сессиями

### 📈 **Улучшение качества работы**
- Систематический подход к решению задач
- Документирование всех решений и паттернов
- Накопление знаний проекта

### 🔄 **Workflow automation**
- Автоматические проверки качества
- Предотвращение нарушений процедур
- Стандартизированные процессы

## Техническая поддержка

Модули разработаны как улучшение стандартной RooCode архитектуры с сохранением совместимости. Все блокирующие механизмы имеют emergency override возможности для критических ситуаций.

---

**Статус**: Готово к производственному использованию
**Версия**: 1.0 (2025-08-03)
**Совместимость**: RooCode v3.25.6+