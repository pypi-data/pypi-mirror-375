_h='token_permission'
_g='plot_db_chart_obj'
_f='fullPath'
_e='thumbnail'
_d='static'
_c='previewImage'
_b='plotDBProgrammaticAttributes'
_a='itemId'
_Z='itemType'
_Y='gridConfig'
_X='dashboardSlug'
_W='isDashboardPublic'
_V='isDashboardExpose'
_U='dashboardDescription'
_T='mainIpynbFullPath'
_S='dashboardPassword'
_R='main_ipynb_fullpath'
_Q='json_data'
_P='is_public_dashboard'
_O='has_password'
_N='is_expose_dashboard'
_M='description'
_L='luminoLayout'
_K='hasDashboardPassword'
_J='dashboard'
_I='dashboardName'
_H='dashboard_id'
_G='dashboardId'
_F='errorMsg'
_E='dashboard_obj'
_D=True
_C=False
_B=None
_A='res'
import re,os,json,io,sys,base64,traceback,uuid
from django.db.models import Q
from django.utils.text import slugify
from datetime import datetime,timedelta
import pytz
UTC=pytz.utc
from project.models_spartaqube import Dashboard,DashboardShared,PlotDBChart,PlotDBPermission,DataFrameHistory,DataFrameShared,DataFrameModel,DataFramePermission
from project.models import ShareRights
from project.sparta_5354ac8663.sparta_c0f904d512 import qube_ac67c5d252 as qube_ac67c5d252
from project.sparta_5354ac8663.sparta_b8b7994f57 import qube_98ef18f3d2 as qube_98ef18f3d2
from project.sparta_5354ac8663.sparta_f5fe72cd94.qube_d156d5fc7b import Connector as Connector
from project.sparta_5354ac8663.sparta_b8b7994f57.qube_6ee1b476a3 import sparta_f6caba58f6
from project.sparta_5354ac8663.sparta_82fa1097b7.qube_3713da2649 import sparta_416d6d8c82
from project.sparta_5354ac8663.sparta_d58392c7f1 import qube_3a003c75c0 as qube_3a003c75c0
from project.sparta_5354ac8663.sparta_82fa1097b7.qube_4a8aaacb65 import sparta_ff0e80d635
from project.sparta_5354ac8663.sparta_218a0b6e71 import qube_d14205c11b as qube_d14205c11b
from project.sparta_5354ac8663.sparta_439aa75472.qube_b5da3b3474 import sparta_f7bf9a61de
from project.logger_config import logger
def sparta_fd87ef2187(user_obj):
	A=qube_ac67c5d252.sparta_3530108797(user_obj)
	if len(A)>0:B=[A.user_group for A in A]
	else:B=[]
	return B
def sparta_4090b899fe(json_data,user_obj):
	K='%Y-%m-%d';J='Recently used';D=user_obj;F=sparta_fd87ef2187(D)
	if len(F)>0:A=DashboardShared.objects.filter(Q(is_delete=0,user_group__in=F,dashboard__is_delete=0)|Q(is_delete=0,user=D,dashboard__is_delete=0))
	else:A=DashboardShared.objects.filter(is_delete=0,user=D,dashboard__is_delete=0)
	if A.count()>0:
		C=json_data.get('orderBy',J)
		if C==J:A=A.order_by('-dashboard__last_date_used')
		elif C=='Date desc':A=A.order_by('-dashboard__last_update')
		elif C=='Date asc':A=A.order_by('dashboard__last_update')
		elif C=='Name desc':A=A.order_by('-dashboard__name')
		elif C=='Name asc':A=A.order_by('dashboard__name')
	G=[]
	for E in A:
		B=E.dashboard;L=E.share_rights;H=_B
		try:H=str(B.last_update.strftime(K))
		except:pass
		I=_B
		try:I=str(B.date_created.strftime(K))
		except Exception as M:logger.debug(M)
		G.append({_H:B.dashboard_id,'name':B.name,'slug':B.slug,_M:B.description,_N:B.is_expose_dashboard,_O:B.has_password,_P:B.is_public_dashboard,'is_owner':E.is_owner,'has_write_rights':L.has_write_rights,'last_update':H,'date_created':I})
	return{_A:1,'dashboard_library':G}
