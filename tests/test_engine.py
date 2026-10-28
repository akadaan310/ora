import json, os, sys, tempfile, time, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from service.engine import Engine, PRIME, compile_path, language_inspect, article_structure, grammar_propose

class EngineTests(unittest.TestCase):
 def setUp(self):
  self.d=tempfile.TemporaryDirectory();self.path=self.d.name+'/ora.sqlite3';self.e=Engine(self.path,worker=False)
 def tearDown(self):self.e.shutdown();self.d.cleanup()
 def new(self,goal='Study Wikipedia articles using language grammars'):
  a=self.e.create('',goal);self.e.transition(a['id'],'review');return self.e.transition(a['id'],'activate')
 def test_tower_and_sovereign(self):
  self.assertEqual(len(self.e.tower()['levels']),12);self.assertEqual(self.e.get(PRIME)['life'],'RUNNING')
 def test_create_and_persistence(self):
  a=self.e.create('My Wikipedia','Analyze Wikipedia Arabic articles',placement='android');self.assertEqual(a['life'],'PROPOSED');self.assertEqual(a['placement'],'android')
  other=Engine(self.path,worker=False);self.assertEqual(other.get(a['id'])['name'],'My Wikipedia');other.shutdown()
 def test_parallel_regions(self):
  a=self.e.create('Blue','Discover stars');self.assertEqual(set(a['regions']),{'lifecycle','observation','execution','authority','continuity'})
  a=self.e.transition(a['id'],'review');a=self.e.transition(a['id'],'activate');self.assertEqual(a['regions']['observation']['state'],'AWAKE');self.assertEqual(a['regions']['lifecycle']['state'],'RUNNING')
 def test_version_and_invalid_transition(self):
  a=self.e.create('X','Study language');self.assertRaises(ValueError,self.e.transition,a['id'],'activate')
  self.assertRaises(ValueError,self.e.transition,a['id'],'review',99)
  self.e.transition(a['id'],'review');self.assertRaises(ValueError,self.e.transition,a['id'],'review')
 def test_delegation_attenuation(self):
  a=self.new();b=self.e.create('Child language','Study Arabic alphabets',a['id'],['language.inspect'])
  self.assertEqual(b['grants'],['language.inspect']);self.assertRaises(PermissionError,self.e.create,'Bad','Study music',a['id'],['scene.generate'])
 def test_supported_missions(self):
  a=self.new();article='== Introduction ==\nArabic [[Maqam]] and Greek Ελληνικά.'
  m=self.e.submit(a['id'],'article.structure',{'text':article});done=self.e.run_one(m['id']);self.assertEqual(done['state'],'SUCCEEDED');self.assertEqual(done['result']['wikilink_targets'],['Maqam'])
  x=self.e.submit(a['id'],'language.inspect',{'text':article});self.assertEqual(self.e.run_one(x['id'])['result']['scripts']['Greek']>0,True)
 def test_missing_capability_denied(self):
  a=self.new('Play my piano music');self.assertIn('music.compose',a['missing'])
  self.assertRaises(ValueError,self.e.submit,a['id'],'music.compose',{})
 def test_idempotency(self):
  a=self.new();x=self.e.submit(a['id'],'language.inspect',{'text':'hello'},'retry-job-1');y=self.e.submit(a['id'],'language.inspect',{'text':'hello'},'retry-job-1');self.assertEqual(x['id'],y['id'])
  self.assertRaises(ValueError,self.e.submit,a['id'],'language.inspect',{'text':'different'},'retry-job-1')
 def test_scene_determinism(self):
  a=self.new('Explore sky and stars');x=self.e.submit(a['id'],'scene.generate',{'seed':77,'count':7});y=self.e.submit(a['id'],'scene.generate',{'seed':77,'count':7});z=self.e.submit(a['id'],'scene.generate',{'seed':78,'count':7});
  out=[self.e.run_one(i['id'])['result'] for i in (x,y,z)];self.assertEqual(out[0],out[1]);self.assertNotEqual(out[0],out[2]);self.assertEqual(len(out[0]['stars']),7)
 def test_grammar_is_only_proposal(self):
  a=self.new('Build a grammar generator');x=self.e.submit(a['id'],'grammar.propose',{'text':'alpha beta alpha gamma'});res=self.e.run_one(x['id'])['result'];self.assertEqual(res['admission'],'PROPOSED_ONLY')
 def test_ledger_integrity_and_tamper(self):
  self.new();self.assertTrue(self.e.verify());
  with self.e.write() as c:c.execute("UPDATE events SET kind='FORGED' WHERE seq=1")
  self.assertFalse(self.e.verify())
 def test_url_preview_pure(self):
  a=self.new();path='/o/'+a['id']+'/purl/v1/shift/BUILD/input/abc_123/preview';before=len(self.e.event_stream());p=compile_path(path)
  self.assertEqual(p['effect'],'PREVIEW_ONLY');self.assertEqual(len(self.e.event_stream()),before)
  self.assertRaises(ValueError,compile_path,path.replace('BUILD','INVALID'))
  self.assertRaises(ValueError,compile_path,path.replace('abc_123','../x'))
 def test_source_parsers(self):
  x=language_inspect('hello مرحبا');self.assertEqual(x['scripts']['Arabic'],5)
  a=article_structure('# Lead\n== Body ==\n[[Linked page]]');self.assertEqual(len(a['headings']),2)
  self.assertEqual(grammar_propose('x y z')['admission'],'PROPOSED_ONLY')
 def test_listener_proposes_child(self):
  result=self.e.observe('CAPABILITY_GAP',PRIME,'Build Shopify marketing strategy models')
  self.assertEqual(result['status'],'PROPOSED');self.assertEqual(self.e.get(result['child'])['life'],'PROPOSED')
  self.e.observe('NETWORK_DISCONNECTED',result['child']);self.assertEqual(self.e.get(result['child'])['regions']['continuity']['state'],'OFFLINE')
  self.e.observe('NETWORK_RECONNECTED',result['child']);self.assertTrue(self.e.verify())
 def test_unmapped_does_not_fake_capability(self):
  a=self.e.create('Strategy','Manage Shopify business strategy')
  self.assertEqual(a['grants'],[]);self.assertEqual(a['missing'],['goal.unmapped'])
 def test_worker_async(self):
  e=Engine(self.d.name+'/async.db',worker=True)
  try:
   a=e.create('Worker','Analyze language and scripts');e.transition(a['id'],'review');e.transition(a['id'],'activate')
   m=e.submit(a['id'],'language.inspect',{'text':'hello β'});deadline=time.monotonic()+3
   while time.monotonic()<deadline and e.mission(m['id'])['state'] not in ('SUCCEEDED','FAILED'):time.sleep(.03)
   self.assertEqual(e.mission(m['id'])['state'],'SUCCEEDED');self.assertTrue(e.verify())
  finally:e.shutdown()

if __name__=='__main__':unittest.main()
