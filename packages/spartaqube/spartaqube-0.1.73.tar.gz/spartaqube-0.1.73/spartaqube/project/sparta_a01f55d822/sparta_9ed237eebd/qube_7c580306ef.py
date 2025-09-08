_A='jsonData'
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
from project.models import UserProfile
from project.sparta_5354ac8663.sparta_c38b5baf3c import qube_1309e5eeb5 as qube_1309e5eeb5
from project.sparta_5354ac8663.sparta_9505888039 import qube_ff88198fc7 as qube_ff88198fc7
from project.sparta_5354ac8663.sparta_52de0601a4.qube_1199e87c92 import sparta_5c61c65841
@csrf_exempt
@sparta_5c61c65841
def sparta_8abec88f26(request):
	B=request;I=json.loads(B.body);C=json.loads(I[_A]);A=B.user;D=0;E=UserProfile.objects.filter(user=A)
	if E.count()>0:
		F=E[0]
		if F.has_open_tickets:
			C['userId']=F.user_profile_id;G=qube_ff88198fc7.sparta_8165b1e2e2(A)
			if G['res']==1:D=int(G['nbNotifications'])
	H=qube_1309e5eeb5.sparta_8abec88f26(C,A);H['nbNotificationsHelpCenter']=D;J=json.dumps(H);return HttpResponse(J)
@csrf_exempt
@sparta_5c61c65841
def sparta_9ecadc75bc(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_1309e5eeb5.sparta_f487a8ee1f(C,A.user);E=json.dumps(D);return HttpResponse(E)