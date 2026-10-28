"""ORA SDK 0.2: small authorized network client, for Muse, Codex, Android/Termux, Python scripts."""
import json, urllib.request, urllib.error
class ORAClient:
 def __init__(self,base='http://127.0.0.1:8767',token=None):
  self.base=base.rstrip('/');self.token=token
 def call(self,path,method='GET',body=None,idempotency_key=None):
  headers={'Accept':'application/json'}
  if self.token:headers['Authorization']='Bearer '+self.token
  if idempotency_key:headers['Idempotency-Key']=idempotency_key
  data=None
  if body is not None:
   headers['Content-Type']='application/json';data=json.dumps(body,ensure_ascii=False).encode()
  req=urllib.request.Request(self.base+path,data,headers,method=method)
  with urllib.request.urlopen(req,timeout=15) as r:return json.load(r)
 def health(self):return self.call('/api/v1/health')
 def tower(self):return self.call('/api/v1/tower')
 def list(self):return self.call('/api/v1/oras')['oras']
 def create(self,goal,name='',parent='ora-sovereign',placement='oracle',grants=None):
  return self.call('/api/v1/oras','POST',{'goal':goal,'name':name,'parent':parent,'placement':placement,'grants':grants})['ora']
 def transition(self,ora_id,action,version=None):
  return self.call(f'/api/v1/oras/{ora_id}/transition','POST',{'action':action,'expected_version':version})['ora']
 def observe(self,event,ora_id='ora-sovereign',goal=''):
  return self.call('/api/v1/observe','POST',{'event':event,'ora_id':ora_id,'goal':goal})['observation']
 def mission(self,ora_id,kind,payload,key=None):
  return self.call(f'/api/v1/oras/{ora_id}/missions','POST',{'kind':kind,'payload':payload},key)['mission']
 def result(self,mission_id):return self.call('/api/v1/missions/'+mission_id)['mission']
 def events(self,after=0):return self.call('/api/v1/events?after='+str(after))
 def manifest(self,ora_id):return self.call('/o/'+ora_id+'/manifest')
 def preview(self,ora_id,verb,input_ref):
  return self.call(f'/o/{ora_id}/purl/v1/shift/{verb}/input/{input_ref}/preview')
