_F='bCodeMirror'
_E='menuBar'
_D=False
_C='-1'
_B=True
_A=None
import json,base64
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import project.sparta_62bcd16a7d.sparta_8de12faf71.qube_6e0e558b60 as qube_6e0e558b60
from project.sparta_5354ac8663.sparta_52de0601a4.qube_1199e87c92 import sparta_8345ad4652
from project.sparta_5354ac8663.sparta_b8b7994f57 import qube_6ee1b476a3 as qube_6ee1b476a3
from project.sparta_5354ac8663.sparta_6b03b9aba1 import qube_951781f614 as qube_951781f614
from project.sparta_5354ac8663.sparta_d63ac0c595 import qube_a2bec951ae as qube_a2bec951ae
@csrf_exempt
@sparta_8345ad4652
@login_required(redirect_field_name='login')
def sparta_bcbfdd9798(request):
	B=request;C=B.GET.get('edit')
	if C is _A:C=_C
	A=qube_6e0e558b60.sparta_4d05c20ea8(B);A[_E]=15;E=qube_6e0e558b60.sparta_ea67d6b805(B.user);A.update(E);A[_F]=_B;A['edit_chart_id']=C;D=_B
	if B.headers.get('HX-Request')=='true':D=_D
	A['bFullRender']=D;return render(B,'dist/project/plot-db/plotDB.html',A)
@csrf_exempt
@sparta_8345ad4652
def sparta_36aa037fe9(request,id,api_token_id=_A):
	A=request
	if id is _A:B=A.GET.get('id')
	else:B=id
	return plot_widget_dataframes_func(A,B)
@csrf_exempt
@sparta_8345ad4652
def sparta_d7019160e7(request,dashboard_id,id,password):
	A=request
	if id is _A:B=A.GET.get('id')
	else:B=id
	C=base64.b64decode(password).decode();print('plot widget dadshboard');return plot_widget_dataframes_func(A,B,dashboard_id=dashboard_id,dashboard_password=C)
def plot_widget_dataframes_func(request,slug,session=_C,dashboard_id=_C,token_permission='',dashboard_password=_A):
	K='token_permission';I=dashboard_id;H=slug;G='res';E=token_permission;D=request;C=_D
	if H is _A:C=_B
	else:
		B=qube_951781f614.sparta_ced098d4de(H,D.user);F=B[G]
		if F==-1:C=_B
	if C:
		if I!=_C:
			B=qube_a2bec951ae.has_dataframe_access(I,H,D.user,dashboard_password);F=B[G]
			if F==1:E=B[K];C=_D
	if C:
		if len(E)>0:
			B=qube_951781f614.sparta_40fd19e718(E);F=B[G]
			if F==1:C=_D
	if C:return sparta_bcbfdd9798(D)
	A=qube_6e0e558b60.sparta_4d05c20ea8(D);A[_E]=15;L=qube_6e0e558b60.sparta_ea67d6b805(D.user);A.update(L);A[_F]=_B;J=B['dataframe_model_obj'];A['b_require_password']=0 if B[G]==1 else 1;A['slug']=J.slug;A['dataframe_model_name']=J.table_name;A['session']=str(session);A['is_dashboard_widget']=1 if I!=_C else 0;A['is_token']=1 if len(E)>0 else 0;A[K]=str(E);return render(D,'dist/project/dataframes/dataframes.html',A)
@csrf_exempt
@sparta_8345ad4652
def sparta_4abbdc1156(request,id,api_token_id=_A):
	A=request
	if id is _A:B=A.GET.get('id')
	else:B=id
	return plot_widget_dataframes_func(A,B)
@csrf_exempt
def sparta_d7c565a6d6(request,token):return plot_widget_dataframes_func(request,slug=_A,token_permission=token)
@csrf_exempt
@sparta_8345ad4652
def sparta_89871a0ac7(request):C='name';B=request;A=qube_6e0e558b60.sparta_4d05c20ea8(B);A[_E]=7;D=qube_6e0e558b60.sparta_ea67d6b805(B.user);A.update(D);A[_F]=_B;A['serialized_data']=B.POST.get('data');A[C]=B.POST.get(C);return render(B,'dist/project/dataframes/plotDataFramesGUI.html',A)