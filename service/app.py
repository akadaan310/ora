#!/usr/bin/env python3
"""HTTP launch surface for ORA Engine. Loopback by default; remote requires trusted reverse proxy/auth."""
import argparse, contextlib, hmac, json, os, re, threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
from .engine import Engine, PRIME, CAPABILITIES, compile_path

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_WEB=ROOT.parent/'ORASPACE'/'web'
class APIServer(ThreadingHTTPServer):
    daemon_threads=True
    def __init__(self,address,engine,web,token):
        self.engine=engine;self.web=Path(web);self.token=token
        super().__init__(address,Handler)
class Handler(BaseHTTPRequestHandler):
    server_version='ORA/0.2'
    def log_message(self,format,*args):pass
    def reply(self,status,value):
        blob=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(blob)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','no-referrer')
        self.end_headers();self.wfile.write(blob)
    def authorized(self):
        if not self.server.token:return True # loopback development only; enforced by serve()
        header=self.headers.get('Authorization','')
        return hmac.compare_digest(header,'Bearer '+self.server.token)
    def require_auth(self):
        if not self.authorized():self.reply(401,{'error':'AUTH_REQUIRED','message':'Pass an owner-provided Bearer token over HTTPS.'});return False
        return True
    def do_GET(self):
        u=urlsplit(self.path);p=u.path;eng=self.server.engine
        if p in ('/','/index.html'):
            page=(self.server.web/'index.html')
            if not page.is_file():return self.reply(404,{'error':'web app not installed'})
            blob=page.read_bytes();self.send_response(200)
            for k,v in [('Content-Type','text/html; charset=utf-8'),('Content-Length',str(len(blob))),('X-Content-Type-Options','nosniff'),('Cache-Control','no-store'),('Referrer-Policy','no-referrer'),('Content-Security-Policy',"default-src 'self'; img-src 'self' data:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; base-uri 'none'; object-src 'none'; form-action 'self'")]:self.send_header(k,v)
            self.end_headers();self.wfile.write(blob);return
        if p=='/api/v1/health':return self.reply(200,{'ok':True,'service':'ORA Engine','version':'0.2','mode':'LOCAL_OR_AUTHENTICATED','native_cpp':eng.native is not None,'ledger_valid':eng.verify(),'deployment':'REFERENCE_SERVER'})
        if p in ('/.well-known/ora.json','/.well-known/ora'):
            return self.reply(200,{'protocol':'ora-purl/0.2','name':'ORA Space','root':PRIME,'verbs':sorted(['START','SWITCH','WRITE','COMMIT','BUILD','TALK','PERTURB','WITNESS']),'read_only_navigation':True,'preview_template':'/o/{ora_id}/purl/v1/shift/{verb}/input/{opaque_ref}/preview','execution':'Separate owner-authenticated API mutation required','version':'0.2'})
        if p=='/api/v1/tower':return self.reply(200,eng.tower())
        if p=='/api/v1/capabilities':return self.reply(200,{'capabilities':CAPABILITIES})
        if p=='/api/v1/catalog':
            x=json.loads((ROOT/'catalog'/'160_candidates.json').read_text());defs=x.get('ora_definitions',[])
            try:offset=min(150,max(0,int(parse_qs(u.query).get('offset',['0'])[0])));limit=min(30,max(1,int(parse_qs(u.query).get('limit',['12'])[0])))
            except ValueError:return self.reply(400,{'error':'invalid pagination'})
            return self.reply(200,{'count':len(defs),'status':'CANDIDATES_ONLY','results':defs[offset:offset+limit]})
        m=re.fullmatch(r'/o/(ora-[a-z0-9-]{4,72})',p)
        if m:
            a=eng.get(m.group(1))
            return self.reply(200,{'id':a['id'],'name':a['name'],'life':a['life'],'protocol':'ora-purl/0.2','manifest':p+'/manifest','private_goal':'REDACTED'}) if a else self.reply(404,{'error':'ORA_NOT_FOUND'})
        m=re.fullmatch(r'/o/(ora-[a-z0-9-]{4,72})/manifest',p)
        if m:
            a=eng.get(m.group(1))
            if not a:return self.reply(404,{'error':'ORA_NOT_FOUND'})
            return self.reply(200,{'schema':'ora.public-manifest/0.2','id':a['id'],'name':a['name'],'status':a['life'],'capability_contracts':a['grants'],'private_fields':'REDACTED','continuity':p.replace('/manifest',''),'model_requirement':'NONE'})
        if '/purl/v1/shift/' in p:
            try:
                result=compile_path(p)
                if not eng.get(result['ora_id']):return self.reply(404,{'error':'ORA_NOT_FOUND'})
                return self.reply(200,result)
            except ValueError as e:return self.reply(422,{'error':'INVALID_PROGRAM','detail':str(e)})
        if p.startswith('/api/v1/'):
            if not self.require_auth():return
            if p=='/api/v1/oras':return self.reply(200,{'oras':eng.list()})
            if p=='/api/v1/events':
                try:after=max(0,int(parse_qs(u.query).get('after',['0'])[0]))
                except ValueError:return self.reply(400,{'error':'invalid sequence'})
                return self.reply(200,{'events':eng.event_stream(after,100),'chain_valid':eng.verify()})
            m=re.fullmatch(r'/api/v1/oras/(ora-[a-z0-9-]{4,72})',p)
            if m:
                a=eng.get(m.group(1));return self.reply(200,{'ora':a}) if a else self.reply(404,{'error':'ORA_NOT_FOUND'})
            m=re.fullmatch(r'/api/v1/missions/(mission-[a-z0-9]{20})',p)
            if m:
                a=eng.mission(m.group(1));return self.reply(200,{'mission':a}) if a else self.reply(404,{'error':'MISSION_NOT_FOUND'})
        return self.reply(404,{'error':'NOT_FOUND'})
    def do_POST(self):
        p=urlsplit(self.path).path;eng=self.server.engine
        if not p.startswith('/api/v1/'):return self.reply(404,{'error':'NOT_FOUND'})
        if not self.require_auth():return
        origin=self.headers.get('Origin')
        if origin:
            # Basic same-origin check. Production additionally requires HTTPS reverse-proxy policy.
            try:
                origin_host=urlsplit(origin).netloc.casefold();host=self.headers.get('Host','').casefold()
            except ValueError:return self.reply(403,{'error':'origin invalid'})
            if origin_host!=host:return self.reply(403,{'error':'cross-origin writes forbidden'})
        if self.headers.get('Content-Type','').split(';',1)[0].strip()!='application/json':return self.reply(415,{'error':'application/json required'})
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 1<=size<=245760:return self.reply(413,{'error':'payload must be 1..245760 bytes'})
            doc=json.loads(self.rfile.read(size))
            if not isinstance(doc,dict):return self.reply(422,{'error':'expected JSON object'})
            if p=='/api/v1/observe':
                return self.reply(202,{'observation':eng.observe(doc.get('event',''),doc.get('ora_id',PRIME),doc.get('goal',''))})
            if p=='/api/v1/oras':
                a=eng.create(doc.get('name',''),doc.get('goal',''),doc.get('parent',PRIME),doc.get('grants'),doc.get('placement','oracle'))
                return self.reply(201,{'ora':a})
            m=re.fullmatch(r'/api/v1/oras/(ora-[a-z0-9-]{4,72})/transition',p)
            if m:
                a=eng.transition(m.group(1),doc.get('action',''),doc.get('expected_version'))
                return self.reply(200,{'ora':a})
            m=re.fullmatch(r'/api/v1/oras/(ora-[a-z0-9-]{4,72})/missions',p)
            if m:
                x=eng.submit(m.group(1),doc.get('kind',''),doc.get('payload',{}),self.headers.get('Idempotency-Key'))
                return self.reply(202,{'mission':x})
            return self.reply(404,{'error':'NOT_FOUND'})
        except PermissionError as e:return self.reply(403,{'error':'DENIED','detail':str(e)})
        except KeyError as e:return self.reply(404,{'error':'NOT_FOUND','detail':str(e)})
        except (ValueError,TypeError,json.JSONDecodeError) as e:return self.reply(422,{'error':'INVALID_REQUEST','detail':str(e)})

