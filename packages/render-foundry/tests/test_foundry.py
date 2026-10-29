import json, sys, tempfile, unittest
from copy import deepcopy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from render_foundry import *
R=Path(__file__).resolve().parents[1]
class FoundryTests(unittest.TestCase):
 def setUp(self):self.recipe=json.loads((R/'examples/waterfront-cell.json').read_text())
 def test_manifest(self):self.assertEqual(manifest()['id'],'ora-render-foundry')
 def test_gpu_bake_not_falsely_implemented(self):self.assertFalse(manifest()['capabilities']['render.gpu.bake']['implemented'])
 def test_plan_prepared(self):self.assertEqual(compile_recipe(self.recipe)['state'],'PREPARED_NOT_EXECUTED')
 def test_plan_replay(self):self.assertEqual(compile_recipe(self.recipe),compile_recipe(self.recipe))
 def test_plan_gpu_target(self):self.assertEqual(compile_recipe(self.recipe)['tasks'][1]['gpu_requested'],'L40S')
 def test_plan_no_estimated_cost(self):self.assertEqual(compile_recipe(self.recipe)['estimated_gpu_cost_usd'],'NOT_ESTIMATED_UNTIL_MEASURED')
 def test_gltf_has_shared_meshes(self):
  g=gltf_for([{**x,'recipe':'fixture'} for x in self.recipe['instances']]);self.assertEqual(len(g['nodes']),8);self.assertEqual(len(g['meshes']),5)
  buildings=[x for x in g['nodes'] if x['name'].startswith('building/')];self.assertEqual(len(set(x['mesh'] for x in buildings)),1)
 def test_gltf_buffer(self):
  g=gltf_for([{**x,'recipe':'fixture'} for x in self.recipe['instances']]);raw=base64.b64decode(g['buffers'][0]['uri'].split(',',1)[1]);self.assertEqual(len(raw),g['buffers'][0]['byteLength'])
 def test_scene_output_is_repeatable(self):
  with tempfile.TemporaryDirectory() as d:
   a=export_cell(self.recipe,d);b=export_cell(self.recipe,d)
   self.assertEqual(a['receipt'],b['receipt']);self.assertTrue(verify_export(a['artifact_dir']))
 def test_cache_key_changes_when_placement_changes(self):
  r=deepcopy(self.recipe);r['instances'][0]['position'][0]+=2
  self.assertNotEqual(compile_recipe(r)['source_digest'],compile_recipe(self.recipe)['source_digest'])
 def test_bad_target(self):
  self.recipe['renderer']='unknown';self.assertRaises(ValueError,compile_recipe,self.recipe)
 def test_unbounded_objects_rejected(self):
  self.recipe['instances']*=200;self.assertRaises(ValueError,compile_recipe,self.recipe)
 def test_invalid_kind(self):
  self.recipe['instances'][0]['kind']='shell';self.assertRaises(ValueError,compile_recipe,self.recipe)
 def test_duplicate_ids(self):
  self.recipe['instances'][1]['id']=self.recipe['instances'][0]['id'];self.assertRaises(ValueError,compile_recipe,self.recipe)
 def test_negative_size_rejected(self):
  self.recipe['instances'][1]['scale'][0]=-1;self.assertRaises(ValueError,compile_recipe,self.recipe)
 def test_tamper_detection(self):
  with tempfile.TemporaryDirectory() as d:
   a=export_cell(self.recipe,d);Path(a['gltf_path']).write_text('tampered');self.assertFalse(verify_export(a['artifact_dir']))
 def test_bad_schema(self):
  self.recipe['schema']='other';self.assertRaises(ValueError,compile_recipe,self.recipe)
 def test_local_gpu_stays_zero(self):
  with tempfile.TemporaryDirectory() as d:self.assertEqual(export_cell(self.recipe,d)['receipt']['gpu_hours'],0)
if __name__=='__main__':unittest.main()
