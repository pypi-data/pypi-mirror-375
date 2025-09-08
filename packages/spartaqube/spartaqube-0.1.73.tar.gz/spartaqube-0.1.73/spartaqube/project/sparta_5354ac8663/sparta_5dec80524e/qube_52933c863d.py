_E='subscription_key'
_D=True
_C='errorMsg'
_B=False
_A='res'
import requests
from datetime import datetime
from django.conf import settings as conf_settings
from urllib.parse import urlsplit
from project.models import AIPlan,AIPlanSubscription,CloudPlan
def sparta_c8dfc753b3(json_data,user_obj):
	F='captcha';B=json_data;A=user_obj.email;G='Contact US - New Message';C=B['message'];D=f"<h3>Message:{C}</h3>";D+=f"<hr><div>Sender:{A}</div>";H=B[F];I=f"*ContactUS Message:* {C}\n*From Sender:* {A}\n",;E=requests.post(f"{conf_settings.SERVER_CF}/contact-us",json={'recipient':A,'subject':G,'email_msg':D,'slack_msg':I,F:H},allow_redirects=_B)
	try:
		if E.status_code==400:return{_A:-1,_C:E.text}
		return{_A:1}
	except Exception as J:return{_A:-1,_C:str(J)}
def sparta_070304c20c(json_data,user_obj):from project.sparta_5354ac8663.sparta_8e4c740650 import qube_9b62fc9ff7 as A;B=json_data['cloud_id'];C=A.sparta_7a01c597a0(B);return C
def sparta_57093ebf9f(json_data,user_obj):
	N='%Y-%m-%d';C=user_obj;D=_B;E=[];F=AIPlanSubscription.objects.filter(ai_plan__user=C,status='active')
	if F.count()>0:
		D=_D
		for B in F:E.append({_E:B.subscription_key,'billed_frequency':B.billed_frequency,'date_created':datetime.strftime(B.date_created,N),'last_update':datetime.strftime(B.last_update,N)})
	G='';H='';I=AIPlan.objects.filter(user=C,is_dev=conf_settings.IS_DEV_CF)
	if I.count()>0:J=I[0];H=J.api_key_ai_plan;G=J.existing_api_key_ai_plan
	K=_B;L=[];M=CloudPlan.objects.filter(user=C,is_destroyed=_B,is_verified=_D,is_dev=conf_settings.IS_DEV_CF)
	if len(M)>0:
		K=_D
		for O in M:
			A=(O.ipv4 or'').strip()
			if not A:continue
			if not urlsplit(A).scheme:A=f"http://{A}"
	L.append(A);return{_A:1,'has_ai_plan':D,'has_cloud_plan':K,'cloud_plans_ip':L,'ai_plan_subs':E,'ai_api_key':H,'existing_api_key_ai_plan':G}
def sparta_8e0eefb7ca(json_data,user_obj):
	B=user_obj;C=json_data[_E];D=AIPlan.objects.filter(user=B,is_dev=conf_settings.IS_DEV_CF)
	if D.count()>0:
		I=D[0];J=I.api_key_ai_plan;E=f"{conf_settings.SERVER_CF}/unsubscribe-ai-test";F=_B
		if not conf_settings.IS_DEV:F=_D
		if F:E=f"{conf_settings.SERVER_CF}/unsubscribe-ai"
		A=requests.post(E,json={_E:C,'api_key':J},allow_redirects=_B);print('response');print(A);print(A.status_code);print(A.text)
		if A.status_code==200:
			G=AIPlanSubscription.objects.filter(ai_plan__user=B,subscription_key=C)
			if G.count()>0:H=G[0];H.status='revoked';H.save()
			return{_A:1}
		else:
			try:return{_A:-1,_C:str(A.text)}
			except:pass
	return{_A:-1,_C:'An unexpected error occurred, could not process the query'}