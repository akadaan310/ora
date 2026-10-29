import json, sys, tempfile, threading, urllib.error, urllib.request, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from server import Server
from render_foundry import VERSION
P=Path(__file__).resolve().parents[1]
class HTTPTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  self.server=Server(('127.0.0.1',0),self.tmp.name,'')
  self.worker=threading.Thread(target=self.server.serve_forever,daemon=True);self.worker.start()
  self.base='http://127.0.0.1:'+str(self.server.server_port)
 def tearDown(self):self.server.shutdown();self.server.server_close();self.worker.join(timeout=2);self.tmp.cleanup()
 def get(self,path):
  with urllib.request.urlopen(self.base+path,timeout=3) as r:return json.load(r)
 def post(self,path,data,headers=None):
  request=urllib.request.Request(self.base+path,json.dumps(data).encode(),{'Content-Type':'application/json',**(headers or {})},method='POST')
  with urllib.request.urlopen(request,timeout=3) as r:return json.load(r)
 def test_manifest_url(self):self.assertEqual(self.get('/o/ora-render-foundry/manifest')['id'],'ora-render-foundry')
 def test_health(self):self.assertFalse(self.get('/health')['cloud_gpu_connected'])
 def test_plan_endpoint(self):
  spec=json.loads((P/'examples/waterfront-cell.json').read_text())
  self.assertEqual(self.post('/api/v1/render-foundry/plan',spec)['plan']['schema'],VERSION)
 def test_build_endpoint(self):
  spec=json.loads((P/'examples/waterfront-cell.json').read_text())
  result=self.post('/api/v1/render-foundry/build',spec)['result'];self.assertTrue(Path(result['gltf_path']).exists())
 def test_denied_wrong_token(self):
  self.server.token='owner-secret'
  spec=json.loads((P/'examples/waterfront-cell.json').read_text())
  try:self.post('/api/v1/render-foundry/build',spec)
  except urllib.error.HTTPError as e:self.assertEqual(e.code,401)
  else:self.fail('missing auth requirement')
 def test_denied_cross_origin(self):
  spec=json.loads((P/'examples/waterfront-cell.json').read_text())
  try:self.post('/api/v1/render-foundry/build',spec,{'Origin':'https://evil.example'})
  except urllib.error.HTTPError as e:self.assertEqual(e.code,403)
  else:self.fail('cross origin accepted')
if __name__=='__main__':unittest.main()
