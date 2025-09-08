_R='serialized_data'
_Q='has_access'
_P='plot_name'
_O='plot_chart_id'
_N='plot_db_chart_obj'
_M='dist/project/plot-db/plotDB.html'
_L='bFullRender'
_K='true'
_J='HX-Request'
_I='edit_chart_id'
_H='edit'
_G='login'
_F='-1'
_E=False
_D='bCodeMirror'
_C='menuBar'
_B=None
_A=True
import json,base64
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import project.sparta_62bcd16a7d.sparta_8de12faf71.qube_6e0e558b60 as qube_6e0e558b60
from project.sparta_5354ac8663.sparta_52de0601a4.qube_1199e87c92 import sparta_8345ad4652
from project.sparta_5354ac8663.sparta_b8b7994f57 import qube_6ee1b476a3 as qube_6ee1b476a3
from project.sparta_5354ac8663.sparta_d63ac0c595 import qube_a2bec951ae as qube_a2bec951ae
@csrf_exempt
@sparta_8345ad4652
@login_required(redirect_field_name=_G)
def sparta_914ddeb3a7(request):
	B=request;C=B.GET.get(_H)
	if C is _B:C=_F
	A=qube_6e0e558b60.sparta_4d05c20ea8(B);A[_C]=7;E=qube_6e0e558b60.sparta_ea67d6b805(B.user);A.update(E);A[_D]=_A;A[_I]=C;D=_A
	if B.headers.get(_J)==_K:D=_E
	A[_L]=D;return render(B,_M,A)
@csrf_exempt
@sparta_8345ad4652
@login_required(redirect_field_name=_G)
def sparta_7942b81299(request):
	B=request;C=B.GET.get(_H)
	if C is _B:C=_F
	A=qube_6e0e558b60.sparta_4d05c20ea8(B);A[_C]=10;E=qube_6e0e558b60.sparta_ea67d6b805(B.user);A.update(E);A[_D]=_A;A[_I]=C;D=_A
	if B.headers.get(_J)==_K:D=_E
	A[_L]=D;return render(B,_M,A)
@csrf_exempt
@sparta_8345ad4652
@login_required(redirect_field_name=_G)
def sparta_80f6ebc2b3(request):
	B=request;C=B.GET.get(_H)
	if C is _B:C=_F
	A=qube_6e0e558b60.sparta_4d05c20ea8(B);A[_C]=11;E=qube_6e0e558b60.sparta_ea67d6b805(B.user);A.update(E);A[_D]=_A;A[_I]=C;D=_A
	if B.headers.get(_J)==_K:D=_E
	A[_L]=D;return render(B,_M,A)
@csrf_exempt
@sparta_8345ad4652
@login_required(redirect_field_name=_G)
def sparta_bcbfdd9798(request):
	B=request;C=B.GET.get(_H)
	if C is _B:C=_F
	A=qube_6e0e558b60.sparta_4d05c20ea8(B);A[_C]=15;E=qube_6e0e558b60.sparta_ea67d6b805(B.user);A.update(E);A[_D]=_A;A[_I]=C;D=_A
	if B.headers.get(_J)==_K:D=_E
	A[_L]=D;return render(B,_M,A)
@csrf_exempt
@sparta_8345ad4652
@login_required(redirect_field_name=_G)
def sparta_98ca1bb1cc(request):
	A=request;C=A.GET.get('id');D=_E
	if C is _B:D=_A
	else:E=qube_6ee1b476a3.sparta_4ff5d8fe0d(C,A.user);D=not E[_Q]
	if D:return sparta_914ddeb3a7(A)
	B=qube_6e0e558b60.sparta_4d05c20ea8(A);B[_C]=7;F=qube_6e0e558b60.sparta_ea67d6b805(A.user);B.update(F);B[_D]=_A;B[_O]=C;G=E[_N];B[_P]=G.name;return render(A,'dist/project/plot-db/plotFull.html',B)
@csrf_exempt
@sparta_8345ad4652
def sparta_bced6d3bfd(request,id,api_token_id=_B):
	A=request
	if id is _B:B=A.GET.get('id')
	else:B=id
	return plot_widget_func(A,B)
