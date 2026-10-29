"""Minimal local interface: only validated findings are displayed as numerical evidence."""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit,parse_qs
import html
from evidence_db import connect,QUERIES
def esc(v):return html.escape(str(v or ""),quote=True)
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  u=urlsplit(self.path)
  if u.path!="/":self.send_error(404);return
  key=parse_qs(u.query).get("variable",["uveitis_intermedia"])[0]
  if key not in QUERIES:key="uveitis_intermedia"
  with connect() as d:
   findings=d.execute("SELECT f.category,f.measure,f.value,f.population,a.url FROM findings f JOIN articles a ON a.pmid=f.pmid WHERE f.variable=? AND f.verified=1",(key,)).fetchall()
   articles=d.execute("SELECT a.title,a.year,a.url FROM articles a JOIN article_variables v ON a.pmid=v.pmid WHERE v.variable=? ORDER BY a.year DESC LIMIT 100",(key,)).fetchall()
  options="".join('<option value="'+esc(k)+'" '+("selected" if k==key else "")+'>'+esc(k.replace("_"," ").title())+'</option>' for k in QUERIES)
  fhtml="".join('<p><strong>'+esc(measure)+": "+esc(value)+'</strong> ('+esc(category)+') · '+esc(pop)+' <a href="'+esc(url)+'">Fuente</a></p>' for category,measure,value,pop,url in findings) or "<p>Sin resultados cuantitativos verificados registrados.</p>"
  ahtml="".join('<p>'+esc(y)+' · <a href="'+esc(url)+'">'+esc(title)+'</a></p>' for title,y,url in articles) or "<p>Sin artículos indexados todavía. Ejecutar sync desde terminal.</p>"
  page='<!doctype html><html lang="es"><meta charset="utf-8"><title>NeuroPredict</title><style>body{font:16px Arial;max-width:900px;margin:40px auto;padding:20px;color:#123}section{padding:20px;background:#f2f5f8;border-radius:12px;margin:16px 0}select,button{padding:10px}</style><h1>NeuroPredict · Esclerosis múltiple</h1><form><select name="variable">'+options+'</select><button>Consultar</button></form><section><h2>Resultados verificados</h2>'+fhtml+'</section><section><h2>Artículos indexados</h2>'+ahtml+'</section><p>Publicación indexada ≠ porcentaje verificado. No contiene historias de pacientes.</p></html>'
  body=page.encode()
  self.send_response(200);self.send_header("Content-Type","text/html; charset=utf-8");self.send_header("Content-Length",str(len(body)));self.send_header("Content-Security-Policy","default-src 'none';style-src 'unsafe-inline';form-action 'self'");self.end_headers();self.wfile.write(body)
if __name__=="__main__":
 connect().close()
 print("Abrir http://127.0.0.1:8765",flush=True)
 ThreadingHTTPServer(("127.0.0.1",8765),Handler).serve_forever()
