# 🚨 КРИТИЧНО: Workflow Enforcement System - Priority Coded

**💰 СТОИМОСТЬ ОШИБКИ**: Workflow violation = полная потеря контекста проекта = начало с нуля = потеря дней работы

⚠️ **ВАЖНО**: Предотвратить нарушения Memory Bank First Pattern через циклическое укрепление нейронных паттернов

## 🔄 СИСТЕМА ЦИКЛИЧЕСКОГО УКРЕПЛЕНИЯ

**🧠 NEURONAL PATTERN REINFORCEMENT**:
- 🚨 **КРИТИЧНО**: Каждые 3-5 tool операций → обязательное re-read activeContext.md
- ⚠️ **ВАЖНО**: Перед значимыми решениями → consult decisionLog.md
- ℹ️ **ИНФОРМАЦИЯ**: При workflow нарушениях → emergency Memory Bank reinforcement

**💰 COST ANALYSIS**:
- ✅ **Compliance Success**: Preserved context + productive work + user satisfaction
- ❌ **Violation Cost**: Lost progress + restart work + user frustration + wasted time

---

## 🚨 БЛОКИРУЮЩИЕ ПРАВИЛА - МАКСИМАЛЬНЫЙ ПРИОРИТЕТ

### 1. 🚨 КРИТИЧНО: SESSION INITIALIZATION CHECK
```
💰 FAILURE COST: Complete project context loss = starting from zero
🔒 БЛОКИРОВКА: Никакие действия не могут быть выполнены до чтения Memory Bank

ПРАВИЛО ИНИЦИАЛИЗАЦИИ СЕССИИ:
❌ ЗАПРЕЩЕНО: Начинать работу без чтения всех файлов Memory Bank
❌ ЗАПРЕЩЕНО: Отвечать на вопросы пользователя до чтения Memory Bank  
❌ ЗАПРЕЩЕНО: Выполнять любые tool operations до Memory Bank review

✅ ОБЯЗАТЕЛЬНО: 
1. Прочитать productContext.md
2. Прочитать activeContext.md  
3. Прочитать systemPatterns.md
4. Прочитать decisionLog.md
5. Прочитать progress.md
6. Установить статус [MEMORY BANK: ACTIVE]
7. ТОЛЬКО ПОСЛЕ ЭТОГО приступать к задачам
```

### 2. 🚨 КРИТИЧНО: PRE-COMPLETION CHECK
```
💰 FAILURE COST: Session work lost + next assistant confusion + restart overhead
🔒 БЛОКИРОВКА: attempt_completion заблокирован без обновления Memory Bank

🚨 КРИТИЧНО - ПРАВИЛО ЗАВЕРШЕНИЯ:
❌ ЗАПРЕЩЕНО: attempt_completion без обновления Memory Bank
❌ ЗАПРЕЩЕНО: Финализация задач без git commit Memory Bank изменений
❌ ЗАПРЕЩЕНО: attempt_completion без проверки activation protocol

⚠️ ВАЖНО - ОБЯЗАТЕЛЬНАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ:
1. Завершить все технические задачи
2. Обновить релевантные Memory Bank файлы с timestamps
3. Применить ACTIVATION PROTOCOL проверку
4. Зафиксировать Memory Bank в git commit
5. ТОЛЬКО ПОСЛЕ ЭТОГО attempt_completion
```

### 3. 🚨 КРИТИЧНО: MEMORY BANK UPDATE TRIGGERS
```
💰 FAILURE COST: Decision context loss + repeated mistakes + architectural drift

🚨 АВТОМАТИЧЕСКИЕ ТРИГГЕРЫ ОБНОВЛЕНИЯ:

⚠️ ВАЖНО - ОБЯЗАТЕЛЬНО обновлять Memory Bank при:
- Завершении любой значимой задачи (🚨 КРИТИЧНО для continuity)
- Принятии архитектурных решений (🚨 КРИТИЧНО для consistency)
- Обнаружении критических проблем (⚠️ ВАЖНО для future sessions)
- Завершении этапов разработки (⚠️ ВАЖНО for progress tracking)
- Изменении статуса проекта (ℹ️ ИНФОРМАЦИЯ for status awareness)
- Создании новых паттернов или решений (🚨 КРИТИЧНО for reuse)

💰 COST ANALYSIS - ФАЙЛЫ ДЛЯ ОБНОВЛЕНИЯ:
- progress.md: при завершении задач (💰 HIGH COST if missed)
- activeContext.md: при изменении фокуса (💰 HIGH COST if missed)
- decisionLog.md: при принятии решений (💰 EXTREME COST if missed)
- systemPatterns.md: при создании новых паттернов (💰 MEDIUM COST if missed)
```

