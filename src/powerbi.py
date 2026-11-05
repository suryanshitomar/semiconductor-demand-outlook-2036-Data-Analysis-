"""Generate a portable PBIP project with embedded, refreshable snapshot tables."""
import json
import uuid
from pathlib import Path
from analysis import ROOT, load_inputs, tables_from

SCHEMA='https://developer.microsoft.com/json-schemas/fabric/item/report/'

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n',encoding='utf-8')

def m_literal(value):
    if value is None:return 'null'
    if isinstance(value,bool):return str(value).lower()
    if isinstance(value,(int,float)):return repr(value)
    return '"'+str(value).replace('"','""').replace('\n','#(lf)').replace('\r','')+'"'

def make_table(name, rows):
    fields=list(rows[0]); columns=[]; types=[]
    for key in fields:
        values=[r[key] for r in rows if r[key] is not None]
        example=values[0] if values else ''
        dtype='boolean' if isinstance(example,bool) else 'int64' if isinstance(example,int) else 'double' if isinstance(example,float) else 'string'
        mtype={'boolean':'logical','int64':'Int64.Type','double':'number','string':'text'}[dtype]
        columns.append({'name':key,'dataType':dtype,'sourceColumn':key,'summarizeBy':'none'})
        types.append(key+' = '+('nullable '+mtype if mtype not in ['Int64.Type'] else mtype))
    expression='#table(type table ['+', '.join(types)+'], {'+',\n'.join('{'+', '.join(m_literal(r[k]) for k in fields)+'}' for r in rows)+'})'
    return {'name':name,'columns':columns,'partitions':[{'name':name,'mode':'import','source':{'type':'m','expression':expression.splitlines()}}]}

def column(table, name, label=None):
    return {'field':{'Column':{'Expression':{'SourceRef':{'Entity':table}},'Property':name}},
            'queryRef':table+'.'+name,'displayName':label or name}

def measure(table, name):
    return {'field':{'Measure':{'Expression':{'SourceRef':{'Entity':table}},'Property':name}},'queryRef':table+'.'+name}

def visual(name, kind, query, x,y,w,h,title):
    title_properties={'show':{'expr':{'Literal':{'Value':'true'}}},
                      'text':{'expr':{'Literal':{'Value':"'"+title.replace("'","''")+"'"}}}}
    return {'$schema':SCHEMA+'definition/visualContainer/2.0.0/schema.json','name':name,
        'position':{'x':x,'y':y,'z':0,'width':w,'height':h,'tabOrder':0},
        'visual':{'visualType':kind,'query':{'queryState':{role:{'projections':fields} for role,fields in query.items()}},
            'visualContainerObjects':{'title':[{'properties':title_properties}]}}}

