"""Read-only routing demonstration over a local fixture, not an authentication service.

grant entries are trusted TEST INPUTS. CLI principal selection does not authenticate anyone.
Production must obtain the principal and grants from the host before loading authorized data.
"""
import argparse,json
from pathlib import Path

MODES={'consulting','training','service','agent'}
def query(index,grants,principal,pattern=None,org=None,mode='agent',term=None):
 if mode not in MODES:raise ValueError('Unsupported mode')
 allowed=set(grants.get(principal,[]))
 # Filter before matching, counting, or generating explanations.
 scoped=[r for r in index['records'] if r['org_id']+'/'+r['project_id'] in allowed]
 if org:scoped=[r for r in scoped if r['org_id']==org]
 rows=[]
 for r in scoped:
  if mode not in r['modes']:continue
  if pattern and pattern not in r['patterns']:continue
  if term and term.casefold() not in (r['text']+' '+r['department']+' '+' '.join(r.get('aliases',[]))+' '+json.dumps(r.get('constraints',[]),ensure_ascii=False)).casefold():continue
  rows.append({k:r[k] for k in ['id','org_id','org_label','project_id','department','revision','path','source_id','source_cell','text','constraints','status']})
 return {'revision':index['revision'],'mode':mode,'count':len(rows),'items':rows,'note':'Test-scope routing only; no identity or storage ACL verification'}

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('workspace',type=Path);p.add_argument('--principal',required=True)
 p.add_argument('--pattern');p.add_argument('--org');p.add_argument('--mode',default='agent',choices=sorted(MODES));p.add_argument('--term')
 a=p.parse_args();index=json.loads((a.workspace/'router-index.json').read_text());grants=json.loads((a.workspace/'test-grants.json').read_text())['grants']
 print(json.dumps(query(index,grants,a.principal,a.pattern,a.org,a.mode,a.term),ensure_ascii=False,indent=2))
