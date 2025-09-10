---
inclusion: always
---

# SuperKiro Steering

Lightweight, always-included guides that you target by file path (and optional hashtag triggers).

This project organizes steering as:
- `.kiro/steering/super_kiro.md` (this overview)
- `.kiro/super_kiro/commands/*` (all command templates)

- Include all files in this folder in the system/context using the `inclusion: always` front matter.
- Primary usage: reference the steering file explicitly in your message.
  - Example: `Use .kiro/super_kiro/commands/sk_document.md src/api --type api --style detailed`
- Hashtag triggers: `#sk_<name>` or `#sk:<name>` at message start selects the corresponding steering file.
  - Example: `#sk_document src/api --type api --style detailed`
  - Mapping: `#sk_<name>` selects the corresponding command behavior
  - Tokenization: split on spaces; support quoted segments ("...") for paths with spaces.
  - Behavior: Treat the remainder of the message as arguments to the steering behavior.
  - Agents: use plain `#<agent_name>` (e.g., `#security_engineer`) to select persona files under `.kiro/steering/`.
- Flags announcement: If global flags are present (e.g., `--ultrathink`), announce them immediately after the consulted line, e.g., `Applied flags: --ultrathink`.

## CRITICAL EXECUTION PROTOCOL

**BEFORE outputting the header, you MUST:**
1. **FIRST** read the actual command file `.kiro/super_kiro/commands/sk_<name>.md`
2. **THEN** output the mandatory header
3. **THEN** follow the instructions in that command file

**DO NOT:**
- Output the header without reading the command file first
- Assume what the command file contains
- Skip reading the command file and proceed with generic behavior

**VERIFICATION STEPS:**
1. Parse the `#sk_<name>` command from user input
2. Use readFile tool to read `.kiro/super_kiro/commands/sk_<name>.md`
3. Output the mandatory header with correct command name
4. Follow the specific behavioral flow and patterns defined in that command file

## Strict Command Resolution & Execution Protocol

When a `#sk_<name>` command is invoked, follow this protocol exactly, before any reasoning or action:

1) Resolve path
- Construct: `.kiro/super_kiro/commands/sk_<name>.md` relative to the current project root.
- Do not search other locations (do not use global install dir). No fallbacks.

2) Load file
- If the file exists, read its entire contents first. Do not begin analysis or produce output before loading the file.
- If missing, stop and print: `Consulted: .kiro/super_kiro/commands/sk_<name>.md (NOT FOUND)` and a one‑line reason; suggest `SuperKiro kiro-init . --sync`.

3) Announce consultation
- Start the response with these exact lines:
  - `Consulted: .kiro/super_kiro/commands/sk_<name>.md`
  - `Applied flags: <flags>` (include only if flags are present)

4) Execute as specified
- Treat the loaded file as authoritative for behavior, tools, scope, and boundaries. Apply its sections (Usage, Behavioral Flow, Tool Coordination, Key Patterns, Examples) exactly.
- Parse `#sk_<name> ...args` into flags/params as documented by that file. Do not infer undocumented behaviors.
- Respect all “Will/Will Not” constraints from the file.

5) Safety & precedence
- Framework rules in this overview apply unless the command file explicitly overrides them.
- Never invent, relocate, or silently ignore the command path. If anything is ambiguous, ask a concise clarification question before proceeding.

## Command Files

Command files live under `.kiro/super_kiro/commands/` and are named `sk_<name>.md`.
  - Mapping: `<name>` → `sk_<name>.md`
- Examples: `sk_document.md`, `sk_analyze.md`, `sk_explain.md`, `sk_improve.md`, etc.

## Global Flags & Rules

Use these flags with any command file. Apply definitions exactly as documented; do not infer unspecified behavior.

Analysis Depth
- `--think`: Structured analysis (~4K tokens).
- `--think-hard`: Deep analysis (~10K tokens).
- `--ultrathink`: Maximum depth (~32K tokens).

MCP Control
- `--all-mcp`: Enable all MCP servers.
- `--no-mcp`: Disable all MCP servers (overrides others).
- Individual servers: `--seq` (Sequential), `--c7` (Context7), `--magic` (UI/Magic), `--play` (Playwright), `--morph` (Morphllm), `--serena` (Memory/Symbols).

Safety & Execution
- `--safe-mode`: Maximum validation; auto-enables `--uc` and `--validate`.
- `--validate`: Pre-execution checks and risk assessment.
- `--loop`: Iterative improvement cycles; combine with `--iterations N`.
- `--concurrency N`: Parallel operations (1–15).

Output Optimization
- `--uc` / `--ultracompressed`: 30–50% token reduction with symbol-enhanced communication.

