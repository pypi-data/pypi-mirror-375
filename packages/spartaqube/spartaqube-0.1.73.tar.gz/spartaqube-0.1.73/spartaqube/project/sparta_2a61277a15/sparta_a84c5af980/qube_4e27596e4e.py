_Q='Invalid request'
_P='Location'
_O='subscription'
_N='stripe_cf_test_env'
_M='fingerprint'
_L='subscription_key'
_K='frequency'
_J='STRIPE_CF_TEST_ENV'
_I='yearly'
_H='monthly'
_G='is_monthly'
_F='error'
_E='base_url_redirect'
_D='menuBar'
_C=True
_B=False
_A='login'
import json,base64,requests,uuid,hashlib
from django.http import HttpResponseRedirect,HttpResponse,JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
import project.sparta_62bcd16a7d.sparta_8de12faf71.qube_6e0e558b60 as qube_6e0e558b60
from project.sparta_5354ac8663.sparta_52de0601a4.qube_1199e87c92 import sparta_8345ad4652
from project.sparta_5354ac8663.sparta_df1fc45e2b.qube_03fc51dbbb import sparta_490b401d3c
from project.models import UserProfile,AIPlan,AIPlanSubscription,CloudPlan
from datetime import datetime
import pytz
UTC=pytz.utc
from spartaqube_app.secrets import sparta_1c1a070836
@csrf_exempt
@sparta_8345ad4652
@login_required(redirect_field_name=_A)
def sparta_5fd294ff20(request):C='CAPTCHA_SITEKEY';B=request;A=qube_6e0e558b60.sparta_4d05c20ea8(B);A[_D]=-1;D=qube_6e0e558b60.sparta_ea67d6b805(B.user);A.update(D);A[C]=sparta_1c1a070836()[C];return render(B,'dist/project/plans/plans.html',A)
def sparta_363d7e9344():A=uuid.uuid4();B=hashlib.sha256(str(A).encode());C=B.hexdigest();return C
def sparta_01e612dbe9(user_obj):
	D=user_obj;E=AIPlan.objects.filter(user=D,is_dev=conf_settings.IS_DEV_CF)
	if E.count()>0:
		A=E[0];B=_B
		if A.api_key_ai_plan is None:B=_C
		elif len(A.api_key_ai_plan)==0:B=_C
		if B:A.api_key_ai_plan=sparta_363d7e9344()
		C=_B
		if A.reset_api_key_ai_plan is None:C=_C
		elif len(A.reset_api_key_ai_plan)==0:C=_C
		if C:A.reset_api_key_ai_plan=sparta_363d7e9344()
		A.save();return A
	else:F=datetime.now().astimezone(UTC);A=AIPlan.objects.create(user=D,api_key_ai_plan=sparta_363d7e9344(),reset_api_key_ai_plan=sparta_363d7e9344(),last_update=F,date_created=F,is_dev=conf_settings.IS_DEV_CF);return A
@csrf_exempt
@sparta_8345ad4652
@login_required(redirect_field_name=_A)
def sparta_3af0da448c(request):
	A=request
	if A.method=='POST':
		J=A.user.email;K=A.POST.get(_G);L=A.POST.get(_E)
		if str(K).lower()=='true':C=_H
		else:C=_I
		try:
			D=sparta_01e612dbe9(A.user);M=D.api_key_ai_plan;N=D.reset_api_key_ai_plan;E=sparta_363d7e9344();F=datetime.now().astimezone(UTC);AIPlanSubscription.objects.create(ai_plan=D,subscription_key=E,billed_frequency=C,last_update=F,date_created=F);G=f"{conf_settings.SERVER_CF}/create-checkout-session-ai-test";H=_B;I=''
			if not conf_settings.IS_DEV_CF:H=_C
			else:I=sparta_1c1a070836()[_J]
			if H:G=f"{conf_settings.SERVER_CF}/create-checkout-session-ai"
			B=requests.post(G,json={'email':J,_K:C,'mode':_O,'api_key':M,_L:E,'reset_api_key_ai_plan':N,_M:sparta_490b401d3c(),_E:L,_N:I},allow_redirects=_B)
			if B.status_code==302:return HttpResponseRedirect(B.headers[_P])
			return JsonResponse({_F:B.text},status=B.status_code)
		except Exception as O:import traceback as P;print(P.format_exc());return JsonResponse({_F:str(O)},status=500)
	return HttpResponse(_Q,status=405)
