import os,json,getpass,platform
from pathlib import Path
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
import project.sparta_62bcd16a7d.sparta_8de12faf71.qube_6e0e558b60 as qube_6e0e558b60
from project.sparta_5354ac8663.sparta_52de0601a4.qube_1199e87c92 import sparta_8345ad4652
from project.sparta_5354ac8663.sparta_b8b7994f57 import qube_6ee1b476a3 as qube_6ee1b476a3
from project.sparta_5354ac8663.sparta_d63ac0c595 import qube_a2bec951ae as qube_a2bec951ae
def sparta_0368e4aa96():
	A=platform.system()
	if A=='Windows':return'windows'
	elif A=='Linux':return'linux'
	elif A=='Darwin':return'mac'
	else:return
@csrf_exempt
@sparta_8345ad4652
@login_required(redirect_field_name='login')
def sparta_becdc80cf4(request):
	E='template';D='developer';B=request
	if not conf_settings.IS_DEV_VIEW_ENABLED:A=qube_6e0e558b60.sparta_4d05c20ea8(B);return render(B,'dist/project/homepage/homepage.html',A)
	A=qube_6e0e558b60.sparta_4d05c20ea8(B);A['menuBar']=12;F=qube_6e0e558b60.sparta_ea67d6b805(B.user);A.update(F);A['bCodeMirror']=True;G=os.path.dirname(__file__);C=os.path.dirname(os.path.dirname(G));H=os.path.join(C,'static');I=os.path.join(H,'js',D,E,'frontend');A['frontend_path']=I;J=os.path.dirname(C);K=os.path.join(J,'django_app_template',D,E,'backend');A['backend_path']=K;return render(B,'dist/project/developer/developerExamples.html',A)