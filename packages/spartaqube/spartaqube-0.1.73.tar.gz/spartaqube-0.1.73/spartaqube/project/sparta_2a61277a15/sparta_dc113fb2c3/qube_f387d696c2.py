from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf import settings as conf_settings
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import hashlib,project.sparta_62bcd16a7d.sparta_8de12faf71.qube_6e0e558b60 as qube_6e0e558b60
from project.sparta_5354ac8663.sparta_52de0601a4.qube_1199e87c92 import sparta_8345ad4652
@csrf_exempt
def sparta_69c91a8bfc(request):
	B=request;A=qube_6e0e558b60.sparta_4d05c20ea8(B);A['menuBar']=8;A['bCodeMirror']=True;D=qube_6e0e558b60.sparta_ea67d6b805(B.user);A.update(D);C=True
	if B.headers.get('HX-Request')=='true':C=False
	A['bFullRender']=C;return render(B,'dist/project/api/api.html',A)