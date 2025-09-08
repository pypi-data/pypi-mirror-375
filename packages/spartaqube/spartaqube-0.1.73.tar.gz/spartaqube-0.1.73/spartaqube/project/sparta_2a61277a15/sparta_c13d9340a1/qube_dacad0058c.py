from urllib.parse import urlparse,urlunparse
from django.contrib.auth.decorators import login_required
from django.conf import settings as conf_settings
from django.shortcuts import render
import project.sparta_62bcd16a7d.sparta_8de12faf71.qube_6e0e558b60 as qube_6e0e558b60
from project.models import UserProfile
from project.sparta_5354ac8663.sparta_52de0601a4.qube_1199e87c92 import sparta_8345ad4652
from project.sparta_2a61277a15.sparta_bf83c91e11.qube_a25d19af25 import sparta_a4723bc181
@sparta_8345ad4652
@login_required(redirect_field_name='login')
def sparta_76d7c05198(request,idSection=1):
	B=request;D=UserProfile.objects.get(user=B.user);E=D.avatar
	if E is not None:E=D.avatar.avatar
	C=urlparse(conf_settings.URL_TERMS)
	if not C.scheme:C=urlunparse(C._replace(scheme='http'))
	G={'item':1,'idSection':idSection,'userProfil':D,'avatar':E,'url_terms':C};A=qube_6e0e558b60.sparta_4d05c20ea8(B);A.update(qube_6e0e558b60.sparta_ea67d6b805(B.user));A.update(G);H='';A['accessKey']=H;A['menuBar']=4;A.update(sparta_a4723bc181());F=True
	if B.headers.get('HX-Request')=='true':F=False
	A['bFullRender']=F;return render(B,'dist/project/auth/settings.html',A)