# Google Antigravity Adapter

**Status:** Native & Active in this repository  
**Discovery Path:** `.agents/skills/<skill-name>/SKILL.md`  
**Loading Priority:** Workspace Project (`.agents/skills/`) > Declared > Global (`~/.gemini/config/`) > Built-in  

### How It Works
Google Antigravity automatically discovers skills placed in `.agents/skills/`. It uses **progressive disclosure**:
- Only the YAML frontmatter `name:` and `description:` are injected into the agent system prompt.
- The full body of `SKILL.md` is loaded dynamically on demand when the skill is activated.

### Invocation
- Slash commands: e.g. `/plan`, `/goal`, `/grill-me`, `/teamwork`, `/compact`.
- Chat prompt: e.g. `/project-discovery` or "Run project discovery on this codebase".
