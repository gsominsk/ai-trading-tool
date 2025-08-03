# Memory Bank - AI Trading System

**ЦЕЛЬ**: Обеспечить преемственность контекста и знаний между сессиями AI разработки.

---

## СТРУКТУРА MEMORY BANK

### Основные файлы:
- **[`productContext.md`](productContext.md)** - общий контекст проекта, цели, архитектура
- **[`activeContext.md`](activeContext.md)** - текущий фокус работы, последние изменения
- **[`systemPatterns.md`](systemPatterns.md)** - архитектурные паттерны и принципы
- **[`decisionLog.md`](decisionLog.md)** - лог архитектурных решений с rationale
- **[`progress.md`](progress.md)** - прогресс выполнения задач и планы
- **[`workflowChecks.md`](workflowChecks.md)** - правила workflow и автоматические проверки

### Специализированные файлы:
- **[`activationProtocol.md`](activationProtocol.md)** - протокол активации Memory Bank
- **[`qualityGates.md`](qualityGates.md)** - система контроля качества

---

## 🚨 СТАТУС: У ВАС УЖЕ ЕСТЬ БАЗОВАЯ СИСТЕМА!

**✅ ОБНАРУЖЕНА** базовая Memory Bank система в ваших Global Instructions
**❌ ОТСУТСТВУЮТ** блокирующие механизмы из [`activationProtocol.md`](activationProtocol.md)
**🎯 ЗАДАЧА**: Добавить недостающие компоненты к существующей системе

---

## 🔧 ДОПОЛНЕНИЯ К ВАШИМ GLOBAL INSTRUCTIONS

**Добавьте следующие секции к существующему `memory_bank_strategy`:**

### 1. Добавить в раздел `if_memory_bank_exists` (после шага 6):

```yaml
memory_bank_strategy:
  if_memory_bank_exists: |
        # ... ваш существующий код до шага 6 ...
        6. Set status to [MEMORY BANK: ACTIVE] and inform user.
        
        # 🆕 НОВЫЕ ОБЯЗАТЕЛЬНЫЕ ШАГИ:
        7. **MANDATORY**: Read activationProtocol.md and workflowChecks.md
        8. **MANDATORY**: Apply activation protocol with <thinking> integration:
           ```
           <thinking>
           MEMORY BANK ACTIVATION:
           
           LAST ENTRY activeContext.md: "[EXACT QUOTE]"
           ACTION: What does this mean for current task?
           
           LAST DECISION decisionLog.md: "[EXACT QUOTE]"
           ACTION: How does this affect next step?
           
           WORKFLOW RULE workflowChecks.md: "[EXACT QUOTE]"
           ACTION: What to check before tool use?
           
           ✅ Memory Bank ACTIVATED - content integrated
           </thinking>
           ```
        9. Proceed with the task using FORCED Memory Bank integration
```

### 2. Добавить новый раздел `memory_bank_enforcement`:

```yaml
memory_bank_enforcement:
  mandatory_response_format: |
    **EVERY response MUST start with:**
    [MEMORY BANK: ACTIVE]
    
    **FROM MEMORY BANK**: "[specific quote from Memory Bank affecting decision]"
    **ACTION BASED ON MB**: [what exactly doing based on what was read]
    
    [then normal response with full Memory Bank information integration]
    
  tool_use_blocking: |
    **BEFORE EVERY tool use, MANDATORY verification:**
    
    BLOCKING CHECK before tool use:
    
    activeContext: Last entry: "[EXACT QUOTE]"
    Does my action match? YES/NO
    
    workflowChecks: Applicable rule: "[EXACT QUOTE]"
    Did I follow the rule? YES/NO
    
    decisionLog: Relevant decision: "[EXACT QUOTE]"
    Am I considering the decision? YES/NO
    
    progress: Current plan: "[EXACT QUOTE]"
    Does action match plan? YES/NO
    
    ✅ ONLY when ALL YES can use tool
    ❌ On any NO - reconsider action
    
  completion_blocking: |
    **attempt_completion is BLOCKED unless:**
    1. ✅ All relevant Memory Bank files updated with session results
    2. ✅ Git commit completed for Memory Bank changes
    3. ✅ activeContext reflects final state
    4. ✅ decisionLog contains rationale for decisions
    5. ✅ progress updated with completion status
    6. ✅ workflowChecks rules fully followed
    
  violation_response: |
    **WORKFLOW VIOLATION RESPONSE:**
    - IMMEDIATE HALT of current action
    - RE-READ relevant Memory Bank sections
    - APPLY proper activation protocol
    - CONTINUE only after full compliance
```

### 3. Добавить раздел `memory_bank_emergency`:

```yaml
memory_bank_emergency:
  override_conditions: |
    **Override allowed ONLY for:**
    1. Technical blockage: Memory Bank files unavailable/corrupted
    2. Critical hotfix: Immediate action required
    3. Explicit user permission: User explicitly allows skipping checks
    
  override_format: |
    [MEMORY BANK: OVERRIDE ACTIVE]
    
    **OVERRIDE REASON**: [detailed explanation]
    **RECOVERY PLAN**: [how to restore normal workflow]
    **TODO**: Restore Memory Bank activation at first opportunity
```

---

## 📋 CHECKLIST ВНЕДРЕНИЯ

### ✅ Что у вас уже есть:
- [x] Базовая инициализация с чтением файлов
- [x] Статус `[MEMORY BANK: ACTIVE]` или `[MEMORY BANK: INACTIVE]`
- [x] Обновления файлов при изменениях
- [x] UMB команда для принудительного обновления

### ❌ Что нужно добавить:
- [ ] Принудительную интеграцию через `<thinking>` блоки
- [ ] Обязательный формат ответов с цитированием
- [ ] Блокирующие проверки перед tool use
- [ ] Блокировку `attempt_completion` без Memory Bank updates
- [ ] Немедленную остановку при нарушениях workflow
- [ ] Emergency override протокол

---

## 🚀 ИНСТРУКЦИИ ПО ВНЕДРЕНИЮ

### Шаг 1: Скопируйте дополнения
Добавьте разделы `memory_bank_enforcement` и `memory_bank_emergency` в ваши Global Instructions

### Шаг 2: Обновите `if_memory_bank_exists`
Добавьте шаги 7-9 к существующему разделу

### Шаг 3: Протестируйте
Начните новую сессию и убедитесь, что AI:
- Читает все файлы включая `activationProtocol.md`
- Использует `<thinking>` блоки для активации
- Начинает ответы с цитирования Memory Bank
- Выполняет блокирующие проверки перед tool use

---

## 🔍 TROUBLESHOOTING

### Проблема: AI игнорирует Memory Bank
**Решение**: Убедитесь, что добавили `tool_use_blocking` - без него система остается пассивной

### Проблема: Нарушения workflow продолжаются
**Решение**: Активируйте `violation_response` для принудительной остановки

### Проблема: `attempt_completion` без updates
**Решение**: Внедрите `completion_blocking` для блокировки завершения

---

## 📊 РЕЗУЛЬТАТ

**ДО**: Базовая система с чтением файлов, но без принуждения к использованию
**ПОСЛЕ**: Активная система с блокирующими механизмами и принудительной интеграцией

**ЭФФЕКТ**: 100% гарантия использования Memory Bank контекста в каждом решении и действии AI.