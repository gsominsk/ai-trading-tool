# Quality Gates Framework

**Цель:** Автоматизация quality assurance процесса для предотвращения преждевременного завершения задач без надлежащего тестирования.

**Принцип:** Блокировка всех completion операций до прохождения всех обязательных качественных ворот.

## 🚨 CRITICAL WORKFLOW RULES

### **БЛОКИРУЮЩИЕ ОПЕРАЦИИ:**
1. **`update_todo_list` с статусом "Completed"** - ЗАБЛОКИРОВАН без прохождения Quality Gates
2. **`git commit`** - ЗАБЛОКИРОВАН без подтверждения качества
3. **`attempt_completion`** - ЗАБЛОКИРОВАН без полной валидации

### **ОБЯЗАТЕЛЬНОЕ ОБНОВЛЕНИЕ:**
- **`activeContext.md`** автоматически обновляется при нарушении Quality Gates

## 🎯 MANDATORY QUALITY GATES

### **GATE 1: CODE IMPLEMENTATION** ✅ 
- [ ] Код написан и функционален
- [ ] Логика соответствует требованиям
- [ ] Нет синтаксических ошибок

### **GATE 2: UNIT TESTING** 🧪
- [ ] Unit тесты созданы
- [ ] Все тесты проходят (зеленые)
- [ ] Покрытие основных сценариев

### **GATE 3: EDGE CASES COVERAGE** ⚡
- [ ] Edge cases идентифицированы
- [ ] Тесты для edge cases созданы
- [ ] Защита от граничных условий

### **GATE 4: MANUAL VERIFICATION** 👨‍💻
- [ ] Ручное тестирование выполнено
- [ ] Реальные данные протестированы
- [ ] Результаты зафиксированы

### **GATE 5: REAL-WORLD TESTING** 🌍
- [ ] Интеграционное тестирование
- [ ] Production-like условия
- [ ] Performance validation

### **GATE 6: DOCUMENTATION** 📚
- [ ] Изменения документированы
- [ ] Commit message детальный
- [ ] Memory Bank обновлен

## 🔧 WORKFLOW PATTERNS

### **NEW FEATURE DEVELOPMENT**
```
Code Implementation → Unit Tests → Edge Cases → Manual Testing → Real-world Testing → Documentation → Git Commit
```

**ОБЯЗАТЕЛЬНЫЕ GATES:** 1, 2, 3, 4, 5, 6

### **BUG FIXING** 
```
Problem Analysis → Fix Implementation → Regression Tests → Manual Verification → Edge Cases → Git Commit
```

**ОБЯЗАТЕЛЬНЫЕ GATES:** 1, 2, 3, 4, 6

### **CODE MAINTENANCE**
```
Code Updates → Unit Test Updates → Manual Verification → Documentation → Git Commit  
```

**ОБЯЗАТЕЛЬНЫЕ GATES:** 1, 2, 4, 6

### **CRITICAL HOTFIX**
```
Emergency Fix → Minimal Testing → Manual Verification → Git Commit → Post-fix Comprehensive Testing
```

**ОБЯЗАТЕЛЬНЫЕ GATES:** 1, 4, 6 (с последующим возвратом к полным gates)

## 🚫 GATE ENFORCEMENT PROTOCOL

### **ПЕРЕД `update_todo_list` → "Completed":**

**ОБЯЗАТЕЛЬНАЯ ПРОВЕРКА:**
```
1. Читать текущий qualityGates.md
2. Сопоставить задачу с workflow pattern
3. Проверить все обязательные gates
4. Если НЕ ВСЕ gates пройдены → БЛОКИРОВАТЬ update
5. Если ВСЕ gates пройдены → разрешить update
```

### **ПЕРЕД `git commit`:**

**ОБЯЗАТЕЛЬНАЯ ПРОВЕРКА:**
```  
1. Убедиться что все gates пройдены
2. Если gates не пройдены → БЛОКИРОВАТЬ commit
3. Записать в activeContext.md о блокировке
```

### **ПЕРЕД `attempt_completion`:**

**ОБЯЗАТЕЛЬНАЯ ПРОВЕРКА:**
```
1. Полная валидация всех выполненных задач
2. Проверка что ВСЕ completed задачи прошли gates
3. Если есть нарушения → БЛОКИРОВАТЬ completion
```

## 🔄 AUTO-UPDATE TRIGGERS

### **НАРУШЕНИЕ QUALITY GATES:**
Автоматически добавить в `activeContext.md`:
```
[TIMESTAMP] - QUALITY GATE VIOLATION
Task: [название задачи]  
Violated Gates: [список не пройденных gates]
Action Required: [конкретные действия для исправления]
Status: BLOCKED until gates passed
```