def sparta_9fa793fddf(json_data,user_obj):
	E=json_data;C=user_obj;logger.debug(_Q);logger.debug(E);D=E[_G];G=E.get('modalPassword',_B)
	if not C.is_anonymous:
		F=Dashboard.objects.filter(dashboard_id__startswith=D,is_delete=_C).all()
		if F.count()==1:
			A=F[F.count()-1];D=A.dashboard_id;B=has_dashboard_access(D,C,password_dashboard=G)
			if B[_A]!=1:return{_A:B[_A],_F:B[_F]}
		else:return{_A:-1,_F:'Dashboard not found...'}
	else:
		B=has_dashboard_access(D,C,password_dashboard=G)
		if B[_A]!=1:return{_A:B[_A],_F:B.get(_F,'You do not have access to this dashboard')}
		A=B[_E]
	if not C.is_anonymous:
		I=DashboardShared.objects.filter(is_owner=_D,dashboard=A,user=C)
		if I.count()>0:J=datetime.now().astimezone(UTC);A.last_date_used=J;A.save()
	H=dict()
	if A.plot_db_programmatic_attributes is not _B:H=json.loads(A.plot_db_programmatic_attributes)
	return{_A:1,_J:{'basic':{_H:A.dashboard_id,'name':A.name,'slug':A.slug,_M:A.description,_N:A.is_expose_dashboard,_P:A.is_public_dashboard,_O:A.has_password,'dashboard_venv':A.dashboard_venv,'project_path':A.project_path},'lumino':{'main_ipynb_filename':os.path.basename(A.main_ipynb_fullpath),_R:A.main_ipynb_fullpath,'lumino_layout':A.lumino_layout,'notebook_cells':qube_d14205c11b.sparta_4ccd22aeaf(A.main_ipynb_fullpath)},'grid_config':json.loads(A.grid_config),'plot_db_programmatic_attributes':H}}
def sparta_fe4eb439eb(json_data,user_obj):
	J=user_obj;A=json_data;R=A['isNewDashboard']
	if not R:return sparta_432b81a754(A,J)
	C=datetime.now().astimezone(UTC);K=str(uuid.uuid4());H=A[_K];E=_B
	if H:E=A[_S];E=qube_98ef18f3d2.sparta_18bc87529f(E)
	S=A[_L];L=A[_T];T=A[_I];U=A[_U];D=A['projectPath'];D=sparta_ff0e80d635(D);V=A[_V];W=A[_W];H=A[_K];X=A.get('dashboardVenv',_B);B=A[_X]
	if len(B)==0:B=A[_I]
	M=slugify(B);B=M;N=1
	while Dashboard.objects.filter(slug=B).exists():B=f"{M}-{N}";N+=1
	O=A[_Y];F=[]
	for(g,Y)in O.items():
		for P in Y:
			if P[_Z]==1:F.append(P[_a])
	F=list(set(F));Z=A[_b];I=_B;G=A.get(_c,_B)
	if G is not _B:
		try:
			G=G.split(',')[1];a=base64.b64decode(G);b=os.path.dirname(__file__);D=os.path.dirname(os.path.dirname(os.path.dirname(b)));Q=os.path.join(D,_d,_e,_J);os.makedirs(Q,exist_ok=_D);I=str(uuid.uuid4());c=os.path.join(Q,f"{I}.png")
			with open(c,'wb')as d:d.write(a)
		except:pass
	logger.debug('SAVE DASHBOARD dashboard_notebook');logger.debug(_R);logger.debug(L);e=Dashboard.objects.create(dashboard_id=K,name=T,slug=B,description=U,is_expose_dashboard=V,is_public_dashboard=W,has_password=H,password_e=E,lumino_layout=S,project_path=D,dashboard_venv=X,main_ipynb_fullpath=L,grid_config=json.dumps(O),plot_db_programmatic_attributes=json.dumps(Z),plot_db_dependencies=json.dumps(F),thumbnail_path=I,date_created=C,last_update=C,last_date_used=C,spartaqube_version=sparta_f7bf9a61de());f=ShareRights.objects.create(is_admin=_D,has_write_rights=_D,has_reshare_rights=_D,last_update=C);DashboardShared.objects.create(dashboard=e,user=J,share_rights=f,is_owner=_D,date_created=C);return{_A:1,_H:K}
def sparta_6c992b39e7(lumino_dict,entrypoint_full_path):
	B=entrypoint_full_path;A=lumino_dict;C=A['type']
	if C=='split-area':
		D=A['children']
		for E in D:return sparta_6c992b39e7(E,B)
	else:
		F=A['widgets']
		for G in F:
			if sparta_ff0e80d635(G[_f])==B:return _D
	return _C
