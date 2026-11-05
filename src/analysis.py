"""Rebuild the analysis, Power BI inputs, charts and SQL database from pinned facts."""
from __future__ import annotations
import csv
import json
import math
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_inputs(root=ROOT):
    return (json.loads((root / 'data/raw/research_snapshot.json').read_text(encoding='utf-8')),
            json.loads((root / 'config/scenarios.json').read_text(encoding='utf-8')))

def unique(rows, fields):
    keys = [tuple(row[k] for k in fields) for row in rows]
    if len(set(keys)) != len(keys):
        raise ValueError('Duplicate key: ' + ', '.join(fields))

def validate(raw, assumptions):
    unique(raw['sources'], ['source_id'])
    unique(raw['revenues'], ['company_id', 'fiscal_year'])
    unique(assumptions, ['theme_id', 'scenario'])
    source_ids = {s['source_id'] for s in raw['sources']}
    companies = {c['company_id'] for c in raw['companies']}
    themes = {t['theme_id'] for t in raw['themes']}
    for collection in ['revenues', 'market', 'published', 'map', 'companies']:
        for row in raw[collection]:
            if row['source_id'] not in source_ids:
                raise ValueError('Unknown source')
    for row in raw['revenues']:
        if row['company_id'] not in companies or row['revenue_millions'] <= 0:
            raise ValueError('Invalid company revenue')
    selected = [r for r in raw['market'] if r['selected']]
    unique(selected, ['year'])
    for a in assumptions:
        if a['theme_id'] not in themes or a['basis'] != 'analyst_assumption':
            raise ValueError('Invalid assumption provenance')
        if not a['base_year'] < a['early_end'] < a['end_year']:
            raise ValueError('Invalid scenario horizon')
        if any(not math.isfinite(a[k]) or a[k] <= -1 for k in ['early_growth', 'late_growth']):
            raise ValueError('Invalid growth rate')
    expected = {(t, s) for t in themes for s in ['Conservative', 'Base', 'Accelerated']}
    if {(a['theme_id'], a['scenario']) for a in assumptions} != expected:
        raise ValueError('Incomplete scenario grid')

def index_at(a, year):
    """2026=100; 2027-30 use early growth; 2031-36 use late growth."""
    if not a['base_year'] <= year <= a['end_year']:
        raise ValueError('Year outside scenario horizon')
    early = min(year, a['early_end']) - a['base_year']
    late = max(0, year - a['early_end'])
    return 100 * (1 + a['early_growth']) ** early * (1 + a['late_growth']) ** late

def tables_from(raw, assumptions):
    validate(raw, assumptions)
    company = {c['company_id']: c for c in raw['companies']}
    theme = {t['theme_id']: t for t in raw['themes']}
    revenues = []
    for cid in sorted(company):
        group = sorted([r for r in raw['revenues'] if r['company_id'] == cid], key=lambda r:r['fiscal_year'])
        for i, r in enumerate(group):
            prev = group[i-1] if i else None
            if prev and r['currency'] != prev['currency']:
                raise ValueError('Currency changes require explicit conversion policy')
            revenues.append({**r, 'company': company[cid]['company'],
                'yoy_growth': r['revenue_millions']/prev['revenue_millions']-1 if prev else None,
                'within_company_index': r['revenue_millions']/group[0]['revenue_millions']*100,
                'index_base_fiscal_year': group[0]['fiscal_year']})
    scenarios = []
    for a in assumptions:
        for year in range(a['base_year'], a['end_year']+1):
            scenarios.append({'theme_id': a['theme_id'], 'theme':theme[a['theme_id']]['theme'],
                'scenario': a['scenario'], 'year': year, 'index_value': index_at(a, year),
                'basis': a['basis'], 'base_year': a['base_year'],
                'early_growth': a['early_growth'], 'late_growth':a['late_growth']})
    mapping = [{**r, 'company':company[r['company_id']]['company'],
        'theme':theme[r['theme_id']]['theme'], 'documented_link':1} for r in raw['map']]
    market = []
    selected = sorted([r for r in raw['market'] if r['selected']], key=lambda r:r['year'])
    for row in raw['market']:
        prev = next((r for r in selected if r['year']==row['year']-1), None)
        market.append({**row, 'yoy_growth':row['value_usd_billions']/prev['value_usd_billions']-1
                       if prev and row['selected'] else None})
    return {'sources':raw['sources'], 'company_revenue':revenues, 'market':market,
        'published_outlook':raw['published'], 'themes':raw['themes'], 'company_theme':mapping,
        'assumptions':assumptions, 'scenarios':scenarios}

