# RooCode Modules - Memory Bank Enhanced

This directory contains Memory Bank enhanced versions of all RooCode mode prompts, designed to provide seamless integration with the Memory Bank system for context continuity across sessions.

## Available Modules

### 🏗️ [Architect Mode](architect.md)
- **Focus**: System architecture design and technical planning
- **Memory Bank Integration**: Builds on previous architectural decisions and established patterns
- **Key Features**: Design pattern selection, technology evaluation, system documentation
- **File Restrictions**: Documentation and design files only (`.md`, `architecture/.*`, `docs/.*`)

### 💻 [Code Mode](code.md) 
- **Focus**: Code implementation, debugging, and feature development
- **Memory Bank Integration**: Applies established coding patterns and builds on previous implementations
- **Key Features**: Full code editing, testing, optimization, error handling
- **File Access**: Complete project access including source code, tests, and configuration

### 🪲 [Debug Mode](debug.md)
- **Focus**: Systematic troubleshooting and issue investigation
- **Memory Bank Integration**: Leverages historical debugging patterns and known issue solutions
- **Key Features**: Root cause analysis, error reproduction, performance debugging
- **Methodology**: Systematic investigation with Memory Bank context

### ❓ [Ask Mode](ask.md)
- **Focus**: Technical explanations and guidance
- **Memory Bank Integration**: Provides contextually-aware answers based on project history
- **Key Features**: Code analysis, best practice guidance, concept explanation
- **Approach**: Comprehensive answers building on established project knowledge

### 🪃 [Orchestrator Mode](orchestrator.md)
- **Focus**: Complex multi-step project coordination
- **Memory Bank Integration**: Strategic planning with full historical context
- **Key Features**: Task decomposition, workflow coordination, progress tracking
- **Scope**: Manages large initiatives across multiple domains

## Memory Bank Integration Features

### Universal Activation Protocol
All modes implement the same Memory Bank activation sequence:

1. **Automatic Detection**: Check for memory-bank/ directory existence
2. **Comprehensive Reading**: Load all Memory Bank files for context
3. **Thinking Integration**: Mandatory `<thinking>` blocks for activation
4. **Status Declaration**: Begin responses with `[MEMORY BANK: ACTIVE]`
5. **Context Application**: Quote and apply relevant Memory Bank content

### Blocking Mechanisms
Each mode includes enforcement mechanisms:

- **Tool Use Blocking**: Verification checks before every tool use
- **Completion Blocking**: `attempt_completion` blocked without Memory Bank updates
- **Workflow Compliance**: Adherence to established workflow rules
- **Quality Gates**: Ensure decisions build on established context

### Response Format
Standard response structure across all modes:

```
[MEMORY BANK: ACTIVE]

**FROM MEMORY BANK**: "[specific relevant quote]"
**[MODE] ACTION**: [mode-specific action based on Memory Bank context]

[Rest of response with full integration]
```

### Emergency Override
All modes support emergency override when Memory Bank is unavailable:

```
[MEMORY BANK: OVERRIDE ACTIVE]

**OVERRIDE REASON**: [explanation]
**RECOVERY PLAN**: [restoration approach]
**TODO**: Restore Memory Bank activation
```

## Implementation Instructions

### For RooCode Setup:
1. **Replace Existing Prompts**: Use these enhanced versions instead of standard RooCode prompts
2. **Verify Memory Bank**: Ensure memory-bank/ directory exists in your project
3. **Test Activation**: Confirm Memory Bank activation works in each mode
4. **Monitor Compliance**: Verify blocking mechanisms function correctly

### For New Projects:
1. **Initialize Memory Bank**: Create memory-bank/ directory with core files
2. **Install Mode Prompts**: Add these files to your RooCode modules directory
3. **Configure Integration**: Ensure proper file paths and permissions
4. **Validate Workflow**: Test complete Memory Bank integration

## Benefits

### Context Continuity
- **Session Persistence**: Work continues seamlessly across sessions
- **Decision History**: Full record of architectural and implementation decisions
- **Pattern Recognition**: Established patterns automatically applied
- **Knowledge Accumulation**: Learning builds over time

### Quality Assurance
- **Consistency**: All work follows established patterns and standards
- **Completeness**: Blocking mechanisms prevent incomplete work
- **Traceability**: Full audit trail of decisions and changes
- **Best Practices**: Accumulated best practices automatically applied

### Efficiency Gains
- **Reduced Rework**: Avoid repeating previous mistakes
- **Faster Onboarding**: New sessions start with full context
- **Better Decisions**: Informed by complete project history
- **Systematic Progress**: Coordinated advancement toward goals

## Troubleshooting

### Memory Bank Not Activating
- Verify memory-bank/ directory exists
- Check file permissions and accessibility
- Ensure all required Memory Bank files are present
- Validate file content format and structure

### Blocking Mechanisms Not Working
- Confirm prompts include blocking verification sections
- Verify Memory Bank files contain required content
- Check for proper integration in mode configuration
- Test with simple scenarios to validate functionality

### Context Not Integrating
- Ensure activation protocol runs completely
- Verify `<thinking>` blocks execute properly
- Check Memory Bank file content relevance
- Validate quote extraction and application

## Maintenance

### Regular Updates
- Keep Memory Bank files current with project progress
- Update mode prompts when new features are needed
- Validate integration continues to work correctly
- Monitor for any drift or degradation in quality

### Version Control
- Track changes to mode prompts in version control
- Document any customizations or modifications
- Maintain backup copies of working configurations
- Test changes in non-production environments first

---

**Result**: These Memory Bank enhanced RooCode modules provide seamless context continuity, systematic quality assurance, and efficient project development through intelligent integration of accumulated knowledge and established patterns.