def build(root=ROOT):
    raw,assumptions=load_inputs(root); tables=tables_from(raw, assumptions)
    # Keep market revisions in the audit CSV; model chart contains selected rows only.
    tables['market']=[r for r in tables['market'] if r['selected']]
    # Explicitly add latest-only tables for charts, avoiding aggregation across years.
    tables['latest_company']=[max([r for r in tables['company_revenue'] if r['company_id']==cid],key=lambda r:r['fiscal_year'])
        for cid in sorted({r['company_id'] for r in tables['company_revenue']})]
    tables['scenario_endpoints']=[r for r in tables['scenarios'] if r['year']==2036]
    modeltables=[make_table(name,rows) for name,rows in tables.items()]
    measures={
        'market':[{'name':'Market sales USD bn','expression':'IF(HASONEVALUE(market[year]), MAX(market[value_usd_billions]))','formatString':'#,0.0'}],
        'latest_company':[{'name':'Latest revenue growth','expression':'IF(HASONEVALUE(latest_company[company_id]), MAX(latest_company[yoy_growth]))','formatString':'0.0%'}],
        'scenarios':[{'name':'Scenario index','expression':'IF(HASONEVALUE(scenarios[theme_id]) && HASONEVALUE(scenarios[scenario]) && HASONEVALUE(scenarios[year]), MAX(scenarios[index_value]))','formatString':'0.0'}],
        'scenario_endpoints':[{'name':'2036 index','expression':'IF(HASONEVALUE(scenario_endpoints[theme_id]) && HASONEVALUE(scenario_endpoints[scenario]), MAX(scenario_endpoints[index_value]))','formatString':'0.0'}]
    }
    for t in modeltables:
        if t['name'] in measures:t['measures']=measures[t['name']]
    pb=root/'powerbi'; report=pb/'Outlook.Report'; sm=pb/'Outlook.SemanticModel'
    write_json(pb/'Semiconductor-Outlook.pbip',{'version':'1.0','artifacts':[{'report':{'path':'Outlook.Report'}}],'settings':{'enableAutoRecovery':True}})
    write_json(sm/'definition.pbism',{'version':'1.0','settings':{}})
    write_json(sm/'model.bim',{'name':'SemiconductorOutlook','compatibilityLevel':1567,
        'model':{'culture':'en-US','defaultPowerBIDataSourceVersion':'powerBI_V3','tables':modeltables}})
    write_json(report/'definition.pbir',{'$schema':SCHEMA+'definitionProperties/2.0.0/schema.json','version':'4.0','datasetReference':{'byPath':{'path':'../Outlook.SemanticModel'}}})
    write_json(report/'definition/version.json',{'version':'2.0.0'})
    write_json(report/'definition/report.json',{'$schema':SCHEMA+'definition/report/3.0.0/schema.json','themeCollection':{}})
    pages=[('market','Market history'),('companies','Company growth and exposure'),('scenarios','2036 assumption scenarios'),('sources','Sources and published outlook')]
    write_json(report/'definition/pages/pages.json',{'$schema':SCHEMA+'definition/pagesMetadata/1.0.0/schema.json','pageOrder':[p[0] for p in pages],'activePageName':'market'})
    for pid,title in pages:
        write_json(report/f'definition/pages/{pid}/page.json',{'$schema':SCHEMA+'definition/page/1.0.0/schema.json',
            'name':pid,'displayName':title,'displayOption':'FitToPage','width':1280,'height':720})
    visuals={
        'market':[
            visual('markettrend','lineChart',{'Category':[column('market','year')],'Y':[measure('market','Market sales USD bn')]},20,20,1240,350,'Selected reported global sales · USD billions · mixed vintages'),
            visual('marketdetail','tableEx',{'Values':[column('market',k) for k in ['year','value_usd_billions','source_id','status']]},20,400,1240,290,'Historical source details · no 2036 extrapolation')],
        'companies':[
            visual('growth','clusteredBarChart',{'Category':[column('latest_company','company')],'Y':[measure('latest_company','Latest revenue growth')]},20,20,600,350,'Within-company YoY · different fiscal ends'),
            visual('growthdetails','tableEx',{'Values':[column('latest_company',k) for k in ['company','fiscal_year','period_end','currency','source_id']]},650,20,610,350,'Fiscal period and currency context'),
            visual('links','tableEx',{'Values':[column('company_theme',k) for k in ['company','theme','source_id','interpretation']]},20,400,1240,290,'Documented links · not market share or revenue weights')],
        'scenarios':[
            visual('scenarioend','clusteredBarChart',{'Category':[column('scenario_endpoints','theme')],'Series':[column('scenario_endpoints','scenario')],'Y':[measure('scenario_endpoints','2036 index')]},20,20,1240,350,'2036 index · 2026 = 100 · analyst assumptions only'),
            visual('assumptiontable','tableEx',{'Values':[column('assumptions',k) for k in ['theme_id','scenario','early_growth','late_growth','basis']]},20,400,1240,290,'2027–30 early rate; 2031–36 late rate · edit config/scenarios.json and rebuild')],
        'sources':[
            visual('published','tableEx',{'Values':[column('published_outlook',k) for k in ['metric','year','value','unit','status','source_id']]},20,20,1240,260,'Published estimates and forecasts · separate from reported history'),
            visual('sources','tableEx',{'Values':[column('sources',k) for k in ['source_id','title','url','published_date','accessed_date']]},20,320,1240,370,'Source register · blank publication date means not established')]
    }
    for pid,items in visuals.items():
        for v in items:write_json(report/f'definition/pages/{pid}/visuals/{v["name"]}/visual.json',v)
    dax='\n\n'.join(m['name']+' = '+m['expression'] for group in measures.values() for m in group)
    (pb/'measures.dax').write_text(dax+'\n',encoding='utf-8')
    write_json(pb/'theme.json',{'name':'Semiconductor Outlook','dataColors':['#007E87','#386CB0','#C58530','#7B61A8','#B94D4D','#5C8871','#586C85'],'background':'#F6F8FB','foreground':'#142B43','tableAccent':'#007E87'})
    print('Built portable PBIP: 4 pages, 9 visuals, embedded M snapshot tables.')

if __name__=='__main__':build()
