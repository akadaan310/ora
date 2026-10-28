import json,sys,types,threading,urllib.request,urllib.error,tempfile,unittest
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
# Replace inaccessible legacy ORA 0.2 modules in local test only. When installed
# in akadaan310/ORA, service.app / service.engine are the actual runtime.
try:
 import service.app
except ModuleNotFoundError:
 mod=types.ModuleType('service.app')
 class BaseHandler(BaseHTTPRequestHandler):
  def reply(self,status,val):
   b=json.dumps(val).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
  def require_auth(self):
   if self.server.token and self.headers.get('Authorization','')!='Bearer '+self.server.token:self.reply(401,{'error':'AUTH_REQUIRED'});return False
   return True
  def do_GET(self):
   if self.path=='/':
    b=(Path(self.server.web)/'index.html').read_bytes();self.send_response(200);self.send_header('Content-Type','text/html');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b);return
   self.reply(404,{'error':'LEGACY_NOT_IMPLEMENTED_IN_MOCK'})
  def do_POST(self):self.reply(404,{'error':'LEGACY_NOT_IMPLEMENTED_IN_MOCK'})
  def log_message(self,*a):pass
 class MockAPI(ThreadingHTTPServer):
  daemon_threads=True
  def __init__(self,address,engine,web,token):
   self.engine=engine;self.web=Path(web);self.token=token
   super().__init__(address,BaseHandler)
 mod.APIServer=MockAPI;mod.Handler=BaseHandler;sys.modules['service.app']=mod
 legacy=types.ModuleType('service.engine')
 class Engine:
  def __init__(self,*args,**kwargs):self.oras={}
  def create(self,name,goal,placement='oracle'):
   value={'id':'ora-'+str(len(self.oras)+100000),'name':name,'goal':goal,'placement':placement,'life':'PROPOSED'};self.oras[value['id']]=value;return value
  def get(self,id):return self.oras.get(id)
  def shutdown(self):pass
 legacy.Engine=Engine;sys.modules['service.engine']=legacy
from service.ora360 import Store
from service.oraspace360 import Server360
from service.engine import Engine

class HTTP360(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.eng=Engine();self.store=Store(Path(self.tmp.name)/'ora360.sqlite')
  self.server=Server360(('127.0.0.1',0),self.eng,Path(__file__).resolve().parents[2]/'ORASPACE'/'web','',self.store)
  self.t=threading.Thread(target=self.server.serve_forever,daemon=True);self.t.start();self.url='http://127.0.0.1:'+str(self.server.server_port)
 def tearDown(self):self.server.shutdown();self.server.server_close();self.tmp.cleanup()
 def req(self,path,doc=None):
  headers={'Content-Type':'application/json'} if doc is not None else {}
  r=urllib.request.Request(self.url+path, json.dumps(doc).encode() if doc is not None else None, headers=headers,method='POST' if doc is not None else 'GET')
  with urllib.request.urlopen(r,timeout=4) as x:return x.status,json.loads(x.read())
 def test_catalog(self):
  code,p=self.req('/api/v1/360/catalog');self.assertEqual(code,200);self.assertGreater(len(p['seeds']),10)
 def test_website(self):
  with urllib.request.urlopen(self.url+'/') as r:self.assertIn(b'Ideas',r.read())
  for a in ('/app.js','/style.css','/scene.js'):
   with urllib.request.urlopen(self.url+a) as r:self.assertEqual(r.status,200)
 def test_full_flow(self):
  code,created=self.req('/api/v1/360/realize',{'intent':'Build an innovative software website for a new university'})
  self.assertEqual(code,201);oid=created['object']['id'];ora=created['ora']['id']
  self.assertEqual(created['object']['ora_id'],ora)
  code,p=self.req('/api/v1/360/objects/'+oid+'/render/web');self.assertEqual(code,200);self.assertIn('<!doctype html>',p['content'])
  code,a=self.req('/api/v1/360/objects/'+oid+'/approve',{'revision':1});self.assertEqual(a['object']['state'],'REALIZED_LOCAL')
  code,an=self.req('/api/v1/360/anchors',{'ora_id':ora,'principal':'codex-oracle'})
  aid=an['anchor']['id'];secret=an['anchor']['one_time_secret']
  code,preview=self.req('/o/'+ora+'/anchor/'+aid);self.assertFalse(preview['secret_in_url'])
  self.assertNotIn('one_time_secret',json.dumps(preview))
  code,attached=self.req('/api/v1/360/anchors/'+aid+'/attach',{'principal':'codex-oracle','secret':secret});self.assertEqual(attached['anchor']['status'],'ATTACHED')
  code,b=self.req('/api/v1/360/batons',{'ora_id':ora,'recipient':'codex-oracle','subject':'Review the saved university artifact'})
  bid=b['baton']['id'];code,capsule=self.req('/b/'+bid+'/capsule');self.assertEqual(capsule['private_message'],'REDACTED')
  self.assertTrue(self.req('/api/v1/360/health')[1]['ledger_valid'])
 def test_auth_on_mutation(self):
  self.server.token='x'*40
  try:self.req('/api/v1/360/realize',{'intent':'Build a website'})
  except urllib.error.HTTPError as e:self.assertEqual(e.code,401)
  else:self.fail('unauthorized write')

if __name__=='__main__':unittest.main()