def serve(host,port,db,web):
    token=os.environ.get('ORA_ADMIN_TOKEN')
    if host not in ('127.0.0.1','::1','localhost') and (not token or len(token)<32):
        raise SystemExit('Non-loopback binding requires ORA_ADMIN_TOKEN of at least 32 characters, plus an external TLS reverse proxy.')
    engine=Engine(db,worker=True)
    # Requeue durable jobs from a prior stopped service, preserving idempotent mission IDs.
    with contextlib.closing(engine._db()) as c:
        pending=[r[0] for r in c.execute("SELECT id FROM missions WHERE state='QUEUED' ORDER BY created")]
    for mid in pending:engine.jobs.put(mid)
    server=APIServer((host,port),engine,web,token)
    print(f'ORA 0.2 ready on http://{host}:{port}; C++={engine.native is not None}; auth={bool(token)}',flush=True)
    try:server.serve_forever(poll_interval=.2)
    except KeyboardInterrupt:pass
    finally:server.server_close();engine.shutdown()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--host',default='127.0.0.1');parser.add_argument('--port',type=int,default=8767)
    parser.add_argument('--db',default=str(ROOT/'data'/'ora.sqlite3'));parser.add_argument('--web',default=str(DEFAULT_WEB))
    args=parser.parse_args();serve(args.host,args.port,args.db,args.web)
if __name__=='__main__':main()
