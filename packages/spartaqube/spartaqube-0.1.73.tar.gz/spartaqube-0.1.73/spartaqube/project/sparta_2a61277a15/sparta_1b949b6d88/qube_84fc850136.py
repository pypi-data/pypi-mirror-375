_M='bPublicUser'
_L='developer_name'
_K='b_require_password'
_J='developer_obj'
_I='dist/project/homepage/homepage.html'
_H='developer_id'
_G=False
_F='default_project_path'
_E='bCodeMirror'
_D='menuBar'
_C='res'
_B=None
_A=True
import os,json,getpass,platform
from pathlib import Path
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.static import serve
from django.http import FileResponse,Http404
from urllib.parse import unquote
from django.conf import settings as conf_settings
import project.sparta_62bcd16a7d.sparta_8de12faf71.qube_6e0e558b60 as qube_6e0e558b60
from project.sparta_5354ac8663.sparta_52de0601a4.qube_1199e87c92 import sparta_8345ad4652
from project.sparta_5354ac8663.sparta_48a83eeec3 import qube_b2f294a307 as qube_b2f294a307
from project.sparta_5354ac8663.sparta_82fa1097b7.qube_0e647c534b import sparta_fba3132a9a
@csrf_exempt
@sparta_8345ad4652
@login_required(redirect_field_name='login')
def sparta_d9237f1a9c(request):
	B=request
	if not conf_settings.IS_DEV_VIEW_ENABLED:A=qube_6e0e558b60.sparta_4d05c20ea8(B);return render(B,_I,A)
	qube_b2f294a307.sparta_748a09c1e1();A=qube_6e0e558b60.sparta_4d05c20ea8(B);A[_D]=12;E=qube_6e0e558b60.sparta_ea67d6b805(B.user);A.update(E);A[_E]=_A
	def F(path):
		A=Path(path)
		if not A.exists():A.mkdir(parents=_A)
	G=sparta_fba3132a9a();C=os.path.join(G,'developer');F(C);A[_F]=C;D=_A
	if B.headers.get('HX-Request')=='true':D=_G
	A['bFullRender']=D;return render(B,'dist/project/developer/developer.html',A)
@csrf_exempt
def sparta_6223b7d078(request,id):
	B=request
	if not conf_settings.IS_DEV_VIEW_ENABLED:A=qube_6e0e558b60.sparta_4d05c20ea8(B);return render(B,_I,A)
	if id is _B:C=B.GET.get('id')
	else:C=id
	D=_G
	if C is _B:D=_A
	else:
		E=qube_b2f294a307.has_developer_access(C,B.user);G=E[_C]
		if G==-1:D=_A
	if D:return sparta_d9237f1a9c(B)
	A=qube_6e0e558b60.sparta_4d05c20ea8(B);A[_D]=12;H=qube_6e0e558b60.sparta_ea67d6b805(B.user);A.update(H);A[_E]=_A;F=E[_J];A[_F]=F.project_path;A[_K]=0 if E[_C]==1 else 1;A[_H]=F.developer_id;A[_L]=F.name;A[_M]=B.user.is_anonymous;return render(B,'dist/project/developer/developerRun.html',A)
@csrf_exempt
@sparta_8345ad4652
@login_required(redirect_field_name='login')
def sparta_e984349e61(request,id):
	B=request;print('OPEN DEVELOPER DETACHED')
	if id is _B:C=B.GET.get('id')
	else:C=id
	print(_H);print(C);D=_G
	if C is _B:D=_A
	else:
		E=qube_b2f294a307.has_developer_access(C,B.user);G=E[_C]
		if G==-1:D=_A
	print('b_redirect_developer_db');print(D)
	if D:return sparta_d9237f1a9c(B)
	A=qube_6e0e558b60.sparta_4d05c20ea8(B);A[_D]=12;H=qube_6e0e558b60.sparta_ea67d6b805(B.user);A.update(H);A[_E]=_A;F=E[_J];A[_F]=F.project_path;A[_K]=0 if E[_C]==1 else 1;A[_H]=F.developer_id;A[_L]=F.name;A[_M]=B.user.is_anonymous;return render(B,'dist/project/developer/developerDetached.html',A)
def sparta_cd146b80ce(request,project_path,file_name):A=project_path;A=unquote(A);return serve(request,file_name,document_root=A)