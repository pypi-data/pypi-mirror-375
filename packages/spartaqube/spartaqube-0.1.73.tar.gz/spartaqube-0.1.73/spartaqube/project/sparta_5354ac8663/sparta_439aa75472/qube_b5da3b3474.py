_A=False
import re,os,json,requests
from datetime import datetime
from packaging.version import parse
from project.models import AppVersioning
from project.logger_config import logger
import pytz
UTC=pytz.utc
proxies_dict={'http':os.environ.get('http_proxy',None),'https':os.environ.get('https_proxy',None)}
def sparta_28025b541c():0
def sparta_bc65d2721d():A='name';B='https://api.github.com/repos/SpartaQube/spartaqube-version/tags';C=requests.get(B,proxies=proxies_dict,verify=_A);D=json.loads(C.text);E=max(D,key=lambda t:parse(t[A]));return E[A]
def sparta_69b3ea6b29():A='https://spartaqube-version.pages.dev/latest_version.txt';B=requests.get(A,proxies=proxies_dict,verify=_A,timeout=1);return B.text.split('\n')[0]
def sparta_c820eee9e5():A='https://spartaqube-version.pages.dev/latest_features.json';B=requests.get(A,proxies=proxies_dict,verify=_A,timeout=1);return json.loads(B.text)
def sparta_69eb10bcaf():
	try:A='https://pypi.org/project/spartaqube/';B=requests.get(A,proxies=proxies_dict,verify=_A).text;C=re.search('<h1 class="package-header__name">(.*?)</h1>',B,re.DOTALL);D=C.group(1);E=D.strip().split('spartaqube ')[1];return E
	except:pass
def sparta_f7bf9a61de():
	B=os.path.dirname(__file__);C=os.path.dirname(B);D=os.path.dirname(C);E=os.path.dirname(D)
	try:
		with open(os.path.join(E,'app_version.json'),'r')as F:G=json.load(F);A=G['version']
	except:A='0.1.1'
	return A
def sparta_7431c44234():
	I='res'
	try:
		C=sparta_f7bf9a61de();A=sparta_69b3ea6b29();D=AppVersioning.objects.all();E=datetime.now().astimezone(UTC)
		if D.count()==0:AppVersioning.objects.create(last_available_version_pip=A,last_check_date=E)
		else:B=D[0];B.last_available_version_pip=A;B.last_check_date=E;B.save()
		F=not C==A;G=[]
		if F:J=sparta_c820eee9e5();G=J['features']
		return{'current_version':C,'latest_version':A,'latest_features_list':G,'b_update':F,'humanDate':'A moment ago',I:1}
	except Exception as H:logger.debug('Exception versioning update');logger.debug(H);return{I:-1,'errorMsg':str(H)}