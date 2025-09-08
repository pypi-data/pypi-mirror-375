_I='error.txt'
_H='zipName'
_G='utf-8'
_F='attachment; filename={0}'
_E='appId'
_D='res'
_C='Content-Disposition'
_B='projectPath'
_A='jsonData'
import json,base64
from django.http import HttpResponse,Http404
from django.views.decorators.csrf import csrf_exempt
from project.sparta_5354ac8663.sparta_cb71be64a2 import qube_eb6d552caa as qube_eb6d552caa
from project.sparta_5354ac8663.sparta_cb71be64a2 import qube_9db6b66db0 as qube_9db6b66db0
from project.sparta_5354ac8663.sparta_82fa1097b7 import qube_4a8aaacb65 as qube_4a8aaacb65
from project.sparta_5354ac8663.sparta_52de0601a4.qube_1199e87c92 import sparta_5c61c65841
@csrf_exempt
@sparta_5c61c65841
def sparta_28c0c183dd(request):
	D='files[]';A=request;E=A.POST.dict();B=A.FILES
	if D in B:C=qube_eb6d552caa.sparta_3c8c9d83b3(E,A.user,B[D])
	else:C={_D:1}
	F=json.dumps(C);return HttpResponse(F)
@csrf_exempt
@sparta_5c61c65841
def sparta_b0645db80d(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_eb6d552caa.sparta_161aff7626(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
def sparta_349df9815d(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_eb6d552caa.sparta_1c9ef740c9(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
def sparta_4d761183da(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_eb6d552caa.sparta_34b39f9e19(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
def sparta_fecf187ef0(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_9db6b66db0.sparta_f76688f23b(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
def sparta_89b5f36419(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_eb6d552caa.sparta_a94fd7514d(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
def sparta_d80f7d850c(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_eb6d552caa.sparta_950209ca9c(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
def sparta_11b5f0d391(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_eb6d552caa.sparta_c0b8f3011b(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
def sparta_6ace9530f9(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_eb6d552caa.sparta_ee2f582727(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
def sparta_56d8f89f08(request):
	F='filePath';E='fileName';A=request;B=A.GET[E];G=A.GET[F];H=A.GET[_B];I=A.GET[_E];J={E:B,F:G,_E:I,_B:base64.b64decode(H).decode(_G)};C=qube_eb6d552caa.sparta_9c7e5dcd80(J,A.user)
	if C[_D]==1:
		try:
			with open(C['fullPath'],'rb')as K:D=HttpResponse(K.read(),content_type='application/force-download');D[_C]='attachment; filename='+str(B);return D
		except Exception as L:pass
	raise Http404
@csrf_exempt
@sparta_5c61c65841
def sparta_2a3fdf7ba8(request):
	E='folderName';B=request;F=B.GET[_B];D=B.GET[E];G={_B:base64.b64decode(F).decode(_G),E:D};C=qube_eb6d552caa.sparta_d5f9ba6c96(G,B.user)
	if C[_D]==1:H=C['zip'];I=C[_H];A=HttpResponse();A.write(H.getvalue());A[_C]=_F.format(f"{I}.zip")
	else:A=HttpResponse();J=f"Could not download the folder {D}, please try again";K=_I;A.write(J);A[_C]=_F.format(K)
	return A
@csrf_exempt
@sparta_5c61c65841
def sparta_e5400bdd8a(request):
	B=request;D=B.GET[_E];E=B.GET[_B];F={_E:D,_B:base64.b64decode(E).decode(_G)};C=qube_eb6d552caa.sparta_beb06bf02c(F,B.user)
	if C[_D]==1:G=C['zip'];H=C[_H];A=HttpResponse();A.write(G.getvalue());A[_C]=_F.format(f"{H}.zip")
	else:A=HttpResponse();I='Could not download the application, please try again';J=_I;A.write(I);A[_C]=_F.format(J)
	return A