_E='title_override'
_D='dataframe_llm_obj'
_C='has_write_rights'
_B='res'
_A='dataframe_llm_id'
import os,sys,requests,subprocess,socket
from datetime import datetime
import pytz
UTC=pytz.utc
from project.sparta_5354ac8663.sparta_82fa1097b7.qube_0e647c534b import sparta_fba3132a9a
from project.models import DataFrameLLM
from project.sparta_5354ac8663.sparta_df1fc45e2b.qube_22cf6479bc import LLMLauncher
from project.sparta_5354ac8663.sparta_df1fc45e2b.qube_34b32d54de import sparta_d02ce93b53
def sparta_51d0508b88(json_data,user_obj):
	H=json_data['dataframe_slug'];D=DataFrameLLM.objects.filter(user=user_obj,dataframe_model__slug=H,is_delete=False).order_by('-last_update').all();E=[]
	if D.count()>0:
		for A in D:
			F=A.initial_prompt;G=A.llm_one_liner;B=A.title_override;C=F
			if B is not None:C=B
			elif G is not None:C=B
			E.append({'initial_prompt':F,'llm_one_liner':G,_E:B,'title_to_display':C,_A:A.dataframe_llm_id})
	return{_B:1,'dataframe_llm_history':E}
def sparta_f7c20eb31d(dataframe_llm_id,user_obj):
	A=DataFrameLLM.objects.filter(dataframe_llm_id=dataframe_llm_id,user=user_obj);C=A.count()>0;B=None
	if C:B=A[0]
	return{_C:A.count()>0,_D:B}
def sparta_25f5e5cfcf(json_data,user_obj):
	A=json_data;D=A[_A];B=sparta_f7c20eb31d(D,user_obj)
	if B[_C]:C=B[_D];C.title_override=A[_E];C.save()
	return{_B:1}
def sparta_5fdc49bbbb(json_data,user_obj):
	B=json_data[_A];A=sparta_f7c20eb31d(B,user_obj)
	if A[_C]:C=A[_D]
	return{_B:1}
def sparta_e3d6b25b9a(json_data,user_obj):
	C=json_data[_A];A=sparta_f7c20eb31d(C,user_obj)
	if A[_C]:B=A[_D];B.is_delete=True;B.save()
	return{_B:1}