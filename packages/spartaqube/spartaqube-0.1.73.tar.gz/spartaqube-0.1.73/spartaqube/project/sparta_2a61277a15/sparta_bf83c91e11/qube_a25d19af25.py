_P='Please send valid data'
_O='dist/project/auth/resetPasswordChange.html'
_N='captcha'
_M='cypress_tests@gmail.com'
_L='password'
_K='POST'
_J=False
_I='login'
_H='error'
_G='form'
_F='email'
_E='res'
_D='home'
_C='manifest'
_B='errorMsg'
_A=True
import json,hashlib,uuid
from datetime import datetime
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
from django.urls import reverse
import project.sparta_62bcd16a7d.sparta_8de12faf71.qube_6e0e558b60 as qube_6e0e558b60
from project.forms import ConnexionForm,RegistrationTestForm,RegistrationBaseForm,RegistrationForm,ResetPasswordForm,ResetPasswordChangeForm
from project.sparta_5354ac8663.sparta_52de0601a4.qube_1199e87c92 import sparta_8345ad4652
from project.sparta_5354ac8663.sparta_52de0601a4 import qube_1199e87c92 as qube_1199e87c92
from project.sparta_a01f55d822.sparta_9bb7eeac26 import qube_2a57ba1860 as qube_2a57ba1860
from project.models import LoginLocation,UserProfile
from project.logger_config import logger
def sparta_a4723bc181():return{'bHasCompanyEE':-1}
def sparta_6dd7515f46(request):B=request;A=qube_6e0e558b60.sparta_4d05c20ea8(B);A[_C]=qube_6e0e558b60.sparta_4dabcfaf6f();A['forbiddenEmail']=conf_settings.FORBIDDEN_EMAIL;return render(B,'dist/project/auth/banned.html',A)
@sparta_8345ad4652
def sparta_b86cc6c3cd(request):
	C=request;B='/';A=C.GET.get(_I)
	if A is not None:D=A.split(B);A=B.join(D[1:]);A=A.replace(B,'$@$')
	return sparta_8f0a80f63f(C,A)
def sparta_dae2ff6e9e(request,redirectUrl):return sparta_8f0a80f63f(request,redirectUrl)
def sparta_8f0a80f63f(request,redirectUrl):
	E=redirectUrl;A=request;logger.debug('Welcome to loginRedirectFunc')
	if A.user.is_authenticated:return redirect(_D)
	G=_J;H='Email or password incorrect'
	if A.method==_K:
		C=ConnexionForm(A.POST)
		if C.is_valid():
			I=C.cleaned_data[_F];J=C.cleaned_data[_L];F=authenticate(username=I,password=J)
			if F:
				if qube_1199e87c92.sparta_dbbecdd685(F):return sparta_6dd7515f46(A)
				login(A,F);K,L=qube_6e0e558b60.sparta_a772e67a31();LoginLocation.objects.create(user=F,hostname=K,ip=L,date_login=datetime.now())
				if E is not None:
					D=E.split('$@$');D=[A for A in D if len(A)>0]
					if len(D)>1:M=D[0];return redirect(reverse(M,args=D[1:]))
					return redirect(E)
				return redirect(_D)
			else:G=_A
		else:G=_A
	C=ConnexionForm();B=qube_6e0e558b60.sparta_4d05c20ea8(A);B.update(qube_6e0e558b60.sparta_0472815ab1(A));B[_C]=qube_6e0e558b60.sparta_4dabcfaf6f();B[_G]=C;B[_H]=G;B['redirectUrl']=E;B[_B]=H;B.update(sparta_a4723bc181());return render(A,'dist/project/auth/login.html',B)
def sparta_f326eefb45(request):
	B='public@spartaqube.com';A=User.objects.filter(email=B).all()
	if A.count()>0:C=A[0];login(request,C)
	return redirect(_D)
@sparta_8345ad4652
def sparta_ed34c468d5(request):
	A=request
	if A.user.is_authenticated:return redirect(_D)
	E='';D=_J;F=qube_1199e87c92.sparta_d0dbc5e23e()
	if A.method==_K:
		if F:B=RegistrationForm(A.POST)
		else:B=RegistrationBaseForm(A.POST)
		if B.is_valid():
			I=B.cleaned_data;H=None
			if F:
				H=B.cleaned_data['code']
				if not qube_1199e87c92.sparta_a788f246b3(H):D=_A;E='Wrong guest code'
			if not D:
				J=A.META['HTTP_HOST'];G=qube_1199e87c92.sparta_40396c67db(I,J)
				if int(G[_E])==1:K=G['userObj'];login(A,K);return redirect(_D)
				else:D=_A;E=G[_B]
		else:D=_A;E=B.errors.as_data()
	if F:B=RegistrationForm()
	else:B=RegistrationBaseForm()
	C=qube_6e0e558b60.sparta_4d05c20ea8(A);C.update(qube_6e0e558b60.sparta_0472815ab1(A));C[_C]=qube_6e0e558b60.sparta_4dabcfaf6f();C[_G]=B;C[_H]=D;C[_B]=E;C.update(sparta_a4723bc181());return render(A,'dist/project/auth/registration.html',C)