@csrf_exempt
@sparta_8345ad4652
@login_required(redirect_field_name=_A)
def sparta_3e70ea6ad0(request):
	A=request;G=A.GET.get(_L);C=AIPlanSubscription.objects.filter(subscription_key=G)
	if C.count()>0:D=C[0];D.status='active';D.save()
	B=qube_6e0e558b60.sparta_4d05c20ea8(A);B[_D]=-1;H=qube_6e0e558b60.sparta_ea67d6b805(A.user);B.update(H);E=AIPlan.objects.filter(user=A.user,is_dev=conf_settings.IS_DEV_CF)
	if E.count()>0:
		I=E[0];F=I.api_key_ai_plan
		if len(F)>0:B['api_key_ai_plan']=F;return render(A,'dist/project/plans/aiPlansSuccess.html',B)
	return sparta_a7a916173e(A)
@csrf_exempt
@sparta_8345ad4652
@login_required(redirect_field_name=_A)
def sparta_a7a916173e(request):A=request;B=qube_6e0e558b60.sparta_4d05c20ea8(A);B[_D]=-1;C=qube_6e0e558b60.sparta_ea67d6b805(A.user);B.update(C);return render(A,'dist/project/plans/aiPlansCancel.html',B)
@csrf_exempt
@sparta_8345ad4652
@login_required(redirect_field_name=_A)
def sparta_7b9e2df141(request):
	A=request
	if A.method=='POST':
		G=A.user.email;H=A.POST.get(_G);I=str(A.POST.get('instanceType'));J={'1':'small','2':'medium','3':'large'}[I];K=A.POST.get(_E)
		if str(H).lower()=='true':C=_H
		else:C=_I
		try:
			L=datetime.now().astimezone(UTC);D=sparta_363d7e9344();CloudPlan.objects.create(user=A.user,cloud_key=D,is_verified=_B,date_created=L,is_dev=conf_settings.IS_DEV_CF);E=f"{conf_settings.SERVER_CF}/create-checkout-session-cloud-test";F=_B
			if not conf_settings.IS_DEV_CF:F=_C
			else:M=sparta_1c1a070836()[_J]
			if F:E=f"{conf_settings.SERVER_CF}/create-checkout-session-cloud"
			B=requests.post(E,json={'email':G,_K:C,'instance_type':J,'mode':_O,'cloud_key':D,_M:sparta_490b401d3c(),_E:K,_N:M},allow_redirects=_B)
			if B.status_code==302:return HttpResponseRedirect(B.headers[_P])
			return JsonResponse({_F:B.text},status=B.status_code)
		except Exception as N:import traceback as O;print(O.format_exc());return JsonResponse({_F:str(N)},status=500)
	return HttpResponse(_Q,status=405)
@csrf_exempt
@sparta_8345ad4652
@login_required(redirect_field_name=_A)
def sparta_7e3349dfa0(request):
	H='subscription_id';D='cloud_id';A=request;print('ENTER cloud_plans_payment_success');print('GET params:');print(A.GET);C=A.GET.get(D);E=A.GET.get(H);print(D);print(C);print(H);print(E);B=qube_6e0e558b60.sparta_4d05c20ea8(A);B[D]=C;B[_D]=-1;I=qube_6e0e558b60.sparta_ea67d6b805(A.user);B.update(I);F=CloudPlan.objects.filter(user=A.user,cloud_key=C,is_dev=conf_settings.IS_DEV_CF)
	if F.count()>0:G=F[0];G.subscription_id=E;G.save()
	return render(A,'dist/project/plans/cloudPlansSuccess.html',B)
@csrf_exempt
@sparta_8345ad4652
@login_required(redirect_field_name=_A)
def sparta_6307a23207(request):A=request;B=qube_6e0e558b60.sparta_4d05c20ea8(A);B[_D]=-1;C=qube_6e0e558b60.sparta_ea67d6b805(A.user);B.update(C);return render(A,'dist/project/plans/cloudPlansCancel.html',B)