"""Check PBIR against Microsoft's JSON schemas; cache schemas locally, not in Git."""
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path
from hashlib import sha256
import warnings
warnings.filterwarnings('ignore',category=DeprecationWarning)
from jsonschema import Draft7Validator, RefResolver

ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'.cache/schemas'

def fetch(url):
    CACHE.mkdir(parents=True,exist_ok=True)
    path=CACHE/(sha256(url.encode()).hexdigest()+'.json')
    if not path.exists():
        # Some Microsoft $id values use a dot while their published file uses a hyphen.
        try:
            response=urllib.request.urlopen(url,timeout=30)
        except urllib.error.HTTPError as e:
            if e.code!=404 or 'schema.embedded.json' not in url:raise
            response=urllib.request.urlopen(url.replace('schema.embedded.json','schema-embedded.json'),timeout=30)
        with response:
            text=response.read().decode('utf-8')
        json.loads(text)
        path.write_text(text,encoding='utf-8')
    return json.loads(path.read_text(encoding='utf-8'))

def main():
    count=0
    for path in sorted((ROOT/'powerbi').rglob('*.json')):
        value=json.loads(path.read_text(encoding='utf-8'))
        if '$schema' not in value:continue
        url=value['$schema'];schema=fetch(url)
        resolver=RefResolver(base_uri=url,referrer=schema,handlers={'https':fetch})
        errors=list(Draft7Validator(schema,resolver=resolver).iter_errors(value))
        if errors:
            raise ValueError(str(path.relative_to(ROOT))+': '+'; '.join(e.message for e in errors[:4]))
        count+=1
    # Definition properties have .pbir extension, so validate explicitly.
    path=ROOT/'powerbi/Outlook.Report/definition.pbir'
    value=json.loads(path.read_text(encoding='utf-8'));url=value['$schema'];schema=fetch(url)
    Draft7Validator(schema,resolver=RefResolver(base_uri=url,referrer=schema,handlers={'https':fetch})).validate(value)
    print(f'Validated {count+1} schema-bearing report files. Desktop rendering and M/DAX execution still require Power BI Desktop.')

if __name__=='__main__':main()
