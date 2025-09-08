import re,os,json,stat,importlib,io,sys,subprocess,platform,base64,traceback,uuid,shutil
from pathlib import Path
from django.db.models import Q
from django.utils.text import slugify
from datetime import datetime,timedelta
import pytz
UTC=pytz.utc
from spartaqube_app.path_mapper_obf import sparta_4333278bd8
from project.models import ShareRights
from project.sparta_5354ac8663.sparta_c0f904d512 import qube_ac67c5d252 as qube_ac67c5d252
from project.sparta_5354ac8663.sparta_b8b7994f57 import qube_98ef18f3d2 as qube_98ef18f3d2
from project.sparta_5354ac8663.sparta_f5fe72cd94.qube_d156d5fc7b import Connector as Connector
from project.sparta_5354ac8663.sparta_d58392c7f1 import qube_3a003c75c0 as qube_3a003c75c0
from project.sparta_5354ac8663.sparta_82fa1097b7.qube_4a8aaacb65 import sparta_ff0e80d635
from project.sparta_5354ac8663.sparta_218a0b6e71 import qube_d14205c11b as qube_d14205c11b
from project.sparta_5354ac8663.sparta_218a0b6e71 import qube_629b3780b6 as qube_629b3780b6
from project.sparta_5354ac8663.sparta_439aa75472.qube_b5da3b3474 import sparta_f7bf9a61de
from project.sparta_5354ac8663.sparta_82fa1097b7.qube_2ead1b4bcb import sparta_a3ffb5d42e,sparta_82e779a082
from project.logger_config import logger
from project.sparta_5354ac8663.sparta_82fa1097b7.qube_0e647c534b import sparta_fba3132a9a
from project.sparta_5354ac8663.sparta_48a83eeec3 import qube_b2f294a307 as qube_b2f294a307
def sparta_fd87ef2187(user_obj):
	A=qube_ac67c5d252.sparta_3530108797(user_obj)
	if len(A)>0:B=[A.user_group for A in A]
	else:B=[]
	return B
def sparta_9fff090717(json_data,user_obj):A=json_data;A['is_plot_db']=True;return qube_b2f294a307.sparta_8d31a82e30(A,user_obj)
def sparta_cca70e053f():
	B=sparta_fba3132a9a();A=os.path.join(B,'plot_db_developer')
	def C(path):
		A=Path(path)
		if not A.exists():A.mkdir(parents=True)
	C(A);return{'res':1,'path':A}