@csrf_exempt
@sparta_8345ad4652
def sparta_d7019160e7(request,dashboard_id,id,password):
	A=request
	if id is _B:B=A.GET.get('id')
	else:B=id
	C=base64.b64decode(password).decode();return plot_widget_func(A,B,dashboard_id=dashboard_id,dashboard_password=C)
@csrf_exempt
@sparta_8345ad4652
def sparta_1c523cf06f(request,widget_id,session_id,api_token_id):return plot_widget_func(request,widget_id,session_id)
def plot_widget_func(request,plot_chart_id,session=_F,dashboard_id=_F,token_permission='',dashboard_password=_B):
	K='token_permission';I=dashboard_id;H=plot_chart_id;G='res';E=token_permission;D=request;C=_E
	if H is _B:C=_A
	else:
		B=qube_6ee1b476a3.sparta_ced098d4de(H,D.user);F=B[G]
		if F==-1:C=_A
	if C:
		if I!=_F:
			B=qube_a2bec951ae.has_plot_db_access(I,H,D.user,dashboard_password);F=B[G]
			if F==1:E=B[K];C=_E
	if C:
		if len(E)>0:
			B=qube_6ee1b476a3.sparta_40fd19e718(E);F=B[G]
			if F==1:C=_E
	if C:return sparta_914ddeb3a7(D)
	A=qube_6e0e558b60.sparta_4d05c20ea8(D);A[_C]=7;L=qube_6e0e558b60.sparta_ea67d6b805(D.user);A.update(L);A[_D]=_A;J=B[_N];A['b_require_password']=0 if B[G]==1 else 1;A[_O]=J.plot_chart_id;A[_P]=J.name;A['session']=str(session);A['is_dashboard_widget']=1 if I!=_F else 0;A['is_token']=1 if len(E)>0 else 0;A[K]=str(E);return render(D,'dist/project/plot-db/widgets.html',A)
@csrf_exempt
def sparta_78f74b6c01(request,token):return plot_widget_func(request,plot_chart_id=_B,token_permission=token)
@csrf_exempt
@sparta_8345ad4652
def sparta_b4b9b67208(request):B=request;A=qube_6e0e558b60.sparta_4d05c20ea8(B);A[_C]=7;C=qube_6e0e558b60.sparta_ea67d6b805(B.user);A.update(C);A[_D]=_A;A[_R]=B.POST.get('data');return render(B,'dist/project/plot-db/plotGUI.html',A)
@csrf_exempt
@sparta_8345ad4652
@login_required(redirect_field_name=_G)
def sparta_2b9f25d3ec(request,id):
	K=',\n    ';B=request;C=id;F=_E
	if C is _B:F=_A
	else:G=qube_6ee1b476a3.sparta_4ff5d8fe0d(C,B.user);F=not G[_Q]
	if F:return sparta_914ddeb3a7(B)
	L=qube_6ee1b476a3.sparta_b87a5e78d1(G[_N]);D='';H=0
	for(E,I)in L.items():
		if H>0:D+=K
		if I==1:D+=f"{E}=input_{E}"
		else:M=str(K.join([f"input_{E}_{A}"for A in range(I)]));D+=f"{E}=[{M}]"
		H+=1
	J=f"'{C}'";N=f"\n    {J}\n";O=f"Spartaqube().get_widget({N})";P=f"\n    {J},\n    {D}\n";Q=f"Spartaqube().plot({P})";A=qube_6e0e558b60.sparta_4d05c20ea8(B);A[_C]=7;R=qube_6e0e558b60.sparta_ea67d6b805(B.user);A.update(R);A[_D]=_A;A[_O]=C;S=G[_N];A[_P]=S.name;A['plot_data_cmd']=O;A['plot_data_cmd_inputs']=Q;return render(B,'dist/project/plot-db/plotGUISaved.html',A)
@csrf_exempt
@sparta_8345ad4652
def sparta_6d674a9c2a(request,json_vars_html):B=request;A=qube_6e0e558b60.sparta_4d05c20ea8(B);A[_C]=7;C=qube_6e0e558b60.sparta_ea67d6b805(B.user);A.update(C);A[_D]=_A;A.update(json.loads(json_vars_html));A[_R]=B.POST.get('data');return render(B,'dist/project/plot-db/plotAPI.html',A)
@csrf_exempt
@sparta_8345ad4652
def sparta_33593eab8f(request):A={};return render(request,'dist/project/luckysheetIframe/luckysheet-frame.html',A)