---

## WORKFLOW VALIDATION RULES

### RULE 1: Memory Bank First Pattern (Железное правило)
```python
def validate_session_start():
    if not all_memory_bank_files_read():
        raise WorkflowViolation("CANNOT PROCEED: Memory Bank not read")
    if status != "MEMORY_BANK_ACTIVE":
        raise WorkflowViolation("CANNOT PROCEED: Memory Bank status not active")
    return True
```

### RULE 2: Pre-Completion Validation (Обязательная проверка)
```python
def validate_attempt_completion():
    if not memory_bank_updated_in_session():
        raise WorkflowViolation("CANNOT COMPLETE: Memory Bank not updated")
    if not git_commit_memory_bank():
        raise WorkflowViolation("CANNOT COMPLETE: Memory Bank changes not committed")
    return True
```

### RULE 3: Task Completion Pattern (Паттерн завершения задач)
```python
def validate_task_completion():
    if task_completed and not memory_bank_considerations_logged():
        raise WorkflowViolation("MUST LOG: Task completion requires Memory Bank update")
    return True
```

---

## EMERGENCY OVERRIDE PROTOCOL

### Когда можно пропустить Memory Bank checks:
```
🚨 ТОЛЬКО В КРИТИЧЕСКИХ СЛУЧАЯХ:

1. ТЕХНИЧЕСКАЯ БЛОКИРОВКА: Memory Bank файлы недоступны/повреждены
2. ЭКСТРЕННОЕ ИСПРАВЛЕНИЕ: Critical hotfix требует немедленного действия
3. ПОЛЬЗОВАТЕЛЬСКОЕ РАЗРЕШЕНИЕ: Explicit instruction от пользователя пропустить checks

ПРОЦЕДУРА OVERRIDE:
1. Зафиксировать причину в activeContext.md
2. Добавить TODO для восстановления правильного workflow
3. Выполнить необходимые действия с пометкой [OVERRIDE ACTIVE]
4. Восстановить нормальный workflow при первой возможности
```

---

## АВТОМАТИЧЕСКИЕ НАПОМИНАНИЯ

### Self-Check Questions (Вопросы самопроверки):
```
ПЕРЕД КАЖДЫМ ДЕЙСТВИЕМ СПРАШИВАТЬ СЕБЯ:
❓ Прочитал ли я Memory Bank в начале сессии?
❓ Понимаю ли я текущий контекст проекта?
❓ Учитываю ли я предыдущие решения из decisionLog?
❓ Соответствует ли мое действие установленным паттернам?

ПЕРЕД attempt_completion СПРАШИВАТЬ:
❓ Обновлен ли Memory Bank с учетом выполненной работы?
❓ Зафиксированы ли изменения в git?
❓ Есть ли все необходимые решения в decisionLog?
❓ Отражает ли activeContext текущий статус?
```

### Memory Bank Health Indicators:
```
🟢 ЗДОРОВЫЙ WORKFLOW:
- [MEMORY BANK: ACTIVE] статус установлен
- Все файлы прочитаны и поняты
- Регулярные обновления при значимых изменениях
- Git commits включают Memory Bank updates

🟡 ПРЕДУПРЕЖДЕНИЕ:
- Memory Bank не обновлялся длительное время
- Отсутствуют записи о принятых решениях
- activeContext не отражает текущую работу

🔴 КРИТИЧЕСКАЯ ПРОБЛЕМА:
- Работа без чтения Memory Bank
- attempt_completion без обновления Memory Bank
- Нарушение установленных workflow правил
```

---

## ВНЕДРЕНИЕ В ИНСТРУКЦИИ

