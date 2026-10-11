import os
from pathlib import Path

base = Path(__file__).resolve().parent
files = [
    "ADIK.md",
    "ADIK.orchestrator.md",
    "Registry.md",
    "Registry.index.md",
    "agents/builder.agent.md",
    "agents/codebase-analyst.agent.md",
    "skills/sdk-builder/SKILL.md",
    "skills/sdk-builder-tier2/SKILL.md",
    "skills/sdk-consumer/SKILL.md",
    "skills/registry-validator/SKILL.md",
    "skills/vectorize/SKILL.md",
    "scripts/adik-embed.py",
    "scripts/adik-eject.py",
    "mcp/adik-mcp-server.md",
]

total_bytes = 0
total_chars = 0
print(f"{'File':<45} {'Bytes':>8} {'Chars':>8} {'~Tokens':>8} {'Lines':>6}")
print("-" * 80)
for f in files:
    path = os.path.join(base, f)
    if os.path.exists(path):
        size = os.path.getsize(path)
        with open(path, 'r', encoding='utf-8', errors='replace') as fh:
            content = fh.read()
        chars = len(content)
        lines = content.count('\n') + 1
        # ~4 chars per token for English/code markdown
        tokens = chars // 4
        total_bytes += size
        total_chars += chars
        print(f"{f:<45} {size:>8,} {chars:>8,} {tokens:>8,} {lines:>6,}")
    else:
        print(f"{f:<45} NOT FOUND")

print("-" * 80)
print(f"{'TOTAL':<45} {total_bytes:>8,} {total_chars:>8,} {total_chars//4:>8,} ")
print()
print(f"Total bundle size: {total_bytes:,} bytes ({total_bytes/1024:.1f} KB)")
print(f"Estimated tokens:  {total_chars//4:,} tokens")
print()

# Group by category
categories = {
    "Standard + Orchestrator": ["ADIK.md", "ADIK.orchestrator.md"],
    "Agents": ["agents/builder.agent.md", "agents/codebase-analyst.agent.md"],
    "Skills": ["skills/sdk-builder/SKILL.md", "skills/sdk-builder-tier2/SKILL.md", "skills/sdk-consumer/SKILL.md", "skills/registry-validator/SKILL.md", "skills/vectorize/SKILL.md"],
    "Scripts (Python)": ["scripts/adik-embed.py", "scripts/adik-eject.py"],
    "Registry templates": ["Registry.md", "Registry.index.md"],
    "MCP": ["mcp/adik-mcp-server.md"],
}

print("BY CATEGORY:")
print(f"{'Category':<30} {'Bytes':>8} {'~Tokens':>8} {'% of total':>10}")
print("-" * 60)
for cat, cat_files in categories.items():
    cat_bytes = 0
    cat_chars = 0
    for f in cat_files:
        path = os.path.join(base, f)
        if os.path.exists(path):
            cat_bytes += os.path.getsize(path)
            with open(path, 'r', encoding='utf-8', errors='replace') as fh:
                cat_chars += len(fh.read())
    pct = (cat_bytes / total_bytes * 100) if total_bytes > 0 else 0
    print(f"{cat:<30} {cat_bytes:>8,} {cat_chars//4:>8,} {pct:>9.1f}%")
