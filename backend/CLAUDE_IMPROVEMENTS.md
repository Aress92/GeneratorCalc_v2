# Proposed Improvements to CLAUDE.md

Current CLAUDE.md is comprehensive (540+ lines) and well-structured.

## Suggested High-Priority Improvements

### 1. Add Quick Reference at Top
- Most common commands without scrolling
- Access points (URLs, credentials)
- Critical file locations

### 2. Add Common Pitfalls Section
- Don't use Poetry in Docker
- Don't use datetime.utcnow()
- Don't compare UUID objects directly
- Event loop issues in Celery

### 3. Add Architecture Diagram from README
- Visual system overview
- Data flow explanation

### 4. Reorganize Sections
- Move "Recent Fixes" to end
- Keep "Essential Commands" near top
- Add "Troubleshooting" section

### 5. Create CHANGELOG.md
- Move historical fixes (>7 days old)
- Keep CLAUDE.md focused on current state
