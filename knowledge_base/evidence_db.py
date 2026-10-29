"""NeuroPredict evidence store: PubMed metadata; no unvalidated numerical claims."""
import sqlite3,urllib.request,urllib.parse,json,xml.etree.ElementTree as ET
from pathlib import Path
DB=Path(__file__).with_name("evidence.db")
QUERIES={"uveitis_intermedia":'("multiple sclerosis"[tiab]) AND ("intermediate uveitis"[tiab])',"periflebitis_retiniana":'("multiple sclerosis"[tiab]) AND ("retinal periphlebitis"[tiab])',"bandas_oligoclonales":'("multiple sclerosis"[tiab]) AND ("oligoclonal bands"[tiab])',"lesiones_infratentoriales":'("multiple sclerosis"[tiab]) AND ("infratentorial lesions"[tiab])',"oct_gcipl":'("multiple sclerosis"[tiab]) AND ("GCIPL"[tiab] OR "retinal nerve fiber layer"[tiab])'}
def connect():
 d=sqlite3.connect(DB)
 d.executescript("""CREATE TABLE IF NOT EXISTS articles(pmid TEXT PRIMARY KEY,title TEXT,year TEXT,abstract TEXT,url TEXT);
 CREATE TABLE IF NOT EXISTS article_variables(pmid TEXT,variable TEXT,PRIMARY KEY(pmid,variable));
 CREATE TABLE IF NOT EXISTS findings(id INTEGER PRIMARY KEY,pmid TEXT,variable TEXT,category TEXT,measure TEXT,value TEXT,population TEXT,verified INTEGER DEFAULT 0);""")
 return d
def sync(key,limit=20):
 if key not in QUERIES: raise ValueError("Unknown variable")
 def fetch(endpoint,**args):
  req=urllib.request.Request("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"+endpoint+"?"+urllib.parse.urlencode(args),headers={"User-Agent":"NeuroPredict/0.2 academic"})
  with urllib.request.urlopen(req,timeout=25) as r:return r.read()
 ids=json.loads(fetch("esearch.fcgi",db="pubmed",term=QUERIES[key],retmode="json",retmax=limit))["esearchresult"]["idlist"]
 if not ids:return 0
 root=ET.fromstring(fetch("efetch.fcgi",db="pubmed",id=",".join(ids),retmode="xml"))
 with connect() as d:
  n=0
  for item in root.findall(".//PubmedArticle"):
   m=item.find("MedlineCitation")
   if m is None:continue
   pmid=m.findtext("PMID");t=m.find("Article/ArticleTitle")
   if not pmid or t is None:continue
   title="".join(t.itertext()).strip()
   year=m.findtext("Article/Journal/JournalIssue/PubDate/Year") or ""
   abstract=" ".join("".join(a.itertext()) for a in m.findall("Article/Abstract/AbstractText"))
   d.execute("INSERT OR REPLACE INTO articles VALUES(?,?,?,?,?)",(pmid,title,year,abstract,"https://pubmed.ncbi.nlm.nih.gov/"+pmid+"/"))
   d.execute("INSERT OR IGNORE INTO article_variables VALUES(?,?)",(pmid,key));n+=1
 return n
if __name__=="__main__":
 import argparse
 p=argparse.ArgumentParser();p.add_argument("action",choices=["init","sync"]);p.add_argument("--variable",choices=list(QUERIES),default="uveitis_intermedia");p.add_argument("--limit",type=int,default=20);a=p.parse_args()
 if a.action=="init":connect().close();print("Base inicializada")
 else:print("Artículos indexados (NO cifras verificadas):",sync(a.variable,max(1,min(200,a.limit))))
