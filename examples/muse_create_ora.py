"""Example: create, activate, and call a Language ORA using the same public API Muse can use."""
from pathlib import Path
import os,sys,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'sdk'/'python'))
from ora_client import ORAClient
client=ORAClient(os.environ.get('ORA_BASE_URL','http://127.0.0.1:8767'),os.environ.get('ORA_ADMIN_TOKEN'))
a=client.create('Study Arabic and Greek script morphology in encyclopedia articles','Muse Language Research ORA')
print('URL:',client.base+'/o/'+a['id'],'status:',a['life'])
a=client.transition(a['id'],'review',a['version']);a=client.transition(a['id'],'activate',a['version'])
m=client.mission(a['id'],'language.inspect',{'text':'Hello, مرحبا, Καλημέρα'})
for i in range(30):
 r=client.result(m['id'])
 if r['state'] in ('SUCCEEDED','FAILED'):break
 time.sleep(.1)
print('Mission:',r['state'],r['result']);print('Continuity:',client.manifest(a['id']))
