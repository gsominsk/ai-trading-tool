---
description: "Memory Bank Optimization (Safe Version)"
---

# Memory Bank Optimization Guide (Safe Version)

## Quick Reference

### **📋 INSTANT CHECKLIST (SAFE ARCHIVAL)**
```bash
# This checklist uses a timestamped directory to prevent data loss.

# 1. Define a unique archive directory using a UTC timestamp.
TIMESTAMP=$(date -u +"%Y%m%dT%H%M%SZ")
ARCHIVE_DIR="memory-bank/archive/$TIMESTAMP"

# 2. Check if the target directory already exists (it shouldn't). If it does, STOP.
if [ -d "$ARCHIVE_DIR" ]; then
  echo "Error: Archive directory $ARCHIVE_DIR already exists. Aborting."
  exit 1
fi

# 3. Create the unique, timestamped archive directory.
mkdir -p "$ARCHIVE_DIR"
echo "Archive directory created: $ARCHIVE_DIR"

# 4. Git commit current state before making changes.
git add . && git commit -m "pre-optimization checkpoint"

# 5. Copy all current .md files (except archives) into the new directory.
find memory-bank -maxdepth 1 -name "*.md" -exec cp {} "$ARCHIVE_DIR" \;
echo "Files successfully archived to $ARCHIVE_DIR"

# 6. Proceed with optimization of each file using the UNIVERSAL PATTERN.
echo "Now, manually optimize each file as needed."

# 7. Validate new size and functionality.

# 8. Commit with a comprehensive message.

# 9. Update activeContext.md with results.
```

### **🎯 UNIVERSAL OPTIMIZATION PATTERN**
```markdown
# [File Name]

## Archive Reference
Complete [description] history ([X] lines) archived in [`memory-bank/archive/[TIMESTAMP]/[filename].md`](memory-bank/archive/[TIMESTAMP]/[filename].md).

## Recent [Content] (Last 10 Entries)
[last 10 entries with full context]

## Historical [Content] Index (Chronological)
- [Date] - [Brief description]
...

## Summary Statistics
- **Total [Items]**: ~[N] entries
- **Archive Size**: [X] lines of complete history  
- **Current Active**: Last 10 entries
- **Complete History**: Available in the timestamped archive.

---
*Optimized [Date]: Reduced from [X] lines to optimized version + archive reference*
```

### **⚠️ CRITICAL SAFETY RULES**

**❌ NEVER:**
- Delete without archiving first.
- Optimize during active work.
- Skip git commits.
- Lose timestamps or connections.
- **DO NOT OPTIMIZE `systemPatterns.md`**. This file must remain in its complete, original state.

**✅ ALWAYS:**
- Archive FIRST, optimize SECOND.
- Use the timestamped script to prevent data loss.
- Preserve 100% historical context in archives.
- Create clear archive references.
- Test information accessibility after optimization.

## Detailed Process

See complete methodology in [`decisionLog.md`](memory-bank/decisionLog.md) - entry [2025-08-04 23:00:00]

## Recovery

**If problems occur:**
```bash
# Find the latest archive directory
LATEST_ARCHIVE=$(ls -td memory-bank/archive/*/ | head -1)

# Restore a specific file from the latest archive
cp "${LATEST_ARCHIVE}[filename].md" "memory-bank/[filename].md"

# Or revert the last git commit
git revert HEAD