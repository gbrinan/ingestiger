"""Read-only checks for the proposal's active documentation and plugin layout."""
from pathlib import Path
import json,re,sys

root=Path(__file__).resolve().parents[1]
errors=[]
plugin=json.loads((root/'.claude-plugin/plugin.json').read_text())
meta=json.loads((root/'agent/meta.json').read_text())
if plugin['version'] != meta['version']:errors.append('Version drift')
declared={(root/p).resolve() for p in plugin['skills']}
actual={p.parent.resolve() for p in (root/'skills').rglob('SKILL.md')}
if declared != actual:errors.append('Shipped skills differ from manifest')
for p in declared:
 if not (p/'SKILL.md').is_file():errors.append(f'Missing skill: {p}')
 if 'archive' in p.relative_to(root).parts:errors.append('Archive exposed as skill')
for p in root.rglob('*.md'):
 if any(x in p.relative_to(root).parts for x in ('.git','archive')):continue
 text=p.read_text()
 for link in re.findall(r'\]\(([^)]+)\)',text):
  if '://' in link or link.startswith('#'):continue
  target=link.split('#')[0]
  if not (p.parent/target).exists():errors.append(f'{p.relative_to(root)}: broken link {link}')
for name in ['agent/role-directive.md','skills/ingestiger/SKILL.md','agent/meta.json']:
 if re.search(r'(?<![A-Za-z0-9_])(?:RAG|BM25|top-k)(?![A-Za-z0-9_])', (root/name).read_text(),re.I):errors.append(f'Legacy runtime in {name}')
skill=(root/'skills/ingestiger/SKILL.md').read_text()
for section in ['## Goal','## Workflow','## Rules','## Verification']:
 if section not in skill:errors.append(f'Missing {section}')
market=json.loads((root/'.claude-plugin/marketplace.json').read_text())
if market['plugins'][0]['name'] != plugin['name']:errors.append('Marketplace name mismatch')
print(json.dumps({'passed':not errors,'errors':errors,'skills':len(actual),'scope':'Static layout only; not host install or ingestion validation'},ensure_ascii=False,indent=2))
sys.exit(bool(errors))