def export_tables(tables, root=ROOT):
    dest=root/'data/processed'; dest.mkdir(parents=True, exist_ok=True)
    for name, rows in tables.items():
        with (dest/(name+'.csv')).open('w', newline='', encoding='utf-8') as f:
            writer=csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader(); writer.writerows(rows)
    dbpath=root/'outputs/analysis.sqlite'; dbpath.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(dbpath) as db:
        for name, rows in tables.items():
            db.execute('DROP TABLE IF EXISTS "'+name+'"')
            fields=list(rows[0])
            def dtype(k):
                v=next((r[k] for r in rows if r[k] is not None), '')
                return 'INTEGER' if isinstance(v,(int,bool)) else 'REAL' if isinstance(v,float) else 'TEXT'
            db.execute('CREATE TABLE "'+name+'" ('+', '.join('"'+k+'" '+dtype(k) for k in fields)+')')
            db.executemany('INSERT INTO "'+name+'" VALUES ('+','.join('?' for _ in fields)+')',
                           [tuple(r[k] for k in fields) for r in rows])

def make_charts(tables, root=ROOT):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':11, 'axes.spines.top':False,
        'axes.spines.right':False,'axes.titleweight':'bold','figure.facecolor':'#f6f8fb',
        'axes.facecolor':'#f6f8fb','axes.labelcolor':'#24364b','text.color':'#142b43'})
    dest=root/'outputs/charts'; dest.mkdir(parents=True,exist_ok=True)
    def save(fig,name,note):
        fig.text(.08,.025,note, fontsize=9,color='#46586b')
        fig.tight_layout(rect=(0,.08,1,1)); fig.savefig(dest/(name+'.png'),dpi=160); plt.close(fig)
    market=sorted([r for r in tables['market'] if r['selected']],key=lambda r:r['year'])
    fig,ax=plt.subplots(figsize=(10,5.5))
    ax.plot([r['year'] for r in market],[r['value_usd_billions'] for r in market],color='#007e87',marker='o',lw=3)
    for r in market: ax.annotate(f"{r['value_usd_billions']:,.1f}",(r['year'],r['value_usd_billions']),xytext=(0,12),textcoords='offset points',ha='center')
    ax.set(title='Semiconductor sales recovered after the 2023 decline',ylabel='Global sales · USD billions',xticks=[r['year'] for r in market],ylim=(450,870))
    ax.grid(axis='y',alpha=.18)
    save(fig,'market-history','Sources S01, S03, S04 · Mixed release vintages; selected 2024 value is the revised 630.5.')
    latest=[]
    for cid in sorted({r['company_id'] for r in tables['company_revenue']}):
        latest.append(max([r for r in tables['company_revenue'] if r['company_id']==cid],key=lambda r:r['fiscal_year']))
    latest.sort(key=lambda r:r['yoy_growth'])
    fig,ax=plt.subplots(figsize=(10,6))
    labels=[r['company']+' · FY'+str(r['fiscal_year']) for r in latest]
    values=[r['yoy_growth']*100 for r in latest]
    ax.barh(labels,values,color=['#b94d4d' if v<0 else '#007e87' for v in values])
    for i,v in enumerate(values):ax.text(v+(.8 if v>=0 else -.8),i,f'{v:+.1f}%',va='center',ha='left' if v>=0 else 'right')
    ax.set(title='Latest included fiscal-year growth varies sharply',xlabel='Revenue change versus previous fiscal year (%)',xlim=(-15,80))
    ax.axvline(0,color='#a7b2bf',lw=1)
    save(fig,'company-growth','Sources S06–S10, S13–S14 · Different fiscal ends and currencies; no absolute revenue ranking.')
    fig,ax=plt.subplots(figsize=(10,6))
    for a in tables['assumptions']:
        if a['scenario']=='Base':
            rows=[r for r in tables['scenarios'] if r['theme_id']==a['theme_id'] and r['scenario']=='Base']
            ax.plot([r['year'] for r in rows],[r['index_value'] for r in rows],lw=2,label=rows[0]['theme'])
    ax.set(title='Illustrative base scenario · assumptions drive the ordering',ylabel='Scenario index · 2026 = 100',xlabel='Year',xticks=[2026,2028,2030,2032,2034,2036])
    ax.legend(loc='upper left',fontsize=9);ax.grid(alpha=.15)
    save(fig,'scenario-paths','Analyst assumptions only · Not market sizes, chip volumes, company forecasts or probabilities.')
    cos=list(dict.fromkeys(r['company'] for r in tables['company_theme']))
    th=[r['theme'] for r in tables['themes']]
    matrix=[[int(any(r['company']==c and r['theme']==t for r in tables['company_theme'])) for t in th] for c in cos]
    fig,ax=plt.subplots(figsize=(11,6.5))
    ax.imshow(matrix,cmap=ListedColormap(['#e4eaf0','#007e87']),vmin=0,vmax=1,aspect='auto')
    ax.set(xticks=range(len(th)),xticklabels=th,yticks=range(len(cos)),yticklabels=cos,title='Documented company links across technology themes')
    plt.setp(ax.get_xticklabels(),rotation=25,ha='right')
    for i,row in enumerate(matrix):
        for j,v in enumerate(row):
            if v:ax.text(j,i,'Linked',ha='center',va='center',color='white',fontsize=9)
    save(fig,'company-theme-map','Sources in company_theme.csv · Blank = not mapped in this study; it does not establish no involvement.')

