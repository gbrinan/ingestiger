import importlib.util
import json
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('pipeline_budget', Path(__file__).resolve().parents[1] / 'skills/ingestiger/scripts/pipeline.py')
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)


class RequestBudgetTests(unittest.TestCase):
    def source(self, units, **extra):
        return dict(source_id='synthetic', source_revision='one', org_id='org', project_id='project', units=units, **extra)

    def test_cell_metadata_and_unicode_count_towards_complete_request(self):
        units = [dict(unit_id=str(i), locator=str(i), text='허용 조건', cells=['가' * 800]) for i in range(3)]
        result = p.prepare(self.source(units), 'synthetic', 12000, 5000)
        self.assertEqual(len(result['requests']), 3)
        for req, size in zip(result['requests'], result['request_bytes']):
            self.assertEqual(size, len(json.dumps(req, ensure_ascii=False, separators=(',', ':')).encode()))
            self.assertLessEqual(size, 5000)

    def test_oversized_section_is_deferred_whole_not_silently_cut(self):
        units = [dict(unit_id='long', locator='section', text='a' * 101), dict(unit_id='small', locator='other', text='조건')]
        result = p.prepare(self.source(units), 'synthetic', 100, defer_oversized=True)
        self.assertEqual(result['pending_units'], [dict(unit_id='long', reason='source_unit_exceeds_character_budget')])
        self.assertEqual([u['unit_id'] for r in result['requests'] for u in r['units']], ['small'])
        self.assertEqual(units[0]['text'], 'a' * 101)

    def test_all_deferred_and_metadata_overflow_are_explicit(self):
        unit = dict(unit_id='one', locator='s', text='가' * 2000)
        result = p.prepare(self.source([unit]), 'synthetic', 5000, 4000, True)
        self.assertEqual(result['requests'], [])
        self.assertEqual(result['pending_units'][0]['reason'], 'source_unit_exceeds_request_byte_budget')
        with self.assertRaises(ValueError):
            p.prepare(self.source([unit], structure={'heading': 'x' * 5000}), 'synthetic', 5000, 4000, True)

    def test_default_still_rejects_oversized_unit(self):
        with self.assertRaises(ValueError):
            p.prepare(self.source([dict(unit_id='x', locator='x', text='1234')]), 'synthetic', 3)
