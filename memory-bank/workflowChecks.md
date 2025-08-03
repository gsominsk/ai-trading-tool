# Workflow Checks - Автоматические Проверки Memory Bank

**ЦЕЛЬ**: Предотвратить нарушения Memory Bank First Pattern и обеспечить правильный workflow во всех сессиях.

---

## ОБЯЗАТЕЛЬНЫЕ АВТОМАТИЧЕСКИЕ ПРОВЕРКИ

### 1. SESSION INITIALIZATION CHECK
```
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

### 2. PRE-COMPLETION CHECK
```
🔒 БЛОКИРОВКА: attempt_completion заблокирован без обновления Memory Bank

ПРАВИЛО ЗАВЕРШЕНИЯ:
❌ ЗАПРЕЩЕНО: attempt_completion без обновления Memory Bank
❌ ЗАПРЕЩЕНО: Финализация задач без git commit Memory Bank изменений

✅ ОБЯЗАТЕЛЬНАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ:
1. Завершить все технические задачи
2. Обновить релевантные Memory Bank файлы
3. Зафиксировать Memory Bank в git commit
4. ТОЛЬКО ПОСЛЕ ЭТОГО attempt_completion
```

### 3. MEMORY BANK UPDATE TRIGGERS
```
🚨 АВТОМАТИЧЕСКИЕ ТРИГГЕРЫ ОБНОВЛЕНИЯ:

ОБЯЗАТЕЛЬНО обновлять Memory Bank при:
- Завершении любой значимой задачи
- Принятии архитектурных решений
- Обнаружении критических проблем
- Завершении этапов разработки
- Изменении статуса проекта
- Создании новых паттернов или решений

ФАЙЛЫ ДЛЯ ОБНОВЛЕНИЯ:
- progress.md: при завершении задач
- activeContext.md: при изменении фокуса
- decisionLog.md: при принятии решений  
- systemPatterns.md: при создании новых паттернов
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
1. ОБЯЗАТЕЛЬНО прочитать все 5 файлов Memory Bank
2. Установить статус [MEMORY BANK: ACTIVE]  
3. ТОЛЬКО ПОСЛЕ ЭТОГО отвечать на вопросы пользователя

НОВОЕ ПРАВИЛО #2: COMPLETION BLOCKER
ПЕРЕД attempt_completion:
1. ОБЯЗАТЕЛЬНО обновить релевантные Memory Bank файлы
2. ОБЯЗАТЕЛЬНО зафиксировать изменения в git
3. ТОЛЬКО ПОСЛЕ ЭТОГО выполнять attempt_completion
```

---

**РЕЗУЛЬТАТ**: Система автоматических проверок предотвратит нарушения workflow и обеспечит правильное использование Memory Bank во всех будущих сессиях.