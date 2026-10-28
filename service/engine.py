"""Persistent ORA service: bounded, model-free missions, explicit authority, verifiable ledger."""
from __future__ import annotations
import contextlib, datetime, hashlib, json, os, queue, re, sqlite3, threading, time, unicodedata, uuid
from pathlib import Path
from .native import NativeKernel

ROOT=Path(__file__).resolve().parents[1]
CAPABILITIES={
 'language.inspect':{'effect':'PURE','oracle':'language','supported':True,'description':'Script and token inspection of supplied text'},
 'article.structure':{'effect':'PURE','oracle':'wikipedia','supported':True,'description':'Outline and citation-like markers in supplied article text'},
 'scene.generate':{'effect':'PURE','oracle':'surface','supported':True,'description':'Seeded celestial scene manifest via C++ SDK'},
 'grammar.propose':{'effect':'LOCAL_PROPOSAL','oracle':'unison','supported':True,'description':'Generate a candidate lexical grammar; never auto-admit'},
 'clock.sample':{'effect':'OBSERVE','oracle':'clock','supported':True,'description':'Timestamped system-clock sample; explicitly nondeterministic'},
 'ora.delegate':{'effect':'GOVERNED','oracle':'parent','supported':True,'description':'Propose a subordinate ORA with attenuated grants'},
 'wiki.fetch':{'effect':'NETWORK','oracle':'wikipedia','supported':False,'description':'Future licensed Wikipedia retrieval (no fetch in v0.2)'},
 'browser.navigate':{'effect':'NETWORK','oracle':'browser','supported':False,'description':'Future authorized browser adapter'},
 'music.compose':{'effect':'MODEL_OR_DSP','oracle':'music','supported':False,'description':'Future original-score synthesis'},
 'model.text':{'effect':'OPTIONAL_MODEL','oracle':'models','supported':False,'description':'Optional model adapter, not installed'},
}
KEYWORDS=[('language.inspect',r'\blanguage\b|\btranslate\b|\barabic\b|\bgreek\b|\bmorpholog|\bscript\b'),
 ('article.structure',r'\bwikipedia\b|\barticle\b|\bencycloped'),
 ('scene.generate',r'\bsky\b|\bstars?\b|\bconstellations?\b|\bwaterfront\b|\bscene\b'),
 ('grammar.propose',r'\bgrammar\b|\bgenerator\b|\bcompiler\b|\bpattern\b'),
 ('clock.sample',r'\bclock\b|\btime\b'),
 ('wiki.fetch',r'\bfetch\b.*\bwikipedia\b|\bretrieve\b.*\bwikipedia\b'),
 ('browser.navigate',r'\bbrowser\b|\bnavigate\b.*\bsite\b'),
 ('music.compose',r'\bmusic\b|\bsong\b|\bpiano\b'),
 ('model.text',r'\bllm\b|\btext model\b')]
CORE_TOWER=[
 ('observation','Bit, symbol, event, source and tick; evidence must declare what was observed.'),
 ('letter','Typed glyph and letter inventories, scripts, encodings, alphabets.'),
 ('form','Morphological, structural and typed forms; declared transformations.'),
 ('grammar','Productions, syntax, schemas, semantic invariants, lexers.'),
 ('operator','Typed computation: arity, effects, preconditions, postconditions.'),
 ('compiler','Source to AST to typed IR to executable or proposal; no hidden claims.'),
 ('machine','Orthogonal finite state regions, guarded transitions, clock and replay.'),
 ('generator','Grammar-derived artifacts, candidate operators, generators of generators.'),
 ('oracle','Domain knowledge, tools, evidence and explicit limits.'),
 ('orb','Versioned and portable admitted capability bundle.'),
 ('ora','Identity, delegated grants, missions, workers and continuity.'),
 ('sovereign','Tenant-level ORA governor; cannot exceed owner permissions.')]