def sparta_432b81a754(json_data,user_obj):
	H=user_obj;B=json_data;M=datetime.now().astimezone(UTC);I=B[_G];J=Dashboard.objects.filter(dashboard_id__startswith=I,is_delete=_C).all()
	if J.count()==1:
		A=J[J.count()-1];I=A.dashboard_id;N=sparta_fd87ef2187(H)
		if len(N)>0:K=DashboardShared.objects.filter(Q(is_delete=0,user_group__in=N,dashboard__is_delete=0,dashboard=A)|Q(is_delete=0,user=H,dashboard__is_delete=0,dashboard=A))
		else:K=DashboardShared.objects.filter(is_delete=0,user=H,dashboard__is_delete=0,dashboard=A)
		O=_C
		if K.count()>0:
			W=K[0];P=W.share_rights
			if P.is_admin or P.has_write_rights:O=_D
		if O:
			L=B[_L];i=B[_T];X=B[_I];Y=B[_U];Z=B[_V];a=B[_W];b=B[_K];C=B[_X]
			if A.slug!=C:
				if len(C)==0:C=B[_I]
				R=slugify(C);C=R;S=1
				while Dashboard.objects.filter(slug=C).exists():C=f"{R}-{S}";S+=1
			T=B[_Y];D=[]
			for(j,c)in T.items():
				for U in c:
					if U[_Z]==1:D.append(U[_a])
			D=list(set(D));E=_B;F=B.get(_c,_B)
			if F is not _B:
				F=F.split(',')[1];d=base64.b64decode(F)
				try:
					e=os.path.dirname(__file__);f=os.path.dirname(os.path.dirname(os.path.dirname(e)));V=os.path.join(f,_d,_e,_J);os.makedirs(V,exist_ok=_D)
					if A.thumbnail_path is _B:E=str(uuid.uuid4())
					else:E=A.thumbnail_path
					g=os.path.join(V,f"{E}.png")
					with open(g,'wb')as h:h.write(d)
				except:pass
			logger.debug('lumino_layout_dump');logger.debug(L);logger.debug(type(L));A.name=X;A.description=Y;A.slug=C;A.is_expose_dashboard=Z;A.is_public_dashboard=a;A.thumbnail_path=E;A.lumino_layout=L;A.grid_config=json.dumps(T);A.plot_db_programmatic_attributes=json.dumps(B[_b]);A.plot_db_dependencies=json.dumps(D);A.last_update=M;A.last_date_used=M
			if b:
				G=B[_S]
				if len(G)>0:G=qube_98ef18f3d2.sparta_18bc87529f(G);A.password_e=G;A.has_password=_D
			else:A.has_password=_C
			A.save()
	return{_A:1,_H:I}
def sparta_4826af7c5a(json_data,user_obj):
	E=json_data;B=user_obj;F=E[_G];C=Dashboard.objects.filter(dashboard_id__startswith=F,is_delete=_C).all()
	if C.count()==1:
		A=C[C.count()-1];F=A.dashboard_id;G=sparta_fd87ef2187(B)
		if len(G)>0:D=DashboardShared.objects.filter(Q(is_delete=0,user_group__in=G,dashboard__is_delete=0,dashboard=A)|Q(is_delete=0,user=B,dashboard__is_delete=0,dashboard=A))
		else:D=DashboardShared.objects.filter(is_delete=0,user=B,dashboard__is_delete=0,dashboard=A)
		H=_C
		if D.count()>0:
			J=D[0];I=J.share_rights
			if I.is_admin or I.has_write_rights:H=_D
		if H:K=E[_L];A.lumino_layout=K;A.save()
	return{_A:1}
def sparta_37d4b5846b(json_data,user_obj):
	C=user_obj;B=json_data;logger.debug(_Q);logger.debug(B);F=B[_G];D=Dashboard.objects.filter(dashboard_id__startswith=F,is_delete=_C).all()
	if D.count()==1:
		A=D[D.count()-1];F=A.dashboard_id;G=sparta_fd87ef2187(C)
		if len(G)>0:E=DashboardShared.objects.filter(Q(is_delete=0,user_group__in=G,dashboard__is_delete=0,dashboard=A)|Q(is_delete=0,user=C,dashboard__is_delete=0,dashboard=A))
		else:E=DashboardShared.objects.filter(is_delete=0,user=C,dashboard__is_delete=0,dashboard=A)
		H=_C
		if E.count()>0:
			J=E[0];I=J.share_rights
			if I.is_admin or I.has_write_rights:H=_D
		if H:K=sparta_ff0e80d635(B[_f]);A.main_ipynb_fullpath=K;A.save()
	return{_A:1}
