"""GLASS Render Foundry ORA 0.1 — zero-GPU-cost deterministic world-cell compiler.

The local stage generates real reusable glTF mesh instances. Photorealistic
Blender/Modal baking remains a typed, unexecuted provider-dependent job plan.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import argparse, base64, json, math, os, struct

ORA_ID = 'ora-render-foundry'
VERSION = 'glass.render-foundry/0.1'
KINDS = ('building','road','plaza','water','lamp')
PASSES = ('beauty','albedo','normal','linear-depth','roughness','emission','object-id')
GPU_PRESETS = {'preview-cpu': {'requires_gpu': False, 'target':'cpu'},
               'bake-l4': {'requires_gpu': True, 'target':'L4'},
               'bake-l40s': {'requires_gpu': True, 'target':'L40S'}}


def canonical(v): return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
def digest(v): return sha256(canonical(v).encode('utf-8')).hexdigest()


def box_mesh():
    # Twelve triangles, 24 vertices (separate faces). Tile templates share this geometry.
    faces=[([(-.5,-.5,.5),(.5,-.5,.5),(.5,.5,.5),(-.5,.5,.5)],(0,0,1)),
           ([(.5,-.5,-.5),(-.5,-.5,-.5),(-.5,.5,-.5),(.5,.5,-.5)],(0,0,-1)),
           ([(-.5,.5,.5),(.5,.5,.5),(.5,.5,-.5),(-.5,.5,-.5)],(0,1,0)),
           ([(-.5,-.5,-.5),(.5,-.5,-.5),(.5,-.5,.5),(-.5,-.5,.5)],(0,-1,0)),
           ([(.5,-.5,.5),(.5,-.5,-.5),(.5,.5,-.5),(.5,.5,.5)],(1,0,0)),
           ([(-.5,-.5,-.5),(-.5,-.5,.5),(-.5,.5,.5),(-.5,.5,-.5)],(-1,0,0))]
    v=[];norm=[];ind=[]
    for poly,normal in faces:
        p=len(v);v.extend(poly);norm.extend([normal]*4);ind.extend([p,p+1,p+2,p,p+2,p+3])
    return v,norm,ind


def gltf_for(instances):
    """A valid glTF 2.0 with one shared geometry and multiple spatial instances."""
    positions,normals,indices=box_mesh()
    buf=bytearray();views=[];accessors=[]
    def append(data,fmt,target,component,count,typ,mins=None,maxs=None):
        start=len(buf)
        for item in data:
            seq=item if isinstance(item,(tuple,list)) else (item,)
            buf.extend(struct.pack('<'+fmt,*seq))
        while len(buf)%4: buf.append(0)
        v={'buffer':0,'byteOffset':start,'byteLength':len(buf)-start,'target':target}
        views.append(v)
        a={'bufferView':len(views)-1,'componentType':component,'count':count,'type':typ}
        if mins is not None:a['min']=mins;a['max']=maxs
        accessors.append(a)
        return len(accessors)-1
    pos=append(positions,'fff',34962,5126,len(positions),'VEC3',[-.5,-.5,-.5],[.5,.5,.5])
    norm=append(normals,'fff',34962,5126,len(normals),'VEC3')
    ix=append(indices,'H',34963,5123,len(indices),'SCALAR')
    colors={'building':[.18,.26,.36,1],'road':[.22,.23,.31,1], 'plaza':[.36,.3,.27,1],
            'water':[.035,.13,.24,1],'lamp':[.95,.63,.3,1]}
    materials=[{'name':'glass.cell.'+k,'pbrMetallicRoughness':{'baseColorFactor':v,'metallicFactor':.05,'roughnessFactor':.62},
                'doubleSided':False} for k,v in colors.items()]
    mesh=[{'name':'shared.box/'+k,'primitives':[{'attributes':{'POSITION':pos,'NORMAL':norm},'indices':ix,'material':i}]} for i,k in enumerate(colors)]
    nodes=[]
    for j,item in enumerate(instances):
        kind=item['kind']
        x,y,z=item['position'];w,h,d=item['scale']
        nodes.append({'name':f"{kind}/{j:04d}", 'mesh':KINDS.index(kind),
                      'translation':[x,y,z],'scale':[w,h,d],
                      'extras':{'instance_id':item['id'],'source_recipe':item['recipe']}})
    return {'asset':{'version':'2.0','generator':VERSION},'scene':0,'scenes':[{'nodes':list(range(len(nodes)))}],
            'nodes':nodes,'meshes':mesh,'materials':materials,
            'buffers':[{'uri':'data:application/octet-stream;base64,'+base64.b64encode(buf).decode(), 'byteLength':len(buf)}],
            'bufferViews':views,'accessors':accessors,
            'extras':{'truth':'PROCEDURAL_BASE_GEOMETRY_NO_CLOUD_BAKE','instancing':'One mesh template per kind, reused by nodes'}}


def validate_recipe(r):
    if not isinstance(r,dict) or r.get('schema')!=VERSION:raise ValueError('unsupported recipe schema')
    if not isinstance(r.get('cell_id'),str) or not 1<=len(r['cell_id'])<=100:raise ValueError('invalid cell ID')
    if not isinstance(r.get('seed'),int) or type(r['seed']) is bool or r['seed']<0 or r['seed']>=2**64:raise ValueError('bad seed')
    if r.get('renderer') not in GPU_PRESETS:raise ValueError('unknown GPU target')
    inst=r.get('instances')
    if not isinstance(inst,list) or not 1<=len(inst)<=1000:raise ValueError('1..1000 instances required')
    ids=set()
    for obj in inst:
        if not isinstance(obj,dict) or obj.get('kind') not in KINDS:raise ValueError('unknown instance kind')
        if not isinstance(obj.get('id'),str) or not obj['id'] or obj['id'] in ids:raise ValueError('invalid or duplicate instance ID')
        ids.add(obj['id'])
        for field in ('position','scale'):
            v=obj.get(field)
            if not isinstance(v,list) or len(v)!=3 or any(type(n) not in (int,float) or not math.isfinite(n) for n in v):raise ValueError('invalid spatial vector')
        if any(n<=0 or n>1000 for n in obj['scale']):raise ValueError('invalid scale')
    return inst


def compile_recipe(r):
    instances=validate_recipe(r)
    canonical_input=digest(r)
    gpu=GPU_PRESETS[r['renderer']]
    tasks=[{'kind':'export-base-gltf','status':'AVAILABLE_LOCAL','input_hash':canonical_input,'output_format':'glTF2'},
           {'kind':'build-cinematic-passes','status':'UNIMPLEMENTED_PROVIDER_ADAPTER' if gpu['requires_gpu'] else 'OPTIONAL',
            'gpu_requested':gpu['target'],'passes':PASSES},
           {'kind':'package-content-addressed-cache','status':'AVAILABLE_LOCAL','key':canonical_input},
           {'kind':'runtime-materialization','status':'CONSUMER_REQUIRED','consumers':['ORASPACE','HOMELESS','WORLDOS']}]
    plan={'ora_id':ORA_ID,'schema':VERSION,'kind':'RENDER_FOUNDRY_MISSION','state':'PREPARED_NOT_EXECUTED',
          'cell_id':r['cell_id'],'source_digest':canonical_input,'instances':len(instances),
          'unique_meshes':len(set(x['kind'] for x in instances)), 'tasks':tasks,
          'estimated_gpu_cost_usd':'NOT_ESTIMATED_UNTIL_MEASURED','provider':'NONE_CONNECTED',
          'truth':'COMPUTATIONAL_PROPOSAL'}
    plan['plan_digest']=digest(plan)
    return plan


def export_cell(r,root):
    plan=compile_recipe(r);root=Path(root)
    out=root/plan['source_digest'][:2]/plan['source_digest']
    out.mkdir(parents=True,exist_ok=True)
    scene=out/'world-cell.gltf';manifest=out/'receipt.json'
    # Build bytes deterministically; contents are idempotent and hash-verifiable.
    gltf=gltf_for([{**item,'recipe':plan['source_digest']} for item in r['instances']])
    serialized=canonical(gltf).encode('utf-8')
    if scene.exists() and scene.read_bytes()!=serialized:
        raise ValueError('content-addressed cache collision or corruption')
    scene.write_bytes(serialized)
    receipt={'schema':VERSION,'ora_id':ORA_ID,'cell_id':r['cell_id'],'source_digest':plan['source_digest'],
             'gltf_sha256':sha256(serialized).hexdigest(),'mesh_instances':len(r['instances']),
             'mesh_templates':len(set(x['kind'] for x in r['instances'])), 'gpu_hours':0,
             'claim':'PROCEDURAL_LOW_POLY_GEOMETRY_ONLY','plan_digest':plan['plan_digest']}
    receipt['receipt_digest']=digest(receipt)
    manifest.write_text(canonical(receipt)+'\n',encoding='utf-8')
    return {'artifact_dir':str(out),'gltf_path':str(scene),'receipt_path':str(manifest),'receipt':receipt}


def verify_export(folder):
    folder=Path(folder)
    r=json.loads((folder/'receipt.json').read_text(encoding='utf-8'))
    d=dict(r);check=d.pop('receipt_digest',None)
    return (check==digest(d) and sha256((folder/'world-cell.gltf').read_bytes()).hexdigest()==r['gltf_sha256'])


def manifest():
    return {'id':ORA_ID,'name':'GLASS Render Foundry ORA','parent':'ora-sovereign','type':'ORA_CAPABILITY_PACKAGE',
     'schema':VERSION,'life':'PROPOSED_RESEARCH_PACKAGE','capabilities':{
        'render.plan':{'effect':'PURE','implemented':True},
        'render.cell.generate':{'effect':'LOCAL_WRITE','implemented':True},
        'render.cache.verify':{'effect':'LOCAL_READ','implemented':True},
        'render.gpu.bake':{'effect':'CLOUD_GPU','implemented':False,'requires':'provider adapter, credentials, explicit budget and cost guard'},
        'render.stream':{'effect':'NETWORK','implemented':False}},
      'outputs':['glTF2 instance graph','content-addressed receipts','GPU bake proposals'],
      'consumers':['ORA Space','HOMELESS','World OS','Space OS'],
      'scope':'TESTED_OFFLINE_REFERENCE_NOT_ADMITTED_TO_ORA_PRODUCTION'}


def main():
    p=argparse.ArgumentParser(description='GLASS Render Foundry ORA · typed model-free cell compiler')
    p.add_argument('command',choices=['manifest','plan','build','verify'])
    p.add_argument('--recipe',type=Path);p.add_argument('--output',type=Path,default=Path('render-cache'))
    args=p.parse_args()
    if args.command=='manifest':result=manifest()
    elif args.command=='verify':result={'valid':verify_export(args.output)}
    else:
        if not args.recipe:raise SystemExit('--recipe required')
        r=json.loads(args.recipe.read_text(encoding='utf-8'))
        result=compile_recipe(r) if args.command=='plan' else export_cell(r,args.output)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
