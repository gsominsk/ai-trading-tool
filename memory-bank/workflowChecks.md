# Memory Bank Workflow Rules

## CRITICAL RULE - NEVER VIOLATE!

### 🚫 File Creation Policy
**NEVER CREATE NEW FILES WITHOUT EXPLICIT USER PERMISSION**
- Do not create configuration files, scripts, or any other files
- Always ask user permission before creating any new file

## Simple Rules (replacing 374-line complex system)

### Rule 1: Start with Memory Bank
Read all Memory Bank files at session start, set `[MEMORY BANK: ACTIVE]` status.

### Rule 2: Update on Changes
Update relevant Memory Bank files when completing tasks or making decisions.

### Rule 3: Commit Before Completion
Update Memory Bank and git commit before using `attempt_completion`.

## Archive Reference
Complex workflow rules (374 lines) archived in `memory-bank/archive/workflowChecks.md` for reference.

---
*Simplified 2025-01-04: Reduced from 374 lines to 3 rules for efficiency*