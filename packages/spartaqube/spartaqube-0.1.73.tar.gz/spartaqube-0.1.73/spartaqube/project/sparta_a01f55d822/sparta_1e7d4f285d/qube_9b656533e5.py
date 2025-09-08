_E='Content-Disposition'
_D='utf-8'
_C='dashboardId'
_B='projectPath'
_A='jsonData'
import os,json,base64
from django.http import HttpResponse,Http404
from django.views.decorators.csrf import csrf_exempt
from project.sparta_5354ac8663.sparta_218a0b6e71 import qube_344207cff1 as qube_344207cff1
from project.sparta_5354ac8663.sparta_218a0b6e71 import qube_11f6eef4bd as qube_11f6eef4bd
from project.sparta_5354ac8663.sparta_d63ac0c595 import qube_a2bec951ae as qube_a2bec951ae
from project.sparta_5354ac8663.sparta_52de0601a4.qube_1199e87c92 import sparta_5c61c65841,sparta_dacedd4e08
@csrf_exempt
def sparta_4cb5f193b2(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_344207cff1.sparta_4cb5f193b2(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
def sparta_d669f7897d(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_344207cff1.sparta_d669f7897d(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
def sparta_b6a7c7acb9(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_344207cff1.sparta_b6a7c7acb9(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
def sparta_2917553648(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_344207cff1.sparta_2917553648(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
@sparta_dacedd4e08
def sparta_239c88ba15(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_344207cff1.sparta_239c88ba15(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
def sparta_fd3590ad21(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_344207cff1.sparta_fd3590ad21(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
def sparta_27750a1549(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_344207cff1.sparta_27750a1549(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
def sparta_068335bd08(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_344207cff1.sparta_068335bd08(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
def sparta_ea1c4c6bfe(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_344207cff1.sparta_ea1c4c6bfe(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
def sparta_8fb21d3c10(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_344207cff1.sparta_8fb21d3c10(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
def sparta_7006fc4c6e(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_344207cff1.dashboard_project_explorer_delete_multiple_resources(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
def sparta_fbbd9801b3(request):A=request;B=A.POST.dict();C=A.FILES;D=qube_344207cff1.sparta_fbbd9801b3(B,A.user,C['files[]']);E=json.dumps(D);return HttpResponse(E)
def sparta_73ed5fabf2(path):
	A=path;A=os.path.normpath(A)
	if os.path.isfile(A):A=os.path.dirname(A)
	return os.path.basename(A)
def sparta_19cf179865(path):A=path;A=os.path.normpath(A);return os.path.basename(A)
@csrf_exempt
@sparta_5c61c65841
def sparta_39bc821b15(request):
	E='pathResource';A=request;B=A.GET[E];B=base64.b64decode(B).decode(_D);F=A.GET[_B];G=A.GET[_C];H=sparta_19cf179865(B);I={E:B,_C:G,_B:base64.b64decode(F).decode(_D)};C=qube_344207cff1.sparta_9c7e5dcd80(I,A.user)
	if C['res']==1:
		try:
			with open(C['fullPath'],'rb')as J:D=HttpResponse(J.read(),content_type='application/force-download');D[_E]='attachment; filename='+str(H);return D
		except Exception as K:pass
	raise Http404
@csrf_exempt
@sparta_5c61c65841
def sparta_5175bba386(request):
	D='attachment; filename={0}';B=request;E=B.GET[_C];F=B.GET[_B];G={_C:E,_B:base64.b64decode(F).decode(_D)};C=qube_344207cff1.sparta_beb06bf02c(G,B.user)
	if C['res']==1:H=C['zip'];I=C['zipName'];A=HttpResponse();A.write(H.getvalue());A[_E]=D.format(f"{I}.zip")
	else:A=HttpResponse();J='Could not download the application, please try again';K='error.txt';A.write(J);A[_E]=D.format(K)
	return A
@csrf_exempt
@sparta_5c61c65841
@sparta_dacedd4e08
def sparta_f3fccc5174(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_11f6eef4bd.sparta_f3fccc5174(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
@sparta_dacedd4e08
def sparta_349ce76626(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_11f6eef4bd.sparta_349ce76626(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
@sparta_dacedd4e08
def sparta_8731a2ad33(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_11f6eef4bd.sparta_8731a2ad33(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
@sparta_dacedd4e08
def sparta_016853fbec(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_11f6eef4bd.sparta_016853fbec(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
@sparta_dacedd4e08
def sparta_d417f72b8a(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_11f6eef4bd.sparta_d417f72b8a(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
@sparta_dacedd4e08
def sparta_de49abdcb3(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_11f6eef4bd.sparta_de49abdcb3(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
@sparta_dacedd4e08
def sparta_0d18b52802(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_11f6eef4bd.sparta_0d18b52802(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
@sparta_dacedd4e08
def sparta_779b4ac7dc(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_11f6eef4bd.sparta_779b4ac7dc(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
@sparta_dacedd4e08
def sparta_ab5de752d5(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_11f6eef4bd.sparta_ab5de752d5(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
@sparta_dacedd4e08
def sparta_46c5a531cf(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_11f6eef4bd.sparta_46c5a531cf(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
@sparta_dacedd4e08
def sparta_c47685e302(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_11f6eef4bd.sparta_c47685e302(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
@sparta_dacedd4e08
def sparta_ed572beed7(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_11f6eef4bd.sparta_ed572beed7(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
@sparta_dacedd4e08
def sparta_fccd060073(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_11f6eef4bd.sparta_fccd060073(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
@sparta_dacedd4e08
def sparta_955b40b189(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_11f6eef4bd.sparta_955b40b189(C,A.user);E=json.dumps(D);return HttpResponse(E)