import importlib.util,tempfile,unittest,zipfile
from pathlib import Path
spec=importlib.util.spec_from_file_location('deck_inventory',Path(__file__).resolve().parents[1]/'skills/ingestiger/scripts/deck_inventory.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class DeckTests(unittest.TestCase):
    def test_pptx_document_order_not_filename_order(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'test.pptx'
            with zipfile.ZipFile(p,'w') as z:
                z.writestr('ppt/presentation.xml','<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><p:sldIdLst><p:sldId id="300" r:id="r2"/><p:sldId id="301" r:id="r1"/></p:sldIdLst></p:presentation>')
                z.writestr('ppt/_rels/presentation.xml.rels','<Relationships><Relationship Id="r1" Target="slides/slide1.xml"/><Relationship Id="r2" Target="slides/slide2.xml"/></Relationships>')
                z.writestr('ppt/slides/slide1.xml','<slide/>');z.writestr('ppt/slides/slide2.xml','<slide/>')
            result=m.inventory(p)
            self.assertEqual([s['part'] for s in result['slides']],['ppt/slides/slide2.xml','ppt/slides/slide1.xml'])
            self.assertFalse(result['content_read'])
    def test_key_archive_count_is_not_slide_count(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'test.key'
            with zipfile.ZipFile(p,'w') as z:
                for n in ['Index/Document.iwa','Index/Slide.iwa','Index/Slide-123-2.iwa','Index/TemplateSlide.iwa']:z.writestr(n,b'placeholder')
            r=m.inventory(p);self.assertIsNone(r['slide_count']);self.assertEqual(r['slide_archive_candidates'],2);self.assertEqual(r['template_archive_candidates'],1)
if __name__=='__main__':unittest.main()