VERBS={'START','SWITCH','WRITE','COMMIT','BUILD','TALK','PERTURB','WITNESS'}
LIFECYCLE={'PROPOSED':{'review':'READY','stop':'STOPPED'},
 'READY':{'activate':'RUNNING','stop':'STOPPED'},
 'RUNNING':{'pause':'PAUSED','stop':'STOPPED'},
 'PAUSED':{'resume':'RUNNING','stop':'STOPPED'},'STOPPED':{}}
PRIME='ora-sovereign'
def canon(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def sha(x):return hashlib.sha256(canon(x).encode('utf-8')).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='milliseconds')
def slug(x):return re.sub(r'[^a-z0-9]+','-',x.casefold()).strip('-')[:54] or 'new-ora'
def guess(goal):
    hits=sorted({key for key,pattern in KEYWORDS if re.search(pattern,goal,re.IGNORECASE)})
    return hits

def language_inspect(text):
    if not isinstance(text,str) or len(text)>200000:raise ValueError('text must be a string <=200000 characters')
    tokens=re.findall(r'\w+',text,flags=re.UNICODE)
    scripts={'Arabic':0,'Greek':0,'Latin':0,'Other':0}
    for ch in text:
        if not ch.isalpha():continue
        name=unicodedata.name(ch,'')
        script='Arabic' if 'ARABIC' in name else 'Greek' if 'GREEK' in name else 'Latin' if 'LATIN' in name else 'Other'
        scripts[script]+=1
    return {'grammar':'language.inspect/0.2','type':'FORMAL_TEXT_INSPECTION',
      'bytes':len(text.encode('utf-8')),'characters':len(text),'token_count':len(tokens),
      'unique_tokens':len(set(x.casefold() for x in tokens)), 'scripts':scripts,'source_sha256':hashlib.sha256(text.encode()).hexdigest(),
      'limitations':['No semantic interpretation','No full Arabic morphology','No automatic translation']}
def article_structure(text):
    if not isinstance(text,str) or len(text)>200000:raise ValueError('text must be a string <=200000 characters')
    headings=[]
    for line_no,line in enumerate(text.splitlines(),1):
        m=re.match(r'^\s*(#{1,6})\s+(.+?)\s*$',line)
        w=re.match(r'^\s*(={2,6})\s*(.+?)\s*=+\s*$',line)
        if m:headings.append({'line':line_no,'level':len(m.group(1)),'title':m.group(2)[:120]})
        elif w:headings.append({'line':line_no,'level':len(w.group(1)),'title':w.group(2)[:120]})
    targets=sorted(set(re.findall(r'\[\[([^\]\|]{1,120})',text)))[:100]
    return {'grammar':'article.structure/0.2','type':'SOURCE_TEXT_STRUCTURE','headings':headings[:100],
      'wikilink_targets':targets,'source_sha256':hashlib.sha256(text.encode()).hexdigest(),
      'language':language_inspect(text)['scripts'],'limitations':['Text supplied by caller, not verified Wikipedia article','No fact checking']}
def grammar_propose(text):
    data=language_inspect(text)
    tokens=re.findall(r'\w+',text.casefold())
    common=sorted(set(t for t in tokens if len(t)>=3),key=lambda t:(-tokens.count(t),t))[:12]
    return {'grammar':'unison.candidate-lexical/0.2','admission':'PROPOSED_ONLY','source_sha256':data['source_sha256'],
      'candidate_rules':[{'lhs':'SIGNAL','literal':t,'output_type':'token','confidence':'UNVERIFIED'} for t in common],
      'proof_obligations':['Novelty witness','Typed unfolding','Independent fixtures','Human admission']}
def scene_python(seed,count):
    # Documented fallback when a matching native C++ shared library isn't compiled.
    import random
    r=random.Random(seed)
    return {'grammar':'surface.stars-python-fallback/0.2','seed':seed,'stars':[{'id':i,'u':r.random(),'v':r.random(),'phase':r.random()*6.283185307179586,'frequency':.2+r.random()*2.7,'amplitude':.1+r.random()*.8} for i in range(count)],'status':'FALLBACK_NOT_NATIVE'}

