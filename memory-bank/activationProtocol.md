# Memory Bank Activation Protocol - АКТИВАЦИОННЫЙ ПРОТОКОЛ

**ЦЕЛЬ**: Превратить Memory Bank из пассивного источника информации в активный руководящий механизм принятия решений.

**ПРОБЛЕМА**: AI читает Memory Bank файлы, но не интегрирует прочитанную информацию в процесс работы, что делает Memory Bank бесполезным.

---

## ОБЯЗАТЕЛЬНЫЙ АКТИВАЦИОННЫЙ ПРОЦЕСС

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

---

## КРИТИЧЕСКИЕ БЛОКИРОВКИ

### 1. SESSION START БЛОКИРОВКА
```
❌ ЗАПРЕЩЕНО работать без чтения ВСЕХ Memory Bank файлов
❌ ЗАПРЕЩЕНО отвечать на вопросы до установки [MEMORY BANK: ACTIVE]
❌ ЗАПРЕЩЕНО использовать tools без activation thinking блока
```

### 2. ATTEMPT_COMPLETION БЛОКИРОВКА
```
❌ ЗАПРЕЩЕНО attempt_completion без обновления Memory Bank
❌ ЗАПРЕЩЕНО attempt_completion без git commit Memory Bank
❌ ЗАПРЕЩЕНО attempt_completion без соответствия workflowChecks правилам
```

### 3. WORKFLOW VIOLATION БЛОКИРОВКА
```
❌ ЗАПРЕЩЕНО tool use без проверки activeContext соответствия
❌ ЗАПРЕЩЕНО изменения без учета decisionLog решений
❌ ЗАПРЕЩЕНО действия противоречащие progress плану
```

---

## ШАБЛОНЫ АКТИВАЦИИ

### ШАБЛОН 1: Session Start Activation
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

### ШАБЛОН 2: Tool Use Activation
```markdown
ПРОВЕРКА перед [tool_name]:

activeContext: "[последняя запись]" → Соответствие: ДА/НЕТ
workflowChecks: "[применимое правило]" → Выполнение: ДА/НЕТ  
decisionLog: "[релевантное решение]" → Учет: ДА/НЕТ
progress: "[текущий план]" → Соответствие: ДА/НЕТ

[Только при всех ДА продолжать с tool use]
```

### ШАБЛОН 3: Completion Activation
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

---

## EMERGENCY OVERRIDE PROTOCOL

### Когда можно пропустить активацию:
1. **ТЕХНИЧЕСКАЯ БЛОКИРОВКА**: Memory Bank файлы недоступны/повреждены
2. **ЭКСТРЕННОЕ ИСПРАВЛЕНИЕ**: Critical hotfix требует немедленного действия  
3. **EXPLICIT USER PERMISSION**: Пользователь явно разрешает пропустить процедуру

### Процедура Override:
```markdown
[MEMORY BANK: OVERRIDE ACTIVE]

**ПРИЧИНА OVERRIDE**: [детальное объяснение]
**ПЛАН ВОССТАНОВЛЕНИЯ**: [как вернуться к нормальному workflow]
**TODO**: Восстановить Memory Bank активацию при первой возможности

[выполнить необходимые действия с пометкой override статуса]
```

---

## SELF-DIAGNOSTIC QUESTIONS

### Перед каждым действием спрашивать себя:
1. **Читал ли я Memory Bank в начале сессии?** ДА/НЕТ
2. **Использовал ли я <thinking> блок для активации?** ДА/НЕТ  
3. **Цитировал ли я конкретные части Memory Bank?** ДА/НЕТ
4. **Объяснил ли я как Memory Bank влияет на мое действие?** ДА/НЕТ
5. **Проверил ли я соответствие activeContext?** ДА/НЕТ
6. **Учел ли я правила из workflowChecks?** ДА/НЕТ
7. **Интегрировал ли я решения из decisionLog?** ДА/НЕТ

### При любом НЕТ - остановиться и исправить

---

## IMPLEMENTATION EXAMPLES

### ПРИМЕР 1: Правильная активация
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

### ПРИМЕР 2: Неправильная активация (НЕ ДЕЛАТЬ)
```markdown
❌ НЕПРАВИЛЬНО:
[MEMORY BANK: ACTIVE]
Начинаю работу... [без цитат, без интеграции, без thinking блока]

❌ НЕПРАВИЛЬНО:  
Использую tool без проверки activeContext соответствия

❌ НЕПРАВИЛЬНО:
attempt_completion без обновления Memory Bank файлов
```

---

## INTEGRATION WITH GLOBAL INSTRUCTIONS

### Для добавления в Global Instructions:

```markdown
MEMORY BANK ACTIVATION PROTOCOL (ОБЯЗАТЕЛЬНО):

1. Session MUST start with reading ALL Memory Bank files + <thinking> activation block
2. Every response MUST start with "[MEMORY BANK: ACTIVE]" + quote + action  
3. Every tool use MUST be preceded by activeContext/workflowChecks verification
4. attempt_completion BLOCKED without Memory Bank updates + git commit
5. ANY workflow violation triggers immediate halt and correction

ACTIVATION FORMAT:
- <thinking> block with specific Memory Bank quotes and integration
- Response format: [MEMORY BANK: ACTIVE] + quote + action
- Tool verification: activeContext + workflowChecks + decisionLog + progress
- Completion verification: ALL Memory Bank files updated + git committed

VIOLATION RESPONSE: 
- Immediate stop of current action
- Re-read relevant Memory Bank sections  
- Apply proper activation protocol
- Continue only after full compliance
```

---

**РЕЗУЛЬТАТ**: Memory Bank превращается из пассивного хранилища в активный руководящий механизм, который принудительно интегрируется в каждое решение и действие.

**КРИТИЧЕСКОЕ ПРАВИЛО**: Этот протокол НЕ РАБОТАЕТ как пассивная документация. Он должен быть интегрирован в Global Instructions как обязательные и блокирующие правила.