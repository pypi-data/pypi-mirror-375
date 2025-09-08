import json,base64
from django.http import HttpResponse,Http404
from django.views.decorators.csrf import csrf_exempt
from project.sparta_5354ac8663.sparta_24eeefa0b1 import qube_725daf7a9d as qube_725daf7a9d
from project.sparta_5354ac8663.sparta_52de0601a4.qube_1199e87c92 import sparta_5c61c65841
@csrf_exempt
@sparta_5c61c65841
def sparta_2fa345d2e9(request):G='api_func';F='key';E='utf-8';A=request;C=A.body.decode(E);C=A.POST.get(F);D=A.body.decode(E);D=A.POST.get(G);B=dict();B[F]=C;B[G]=D;H=qube_725daf7a9d.sparta_2fa345d2e9(B,A.user);I=json.dumps(H);return HttpResponse(I)