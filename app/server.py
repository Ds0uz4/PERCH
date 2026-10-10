import json, os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
ROOT=Path(__file__).parent; RESULTS=Path(os.environ.get('RESULTS_PATH','/results'))
class Handler(SimpleHTTPRequestHandler):
 def do_GET(self):
  if self.path=='/api/status': return self.send_file(RESULTS/'status.json',{})
  if self.path=='/api/log':
   p=RESULTS/'decision_log.jsonl'; rows=[]
   if p.exists():
    for line in p.read_text(encoding='utf8').splitlines()[-30:]:
     try: rows.append(json.loads(line))
     except json.JSONDecodeError: pass
   return self.send_json(rows)
  return super().do_GET()
 def send_file(self,p,default):
  try: return self.send_json(json.loads(p.read_text(encoding='utf8')))
  except (OSError,json.JSONDecodeError): return self.send_json(default)
 def send_json(self,obj):
  raw=json.dumps(obj).encode(); self.send_response(200); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(raw))); self.end_headers(); self.wfile.write(raw)
 def log_message(self,*args): pass
os.chdir(ROOT); ThreadingHTTPServer(('0.0.0.0',80),Handler).serve_forever()
