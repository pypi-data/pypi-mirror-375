_C='isAuth'
_B='jsonData'
_A='res'
import json
from django.contrib.auth import logout
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from project.sparta_5354ac8663.sparta_52de0601a4 import qube_1199e87c92 as qube_1199e87c92
from project.sparta_62bcd16a7d.sparta_8de12faf71.qube_6e0e558b60 import sparta_db79d492ef
from project.logger_config import logger
@csrf_exempt
def sparta_40396c67db(request):A=json.loads(request.body);B=json.loads(A[_B]);return qube_1199e87c92.sparta_40396c67db(B)
@csrf_exempt
def sparta_1eb60b71e2(request):logout(request);A={_A:1};B=json.dumps(A);return HttpResponse(B)
@csrf_exempt
def sparta_a5201b55b0(request):
	if request.user.is_authenticated:A=1
	else:A=0
	B={_A:1,_C:A};C=json.dumps(B);return HttpResponse(C)
def sparta_97d72437ef(request):
	B=request;from django.contrib.auth import authenticate as F,login;from django.contrib.auth.models import User as C;G=json.loads(B.body);D=json.loads(G[_B]);H=D['email'];I=D['password'];E=0
	try:
		A=C.objects.get(email=H);A=F(B,username=A.username,password=I)
		if A is not None:login(B,A);E=1
	except C.DoesNotExist:pass
	J={_A:1,_C:E};K=json.dumps(J);return HttpResponse(K)