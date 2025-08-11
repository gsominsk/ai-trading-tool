---
description: "Memory Bank Optimization"
---

# Memory Bank Optimization Guide

## Quick Reference

### **📋 INSTANT CHECKLIST**
```
[ ] 1. Analyze current size: `find memory-bank -name "*.md" -not -path "*/archive/*" -exec wc -l {} + | tail -1`
[ ] 2. Git commit current state: `git add . && git commit -m "pre-optimization checkpoint"`
[ ] 3. Create archive directory: `mkdir -p memory-bank/archive`
[ ] 4. Archive originals: `cp memory-bank/*.md memory-bank/archive/`
[ ] 5. Optimize each file using UNIVERSAL PATTERN
[ ] 6. Validate new size and functionality
[ ] 7. Commit with comprehensive message
[ ] 8. Update activeContext.md with results
```

### **🎯 UNIVERSAL OPTIMIZATION PATTERN**
```markdown
# [File Name]

## Archive Reference
Complete [description] history ([X] lines) archived in [`memory-bank/archive/[filename].md`](memory-bank/archive/[filename].md).

## Recent [Content] (Last 10 Entries)
[last 10 entries with full context]

## Historical [Content] Index (Chronological)
- [Date] - [Brief description]
...

## Summary Statistics
- **Total [Items]**: ~[N] entries
- **Archive Size**: [X] lines of complete history  
- **Current Active**: Last 10 entries
- **Complete History**: Available in archive

---
*Optimized [Date]: Reduced from [X] lines to optimized version + archive reference*
```

### **⚠️ CRITICAL SAFETY RULES**

**❌ NEVER:**
- Delete without archiving first
- Optimize during active work
- Skip git commits
- Lose timestamps or connections

- **DO NOT OPTIMIZE `systemPatterns.md`**. This file must remain in its complete, original state.
**✅ ALWAYS:**
- Archive FIRST, optimize SECOND
- Preserve 100% historical context
- Create clear archive references
- Test information accessibility

## Detailed Process

See complete methodology in [`decisionLog.md`](memory-bank/decisionLog.md) - entry [2025-08-04 23:00:00]

## Recovery

**If problems occur:**
```bash
# Restore from archive
cp memory-bank/archive/[filename].md memory-bank/[filename].md

# Or revert git
git revert [commit-hash]
```