def sparta_c306ff5d5b(request):A=request;B=qube_6e0e558b60.sparta_4d05c20ea8(A);B[_C]=qube_6e0e558b60.sparta_4dabcfaf6f();return render(A,'dist/project/auth/registrationPending.html',B)
def sparta_7f028b2261(request,token):
	A=request;B=qube_1199e87c92.sparta_9e169dd1e0(token)
	if int(B[_E])==1:C=B['user'];login(A,C);return redirect(_D)
	D=qube_6e0e558b60.sparta_4d05c20ea8(A);D[_C]=qube_6e0e558b60.sparta_4dabcfaf6f();return redirect(_I)
def sparta_1fa26a7318(request):logout(request);return redirect(_I)
def sparta_8ca8b4944b():
	from project.models import PlotDBChartShared as B,PlotDBChart,DashboardShared as C,NotebookShared as D,KernelShared as E,DBConnectorUserShared as F;A=_M;print('Destroy cypress user');G=B.objects.filter(user__email=A).all()
	for H in G:H.delete()
	I=C.objects.filter(user__email=A).all()
	for J in I:J.delete()
	K=D.objects.filter(user__email=A).all()
	for L in K:L.delete()
	M=E.objects.filter(user__email=A).all()
	for N in M:N.delete()
	O=F.objects.filter(user__email=A).all()
	for P in O:P.delete()
def sparta_9d94569ce4(request):
	A=request;B=_M;sparta_8ca8b4944b();from project.sparta_5354ac8663.sparta_cf948f0aee.qube_26db0d415a import sparta_2eadef071a as C;C()
	if A.user.is_authenticated:
		if A.user.email==B:A.user.delete()
	logout(A);return redirect(_I)
def sparta_588a2369b3(request):A={_E:-100,_B:'You are not logged...'};B=json.dumps(A);return HttpResponse(B)
@csrf_exempt
def sparta_012db86841(request):
	A=request;E='';F=_J
	if A.method==_K:
		B=ResetPasswordForm(A.POST)
		if B.is_valid():
			H=B.cleaned_data[_F];I=B.cleaned_data[_N];G=qube_1199e87c92.sparta_012db86841(H.lower(),I)
			try:
				if int(G[_E])==1:C=qube_6e0e558b60.sparta_4d05c20ea8(A);C.update(qube_6e0e558b60.sparta_0472815ab1(A));B=ResetPasswordChangeForm(A.POST);C[_C]=qube_6e0e558b60.sparta_4dabcfaf6f();C[_G]=B;C[_F]=H;C[_H]=F;C[_B]=E;return render(A,_O,C)
				elif int(G[_E])==-1:E=G[_B];F=_A
			except Exception as J:logger.debug('exception ');logger.debug(J);E='Could not send reset email, please try again';F=_A
		else:E=_P;F=_A
	else:B=ResetPasswordForm()
	D=qube_6e0e558b60.sparta_4d05c20ea8(A);D.update(qube_6e0e558b60.sparta_0472815ab1(A));D[_C]=qube_6e0e558b60.sparta_4dabcfaf6f();D[_G]=B;D[_H]=F;D[_B]=E;D.update(sparta_a4723bc181());return render(A,'dist/project/auth/resetPassword.html',D)
@csrf_exempt
def sparta_0dea1b185f(request):
	D=request;E='';B=_J
	if D.method==_K:
		C=ResetPasswordChangeForm(D.POST)
		if C.is_valid():
			I=C.cleaned_data['token'];F=C.cleaned_data[_L];J=C.cleaned_data['password_confirmation'];K=C.cleaned_data[_N];G=C.cleaned_data[_F].lower()
			if len(F)<6:E='Your password must be at least 6 characters';B=_A
			if F!=J:E='The two passwords must be identical...';B=_A
			if not B:
				H=qube_1199e87c92.sparta_0dea1b185f(K,I,G.lower(),F)
				try:
					if int(H[_E])==1:L=User.objects.get(username=G);login(D,L);return redirect(_D)
					else:E=H[_B];B=_A
				except Exception as M:E='Could not change your password, please try again';B=_A
		else:E=_P;B=_A
	else:return redirect('reset-password')
	A=qube_6e0e558b60.sparta_4d05c20ea8(D);A.update(qube_6e0e558b60.sparta_0472815ab1(D));A[_C]=qube_6e0e558b60.sparta_4dabcfaf6f();A[_G]=C;A[_H]=B;A[_B]=E;A[_F]=G;A.update(sparta_a4723bc181());return render(D,_O,A)