def sparta_848aae116e(json_data,user_obj):
	A=user_obj;G=json_data[_G];B=Dashboard.objects.filter(dashboard_id=G,is_delete=_C).all()
	if B.count()>0:
		C=B[B.count()-1];E=sparta_fd87ef2187(A)
		if len(E)>0:D=DashboardShared.objects.filter(Q(is_delete=0,user_group__in=E,dashboard__is_delete=0,dashboard=C)|Q(is_delete=0,user=A,dashboard__is_delete=0,dashboard=C))
		else:D=DashboardShared.objects.filter(is_delete=0,user=A,dashboard__is_delete=0,dashboard=C)
		if D.count()>0:F=D[0];F.is_delete=_D;F.save()
	return{_A:1}
def has_dashboard_access(dashboard_id,user_obj,password_dashboard=_B):
	I='Invalid password';G=password_dashboard;F=dashboard_id;B=user_obj;logger.debug('dashboard_id > '+str(F));logger.debug('password_dashboard > '+str(G));C=Dashboard.objects.filter(dashboard_id__startswith=F,is_delete=_C).all();H=_C
	if C.count()==1:H=_D
	else:
		J=F;C=Dashboard.objects.filter(slug__startswith=J,is_delete=_C).all()
		if C.count()==1:H=_D
	if H:
		A=C[C.count()-1]
		if not B.is_anonymous:
			D=sparta_fd87ef2187(B)
			if len(D)>0:E=DashboardShared.objects.filter(Q(is_delete=0,user_group__in=D,dashboard__is_delete=0,dashboard=A)|Q(is_delete=0,user=B,dashboard__is_delete=0,dashboard=A))
			else:E=DashboardShared.objects.filter(is_delete=0,user=B,dashboard__is_delete=0,dashboard=A)
			if E.count()>0:return{_A:1,_E:A}
		K=A.has_password
		if A.is_expose_dashboard:
			if A.is_public_dashboard:
				if not K:return{_A:1,_E:A}
				elif G is _B:return{_A:2,_F:'Require password',_E:A}
				else:
					try:
						if qube_98ef18f3d2.sparta_f2a6ad3bd9(A.password_e)==G:return{_A:1,_E:A}
						else:return{_A:3,_F:I,_E:A}
					except Exception as L:return{_A:3,_F:I,_E:A}
			elif B.is_authenticated:
				D=sparta_fd87ef2187(B)
				if len(D)>0:E=DashboardShared.objects.filter(Q(is_delete=0,user_group__in=D,dashboard__is_delete=0,dashboard=A)|Q(is_delete=0,user=B,dashboard__is_delete=0,dashboard=A))
				else:E=DashboardShared.objects.filter(is_delete=0,user=B,dashboard__is_delete=0,dashboard=A)
				if E.count()>0:return{_A:1,_E:A}
			else:return{_A:-1}
	return{_A:-1}
def sparta_01e1d4010c(json_data,user_obj):A=sparta_f6caba58f6(json_data,user_obj);return A
def has_plot_db_access(dashboard_id,plot_db_id,user_obj,dashboard_password):
	A=plot_db_id;B=has_dashboard_access(dashboard_id,user_obj,password_dashboard=dashboard_password)
	if B[_A]==1:
		F=B[_E];G=json.loads(F.plot_db_dependencies)
		if A in G:
			C=PlotDBChart.objects.filter(plot_chart_id__startswith=A,is_delete=_C).all()
			if C.count()>0:D=C[0];E=str(uuid.uuid4());H=datetime.now().astimezone(UTC);PlotDBPermission.objects.create(plot_db_chart=D,token=E,date_created=H);return{_A:1,_g:D,_h:E}
	return{_A:-1}
def has_dataframe_access(dashboard_id,slug,user_obj,dashboard_password):
	A=has_dashboard_access(dashboard_id,user_obj,password_dashboard=dashboard_password)
	if A[_A]==1:
		E=A[_E];F=json.loads(E.plot_db_dependencies)
		if plot_db_id in F:
			B=PlotDBChart.objects.filter(slug=slug,is_delete=_C).all()
			if B.count()>0:C=B[0];D=str(uuid.uuid4());G=datetime.now().astimezone(UTC);PlotDBPermission.objects.create(plot_db_chart=C,token=D,date_created=G);return{_A:1,_g:C,_h:D}
	return{_A:-1}