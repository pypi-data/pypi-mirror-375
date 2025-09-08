_A='jsonData'
import json,inspect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.hashers import make_password
from project.sparta_5354ac8663.sparta_c8f7428e65 import qube_fe5cc7a964 as qube_fe5cc7a964
from project.sparta_5354ac8663.sparta_52de0601a4.qube_1199e87c92 import sparta_5c61c65841
def sparta_d3ef7fc66c(request):A={'res':1};B=json.dumps(A);return HttpResponse(B)
@csrf_exempt
@sparta_5c61c65841
def sparta_7e88767b35(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_fe5cc7a964.sparta_7e88767b35(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
def sparta_1514f33223(request):
	C='userObj';B=request;D=json.loads(B.body);E=json.loads(D[_A]);F=B.user;A=qube_fe5cc7a964.sparta_1514f33223(E,F)
	if A['res']==1:
		if C in list(A.keys()):login(B,A[C]);A.pop(C,None)
	G=json.dumps(A);return HttpResponse(G)
@csrf_exempt
@sparta_5c61c65841
def sparta_209c649895(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=A.user;E=qube_fe5cc7a964.sparta_209c649895(C,D);F=json.dumps(E);return HttpResponse(F)
@csrf_exempt
@sparta_5c61c65841
def sparta_674e9b0d2f(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_fe5cc7a964.sparta_674e9b0d2f(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
def sparta_4c115ba4d0(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_fe5cc7a964.sparta_4c115ba4d0(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_5c61c65841
def sparta_7cff604845(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_fe5cc7a964.sparta_7cff604845(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
def sparta_b275bd2f47(request):A=json.loads(request.body);B=json.loads(A[_A]);C=qube_fe5cc7a964.token_reset_password_worker(B);D=json.dumps(C);return HttpResponse(D)
@csrf_exempt
@sparta_5c61c65841
def sparta_7c12dbdade(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_fe5cc7a964.network_master_reset_password(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
def sparta_798c500495(request):A=json.loads(request.body);B=json.loads(A[_A]);C=qube_fe5cc7a964.sparta_798c500495(B);D=json.dumps(C);return HttpResponse(D)
@csrf_exempt
def sparta_cad2971fdf(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_fe5cc7a964.sparta_cad2971fdf(A,C);E=json.dumps(D);return HttpResponse(E)