### Обновленные Global Instructions:
```
НОВОЕ ПРАВИЛО #1: MEMORY BANK MANDATORY CHECK
В НАЧАЛЕ КАЖДОЙ СЕССИИ:
1. ОБЯЗАТЕЛЬНО прочитать все Memory Bank файлы (включая workflowChecks.md)
2. Установить статус [MEMORY BANK: ACTIVE]
3. ПРИМЕНИТЬ ACTIVATION PROTOCOL из данного файла
4. ТОЛЬКО ПОСЛЕ ЭТОГО отвечать на вопросы пользователя

НОВОЕ ПРАВИЛО #2: COMPLETION BLOCKER
ПЕРЕД attempt_completion:
1. ОБЯЗАТЕЛЬНО обновить релевантные Memory Bank файлы
2. ПРИМЕНИТЬ completion verification из данного протокола
3. ОБЯЗАТЕЛЬНО зафиксировать изменения в git
4. ТОЛЬКО ПОСЛЕ ЭТОГО выполнять attempt_completion

НОВОЕ ПРАВИЛО #3: ACTIVATION PROTOCOL ENFORCEMENT
КАЖДЫЙ ОТВЕТ ДОЛЖЕН:
1. Начинаться с [MEMORY BANK: ACTIVE] + цитата + действие
2. Использовать <thinking> блок для активации Memory Bank
3. Проверять соответствие activeContext/workflowChecks перед tool use
4. БЛОКИРОВАТЬ действия при нарушении протокола
```

---

## ДЕТАЛЬНЫЙ ПРОТОКОЛ АКТИВАЦИИ MEMORY BANK

### ЭТАП 1: READING ACTIVATION (после чтения Memory Bank)

**ОБЯЗАТЕЛЬНЫЙ <thinking> БЛОК:**
```markdown
<thinking>
АКТИВАЦИЯ MEMORY BANK:

ПОСЛЕДНЯЯ ЗАПИСЬ activeContext.md: "[ТОЧНАЯ ЦИТАТА из последней записи]"
ДЕЙСТВИЕ: Что именно это означает для моей текущей задачи?

ПОСЛЕДНЕЕ РЕШЕНИЕ decisionLog.md: "[ТОЧНАЯ ЦИТАТА из последнего decision]"
ДЕЙСТВИЕ: Как это решение влияет на мой следующий шаг?

ТЕКУЩИЙ СТАТУС progress.md: "[ТОЧНАЯ ЦИТАТА о current status]"
ДЕЙСТВИЕ: Какой следующий шаг указан в плане?

WORKFLOW ПРАВИЛО workflowChecks.md: "[ТОЧНАЯ ЦИТАТА конкретного правила]"
ДЕЙСТВИЕ: Что я должен проверить перед следующим tool use?

✅ Memory Bank АКТИВИРОВАН - содержимое интегрировано в план действий
</thinking>
```

### ЭТАП 2: RESPONSE ACTIVATION (каждый ответ)

**ОБЯЗАТЕЛЬНЫЙ ФОРМАТ:**
```markdown
[MEMORY BANK: ACTIVE]

**ИЗ MEMORY BANK**: "[конкретная цитата из Memory Bank, влияющая на текущее решение]"
**ДЕЙСТВИЕ НА ОСНОВЕ MB**: [что именно делаю исходя из прочитанного]

[далее обычный ответ с полной интеграцией Memory Bank информации]
```

### ЭТАП 3: TOOL USE ACTIVATION (перед каждым tool)

**ПРИНУДИТЕЛЬНАЯ ПРОВЕРКА:**
```markdown
БЛОКИРУЮЩАЯ ПРОВЕРКА перед tool use:

activeContext: Последняя запись говорит: "[ТОЧНАЯ ЦИТАТА]"
Соответствует ли мое действие этому контексту? ДА/НЕТ

workflowChecks: Применимое правило: "[ТОЧНАЯ ЦИТАТА правила]"
Выполнил ли я это правило? ДА/НЕТ

decisionLog: Релевантное решение: "[ТОЧНАЯ ЦИТАТА решения]"
Учитываю ли я это решение? ДА/НЕТ

progress: Текущий план: "[ТОЧНАЯ ЦИТАТА из плана]"
Соответствует ли мое действие плану? ДА/НЕТ

✅ ТОЛЬКО при ВСЕХ ДА можно использовать tool
❌ При любом НЕТ - пересмотреть действие
```

