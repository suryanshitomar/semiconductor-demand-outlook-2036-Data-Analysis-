import json, sqlite3, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.show=lambda:plt.close('all')
ns={}
nb=json.loads((ROOT/'notebooks/01_exploration.ipynb').read_text(encoding='utf-8'))
for i,cell in enumerate(nb['cells']):
 if cell['cell_type']=='code':exec(compile(''.join(cell['source']),f'notebook-cell-{i}','exec'),ns)
print('Notebook code cells executed successfully.')
with sqlite3.connect(ROOT/'outputs/analysis.sqlite') as db:
 counts=[]
 sql='\n'.join(line for line in (ROOT/'sql/exploration.sql').read_text().splitlines() if not line.lstrip().startswith('--'))
 for query in sql.split(';'):
  if query.strip():counts.append(len(db.execute(query).fetchall()))
print('SQL result row counts:',counts)
assert counts==[4,6,21,0],counts
print('SQL checks passed.')
