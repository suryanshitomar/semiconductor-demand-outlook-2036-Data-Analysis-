import copy
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from analysis import load_inputs, tables_from, validate, index_at

class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.raw,self.a=load_inputs()

    def test_baseline_index(self):
        self.assertEqual(index_at(self.a[0],2026),100)

    def test_compounding_boundary(self):
        a={**self.a[0],'early_growth':.1,'late_growth':.02}
        self.assertAlmostEqual(index_at(a,2030),100*1.1**4)
        self.assertAlmostEqual(index_at(a,2036),100*1.1**4*1.02**6)

    def test_horizon_rejected(self):
        with self.assertRaises(ValueError):index_at(self.a[0],2025)

    def test_missing_source_rejected(self):
        self.raw['revenues'][0]['source_id']='missing'
        with self.assertRaisesRegex(ValueError,'source'):validate(self.raw,self.a)

    def test_duplicate_selected_vintage_rejected(self):
        self.raw['market'][2]['selected']=True
        with self.assertRaisesRegex(ValueError,'Duplicate'):validate(self.raw,self.a)

    def test_scenario_grid_complete(self):
        with self.assertRaisesRegex(ValueError,'Incomplete'):validate(self.raw,self.a[:-1])

    def test_currency_change_rejected(self):
        self.raw['revenues'][1]['currency']='EUR'
        with self.assertRaisesRegex(ValueError,'Currency'):tables_from(self.raw,self.a)

    def test_no_siemens_group_revenue(self):
        self.assertFalse(any(r['company_id']=='SIE' for r in self.raw['revenues']))

    def test_missing_growth_remains_missing(self):
        tables=tables_from(self.raw,self.a)
        first=min([r for r in tables['company_revenue'] if r['company_id']=='NVDA'],key=lambda r:r['fiscal_year'])
        self.assertIsNone(first['yoy_growth'])

    def test_nonfinite_growth_rejected(self):
        self.a[0]['early_growth']=float('nan')
        with self.assertRaisesRegex(ValueError,'growth'):validate(self.raw,self.a)

    def test_scenario_counts_and_ordering(self):
        rows=tables_from(self.raw,self.a)['scenarios']
        self.assertEqual(len(rows),7*3*11)
        for theme in {r['theme_id'] for r in rows}:
            end={r['scenario']:r['index_value'] for r in rows if r['theme_id']==theme and r['year']==2036}
            self.assertLess(end['Conservative'],end['Base']);self.assertLess(end['Base'],end['Accelerated'])

    def test_powerbi_fields_resolve(self):
        model=json.loads((ROOT/'powerbi/Outlook.SemanticModel/model.bim').read_text())
        lookup={t['name']:{'Column':{c['name'] for c in t['columns']},'Measure':{m['name'] for m in t.get('measures',[])}} for t in model['model']['tables']}
        for file in (ROOT/'powerbi/Outlook.Report').rglob('visual.json'):
            value=json.loads(file.read_text())
            for state in value['visual']['query']['queryState'].values():
                for p in state['projections']:
                    kind,field=next(iter(p['field'].items()))
                    self.assertIn(field['Property'],lookup[field['Expression']['SourceRef']['Entity']][kind])

if __name__=='__main__':unittest.main()
