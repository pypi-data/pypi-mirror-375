_A='menuBar'
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
from project.sparta_5354ac8663.sparta_cf948f0aee import qube_26db0d415a as qube_26db0d415a
from project.sparta_5354ac8663.sparta_218a0b6e71 import qube_d14205c11b as qube_d14205c11b
from project.sparta_5354ac8663.sparta_82fa1097b7.qube_0e647c534b import sparta_fba3132a9a
@csrf_exempt
@sparta_8345ad4652
@login_required(redirect_field_name='login')
def sparta_2ab4c3cb30(request):A=request;B=qube_6e0e558b60.sparta_4d05c20ea8(A);B[_A]=-1;C=qube_6e0e558b60.sparta_ea67d6b805(A.user);B.update(C);return render(A,'dist/project/homepage/homepage.html',B)
@csrf_exempt
@sparta_8345ad4652
@login_required(redirect_field_name='login')
def sparta_7933ac8919(request,kernel_manager_uuid):
	D=kernel_manager_uuid;C=True;B=request;E=False
	if D is None:E=C
	else:
		F=qube_26db0d415a.sparta_eebc077c64(B.user,D)
		if F is None:E=C
	if E:return sparta_2ab4c3cb30(B)
	def H(path):
		A=Path(path)
		if not A.exists():A.mkdir(parents=C)
	K=sparta_fba3132a9a();G=os.path.join(K,'kernel');H(G);I=os.path.join(G,D);H(I);J=os.path.join(I,'main.ipynb')
	if not os.path.exists(J):
		L=qube_d14205c11b.sparta_44ea0d8aba()
		with open(J,'w')as M:M.write(json.dumps(L))
	A=qube_6e0e558b60.sparta_4d05c20ea8(B);A['default_project_path']=G;A[_A]=-1;N=qube_6e0e558b60.sparta_ea67d6b805(B.user);A.update(N);A['kernel_name']=F.name;A['kernelManagerUUID']=F.kernel_manager_uuid;A['bCodeMirror']=C;A['bPublicUser']=B.user.is_anonymous;return render(B,'dist/project/sqKernelNotebook/sqKernelNotebook.html',A)