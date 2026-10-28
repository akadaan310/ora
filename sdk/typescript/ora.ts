/** ORA 0.2 — TypeScript transport client. Zero dependencies; requires fetch. */
export type ORAInstance = {
  id: string; name: string; goal: string; parent: string;
  placement: 'oracle'|'android'|'homeless'; life: string;
  version: number; grants: string[]; missing: string[];
  regions: Record<string,{state:string,tick:number}>; url_path:string;
};
export class ORAClient {
  constructor(private baseURL: string, private token?: string) {}
  private async request<T>(path:string, method='GET', body?:unknown):Promise<T> {
    const headers:Record<string,string> = { 'Accept': 'application/json' };
    if(this.token) headers['Authorization']='Bearer '+this.token;
    if(body!==undefined) headers['Content-Type']='application/json';
    const r=await fetch(this.baseURL.replace(/\/$/,'')+path,{method,headers,body:body===undefined?undefined:JSON.stringify(body)});
    const data=await r.json();
    if(!r.ok)throw new Error(data.detail||data.error||`HTTP ${r.status}`);
    return data as T;
  }
  tower(){return this.request<{name:string,levels:Array<{index:number,name:string,function:string}>}>('/api/v1/tower')}
  list(){return this.request<{oras:ORAInstance[]}>('/api/v1/oras')}
  create(goal:string,name='',placement:'oracle'|'android'|'homeless'='oracle'){
    return this.request<{ora:ORAInstance}>('/api/v1/oras','POST',{goal,name,placement});
  }
  transition(id:string,action:'review'|'activate'|'pause'|'resume'|'stop',expected_version:number){
    return this.request<{ora:ORAInstance}>(`/api/v1/oras/${id}/transition`,'POST',{action,expected_version});
  }
  mission(id:string,kind:string,payload:Record<string,unknown>){
    return this.request<{mission:{id:string,state:string}}>(`/api/v1/oras/${id}/missions`,'POST',{kind,payload});
  }
  result(id:string){return this.request<{mission:unknown}>(`/api/v1/missions/${id}`)}
  events(after=0){return this.request<{events:unknown[],chain_valid:boolean}>(`/api/v1/events?after=${after}`)}
  observe(event:'CAPABILITY_GAP'|'NETWORK_DISCONNECTED'|'NETWORK_RECONNECTED',ora_id='ora-sovereign',goal=''){
    return this.request<{observation:unknown}>('/api/v1/observe','POST',{event,ora_id,goal});
  }
}
