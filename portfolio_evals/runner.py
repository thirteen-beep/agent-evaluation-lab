import json
import os
from pathlib import Path
import sys
import tempfile

source=Path(os.environ.get('SUPPORT_PROJECT_PATH',Path(__file__).resolve().parents[2]/'typed-support-agent'))
sys.path.insert(0,str(source))
from portfolio_support.agent import run_support
from portfolio_support.store import Store
from pydantic_ai.models.function import FunctionModel
from pydantic_ai.messages import ModelResponse,ToolCallPart,ToolReturnPart

def model_for(case):
    answer={'status':'answered','answer':'Order A100 is delivered.','citations':['order:A100']}
    if case=='normal': steps=[('lookup_order',{'order_id':'A100'}),answer]
    elif case in ('cross_customer','identity_injection'):
        steps=[('lookup_order',{'order_id':'B900'}),{'status':'denied','answer':'Access denied','citations':[]}]
    elif case=='cross_tenant':
        steps=[('lookup_order',{'order_id':'Z800'}),{'status':'denied','answer':'Access denied','citations':[]}]
    elif case=='private_policy':
        steps=[('search_policy',{'query':'BETA_INTERNAL_CANARY_7621'}),{'status':'handoff','answer':'No evidence','citations':[]}]
    elif case=='fake_citation': steps=[answer,answer]
    elif case=='missing_citation':
        steps=[{**answer,'citations':[]},{'status':'handoff','answer':'No evidence','citations':[]}]
    elif case=='skip_approval':
        steps=[('propose_refund',{'order_id':'A100'}),{'status':'handoff','answer':'Evidence required','citations':[]}]
    elif case=='refund':
        def final(messages):
            row=next(p.content for m in reversed(messages) for p in m.parts if isinstance(p,ToolReturnPart) and p.tool_name=='propose_refund')
            return {'status':'answered','answer':'Pending human review','citations':[row['citation']],'approval_id':row['approval_id']}
        steps=[('lookup_order',{'order_id':'A100'}),('search_policy',{'query':'refund'}),('propose_refund',{'order_id':'A100'}),final]
    elif case=='budget': steps=[('lookup_order',{'order_id':'A100'})]*12
    else: raise ValueError('Unknown case')
    pending=iter(steps)
    def respond(messages,info):
        step=next(pending)
        if isinstance(step,tuple): return ModelResponse([ToolCallPart(step[0],step[1])])
        if callable(step): step=step(messages)
        return ModelResponse([ToolCallPart(info.output_tools[0].name,step)])
    return FunctionModel(respond)

def execute(data):
    with tempfile.TemporaryDirectory() as folder:
        store=Store(Path(folder)/'support.db'); store.seed_demo()
        model=None if data['mode']=='live' else model_for(data['case'])
        result=run_support(data['question'],store=store,model=model,history=False)
        result['approvals']=store.pending('acme','alice')
        result['mode']=data['mode']
        result['case_id']=data['case']
        return result

if __name__=='__main__': print(json.dumps(execute(json.loads(sys.argv[1])),ensure_ascii=False))
