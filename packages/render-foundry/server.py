"""Optional loopback HTTP endpoint for the GLASS Render Foundry ORA.

No public cloud, authentication provider, or Modal integration. Do not expose
on a public interface without a trusted HTTPS reverse proxy and user auth.
"""
import argparse, hmac, json, os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from render_foundry import manifest, compile_recipe, export_cell, verify_export


class Server(ThreadingHTTPServer):
    daemon_threads = True
    def __init__(self, address, cache_dir, token):
        self.cache_dir = Path(cache_dir)
        self.token = token
        super().__init__(address, Handler)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):pass
    def send_json(self, code, data):
        blob=json.dumps(data,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
        self.send_response(code)
        for name,value in [('Content-Type','application/json; charset=utf-8'),('Content-Length',str(len(blob))),
            ('Cache-Control','no-store'),('X-Content-Type-Options','nosniff')]:self.send_header(name,value)
        self.end_headers();self.wfile.write(blob)
    def do_GET(self):
        if self.path in ('/health','/api/v1/render-foundry/health'):
            return self.send_json(200,{'ok':True,'ora_id':'ora-render-foundry','cloud_gpu_connected':False,'local_geometry':True})
        if self.path=='/o/ora-render-foundry/manifest':return self.send_json(200,manifest())
        return self.send_json(404,{'error':'NOT_FOUND'})
    def do_POST(self):
        if self.path not in ('/api/v1/render-foundry/plan','/api/v1/render-foundry/build'):
            return self.send_json(404,{'error':'NOT_FOUND'})
        if self.server.token and not hmac.compare_digest(self.headers.get('Authorization',''),'Bearer '+self.server.token):
            return self.send_json(401,{'error':'AUTH_REQUIRED'})
        # Cross-origin writes aren't permitted; a remote deployment additionally needs TLS/session policy.
        origin=self.headers.get('Origin')
        if origin:
            from urllib.parse import urlsplit
            if urlsplit(origin).netloc!=self.headers.get('Host',''):
                return self.send_json(403,{'error':'WRONG_ORIGIN'})
        if self.headers.get('Content-Type','').split(';')[0].strip()!='application/json':
            return self.send_json(415,{'error':'EXPECTED_JSON'})
        try:
            size=int(self.headers.get('Content-Length','0'))
            if size<2 or size>180000:return self.send_json(413,{'error':'PAYLOAD_LIMIT'})
            spec=json.loads(self.rfile.read(size))
            if self.path.endswith('/plan'):return self.send_json(200,{'plan':compile_recipe(spec)})
            return self.send_json(201,{'result':export_cell(spec,self.server.cache_dir)})
        except (TypeError,ValueError,json.JSONDecodeError) as e:
            return self.send_json(422,{'error':'INVALID_RECIPE','detail':str(e)[:250]})


def serve(host='127.0.0.1',port=8877,cache_dir='render-cache',token=None):
    if host not in ('127.0.0.1','localhost','::1') and (not token or len(token)<32):
        raise ValueError('Non-loopback requires a 32+ character token and a trusted HTTPS reverse proxy')
    with Server((host,port),cache_dir,token) as server:
        print(f'RENDER FOUNDRY ORA http://{host}:{server.server_port}/o/ora-render-foundry/manifest',flush=True)
        server.serve_forever(poll_interval=.1)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--host',default='127.0.0.1');p.add_argument('--port',type=int,default=8877)
    p.add_argument('--cache',default='render-cache');a=p.parse_args()
    serve(a.host,a.port,a.cache,os.environ.get('ORA_RENDER_TOKEN'))
