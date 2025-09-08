_D='bFullRender'
_C='bCodeMirror'
_B='menuBar'
_A=True
import os,json,getpass,platform
from pathlib import Path
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import project.sparta_62bcd16a7d.sparta_8de12faf71.qube_6e0e558b60 as qube_6e0e558b60
from project.sparta_5354ac8663.sparta_52de0601a4.qube_1199e87c92 import sparta_8345ad4652
from project.sparta_5354ac8663.sparta_b8b7994f57 import qube_6ee1b476a3 as qube_6ee1b476a3
from project.sparta_5354ac8663.sparta_d63ac0c595 import qube_a2bec951ae as qube_a2bec951ae
from project.sparta_5354ac8663.sparta_82fa1097b7.qube_0e647c534b import sparta_fba3132a9a
@csrf_exempt
@sparta_8345ad4652
@login_required(redirect_field_name='login')
def sparta_8fa8c85ae4(request):
	B=request;C=B.GET.get('edit')
	if C is None:C='-1'
	A=qube_6e0e558b60.sparta_4d05c20ea8(B);A[_B]=9;F=qube_6e0e558b60.sparta_ea67d6b805(B.user);A.update(F);A[_C]=_A;A['edit_chart_id']=C
	def G(path):
		A=Path(path)
		if not A.exists():A.mkdir(parents=_A)
	H=sparta_fba3132a9a();D=os.path.join(H,'dashboard');G(D);A['default_project_path']=D;E=_A
	if B.headers.get('HX-Request')=='true':E=False
	A[_D]=E;return render(B,'dist/project/dashboard/dashboard.html',A)
@csrf_exempt
def sparta_6a1f13cece(request,id):
	A=request
	if id is None:B=A.GET.get('id')
	else:B=id
	return sparta_1bdaa4c0e6(A,B)
def sparta_1bdaa4c0e6(request,dashboard_id,session='-1'):
	G='res';E=dashboard_id;B=request;C=False
	if E is None:C=_A
	else:
		D=qube_a2bec951ae.has_dashboard_access(E,B.user);H=D[G]
		if H==-1:C=_A
	if C:return sparta_8fa8c85ae4(B)
	A=qube_6e0e558b60.sparta_4d05c20ea8(B);A[_B]=9;I=qube_6e0e558b60.sparta_ea67d6b805(B.user);A.update(I);A[_C]=_A;F=D['dashboard_obj'];A['b_require_password']=0 if D[G]==1 else 1;A['dashboard_id']=F.dashboard_id;A['dashboard_name']=F.name;A['bPublicUser']=B.user.is_anonymous;A['session']=str(session);A[_D]=_A;return render(B,'dist/project/dashboard/dashboardRun.html',A)