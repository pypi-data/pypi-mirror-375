_L='bPublicUser'
_K='notebook_name'
_J='notebook_id'
_I='b_require_password'
_H='notebook_obj'
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
import project.sparta_62bcd16a7d.sparta_8de12faf71.qube_6e0e558b60 as qube_6e0e558b60
from project.sparta_5354ac8663.sparta_52de0601a4.qube_1199e87c92 import sparta_8345ad4652
from project.sparta_5354ac8663.sparta_8c4400abc8 import qube_0e0202d50f as qube_0e0202d50f
from project.sparta_5354ac8663.sparta_82fa1097b7.qube_0e647c534b import sparta_fba3132a9a
@csrf_exempt
@sparta_8345ad4652
@login_required(redirect_field_name='login')
def sparta_fa945839e8(request):
	B=request;A=qube_6e0e558b60.sparta_4d05c20ea8(B);A[_D]=13;E=qube_6e0e558b60.sparta_ea67d6b805(B.user);A.update(E);A[_E]=_A
	def F(path):
		A=Path(path)
		if not A.exists():A.mkdir(parents=_A)
	G=sparta_fba3132a9a();C=os.path.join(G,'notebook');F(C);A[_F]=C;D=_A
	if B.headers.get('HX-Request')=='true':D=_G
	A['bFullRender']=D;return render(B,'dist/project/notebook/notebook.html',A)
@csrf_exempt
def sparta_3fddab23e3(request,id):
	B=request
	if id is _B:C=B.GET.get('id')
	else:C=id
	D=_G
	if C is _B:D=_A
	else:
		E=qube_0e0202d50f.sparta_db46a726c2(C,B.user);G=E[_C]
		if G==-1:D=_A
	if D:return sparta_fa945839e8(B)
	A=qube_6e0e558b60.sparta_4d05c20ea8(B);A[_D]=12;H=qube_6e0e558b60.sparta_ea67d6b805(B.user);A.update(H);A[_E]=_A;F=E[_H];A[_F]=F.project_path;A[_I]=0 if E[_C]==1 else 1;A[_J]=F.notebook_id;A[_K]=F.name;A[_L]=B.user.is_anonymous;return render(B,'dist/project/notebook/notebookRun.html',A)
@csrf_exempt
@sparta_8345ad4652
@login_required(redirect_field_name='login')
def sparta_dc693e6a10(request,id):
	B=request
	if id is _B:C=B.GET.get('id')
	else:C=id
	D=_G
	if C is _B:D=_A
	else:
		E=qube_0e0202d50f.sparta_db46a726c2(C,B.user);G=E[_C]
		if G==-1:D=_A
	if D:return sparta_fa945839e8(B)
	A=qube_6e0e558b60.sparta_4d05c20ea8(B);A[_D]=12;H=qube_6e0e558b60.sparta_ea67d6b805(B.user);A.update(H);A[_E]=_A;F=E[_H];A[_F]=F.project_path;A[_I]=0 if E[_C]==1 else 1;A[_J]=F.notebook_id;A[_K]=F.name;A[_L]=B.user.is_anonymous;return render(B,'dist/project/notebook/notebookDetached.html',A)