import json, os, sys, tempfile, threading, unittest, urllib.request, urllib.error
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from service.engine import Engine
from service.app import APIServer

class HTTPTests(unittest.TestCase):
 def setUp(self):
  self.d=tempfile.TemporaryDirectory();self.e=Engine(self.d.name+'/db.sqlite',worker=True)
  self.server=APIServer(('127.0.0.1',0),self.e,Path(__file__).resolve().parents[2]/'ORASPACE'/'web','')
  self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start();self.base='http://127.0.0.1:'+str(self.server.server_port)
 def tearDown(self):self.server.shutdown();self.server.server_close();self.e.shutdown();self.d.cleanup()
 def get(self,p):
  with urllib.request.urlopen(self.base+p,timeout=3) as r:return json.load(r)
 def post(self,p,doc,headers=None):
  req=urllib.request.Request(self.base+p,json.dumps(doc).encode(),headers={'Content-Type':'application/json',**(headers or {})},method='POST')
  with urllib.request.urlopen(req,timeout=3) as r:return json.load(r)
 def test_health_manifest(self):
  self.assertTrue(self.get('/api/v1/health')['ok']);self.assertEqual(len(self.get('/api/v1/tower')['levels']),12)
  self.assertTrue(self.get('/.well-known/ora.json')['read_only_navigation'])
 def test_create_and_mission_http(self):
  a=self.post('/api/v1/oras',{'name':'Sky','goal':'Explore stars'})['ora']
  path='/o/'+a['id'];self.assertEqual(self.get(path)['private_goal'],'REDACTED')
  self.assertEqual(self.get(path+'/purl/v1/shift/WRITE/input/test1/preview')['effect'],'PREVIEW_ONLY')
  a=self.post('/api/v1/oras/'+a['id']+'/transition',{'action':'review','expected_version':1})['ora']
  a=self.post('/api/v1/oras/'+a['id']+'/transition',{'action':'activate','expected_version':2})['ora']
  m=self.post('/api/v1/oras/'+a['id']+'/missions',{'kind':'scene.generate','payload':{'seed':1,'count':3}})['mission']
  self.assertTrue(m['id'].startswith('mission-'));self.assertTrue(self.get('/api/v1/events')['chain_valid'])
 def test_auth(self):
  self.server.token='S'*36
  try:urllib.request.urlopen(self.base+'/api/v1/oras',timeout=3)
  except urllib.error.HTTPError as e:self.assertEqual(e.code,401)
  else:self.fail('leaked agent list')
  req=urllib.request.Request(self.base+'/api/v1/oras',headers={'Authorization':'Bearer '+'S'*36})
  with urllib.request.urlopen(req) as r:self.assertEqual(r.status,200)
 def test_site(self):
  with urllib.request.urlopen(self.base+'/') as r:
   doc=r.read().decode();self.assertIn('Ideas',doc);self.assertIn('/api/v1/oras',doc)

if __name__=='__main__':unittest.main()