### ШАБЛОНЫ АКТИВАЦИИ

#### ШАБЛОН 1: Session Start Activation
```markdown
<thinking>
АКТИВАЦИЯ MEMORY BANK при старте сессии:

1. productContext.md - цель проекта: "[цитата]"
2. activeContext.md - текущий фокус: "[цитата]"
3. systemPatterns.md - ключевые паттерны: "[цитата]"
4. decisionLog.md - последнее решение: "[цитата]"
5. progress.md - текущий статус: "[цитата]"
6. workflowChecks.md - обязательные правила: "[цитата]"

ИНТЕГРАЦИЯ: На основе прочитанного мой план действий:
- Следующий шаг: [на основе activeContext + progress]
- Ограничения: [на основе workflowChecks + decisionLog]
- Контекст: [на основе productContext + systemPatterns]

✅ Memory Bank полностью активирован и интегрирован
</thinking>

[MEMORY BANK: ACTIVE]

**ИЗ MEMORY BANK**: activeContext.md указывает "[цитата текущего фокуса]"
**ДЕЙСТВИЕ НА ОСНОВЕ MB**: [конкретное действие основанное на прочитанном]
```

#### ШАБЛОН 2: Tool Use Activation
```markdown
ПРОВЕРКА перед [tool_name]:

activeContext: "[последняя запись]" → Соответствие: ДА/НЕТ
workflowChecks: "[применимое правило]" → Выполнение: ДА/НЕТ
decisionLog: "[релевантное решение]" → Учет: ДА/НЕТ
progress: "[текущий план]" → Соответствие: ДА/НЕТ

[Только при всех ДА продолжать с tool use]
```

#### ШАБЛОН 3: Completion Activation
```markdown
ПРОВЕРКА перед attempt_completion:

✅ Memory Bank файлы обновлены с результатами работы?
✅ Git commit выполнен для Memory Bank изменений?
✅ activeContext отражает финальное состояние?
✅ decisionLog содержит rationale для принятых решений?
✅ progress обновлен с completion статусом?
✅ workflowChecks правила соблюдены?

[Только при всех ✅ разрешен attempt_completion]
```

### SELF-DIAGNOSTIC QUESTIONS РАСШИРЕННЫЕ

#### Перед каждым действием спрашивать себя:
1. **Читал ли я Memory Bank в начале сессии?** ДА/НЕТ
2. **Использовал ли я <thinking> блок для активации?** ДА/НЕТ
3. **Цитировал ли я конкретные части Memory Bank?** ДА/НЕТ
4. **Объяснил ли я как Memory Bank влияет на мое действие?** ДА/НЕТ
5. **Проверил ли я соответствие activeContext?** ДА/НЕТ
6. **Учел ли я правила из workflowChecks?** ДА/НЕТ
7. **Интегрировал ли я решения из decisionLog?** ДА/НЕТ

#### При любом НЕТ - остановиться и исправить

### ПРИМЕРЫ АКТИВАЦИИ

#### ПРИМЕР: Правильная активация
```markdown
<thinking>
АКТИВАЦИЯ MEMORY BANK:

activeContext: "Next Decision Point: Choose between logging implementation vs other priorities"
ДЕЙСТВИЕ: Мне нужно определить приоритет на основе текущего состояния проекта

workflowChecks: "attempt_completion заблокирован без обновления Memory Bank"
ДЕЙСТВИЕ: Перед любым attempt_completion должен обновить Memory Bank файлы

✅ Memory Bank активирован - буду следовать установленным приоритетам
</thinking>

[MEMORY BANK: ACTIVE]

**ИЗ MEMORY BANK**: activeContext показывает "Choose between logging implementation vs other priorities"
**ДЕЙСТВИЕ НА ОСНОВЕ MB**: Анализирую текущие приоритеты и выбираю следующий шаг согласно плану
```

#### ПРИМЕР: Неправильная активация (НЕ ДЕЛАТЬ)
```markdown
❌ НЕПРАВИЛЬНО:
[MEMORY BANK: ACTIVE]
Начинаю работу... [без цитат, без интеграции, без thinking блока]

❌ НЕПРАВИЛЬНО:
Использую tool без проверки activeContext соответствия

❌ НЕПРАВИЛЬНО:
attempt_completion без обновления Memory Bank файлов
```