class Engine:
 def __init__(self,db,worker=True,native=True):
    self.db=str(db);Path(self.db).parent.mkdir(parents=True,exist_ok=True);self.lock=threading.RLock();self.native=None
    if native:
        try:self.native=NativeKernel()
        except OSError:pass
    self.jobs=queue.Queue();self.stop=threading.Event();self.thread=None
    self._init()
    if worker:
        self.thread=threading.Thread(target=self._work,daemon=True,name='ora-worker');self.thread.start()
 def _db(self):
    c=sqlite3.connect(self.db,timeout=8);c.row_factory=sqlite3.Row;c.execute('PRAGMA foreign_keys=ON');c.execute('PRAGMA busy_timeout=8000');return c
 @contextlib.contextmanager
 def write(self):
    with self.lock, contextlib.closing(self._db()) as c:
     try:
      c.execute('BEGIN IMMEDIATE');yield c;c.commit()
     except BaseException:
      c.rollback();raise
 def _init(self):
    with self.write() as c:
     c.executescript('''CREATE TABLE IF NOT EXISTS oras(id TEXT PRIMARY KEY,slug TEXT NOT NULL UNIQUE,name TEXT NOT NULL,goal TEXT NOT NULL,parent TEXT,grants TEXT NOT NULL,missing TEXT NOT NULL,life TEXT NOT NULL,version INT NOT NULL,created TEXT NOT NULL,updated TEXT NOT NULL,placement TEXT NOT NULL DEFAULT 'oracle');
      CREATE TABLE IF NOT EXISTS regions(ora_id TEXT NOT NULL,region TEXT NOT NULL,state TEXT NOT NULL,tick INT NOT NULL DEFAULT 0,PRIMARY KEY(ora_id,region));
      CREATE TABLE IF NOT EXISTS missions(id TEXT PRIMARY KEY,ora_id TEXT NOT NULL,kind TEXT NOT NULL,payload TEXT NOT NULL,payload_sha TEXT NOT NULL,state TEXT NOT NULL,result TEXT,error TEXT,created TEXT NOT NULL,updated TEXT NOT NULL,idem_key TEXT,UNIQUE(ora_id,idem_key));
      CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT,ora_id TEXT,kind TEXT NOT NULL,body TEXT NOT NULL,ts TEXT NOT NULL,prev TEXT NOT NULL,hash TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS proposals(id TEXT PRIMARY KEY,ora_id TEXT,kind TEXT NOT NULL,body TEXT NOT NULL,state TEXT NOT NULL,created TEXT NOT NULL);
      CREATE INDEX IF NOT EXISTS idx_events_ora ON events(ora_id,seq);''')
     if 'placement' not in [x[1] for x in c.execute('PRAGMA table_info(oras)')]:
      c.execute("ALTER TABLE oras ADD COLUMN placement TEXT NOT NULL DEFAULT 'oracle'")
     if not c.execute('SELECT 1 FROM oras WHERE id=?',(PRIME,)).fetchone():
      t=now();caps=sorted(x for x,y in CAPABILITIES.items() if y['supported']);c.execute('INSERT INTO oras(id,slug,name,goal,parent,grants,missing,life,version,created,updated,placement) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',(PRIME,'sovereign','ORA Sovereign','Govern capability composition and continuity.','',canon(caps),'[]','RUNNING',1,t,t,'oracle'))
      self._init_regions(c,PRIME,'RUNNING');self._event(c,PRIME,'ROOT_INITIALIZED',{'status':'RUNNING','caps':caps})
 def _init_regions(self,c,oid,life):
    for reg,state in [('lifecycle',life),('observation','AWAKE'),('execution','IDLE'),('authority','SCOPED'),('continuity','LOCAL')]:
     c.execute('INSERT INTO regions(ora_id,region,state) VALUES (?,?,?)',(oid,reg,state))
 def _event(self,c,ora,kind,body):
    x=c.execute('SELECT hash FROM events ORDER BY seq DESC LIMIT 1').fetchone();prev=x['hash'] if x else '0'*64
    ts=now();base={'ora':ora,'kind':kind,'body':body,'ts':ts,'prev':prev};h=sha(base)
    c.execute('INSERT INTO events(ora_id,kind,body,ts,prev,hash) VALUES (?,?,?,?,?,?)',(ora,kind,canon(body),ts,prev,h));return h
 def verify(self):
    with contextlib.closing(self._db()) as c:
     prev='0'*64
     for e in c.execute('SELECT * FROM events ORDER BY seq'):
      base={'ora':e['ora_id'],'kind':e['kind'],'body':json.loads(e['body']),'ts':e['ts'],'prev':prev}
      if e['prev']!=prev or e['hash']!=sha(base):return False
      prev=e['hash']
    return True
 def event_stream(self,after=0,limit=100):
    with contextlib.closing(self._db()) as c:return [self._event_view(x) for x in c.execute('SELECT * FROM events WHERE seq>? ORDER BY seq LIMIT ?',(after,limit))]
 def _event_view(self,r):return {'seq':r['seq'],'ora':r['ora_id'],'kind':r['kind'],'body':json.loads(r['body']),'ts':r['ts'],'hash':r['hash']}
 def tower(self):return {'name':'GLASS Tower','version':'ora.glass-tower/0.2','levels':[{'index':i,'name':a,'function':b} for i,(a,b) in enumerate(CORE_TOWER)]}
 def _view(self,c,row):
    data=dict(row);data['grants']=json.loads(data['grants']);data['missing']=json.loads(data['missing']);data['regions']={r['region']:{'state':r['state'],'tick':r['tick']} for r in c.execute('SELECT * FROM regions WHERE ora_id=?',(data['id'],))}
    data['url_path']='/o/'+data['id'];return data
 def get(self,oid):
    with contextlib.closing(self._db()) as c:
     row=c.execute('SELECT * FROM oras WHERE id=?',(oid,)).fetchone();return self._view(c,row) if row else None
 def list(self):
    with contextlib.closing(self._db()) as c:return [self._view(c,x) for x in c.execute('SELECT * FROM oras ORDER BY created, id LIMIT 150')]
 def create(self,name,goal,parent=PRIME,grants=None,placement='oracle'):
    if not isinstance(goal,str) or not 5<=len(goal)<=4000:raise ValueError('goal must be 5..4000 characters')
    if not isinstance(name,str) or len(name)>100:raise ValueError('name must be <=100 characters')
    if not re.fullmatch(r'ora-[a-z0-9-]{4,72}',parent):raise ValueError('invalid parent id')
    if placement not in ('oracle','android','homeless'):raise ValueError('invalid placement intent')
    inferred=guess(goal);known=[x for x in inferred if CAPABILITIES[x]['supported']];missing=[x for x in inferred if not CAPABILITIES[x]['supported']]
    if not inferred:missing=['goal.unmapped']
    with self.write() as c:
     ancestor=c.execute('SELECT * FROM oras WHERE id=?',(parent,)).fetchone()
     if not ancestor or ancestor['life'] not in ('READY','RUNNING'):raise ValueError('parent not active')
     allowable=set(json.loads(ancestor['grants']))
     proposed=set(grants if grants is not None else known)
     if not proposed.issubset(allowable):raise PermissionError('child cannot extend parent grants')
     if not proposed.issubset(CAPABILITIES):raise ValueError('unknown capability')
     oid='ora-'+uuid.uuid4().hex[:18];nm=name.strip() or ('ORA · '+goal[:35]);base=slug(nm);t=now()
     # stable ID, unique human alias within this installation
     name_slug=base
     if c.execute('SELECT 1 FROM oras WHERE slug=?',(base,)).fetchone():name_slug=base[:40]+'-'+oid[-6:]
     c.execute('INSERT INTO oras(id,slug,name,goal,parent,grants,missing,life,version,created,updated,placement) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',(oid,name_slug,nm,goal,parent,canon(sorted(proposed)),canon(missing),'PROPOSED',1,t,t,placement))
     self._init_regions(c,oid,'PROPOSED');self._event(c,oid,'ORA_PROPOSED',{'parent':parent,'grants':sorted(proposed),'missing':missing,'placement_intent':placement,'goal_sha':sha(goal)})
    return self.get(oid)
 def transition(self,oid,action,expected_version=None):
    with self.write() as c:
     row=c.execute('SELECT * FROM oras WHERE id=?',(oid,)).fetchone()
     if not row:raise KeyError(oid)
     if oid==PRIME:raise PermissionError('Sovereign lifecycle is managed by service')
     if expected_version is not None and row['version']!=expected_version:raise ValueError('stale version')
     new=LIFECYCLE.get(row['life'],{}).get(action)
     if not new:raise ValueError(f'invalid transition from {row["life"]} via {action}')
     c.execute('UPDATE oras SET life=?,version=version+1,updated=? WHERE id=?',(new,now(),oid))
     c.execute('UPDATE regions SET state=? WHERE ora_id=? AND region=?',(new,oid,'lifecycle'))
     c.execute('UPDATE regions SET state=? WHERE ora_id=? AND region=?',('READY' if new=='RUNNING' else 'IDLE',oid,'execution'))
     self._event(c,oid,'LIFECYCLE_'+action.upper(),{'from':row['life'],'to':new,'version':row['version']+1})
    return self.get(oid)
 def submit(self,oid,kind,payload,idem=None):
    if kind not in CAPABILITIES or not CAPABILITIES[kind]['supported']:raise ValueError('capability not implemented')
    if not isinstance(payload,dict) or len(canon(payload))>240000:raise ValueError('payload must be object <= 240KB')
    if idem is not None and (not isinstance(idem,str) or not re.fullmatch(r'[a-zA-Z0-9_.-]{4,100}',idem)):raise ValueError('invalid idempotency key')
    with self.write() as c:
     row=c.execute('SELECT * FROM oras WHERE id=?',(oid,)).fetchone()
     if not row:raise KeyError(oid)
     if row['life']!='RUNNING':raise ValueError('ORA must be RUNNING')
     if kind not in json.loads(row['grants']):raise PermissionError('missing capability grant')
     ph=sha(payload)
     if idem:
      existing=c.execute('SELECT * FROM missions WHERE ora_id=? AND idem_key=?',(oid,idem)).fetchone()
      if existing:
       if existing['kind']!=kind or existing['payload_sha']!=ph:raise ValueError('idempotency conflict')
       return self._mission_view(existing)
     mid='mission-'+uuid.uuid4().hex[:20];t=now()
     c.execute('INSERT INTO missions VALUES (?,?,?,?,?,?,?,?,?,?,?)',(mid,oid,kind,canon(payload),ph,'QUEUED',None,None,t,t,idem))
     self._event(c,oid,'MISSION_QUEUED',{'mission':mid,'kind':kind,'payload_hash':ph})
    if self.thread:self.jobs.put(mid)
    return self.mission(mid)
 def _mission_view(self,r):
    d=dict(r);d['payload']=json.loads(d['payload']);d['result']=json.loads(d['result']) if d['result'] else None;return d
 def mission(self,mid):
    with contextlib.closing(self._db()) as c:
     row=c.execute('SELECT * FROM missions WHERE id=?',(mid,)).fetchone()
     return self._mission_view(row) if row else None
 def _work(self):
    while not self.stop.is_set():
     try:mid=self.jobs.get(timeout=.3)
     except queue.Empty:continue
     try:self.run_one(mid)
     finally:self.jobs.task_done()
 def run_one(self,mid):
    with self.write() as c:
     r=c.execute('SELECT * FROM missions WHERE id=?',(mid,)).fetchone()
     if not r:raise KeyError(mid)
     if r['state']!='QUEUED':return self._mission_view(r)
     c.execute('UPDATE missions SET state=?,updated=? WHERE id=?',('RUNNING',now(),mid))
     c.execute('UPDATE regions SET state=? WHERE ora_id=? AND region=?',('EXECUTING',r['ora_id'],'execution'))
     self._event(c,r['ora_id'],'MISSION_STARTED',{'mission':mid,'kind':r['kind']})
    try:
     kind=r['kind'];data=json.loads(r['payload'])
     if kind=='language.inspect':out=language_inspect(data.get('text',''))
     elif kind=='article.structure':out=article_structure(data.get('text',''))
     elif kind=='grammar.propose':out=grammar_propose(data.get('text',''))
     elif kind=='scene.generate':
      seed=data.get('seed',41729);count=data.get('count',210)
      if type(seed)!=int or not 0<=seed<2**64 or type(count)!=int or not 0<=count<=2000:raise ValueError('seed/count out of bounds')
      out=self.native.scene(seed,count) if self.native else scene_python(seed,count)
     elif kind=='clock.sample':out={'utc':now(),'truth':'OBSERVATION','repeatable':False}
     elif kind=='ora.delegate':
      # Deliberately a proposal, not a privileged subagent creation from a worker.
      goal=data.get('goal','');out={'status':'NEEDS_OWNER_REVIEW','goal':goal[:300],'note':'Call explicit authenticated POST /api/v1/oras with parent and attenuated grants.'}
     else:raise ValueError('unsupported mission')
     status='SUCCEEDED';err=None
    except Exception as e:status='FAILED';out=None;err=str(e)[:280]
    with self.write() as c:
     c.execute('UPDATE missions SET state=?,result=?,error=?,updated=? WHERE id=?',(status,canon(out) if out is not None else None,err,now(),mid))
     c.execute('UPDATE regions SET state=? WHERE ora_id=? AND region=?',('READY',r['ora_id'],'execution'))
     self._event(c,r['ora_id'],'MISSION_'+status,{'mission':mid,'result_sha':sha(out) if out is not None else None,'error':err})
    return self.mission(mid)
 def observe(self,kind,ora_id=PRIME,goal=''):
    """Event-listener finite machine. Can propose children, never self-admit or self-launch."""
    if kind=='CAPABILITY_GAP':
      if not isinstance(goal,str) or len(goal)<5:raise ValueError('goal required for capability gap')
      proposal=self.create('Gap · '+goal[:45],goal,parent=ora_id)
      with self.write() as c:self._event(c,ora_id,'LISTENER_PROPOSED_CHILD',{'trigger':kind,'child':proposal['id']})
      return {'status':'PROPOSED','child':proposal['id'],'trigger':kind}
    if kind not in ('NETWORK_DISCONNECTED','NETWORK_RECONNECTED'):raise ValueError('unsupported listener event')
    state={'NETWORK_DISCONNECTED':'OFFLINE','NETWORK_RECONNECTED':'CONNECTED'}[kind]
    with self.write() as c:
      if not c.execute('SELECT 1 FROM oras WHERE id=?',(ora_id,)).fetchone():raise KeyError(ora_id)
      c.execute('UPDATE regions SET state=? WHERE ora_id=? AND region=?',(state,ora_id,'continuity'))
      self._event(c,ora_id,'CONTINUITY_TRANSITION',{'event':kind,'to':state,'note':'logical state only; no live synchronization performed'})
    return {'status':state,'ora':ora_id}
 def shutdown(self):
    self.stop.set()
    if self.thread:self.thread.join(timeout=2)


def compile_path(path):
    """Pure PURL-compatible path compiler. This function never touches storage or tools."""
    if len(path)>1024:raise ValueError('path too large')
    seg=path.split('/')
    if len(seg)!=10 or seg[0]!='' or seg[1]!='o' or seg[3:6]!=['purl','v1','shift'] or seg[7]!='input' or seg[9]!='preview':raise ValueError('invalid URL program grammar')
    oid,verb,ref=seg[2],seg[6],seg[8]
    if not re.fullmatch(r'ora-[a-z0-9-]{4,72}',oid):raise ValueError('invalid ORA id')
    if verb not in VERBS:raise ValueError('unknown ORA verb')
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,96}',ref):raise ValueError('invalid reference')
    return {'protocol':'ora-purl/0.2','ora_id':oid,'verb':verb,'input_ref':ref,'effect':'PREVIEW_ONLY','requires_authorized_commit':True,'program_hash':sha({'id':oid,'verb':verb,'ref':ref})}
