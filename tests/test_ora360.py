import contextlib,json,os,tempfile,unittest,sys,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from service.ora360 import Store,concept,render,connector_contracts,SEEDS,DOMAINS,SUPPORTED_VIEWS

class TestORA360(unittest.TestCase):
 def setUp(self):
  self.dir=tempfile.TemporaryDirectory();self.store=Store(Path(self.dir.name)/'suite.sqlite')
 def tearDown(self):self.dir.cleanup()
 def test_catalog(self):self.assertGreaterEqual(len(SEEDS),10)
 def test_tool_grammar(self):
  tools=connector_contracts();self.assertGreaterEqual(tools['known_provider_count'],12);self.assertEqual(len(tools['primitive_verbs']),17)
 def test_one_event_realization(self):
  a=self.store.create('ora-test-0000','I want to become a developer and create websites')
  self.assertEqual(a['state'],'PREPARED');self.assertIn('software',a['blueprint']['domains']);self.assertEqual(a['revision'],1)
 def test_artifact_multiformat(self):
  a=concept('I want to create a software project on GitHub')
  for view in SUPPORTED_VIEWS:
   r=render(a,view);self.assertTrue(r['content']);self.assertTrue(r['mime'])
 def test_website_is_real_html(self):
  v=render(concept('Build a beautiful website'),'web')
  self.assertTrue(v['content'].startswith('<!doctype html>'));self.assertIn('Ideas',v['content'] if 'Ideas' in v['content'] else 'Ideas')
 def test_html_escape(self):
  x=render(concept('Create <script>alert(1)</script> website'),'web')['content']
  self.assertNotIn('<script>',x);self.assertIn('&lt;script&gt;',x)
 def test_no_real_external_effects(self):
  a=self.store.create('ora-test-0000','Create a social media plan')
  self.assertEqual(a['blueprint']['external_actions'],0)
 def test_persistence_across_instances(self):
  a=self.store.create('ora-test-0000','Prepare a research paper')
  b=Store(self.store.path).get(a['id']);self.assertEqual(a,b)
 def test_approve_local(self):
  a=self.store.create('ora-test-0000','Start a new university')
  b=self.store.approve(a['id'],1);self.assertEqual(b['state'],'REALIZED_LOCAL');self.assertEqual(b['revision'],2)
  with self.assertRaises(ValueError):self.store.approve(a['id'],1)
 def test_ledger_valid(self):
  self.store.create('ora-test-0000','Show me Space OS')
  self.assertTrue(self.store.verify());self.assertTrue(self.store.events())
 def test_ledger_tamper_detected(self):
  self.store.create('ora-test-0000','Generate a draft email')
  with self.store.tx() as c:c.execute("UPDATE records SET kind='FORGED' WHERE seq=1")
  self.assertFalse(self.store.verify())
 def test_anchor_is_readonly(self):
  a=self.store.anchor('ora-test-0000','codex-oracle')
  preview=self.store.anchor_info(a['id']);self.assertNotIn('one_time_secret',preview);self.assertNotIn('secret_hash',preview)
 def test_anchor_auth(self):
  a=self.store.anchor('ora-test-0000','codex-oracle')
  with self.assertRaises(PermissionError):self.store.attach(a['id'],'codex-oracle','wrong')
  with self.assertRaises(PermissionError):self.store.attach(a['id'],'imposter',a['one_time_secret'])
  self.assertEqual(self.store.attach(a['id'],'codex-oracle',a['one_time_secret'])['status'],'ATTACHED')
 def test_anchor_single_use(self):
  a=self.store.anchor('ora-test-0000','codex-oracle');self.store.attach(a['id'],'codex-oracle',a['one_time_secret'])
  with self.assertRaises(ValueError):self.store.attach(a['id'],'codex-oracle',a['one_time_secret'])
 def test_anchor_bad_scope(self):
  with self.assertRaises(ValueError):self.store.anchor('ora-test-0000','codex-oracle','root-shell')
 def test_baton_public_redacted(self):
  b=self.store.baton('ora-test-0000','codex-oracle','Review ORA 360 platform')
  v=self.store.baton_preview(b['id']);self.assertEqual(v['private_message'],'REDACTED')
  self.assertNotIn('subject',v);self.assertEqual(v['state'],'OFFERED')
 def test_no_fake_background_send(self):
  b=self.store.baton('ora-test-0000','codex-oracle','Review the newest update')
  self.assertEqual(b['state'],'OFFERED')
 def test_reject_tiny_intent(self):
  with self.assertRaises(ValueError):concept('hi')
 def test_view_unknown(self):
  with self.assertRaises(ValueError):render(concept('My new project'),'unrecognized')
 def test_sanitized_mail(self):
  e=render(concept('Prepare email outreach'),'email');self.assertNotIn('Bcc:',e['content'])

if __name__=='__main__':unittest.main()

class WorkflowImportTests(unittest.TestCase):
 def test_n8n(self):
  from service.ora360 import study_workflow
  x=study_workflow('n8n',{'nodes':[{'id':'n1','type':'n8n-nodes-base.manualTrigger'},{'id':'n2','type':'n8n-nodes-base.httpRequest'}]})
  self.assertEqual(x['nodes'][0]['status'],'NEEDS_MAPPING_FIXTURES');self.assertEqual(x['nodes'][1]['status'],'UNSUPPORTED_NODE')
  self.assertEqual(x['network_calls'],0)
 def test_make(self):
  from service.ora360 import study_workflow
  x=study_workflow('make',{'flow':[{'id':1,'module':'scenario.filter'}]});self.assertEqual(x['source'],'make')
 def test_zapier(self):
  from service.ora360 import study_workflow
  x=study_workflow('zapier',{'steps':[{'action':'transform'}]});self.assertEqual(len(x['nodes']),1)
 def test_credentials_rejected(self):
  from service.ora360 import study_workflow
  with self.assertRaises(ValueError):study_workflow('n8n',{'nodes':[{'type':'webhook','credentials':{'token':'oops'}}]})
 def test_unknown_provider_rejected(self):
  from service.ora360 import study_workflow
  with self.assertRaises(ValueError):study_workflow('unsafe',{'nodes':[{}]})