### Integration требования для Global Instructions:
```markdown
MEMORY BANK ACTIVATION PROTOCOL (обязательно добавить):

1. Session MUST start with reading ALL Memory Bank files + <thinking> activation
2. Response format: [MEMORY BANK: ACTIVE] + quote + action MANDATORY
3. Tool use MUST be preceded by activeContext/workflowChecks verification
4. attempt_completion BLOCKED without Memory Bank updates + git commit
5. Workflow violations trigger immediate halt and correction
```

---

**РЕЗУЛЬТАТ**: Memory Bank превращается из пассивного хранилища в активный руководящий механизм, который принудительно интегрируется в каждое решение и действие через детальные шаблоны и обязательные проверки.

--- Appended on Thu Aug  7 00:03:19 EEST 2025 ---


# Инструкция по Управлению TODO-листом

## Основные Принципы:

### Атомарность Задач
Каждый пункт в списке должен представлять собой одно, неделимое действие. Не объединяй несколько действий в один пункт.

**Неправильно:**
```
[ ] 1.5: Запустить тесты, обновить Memory Bank и сделать коммит.
```
**Правильно:**
```
[ ] 1.5: Запустить все тесты для Фазы 1.
[ ] 1.6: Обновить Memory Bank по итогам Фазы 1.
[ ] 1.7: Сделать коммит с сообщением '...'
```

### Строгое Разделение Обязанностей
Административные задачи, такие как `Обновить Memory Bank`, `Сделать коммит`, `Запустить тесты`, ОБЯЗАТЕЛЬНО должны быть отдельными пунктами списка. Их нельзя объединять с задачами по разработке или созданию файлов.

### Фазовая Структура
- Весь план должен быть разбит на пронумерованные фазы: `--- ФАЗА X: [Название Фазы] ---`.
- Каждая задача внутри фазы должна быть пронумерована в формате `X.Y`, где X — номер фазы, а Y — номер шага.

## Пример правильного рабочего процесса для одной фичи:

```
[ ] 1.1: Реализовать фичу X в файле Y.
[ ] 1.2: Создать тест для фичи X в файле Z.
[ ] 1.3: Запустить все тесты для Фазы 1.
[ ] 1.4: Обновить Memory Bank, отразив прогресс по фиче X.
[ ] 1.5: Сделать коммит с сообщением 'feat: implement and test feature X'.

--- Appended on Thu Aug  7 00:03:27 EEST 2025 ---


# Инструкция по Управлению TODO-листом

## Основные Принципы:

### Атомарность Задач
Каждый пункт в списке должен представлять собой одно, неделимое действие. Не объединяй несколько действий в один пункт.

**Неправильно:**
```
[ ] 1.5: Запустить тесты, обновить Memory Bank и сделать коммит.
```
**Правильно:**
```
[ ] 1.5: Запустить все тесты для Фазы 1.
[ ] 1.6: Обновить Memory Bank по итогам Фазы 1.
[ ] 1.7: Сделать коммит с сообщением '...'
```

### Строгое Разделение Обязанностей
Административные задачи, такие как `Обновить Memory Bank`, `Сделать коммит`, `Запустить тесты`, ОБЯЗАТЕЛЬНО должны быть отдельными пунктами списка. Их нельзя объединять с задачами по разработке или созданию файлов.

### Фазовая Структура
- Весь план должен быть разбит на пронумерованные фазы: `--- ФАЗА X: [Название Фазы] ---`.
- Каждая задача внутри фазы должна быть пронумерована в формате `X.Y`, где X — номер фазы, а Y — номер шага.

## Пример правильного рабочего процесса для одной фичи:

```
[ ] 1.1: Реализовать фичу X в файле Y.
[ ] 1.2: Создать тест для фичи X в файле Z.
[ ] 1.3: Запустить все тесты для Фазы 1.
[ ] 1.4: Обновить Memory Bank, отразив прогресс по фиче X.
[ ] 1.5: Сделать коммит с сообщением 'feat: implement and test feature X'.