### **УСПЕШНОЕ ПРОХОЖДЕНИЕ GATES:**
Автоматически добавить в `activeContext.md`:
```
[TIMESTAMP] - QUALITY GATES PASSED
Task: [название задачи]
Gates Passed: [список пройденных gates]  
Status: Ready for completion
```

## 🎯 GATE VALIDATION CHECKLIST

### **ДЛЯ КАЖДОЙ ЗАДАЧИ ПРОВЕРИТЬ:**

**CODE IMPLEMENTATION ✅**
- Изменения внесены в код?
- Код компилируется/запускается?
- Функциональность работает?

**UNIT TESTING 🧪**
- Созданы ли новые тесты?
- Существующие тесты обновлены?
- Все тесты зеленые?

**EDGE CASES ⚡**
- Идентифицированы граничные случаи?
- Созданы тесты для edge cases?
- Протестированы extreme условия?

**MANUAL VERIFICATION 👨‍💻**
- Выполнено ручное тестирование?
- Протестированы реальные сценарии?
- Результаты зафиксированы?

**REAL-WORLD TESTING 🌍**
- Integration testing выполнен?
- Production-like данные?
- Performance приемлемая?

**DOCUMENTATION 📚**
- Изменения документированы?
- Memory Bank обновлен?
- Commit message детальный?

## 🚨 EMERGENCY OVERRIDE

**ТОЛЬКО ПО EXPLICIT РАЗРЕШЕНИЮ ПОЛЬЗОВАТЕЛЯ:**
```
USER OVERRIDE: "Skip quality gates for [specific reason]"
```

**В СЛУЧАЕ OVERRIDE:**
1. Записать причину в activeContext.md
2. Добавить TODO для возврата к полным gates
3. Продолжить workflow с warnings

## 💡 USAGE EXAMPLES

### **ПРАВИЛЬНЫЙ WORKFLOW:**
```
AI: "Задача выполнена, готов пометить completed"
AI: [Читает qualityGates.md]
AI: "Проверяю gates: Code ✅, Unit Tests ❌, Edge Cases ❌"
AI: "GATE БЛОКИРОВКА: Не пройдены Unit Tests и Edge Cases"
AI: [Создает недостающие тесты]
AI: "Все gates пройдены ✅, помечаю completed"
```

### **НЕПРАВИЛЬНЫЙ WORKFLOW (ЗАБЛОКИРОВАН):**
```
AI: "Код работает, помечаю completed"
SYSTEM: "ERROR - Quality Gates не пройдены"
AI: [Обновляет activeContext.md с violation]
AI: "Возвращаюсь к созданию тестов"
```

---

**Последнее обновление:** 2025-08-03  
**Версия:** 1.0  
**Статус:** АКТИВНО ДЕЙСТВУЮЩИЙ FRAMEWORK

--- Appended on Thu Aug  7 00:03:19 EEST 2025 ---


# Quality Gates Framework

## Archive Reference
Complete Quality Gates Framework (201 lines) archived in [`memory-bank/archive/qualityGates.md`](memory-bank/archive/qualityGates.md).

## Core Quality Requirements

### **Mandatory Gates for Production Code**
- **Code Implementation** ✅ - Functional code without syntax errors
- **Unit Testing** 🧪 - All tests passing with edge case coverage  
- **Manual Verification** 👨‍💻 - Real-world testing and result validation
- **Documentation** 📚 - Changes documented, Memory Bank updated

### **Workflow Enforcement**
- **BLOCKED**: `update_todo_list` → "Completed" without passing gates
- **BLOCKED**: `git commit` without quality validation
- **BLOCKED**: `attempt_completion` without full gate verification

### **Emergency Override**
- Only with explicit user permission: "Skip quality gates for [reason]"
- Must document override reason and create follow-up TODO

---
*Optimized 2025-08-05: Reduced from 201 lines to core gates + archive reference*

--- Appended on Thu Aug  7 00:03:27 EEST 2025 ---


# Quality Gates Framework

## Archive Reference
Complete Quality Gates Framework (201 lines) archived in [`memory-bank/archive/qualityGates.md`](memory-bank/archive/qualityGates.md).

## Core Quality Requirements

### **Mandatory Gates for Production Code**
- **Code Implementation** ✅ - Functional code without syntax errors
- **Unit Testing** 🧪 - All tests passing with edge case coverage  
- **Manual Verification** 👨‍💻 - Real-world testing and result validation
- **Documentation** 📚 - Changes documented, Memory Bank updated

### **Workflow Enforcement**
- **BLOCKED**: `update_todo_list` → "Completed" without passing gates
- **BLOCKED**: `git commit` without quality validation
- **BLOCKED**: `attempt_completion` without full gate verification

### **Emergency Override**
- Only with explicit user permission: "Skip quality gates for [reason]"
- Must document override reason and create follow-up TODO

---
*Optimized 2025-08-05: Reduced from 201 lines to core gates + archive reference*