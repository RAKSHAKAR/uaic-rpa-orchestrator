"""
Skill Markdown Renderer
Renders structured skill dictionary specifications into standardized,
fully actionable, production-grade SKILL.md documents adhering to the
Universal AI Development Workflow & Skills Framework.
"""

from typing import Any, Dict


def render_skill_markdown(skill: Dict[str, Any]) -> str:
    name = skill["name"]
    title = name.replace("-", " ").title()
    desc = skill["description"].strip()
    purpose = skill["purpose"].strip()
    
    when_to_use = "\n".join(f"- {item}" for item in skill["when_to_use"])
    when_not_to_use = "\n".join(f"- {item}" for item in skill["when_not_to_use"])
    
    if isinstance(skill["required_inputs"], dict):
        inputs = "\n".join(f"- **{k}**: {v}" for k, v in skill["required_inputs"].items())
    elif isinstance(skill["required_inputs"], list):
        inputs = "\n".join(f"- {v}" for v in skill["required_inputs"])
    else:
        inputs = f"- {skill['required_inputs']}"
        
    prereqs = "\n".join(f"- {item}" for item in skill["prerequisites"])
    
    steps_md = []
    for idx, step in enumerate(skill["procedure"], start=1):
        if isinstance(step, tuple):
            step_title, step_desc = step
            steps_md.append(f"### Step {idx}: {step_title}\n{step_desc}\n")
        else:
            steps_md.append(f"### Step {idx}\n{step}\n")
    procedure_str = "\n".join(steps_md)
    
    safety = "\n".join(f"- {item}" for item in skill["safety"])
    deliverables = "\n".join(f"- {item}" for item in skill["deliverables"])
    acceptance = "\n".join(f"- [ ] {item}" for item in skill["acceptance_criteria"])
    recovery = "\n".join(f"- {item}" for item in skill["error_recovery"])
    
    tool_map = skill.get("tool_invocations", {})
    tools_table = (
        "| AI Tool | Invocation Mechanism | Classification |\n"
        "|---|---|---|\n"
        f"| **Google Antigravity** | {tool_map.get('antigravity', 'Discovered in `.agents/skills/` or invoke via chat prompt')} | `{tool_map.get('antigravity_class', 'CUSTOM SKILL')}` |\n"
        f"| **Cursor** | {tool_map.get('cursor', 'Select rule in `.cursor/rules/` or reference `@' + name + '`')} | `{tool_map.get('cursor_class', 'CUSTOM RULE / SKILL')}` |\n"
        f"| **Claude Code** | {tool_map.get('claude_code', 'Include task in prompt referencing `CLAUDE.md` and skill path')} | `{tool_map.get('claude_class', 'PROJECT INSTRUCTION')}` |\n"
        f"| **OpenAI Codex** | {tool_map.get('codex', 'Discovered via `AGENTS.md` in repository context')} | `{tool_map.get('codex_class', 'CUSTOM SKILL')}` |\n"
        f"| **Gemini CLI** | {tool_map.get('gemini', 'Referenced via `GEMINI.md` repository guidelines')} | `{tool_map.get('gemini_class', 'CUSTOM SKILL')}` |\n"
        f"| **GitHub Copilot** | {tool_map.get('github_copilot', 'Prompt via Copilot Chat or `.github/prompts/' + name + '.prompt.md`')} | `{tool_map.get('copilot_class', 'PROMPT FILE')}` |\n"
        f"| **Windsurf** | {tool_map.get('windsurf', 'Configured via `.windsurfrules` or `.windsurf/workflows/' + name + '.md`')} | `{tool_map.get('windsurf_class', 'WORKFLOW RULE')}` |\n"
    )
    
    refs = "\n".join(f"- {r}" for r in skill.get("references", ["Repository documentation in `README.md` and `docs/`"]))

    return f"""---
name: {name}
description: >-
  {desc}
---

# {title}

## 1. Purpose & Overview
{purpose}

---

## 2. When to Use & When NOT to Use

### When to Use
{when_to_use}

### When NOT to Use
{when_not_to_use}

---

## 3. Required Inputs & Prerequisites

### Required Inputs
{inputs}

### Prerequisites
{prereqs}

---

## 4. Step-by-Step Execution Procedure

{procedure_str}

---

## 5. Safety Considerations & Guardrails
{safety}

---

## 6. Expected Deliverables & Artifacts
{deliverables}

---

## 7. Acceptance Criteria & Definition of Done
{acceptance}

---

## 8. Error Recovery & Troubleshooting
{recovery}

---

## 9. Tool Invocation & Reference Mapping

{tools_table}

### Authoritative References
{refs}
"""
