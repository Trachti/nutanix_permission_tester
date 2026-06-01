import argparse, http.client, json, ssl, time
NTNX_PRISMCENTRAL_IP = "YOUR_IP:9440"
PE_AND_PC_TOKEN = "YOUR GENERATED TOKEN FROM nutanix_auth.py"
PE_HOSTS = ["IP_FROM_ELEMENTS_CLUSTER_1:9440", "IP_FROM_ELEMENTS_CLUSTER_2:9440", "IP_FROM_ELEMENTS_CLUSTER_3:9440"]

def call(host, method, url, payload=None):
    context=ssl._create_unverified_context(); conn=http.client.HTTPSConnection(host,timeout=15,context=context)
    headers={"Accept":"application/json","Authorization":PE_AND_PC_TOKEN,"Content-Type":"application/json"}
    body=json.dumps(payload) if isinstance(payload,dict) else payload; start=time.time(); conn.request(method,url,body=body,headers=headers); res=conn.getresponse(); raw=res.read().decode("utf-8"); ms=round((time.time()-start)*1000,2)
    try: data=json.loads(raw) if raw else {}
    except json.JSONDecodeError: data={"raw":raw}
    return data,res.status,ms

def msg(data):
    if isinstance(data,dict):
        if data.get("message"): return str(data["message"])
        if data.get("error"): return str(data["error"])
    return str(data)[:500]

def test(name,host,method,url,payload=None):
    try:
        data,status,ms=call(host,method,url,payload); ok=200<=status<300
        return {"name":name,"host":host,"method":method,"url":url,"http_status":status,"duration_ms":ms,"success":ok,"message":"OK" if ok else msg(data)}
    except Exception as e:
        return {"name":name,"host":host,"method":method,"url":url,"http_status":None,"duration_ms":None,"success":False,"message":str(e)}

def main():
    p=argparse.ArgumentParser(description="Test Nutanix Prism Central and Prism Element read permissions.")
    p.add_argument("--skip-pe",action="store_true"); p.add_argument("--skip-recovery",action="store_true"); p.add_argument("--skip-images",action="store_true"); p.add_argument("--json-file")
    a=p.parse_args(); payload=lambda kind:{"kind":kind,"length":1,"offset":0}
    tests=[("Prism Central VM read",NTNX_PRISMCENTRAL_IP,"POST","/api/nutanix/v3/vms/list",payload("vm")),("Prism Central cluster read",NTNX_PRISMCENTRAL_IP,"POST","/api/nutanix/v3/clusters/list",payload("cluster")),("Prism Central subnet read",NTNX_PRISMCENTRAL_IP,"POST","/api/nutanix/v3/subnets/list",payload("subnet"))]
    if not a.skip_images: tests.append(("Prism Central image read",NTNX_PRISMCENTRAL_IP,"POST","/api/nutanix/v3/images/list",payload("image")))
    if not a.skip_recovery: tests.append(("Prism Central recovery point read",NTNX_PRISMCENTRAL_IP,"GET","/api/dataprotection/v4.0/config/recovery-points?$limit=1",None))
    rows=[test(*t) for t in tests]
    if not a.skip_pe:
        for pe in PE_HOSTS:
            rows.append(test("Prism Element snapshot read",pe,"GET","/api/nutanix/v2.0/snapshots/")); rows.append(test("Prism Element task endpoint read",pe,"GET","/api/nutanix/v2.0/tasks/"))
    print(json.dumps(rows,indent=2,ensure_ascii=False))
    if a.json_file: open(a.json_file,"w",encoding="utf-8").write(json.dumps(rows,indent=2,ensure_ascii=False))
    if not all(r["success"] for r in rows): raise SystemExit(1)
if __name__=="__main__": main()