Flag Handling Protocol
- Detect global flags in the message args (e.g., `--think`, `--c7`).
- Announce application: print `Applied flags: <flags>` right after the consulted line.
- Apply behaviors exactly as documented (SuperClaude/Core/FLAGS.md, Docs/User-Guide/flags.md). Do not infer extra effects beyond explicit policy.

Flag Priority Rules
- Safety first: `--safe-mode` > `--validate` > optimization flags.
- Explicit override: User-provided flags take precedence over auto-activation.
- Depth hierarchy: `--ultrathink` > `--think-hard` > `--think`.
- MCP control: `--no-mcp` overrides all individual MCP flags.

Flag Interactions
- Compatible: `--think` + `--c7`; `--magic` + `--play`; `--serena` + `--morph`; `--safe-mode` + `--validate`; `--loop` + `--validate`.
- Conflicts: `--all-mcp` vs individual MCP flags (prefer one); `--no-mcp` vs any MCP flags (no-mcp wins); `--safe` vs `--aggressive`; `--quiet` vs `--verbose`.
- Auto-relationships: Use only those explicitly documented by the framework or command. Do not auto-enable MCP servers from depth flags. If policy states `--safe-mode` implies `--uc` (and/or `--validate`), announce and apply accordingly.

## Command Index

Quick links to command templates (paths are relative to workspace root):

- analyze → `.kiro/super_kiro/commands/sk_analyze.md`
- brainstorm → `.kiro/super_kiro/commands/sk_brainstorm.md`
- build → `.kiro/super_kiro/commands/sk_build.md`
- business_panel → `.kiro/super_kiro/commands/sk_business_panel.md`
- cleanup → `.kiro/super_kiro/commands/sk_cleanup.md`
- design → `.kiro/super_kiro/commands/sk_design.md`
- document → `.kiro/super_kiro/commands/sk_document.md`
- estimate → `.kiro/super_kiro/commands/sk_estimate.md`
- explain → `.kiro/super_kiro/commands/sk_explain.md`
- git → `.kiro/super_kiro/commands/sk_git.md`
- implement → `.kiro/super_kiro/commands/sk_implement.md`
- improve → `.kiro/super_kiro/commands/sk_improve.md`
- index → `.kiro/super_kiro/commands/sk_index.md`
- load → `.kiro/super_kiro/commands/sk_load.md`
- reflect → `.kiro/super_kiro/commands/sk_reflect.md`
- save → `.kiro/super_kiro/commands/sk_save.md`
- select_tool → `.kiro/super_kiro/commands/sk_select_tool.md`
- spawn → `.kiro/super_kiro/commands/sk_spawn.md`
- task → `.kiro/super_kiro/commands/sk_task.md`
- test → `.kiro/super_kiro/commands/sk_test.md`
- troubleshoot → `.kiro/super_kiro/commands/sk_troubleshoot.md`
- workflow → `.kiro/super_kiro/commands/sk_workflow.md`

## Agents Index (Manual `#<agent>` Triggers)

These persona templates live directly under `.kiro/steering/` and are triggered manually via `#<agent>` in Kiro chat. Responses MUST begin with `Consulted: <path>` and optional `Applied flags:` line.

Strict Agent Resolution:
- For `#<agent>`, resolve and read `.kiro/steering/sk_<agent>.md` before any output.
- If missing, print `Consulted: .kiro/steering/sk_<agent>.md (NOT FOUND)` and suggest `SuperKiro kiro-init . --only-agents`.

- `#security_engineer` → `.kiro/steering/sk_security_engineer.md`
- `#backend_architect` → `.kiro/steering/sk_backend_architect.md`
- `#system_architect` → `.kiro/steering/sk_system_architect.md`
- `#frontend_architect` → `.kiro/steering/sk_frontend_architect.md`
- `#devops_architect` → `.kiro/steering/sk_devops_architect.md`
- `#quality_engineer` → `.kiro/steering/sk_quality_engineer.md`
- `#performance_engineer` → `.kiro/steering/sk_performance_engineer.md`
- `#python_expert` → `.kiro/steering/sk_python_expert.md`
- `#refactoring_expert` → `.kiro/steering/sk_refactoring_expert.md`
- `#requirements_analyst` → `.kiro/steering/sk_requirements_analyst.md`
- `#root_cause_analyst` → `.kiro/steering/sk_root_cause_analyst.md`
- `#technical_writer` → `.kiro/steering/sk_technical_writer.md`
- `#learning_guide` → `.kiro/steering/sk_learning_guide.md`
- `#socratic_mentor` → `.kiro/steering/sk_socratic_mentor.md`
