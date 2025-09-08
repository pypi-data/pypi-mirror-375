from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from project.sparta_5354ac8663.sparta_52de0601a4.qube_1199e87c92 import sparta_8345ad4652
from project.sparta_5354ac8663.sparta_9505888039 import qube_ff88198fc7 as qube_ff88198fc7
from project.models import UserProfile
import project.sparta_62bcd16a7d.sparta_8de12faf71.qube_6e0e558b60 as qube_6e0e558b60
@sparta_8345ad4652
@login_required(redirect_field_name='login')
def sparta_475a5a2259(request):
	E='avatarImg';B=request;A=qube_6e0e558b60.sparta_4d05c20ea8(B);A['menuBar']=-1;F=qube_6e0e558b60.sparta_ea67d6b805(B.user);A.update(F);A[E]='';C=UserProfile.objects.filter(user=B.user)
	if C.count()>0:
		D=C[0];G=D.avatar
		if G is not None:H=D.avatar.image64;A[E]=H
	A['bInvertIcon']=0;return render(B,'dist/project/helpCenter/helpCenter.html',A)
@sparta_8345ad4652
@login_required(redirect_field_name='login')
def sparta_fcd817f2a6(request):
	A=request;B=UserProfile.objects.filter(user=A.user)
	if B.count()>0:C=B[0];C.has_open_tickets=False;C.save()
	return sparta_475a5a2259(A)