def make_findings(tables, root=ROOT):
    latest=[]
    for cid in sorted({r['company_id'] for r in tables['company_revenue']}):
        latest.append(max([r for r in tables['company_revenue'] if r['company_id']==cid],key=lambda r:r['fiscal_year']))
    latest.sort(key=lambda r:r['yoy_growth'], reverse=True)
    history=sorted([r for r in tables['market'] if r['selected']],key=lambda r:r['year'])
    lines=['# Results and findings','',
        'Research snapshot reviewed 5 November 2026. Results below distinguish reported facts, published outlooks and illustrative analyst assumptions. This is a small market-intelligence study, not a validated ten-year demand forecast.','',
        '## Main conclusion','',
        'The sampled companies show strong recent revenue growth in AI computing, memory and foundry businesses, alongside slower or negative growth in some automotive and industrial suppliers. This supports prioritizing the AI infrastructure ecosystem for further demand research. It does not establish which chip segment or company will perform best by 2036.',
        '', '## Result 1 Global semiconductor sales recovered after 2023','',
        '| Calendar year | Selected reported sales USD billions | Calculated year over year | Source |',
        '| --- | ---: | ---: | --- |']
    for r in history:
        growth=f"{r['yoy_growth']:+.1%}" if r['yoy_growth'] is not None else 'Prior year not included'
        lines.append(f"| {r['year']} | {r['value_usd_billions']:,.1f} | {growth} | {r['source_id']} |")
    lines += ['',
        '**Interpretation:** recovery in aggregate sales provides context for the opportunity, but does not mean every product category grows at the same pace. Revenue includes price and product-mix effects; this table does not measure chips shipped.',
        '**Vintage detail:** the initial 2024 release reported 627.6 billion USD (S02); a later report gives 630.5 billion (S03). Both are retained in the audit data and only the later one is selected. Calculated growth uses selected rows from different release vintages and can differ from a release headline. Do not sum the two 2024 values.',
        '', '## Result 2 Growth differs across the sampled companies','',
        '| Company | Included fiscal year | Period end | Revenue YoY | Source |', '| --- | ---: | --- | ---: | --- |']
    lines += [f"| {r['company']} | {r['fiscal_year']} | {r['period_end']} | {r['yoy_growth']:+.1%} | {r['source_id']} |" for r in latest]
    lines += ['',
        '**Interpretation:** NVIDIA, SK hynix and TSMC have the strongest latest-included growth in this sample. Their different roles suggest that the recent opportunity warrants investigation across compute, memory and manufacturing. This is a comparison of consolidated company results, not measured growth of seven technology markets.',
        'Texas Instruments shows recovery in its latest included year while Infineon and NXP decline. Their exposure to industrial, automotive and power applications remains relevant, but the observed results do not support describing the whole semiconductor industry as one uniform boom.',
        '**Comparability:** fiscal-year labels refer to different periods. NVIDIA FY2026 ends in January 2026; Infineon FY2025 ends in September 2025. Growth is within each company in its reported currency and may reflect pricing, product mix, acquisitions and foreign exchange. No mixed-currency company revenue total or company market share is calculated.',
        '', '## Result 3 The opportunity spans several parts of the value chain','',
        '| Technology theme | Documented company links in this study | Meaning for further research |',
        '| --- | --- | --- |',
        '| AI compute | NVIDIA | Investigate training, inference and competition from custom chips. |',
        '| AI memory | SK hynix | Investigate bandwidth needs, capacity expansion and memory pricing cycles. |',
        '| AI networking | NVIDIA | Investigate connectivity needs as AI systems scale. |',
        '| Power electronics | Infineon and Texas Instruments | Investigate power conversion and efficiency requirements. |',
        '| Automotive and edge AI | Infineon, NXP and Texas Instruments | Investigate adoption timing and automotive qualification cycles. |',
        '| Industrial embedded | Infineon, NXP and Texas Instruments | Investigate automation demand and industrial capital spending. |',
        '| Design tools and packaging | Siemens EDA and TSMC | Investigate design complexity and heterogeneous integration as distinct activities. |',
        '',
        'These links are qualitative product/business relevance, not revenue allocation, market share or a complete competitive map. A company missing from a theme is not proven to have no involvement. Siemens EDA is mapped qualitatively; Siemens group revenue is excluded from chip-company comparisons. Design software and packaging share a broad research theme here, but would need separate market definitions for a market-size forecast.',
        '', '## Published outlook External forecasts provide context','',
        '| External observation | Value | Classification | Source |',
        '| --- | --- | --- | --- |',
        '| Global semiconductor sales in 2026 | Approximately 1.51 trillion USD | WSTS Spring 2026 forecast | S05 |',
        '| Global semiconductor sales in 2027 | Approximately 1.9 trillion USD | WSTS Spring 2026 forecast | S05 |',
        '| Data-center electricity in 2025 | 485 TWh | IEA estimate | S12 |',
        '| Data-center electricity in 2030 | 950 TWh | IEA projection | S12 |',
        '',
        '**Interpretation:** the electricity outlook motivates research into data-center power requirements. It cannot be converted directly into power-chip revenue. WSTS values are rounded, vintage-specific forecasts, not confirmed sales or forecasts for 2036. They are not extended mechanically to 2036 in this project.',
        '', '## Scenario result What the assumptions produce by 2036','',
        'Every theme starts at an artificial index of 100 in 2026. Early rates apply for four annual steps through 2030 and late rates for six steps through 2036. The table below is calculated from config/scenarios.json; it is not an externally validated demand prediction.',
        '', '| Theme | Conservative index | Base index | Accelerated index | Base early rate | Base late rate |',
        '| --- | ---: | ---: | ---: | ---: | ---: |']
    endpoints=[r for r in tables['scenarios'] if r['year']==2036]
    for theme in sorted(tables['themes'],key=lambda t:next(r['index_value'] for r in endpoints if r['theme_id']==t['theme_id'] and r['scenario']=='Base'),reverse=True):
        values={r['scenario']:r['index_value'] for r in endpoints if r['theme_id']==theme['theme_id']}
        base=next(a for a in tables['assumptions'] if a['theme_id']==theme['theme_id'] and a['scenario']=='Base')
        lines.append(f"| {theme['theme']} | {values['Conservative']:.1f} | {values['Base']:.1f} | {values['Accelerated']:.1f} | {base['early_growth']:.1%} | {base['late_growth']:.1%} |")
    lines += ['',
        '**How to read it:** an index of 249.7 means approximately 2.50 times the artificial starting level under the chosen assumptions. AI compute has the highest base index because it was assigned the highest base rates. Power electronics and design tools/packaging have identical base rates and therefore overlap in the chart.',
        '**What it cannot show:** equal index bases do not imply equal market sizes. Indices cannot rank absolute dollar opportunities, company returns or probabilities. Themes overlap and must not be summed. No company revenue, market share or share-price forecast is produced.',
        '', '## Decision What to conclude from this project','',
        'Prioritize further research into AI compute, memory, connectivity, manufacturing/design and power conversion as linked infrastructure needs. Use automotive/edge and industrial embedded as contrasting demand cycles. Treat this as a research shortlist rather than a final 2036 winner ranking.',
        '', '## Evidence needed before a ten-year winner claim','',
        '- Compatible segment market sizes, shipment volumes and pricing series, with non-overlapping definitions.',
        '- Independent adoption forecasts, competitive-share evidence and multiple forecast vintages.',
        '- Explicit evidence for growth assumptions and out-of-period backtesting.',
        '- Common currency/period treatment where absolute comparisons are intended.',
        '', '## Delivery and validation status','',
        'The Python analysis, SQL checks, notebook and chart review are completed. The Power BI report definitions pass structural schema checks and field-reference tests. Opening, refreshing and visually checking the project in Power BI Desktop remain pending; these are release gates before describing the native report as verified.',
        'The study has 16 company-year observations and four selected market years. This sparse snapshot is useful for transparent exploratory analysis, but insufficient for a validated ten-year forecasting model.',
        '', '## Source traceability','',
        'Source IDs resolve to original URLs, access dates and coverage in [sources.csv](../data/processed/sources.csv). Facts are manually curated, not a live feed or exhaustive company universe. Underlying source publications retain their own rights.']
    (root/'reports').mkdir(exist_ok=True)
    (root/'reports/findings.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

def main():
    raw, assumptions=load_inputs(); tables=tables_from(raw, assumptions)
    export_tables(tables); make_charts(tables); make_findings(tables)
    print('Built 8 CSV tables, four charts, SQLite database and findings.')

if __name__=='__main__':main()
