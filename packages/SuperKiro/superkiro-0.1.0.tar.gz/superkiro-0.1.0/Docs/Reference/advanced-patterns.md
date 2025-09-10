# SuperClaude Advanced Patterns

**Advanced Context Usage Patterns**: Sophisticated combinations of commands, agents, and flags for experienced SuperClaude users working on complex projects.

**Remember**: SuperClaude provides context to Claude Code. All patterns here are about guiding Claude's behavior through context, not executing code or coordinating processes.

## Table of Contents

### Context Combination Patterns
- [Multi-Agent Context Patterns](#multi-agent-context-patterns) - Combining multiple specialist contexts
- [Command Sequencing Patterns](#command-sequencing-patterns) - Effective command combinations
- [Flag Combination Strategies](#flag-combination-strategies) - Advanced flag usage

### Workflow Patterns
- [Complex Project Patterns](#complex-project-patterns) - Large project approaches
- [Migration Patterns](#migration-patterns) - Legacy system modernization
- [Review and Audit Patterns](#review-and-audit-patterns) - Comprehensive analysis

## Multi-Agent Context Patterns

### Combining Specialist Contexts

**Security + Backend Pattern:**
```bash
# Security-focused backend development
@agent-security "define authentication requirements"
@agent-backend-architect "design API with security requirements"
#sk_implement "secure API endpoints"

# What happens:
# 1. Security context loaded first
# 2. Backend context added
# 3. Implementation guided by both contexts
# Note: Contexts combine in Claude's understanding, not in execution
```

**Frontend + UX + Accessibility Pattern:**
```bash
# Comprehensive frontend development
@agent-frontend-architect "design component architecture"
#sk_implement "accessible React components" --magic
@agent-quality-engineer "review accessibility compliance"

# Context layering:
# - Frontend patterns guide structure
# - Magic MCP may provide UI components (if configured)
# - Quality context ensures standards
```

### Manual vs Automatic Agent Selection

**Explicit Control Pattern:**
```bash
# Manually control which contexts load
@agent-python-expert "implement data pipeline"
# Only Python context, no auto-activation

# vs Automatic selection
#sk_implement "Python data pipeline"
# May activate multiple agents based on keywords
```

**Override Auto-Selection:**
```bash
# Prevent unwanted agent activation
#sk_implement "simple utility" --no-mcp
@agent-backend-architect "keep it simple"
# Limits context to specified agent only
```

## Command Sequencing Patterns

### Progressive Refinement Pattern

```bash
# Start broad, then focus
#sk_analyze project/
# General analysis

#sk_analyze project/core/ --focus architecture
# Focused on structure

#sk_analyze project/core/auth/ --focus security --think-hard
# Deep security analysis

# Each command builds on previous context within the conversation
```

### Discovery to Implementation Pattern

```bash
# Complete feature development flow
#sk_brainstorm "feature idea"
# Explores requirements

#sk_design "feature architecture"
# Creates structure

@agent-backend-architect "review design"
# Expert review

#sk_implement "feature based on design"
# Implementation follows design

#sk_test --validate
# Verification approach
```

### Iterative Improvement Pattern

```bash
# Multiple improvement passes
#sk_analyze code/ --focus quality
# Identify issues

#sk_improve code/ --fix
# First improvement pass

@agent-refactoring-expert "suggest further improvements"
# Expert suggestions

#sk_improve code/ --fix --focus maintainability
# Refined improvements
```

## Flag Combination Strategies

### Analysis Depth Control

```bash
# Quick overview
#sk_analyze . --overview --uc
# Fast, compressed output

# Standard analysis
#sk_analyze . --think
# Structured thinking

# Deep analysis
#sk_analyze . --think-hard --verbose
# Comprehensive analysis

# Maximum depth (use sparingly)
#sk_analyze . --ultrathink
# Exhaustive analysis
```

### MCP Server Selection

```bash
# Selective MCP usage
#sk_implement "React component" --magic --c7
# Only Magic and Context7 MCP

# Disable all MCP
#sk_implement "simple function" --no-mcp
# Pure Claude context only

# All available MCP
#sk_analyze complex-system/ --all-mcp
# Maximum tool availability (if configured)
```

## Complex Project Patterns

### Large Codebase Analysis

```bash
# Systematic exploration of large projects
# Step 1: Structure understanding
#sk_load project/
#sk_analyze . --overview --focus architecture

# Step 2: Identify problem areas
@agent-quality-engineer "identify high-risk modules"

# Step 3: Deep dive into specific areas
#sk_analyze high-risk-module/ --think-hard --focus quality

# Step 4: Implementation plan
#sk_workflow "improvement plan based on analysis"
```

### Multi-Module Development

```bash
# Developing interconnected modules
# Frontend module
#sk_implement "user interface module"
@agent-frontend-architect "ensure consistency"

# Backend module
#sk_implement "API module"
@agent-backend-architect "ensure compatibility"

# Integration layer
#sk_implement "frontend-backend integration"
# Context from both previous implementations guides this
```

### Cross-Technology Projects

```bash
# Projects with multiple technologies
# Python backend
@agent-python-expert "implement FastAPI backend"

# React frontend
@agent-frontend-architect "implement React frontend"

# DevOps setup
@agent-devops-architect "create deployment configuration"

# Integration documentation
#sk_document --type integration
```

## Migration Patterns

### Legacy System Analysis

```bash
# Understanding legacy systems
#sk_load legacy-system/
#sk_analyze . --focus architecture --verbose

@agent-refactoring-expert "identify modernization opportunities"
@agent-system-architect "propose migration strategy"

#sk_workflow "create migration plan"
```

### Incremental Migration

```bash
# Step-by-step migration approach
# Phase 1: Analysis
#sk_analyze legacy-module/ --comprehensive

# Phase 2: Design new architecture
@agent-system-architect "design modern replacement"

# Phase 3: Implementation
#sk_implement "modern module with compatibility layer"

# Phase 4: Validation
#sk_test --focus compatibility
```

## Review and Audit Patterns

### Security Audit Pattern

```bash
# Comprehensive security review
#sk_analyze . --focus security --think-hard
@agent-security "review authentication and authorization"
@agent-security "check for OWASP vulnerabilities"
#sk_document --type security-audit
```

### Code Quality Review

```bash
# Multi-aspect quality review
#sk_analyze src/ --focus quality
@agent-quality-engineer "review test coverage"
@agent-refactoring-expert "identify code smells"
#sk_improve --fix --preview
```

### Architecture Review

```bash
# System architecture assessment
@agent-system-architect "review current architecture"
#sk_analyze . --focus architecture --think-hard
@agent-performance-engineer "identify bottlenecks"
#sk_design "optimization recommendations"
```

## Important Clarifications

### What These Patterns Actually Do

- ✅ **Guide Claude's Thinking**: Provide structured approaches
- ✅ **Combine Contexts**: Layer multiple expertise areas
- ✅ **Improve Output Quality**: Better code generation through better context
- ✅ **Structure Workflows**: Organize complex tasks

### What These Patterns Don't Do

- ❌ **Execute in Parallel**: Everything is sequential context loading
- ❌ **Coordinate Processes**: No actual process coordination
- ❌ **Optimize Performance**: No code runs, so no performance impact
- ❌ **Persist Between Sessions**: Each conversation is independent

## Best Practices for Advanced Usage

### Context Management

1. **Layer Deliberately**: Add contexts in logical order
2. **Avoid Overload**: Too many agents can dilute focus
3. **Use Manual Control**: Override auto-activation when needed
4. **Maintain Conversation Flow**: Keep related work in same conversation

### Command Efficiency

1. **Progress Logically**: Broad → Specific → Implementation
2. **Reuse Context**: Later commands benefit from earlier context
3. **Document Decisions**: Use `#sk_save` for important summaries
4. **Scope Appropriately**: Focus on manageable chunks

### Flag Usage

1. **Match Task Complexity**: Simple tasks don't need `--ultrathink`
2. **Control Output**: Use `--uc` for concise results
3. **Manage MCP**: Only activate needed servers
4. **Avoid Conflicts**: Don't use contradictory flags

## Summary

Advanced SuperClaude patterns are about sophisticated context management and command sequencing. They help Claude Code generate better outputs by providing richer, more structured context. Remember: all "coordination" and "optimization" happens in how Claude interprets the context, not in any actual execution or parallel processing.
