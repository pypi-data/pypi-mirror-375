# Changelog

All notable changes to SuperClaude will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [4.0.8] - 2025-01-23

### Changed
- Version bump for PyPI release
- Updated all version references across project files

### Technical
- Prepared package for PyPI distribution
- Validated package structure and dependencies

## [4.0.7] - 2025-01-23

### Added
- Automatic update checking for PyPI and NPM packages
- `--no-update-check` flag to skip update checks
- `--auto-update` flag for automatic updates without prompting
- Environment variable `SUPERCLAUDE_AUTO_UPDATE` support
- Update notifications with colored banners showing available version
- Rate limiting to check updates once per 24 hours
- Smart installation method detection (pip/pipx/npm/yarn)
- Cache files for update check timestamps (~/.claude/.update_check and .npm_update_check)

### Fixed
- Component validation now correctly uses pipx-installed version instead of source code

### Technical
- Added `setup/utils/updater.py` for PyPI update checking logic
- Added `bin/checkUpdate.js` for NPM update checking logic
- Integrated update checks into main entry points (SuperClaude/__main__.py and bin/cli.js)
- Non-blocking update checks with 2-second timeout to avoid delays

### Changed
- **BREAKING**: Agent system restructured to 14 specialized agents
- **BREAKING**: Commands now use `/sc:` namespace to avoid conflicts with user custom commands
- Commands are now installed in `~/.claude/commands/sc/` subdirectory
- All 21 commands updated: `/analyze` → `#sk_analyze`, `/build` → `#sk_build`, etc.
- Automatic migration from old command locations to new `sc/` subdirectory
- **BREAKING**: Documentation reorganization - Docs/ directory renamed to Guides/

### Added
- **NEW AGENTS**: 14 specialized domain agents with enhanced capabilities
  - backend-architect.md, devops-architect.md, frontend-architect.md
  - learning-guide.md, performance-engineer.md, python-expert.md
  - quality-engineer.md, refactoring-expert.md, requirements-analyst.md
  - root-cause-analyst.md, security-engineer.md, socratic-mentor.md
- **NEW MODE**: MODE_Orchestration.md for intelligent tool selection mindset (5 total behavioral modes)
- **NEW COMMAND**: `#sk_implement` for feature and code implementation (addresses v2 user feedback)
- **NEW FILE**: CLAUDE.md for project-specific Claude Code instructions
- Migration logic to move existing commands to new namespace automatically
- Enhanced uninstaller to handle both old and new command locations
- Improved command conflict prevention
- Better command organization and discoverability
- Comprehensive PyPI publishing infrastructure
- API key management during SuperClaude MCP setup

### Removed
- **BREAKING**: Removed Templates/ directory (legacy templates no longer needed)
- **BREAKING**: Removed legacy agents and replaced with enhanced 14-agent system

### Improved
- Refactored Modes and MCP documentation for concise behavioral guidance
- Enhanced project cleanup and gitignore for PyPI publishing
- Implemented uninstall and update safety enhancements
- Better agent specialization and domain expertise focus

### Technical Details
- Commands now accessible as `#sk_analyze`, `#sk_build`, `#sk_improve`, etc.
- Migration preserves existing functionality while preventing naming conflicts
- Installation process detects and migrates existing commands automatically
- Tab completion support for `/sc:` prefix to discover all SuperClaude commands
- Guides/ directory replaces Docs/ for improved organization

## [4.0.6] - 2025-08-23

### Fixed
- Component validation now correctly checks .superclaude-metadata.json instead of settings.json (#291)
- Standardized version numbers across all components to 4.0.6
- Fixed agent validation to check for correct filenames (architect vs specialist/engineer)
- Fixed package.json version inconsistency (was 4.0.5)

### Changed  
- Bumped version from 4.0.4 to 4.0.6 across entire project
- All component versions now synchronized at 4.0.6
- Cleaned up metadata file structure for consistency

## [4.0.4] - 2025-08-22

### Added
- **Agent System**: 13 specialized domain experts replacing personas
- **Behavioral Modes**: 4 intelligent modes for different workflows (Brainstorming, Introspection, Task Management, Token Efficiency)
- **Session Lifecycle**: #sk_load and #sk_save for cross-session persistence with Serena MCP
- **New Commands**: #sk_brainstorm, #sk_reflect, #sk_save, #sk_select_tool (21 total commands)
- **Serena MCP**: Semantic code analysis and memory management
- **Morphllm MCP**: Intelligent file editing with Fast Apply capability
- **Core Components**: Python-based framework integration (completely redesigned and implemented)
- **Templates**: Comprehensive templates for creating new components
- **Python-Ultimate-Expert Agent**: Master Python architect for production-ready code

### Changed
- Commands expanded from 16 to 21 specialized commands
- Personas replaced with 13 specialized Agents
- Enhanced MCP integration (6 servers total)
- Improved token efficiency (30-50% reduction with Token Efficiency Mode)
- Session management now uses Serena integration for persistence
- Framework structure reorganized for better modularity

### Improved
- Task management with multi-layer orchestration (TodoWrite, /task, /spawn, /loop)
- Quality gates with 8-step validation cycle
- Performance monitoring and optimization
- Cross-session context preservation
- Intelligent routing with ORCHESTRATOR.md enhancements

## [3.0.0] - 2025-07-14

### Added
- Initial release of SuperClaude v3.0
- 15 specialized slash commands for development tasks
- Smart persona auto-activation system
- MCP server integration (Context7, Sequential, Magic, Playwright)
- Unified CLI installer with multiple installation profiles
- Comprehensive documentation and user guides
- Token optimization framework
- Task management system

### Features
- **Commands**: analyze, build, cleanup, design, document, estimate, explain, git, improve, index, load, spawn, task, test, troubleshoot
- **Personas**: architect, frontend, backend, analyzer, security, mentor, refactorer, performance, qa, devops, scribe
- **MCP Servers**: Official library documentation, complex analysis, UI components, browser automation
- **Installation**: Quick, minimal, and developer profiles with component selection
