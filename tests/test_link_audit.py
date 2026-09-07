import importlib.util
from pathlib import Path
import unittest

BASE=Path(__file__).resolve().parents[1]/'skills/ingestiger/scripts'
s=importlib.util.spec_from_file_location('link_audit',BASE/'link_audit.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

class AuditTests(unittest.TestCase):
    def run_audit(self,cells):
        return m.audit({'spreadsheet_id':'fixture','sheets':[{'title':'lesson','cells':cells}]})
    def test_url_not_local_and_link_only_not_evidence(self):
        a=self.run_audit([{'cell':'D3','value':{'stringValue':'https://chatgpt.com/c/123'}}])
        self.assertEqual(a['exceptions'],[]);self.assertEqual(a['units'],[])
        self.assertEqual(a['links'][0]['kind'],'private_conversation')
        self.assertEqual(a['links'][0]['admission'],'pending')
    def test_text_retained_and_local_path_held(self):
        a=self.run_audit([{'cell':'E3','value':{'stringValue':r'교육 요구 C:\Users\test\a.md https://example.org'}}])
        self.assertIn('교육 요구',a['units'][0]['text'])
        self.assertNotIn('C:',a['units'][0]['text'])
        self.assertEqual(a['exceptions'][0]['reason'],'local_attachment_required')
    def test_rich_link_and_formula_are_not_executed(self):
        a=self.run_audit([{'cell':'F3','value':{'formulaValue':'=HYPERLINK("https://example.org","data")'}},
                          {'cell':'G3','value':{'stringValue':'자료'},'links':['https://example.org']}])
        self.assertEqual(a['summary']['unique_urls'],1)
        self.assertEqual(len(a['units']),1)
        self.assertEqual(a['exceptions'][0]['reason'],'formula_requires_review')
    def test_display_mismatch_and_error(self):
        a=self.run_audit([{'cell':'F3','value':{'stringValue':'https://example.org/a'},'links':['https://example.org/b']},
                          {'cell':'G3','value':{},'error':{'type':'REF'}}])
        self.assertEqual({e['reason'] for e in a['exceptions']},{'display_target_mismatch','formula_error'})
    def test_query_and_fragment_preserved(self):
        self.assertEqual(m.normalize('https://EXAMPLE.org/a?q=1#b'),'https://example.org/a?q=1#b')

if __name__=='__main__':unittest.main()
