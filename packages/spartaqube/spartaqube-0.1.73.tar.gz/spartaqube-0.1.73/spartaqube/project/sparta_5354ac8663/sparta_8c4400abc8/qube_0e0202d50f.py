_y='stdout'
_x='makemigrations'
_w='app.settings'
_v='DJANGO_SETTINGS_MODULE'
_u='python'
_t='Found Cell Code'
_s='sqMetadata'
_r='metadata'
_q='thumbnail'
_p='static'
_o='project'
_n='previewImage'
_m='isExecCodeDisplay'
_l='isPublic'
_k='isExpose'
_j='password'
_i='lumino_layout'
_h='notebook_venv'
_g='lumino'
_f='Project not found...'
_e='You do not have the rights to access this project'
_d='models_access_examples.py'
_c='notebook_models.py'
_b='template'
_a='django_app_template'
_Z='luminoLayout'
_Y='hasPassword'
_X='is_exec_code_display'
_W='is_public_notebook'
_V='main_ipynb_fullpath'
_U='has_password'
_T='is_expose_notebook'
_S='source'
_R='cellId'
_Q='description'
_P='slug'
_O='app'
_N='manage.py'
_M='notebook_id'
_L='project_path'
_K='notebook'
_J='notebook_obj'
_I='name'
_H='projectPath'
_G='notebookId'
_F='main.ipynb'
_E='errorMsg'
_D=None
_C=False
_B='res'
_A=True
import re,os,json,stat,importlib,io,sys,subprocess,platform,base64,traceback,uuid,shutil
from django.db.models import Q
from django.utils.text import slugify
from datetime import datetime,timedelta
import pytz
UTC=pytz.utc
from asgiref.sync import sync_to_async
from spartaqube_app.path_mapper_obf import sparta_4333278bd8
from project.models_spartaqube import Notebook,NotebookShared
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
def sparta_fd87ef2187(user_obj):
	A=qube_ac67c5d252.sparta_3530108797(user_obj)
	if len(A)>0:B=[A.user_group for A in A]
	else:B=[]
	return B
def sparta_5c76630f68(project_path,has_django_models=_A):
	C=has_django_models;B=project_path
	if not os.path.exists(B):os.makedirs(B)
	G=B;D=os.path.join(sparta_4333278bd8()[_a],_K,_b)
	for E in os.listdir(D):
		A=os.path.join(D,E);F=os.path.join(G,E)
		if os.path.isdir(A):
			H=os.path.basename(A)
			if H==_O:
				if not C:continue
			shutil.copytree(A,F,dirs_exist_ok=_A)
		else:
			I=os.path.basename(A)
			if I in[_c,_d]:
				if not C:continue
			shutil.copy2(A,F)
	return{_L:B}
def sparta_1e5ec7a75a(json_data,user_obj):
	F=json_data;B=user_obj;A=F[_H];A=sparta_ff0e80d635(A);G=Notebook.objects.filter(project_path=A).all()
	if G.count()>0:
		C=G[0];H=sparta_fd87ef2187(B)
		if len(H)>0:D=NotebookShared.objects.filter(Q(is_delete=0,user_group__in=H,notebook__is_delete=0,notebook=C)|Q(is_delete=0,user=B,notebook__is_delete=0,notebook=C))
		else:D=NotebookShared.objects.filter(is_delete=0,user=B,notebook__is_delete=0,notebook=C)
		I=_C
		if D.count()>0:
			K=D[0];J=K.share_rights
			if J.is_admin or J.has_write_rights:I=_A
		if not I:return{_B:-1,_E:'Chose another path. A project already exists at this location'}
	if not isinstance(A,str):return{_B:-1,_E:'Project path must be a string.'}
	logger.debug(_L);logger.debug(A)
	try:A=os.path.abspath(A)
	except Exception as E:return{_B:-1,_E:f"Invalid project path: {str(E)}"}
	try:
		if not os.path.exists(A):os.makedirs(A)
		L=F['hasDjangoModels'];M=sparta_5c76630f68(A,L);A=M[_L];return{_B:1,_L:A}
	except Exception as E:return{_B:-1,_E:f"Failed to create folder: {str(E)}"}
def sparta_15093013c5(json_data,user_obj):A=json_data;A['bAddGitignore']=_A;A['bAddReadme']=_A;return qube_629b3780b6.sparta_1b2e390ac6(A,user_obj)
def sparta_8e593ee02f(json_data,user_obj):
	L='%Y-%m-%d';K='Recently used';E=user_obj;G=sparta_fd87ef2187(E)
	if len(G)>0:A=NotebookShared.objects.filter(Q(is_delete=0,user_group__in=G,notebook__is_delete=0)|Q(is_delete=0,user=E,notebook__is_delete=0)|Q(is_delete=0,notebook__is_delete=0,notebook__is_expose_notebook=_A,notebook__is_public_notebook=_A))
	else:A=NotebookShared.objects.filter(Q(is_delete=0,user=E,notebook__is_delete=0)|Q(is_delete=0,notebook__is_delete=0,notebook__is_expose_notebook=_A,notebook__is_public_notebook=_A))
	if A.count()>0:
		C=json_data.get('orderBy',K)
		if C==K:A=A.order_by('-notebook__last_date_used')
		elif C=='Date desc':A=A.order_by('-notebook__last_update')
		elif C=='Date asc':A=A.order_by('notebook__last_update')
		elif C=='Name desc':A=A.order_by('-notebook__name')
		elif C=='Name asc':A=A.order_by('notebook__name')
	H=[]
	for F in A:
		B=F.notebook;M=F.share_rights;I=_D
		try:I=str(B.last_update.strftime(L))
		except:pass
		J=_D
		try:J=str(B.date_created.strftime(L))
		except Exception as N:logger.debug(N)
		D=B.main_ipynb_fullpath
		if D is _D:D=os.path.join(B.project_path,_F)
		elif len(D)==0:D=os.path.join(B.project_path,_F)
		H.append({_M:B.notebook_id,_I:B.name,_P:B.slug,_Q:B.description,_T:B.is_expose_notebook,_U:B.has_password,_V:D,_W:B.is_public_notebook,_X:B.is_exec_code_display,'is_owner':F.is_owner,'has_write_rights':M.has_write_rights,'last_update':I,'date_created':J})
	return{_B:1,'notebook_library':H}
def sparta_4ec47f9b0a(json_data,user_obj):
	C=user_obj;F=json_data[_G];E=Notebook.objects.filter(notebook_id__startswith=F,is_delete=_C).all()
	if E.count()==1:
		A=E[E.count()-1];F=A.notebook_id;G=sparta_fd87ef2187(C)
		if len(G)>0:D=NotebookShared.objects.filter(Q(is_delete=0,user_group__in=G,notebook__is_delete=0,notebook=A)|Q(is_delete=0,user=C,notebook__is_delete=0,notebook=A))
		else:D=NotebookShared.objects.filter(is_delete=0,user=C,notebook__is_delete=0,notebook=A)
		if D.count()==0:return{_B:-1,_E:_e}
	else:return{_B:-1,_E:_f}
	D=NotebookShared.objects.filter(is_owner=_A,notebook=A,user=C)
	if D.count()>0:H=datetime.now().astimezone(UTC);A.last_date_used=H;A.save()
	B=A.main_ipynb_fullpath
	if B is _D:B=os.path.join(A.project_path,_F)
	elif len(B)==0:B=os.path.join(A.project_path,_F)
	return{_B:1,_K:{'basic':{_M:A.notebook_id,_I:A.name,_P:A.slug,_Q:A.description,_T:A.is_expose_notebook,_W:A.is_public_notebook,_X:A.is_exec_code_display,_V:B,_U:A.has_password,_h:A.notebook_venv,_L:A.project_path},_g:{_i:A.lumino_layout}}}
def sparta_c0677db9da(json_data,user_obj):
	H=json_data;B=user_obj;E=H[_G];logger.debug('load_notebook DEBUG');logger.debug(E)
	if not B.is_anonymous:
		G=Notebook.objects.filter(notebook_id__startswith=E,is_delete=_C).all()
		if G.count()==1:
			A=G[G.count()-1];E=A.notebook_id;I=sparta_fd87ef2187(B)
			if len(I)>0:F=NotebookShared.objects.filter(Q(is_delete=0,user_group__in=I,notebook__is_delete=0,notebook=A)|Q(is_delete=0,user=B,notebook__is_delete=0,notebook=A)|Q(is_delete=0,notebook__is_delete=0,notebook__is_expose_notebook=_A,notebook__is_public_notebook=_A))
			else:F=NotebookShared.objects.filter(Q(is_delete=0,user=B,notebook__is_delete=0,notebook=A)|Q(is_delete=0,notebook__is_delete=0,notebook__is_expose_notebook=_A,notebook__is_public_notebook=_A))
			if F.count()==0:return{_B:-1,_E:_e}
		else:return{_B:-1,_E:_f}
	else:
		J=H.get('modalPassword',_D);logger.debug(f"DEBUG DEVELOPER VIEW TEST >>> {J}");C=sparta_db46a726c2(E,B,password_notebook=J);logger.debug('MODAL DEBUG DEBUG DEBUG notebook_access_dict');logger.debug(C)
		if C[_B]!=1:return{_B:C[_B],_E:C[_E]}
		A=C[_J]
	if not B.is_anonymous:
		F=NotebookShared.objects.filter(is_owner=_A,notebook=A,user=B)
		if F.count()>0:K=datetime.now().astimezone(UTC);A.last_date_used=K;A.save()
	D=A.main_ipynb_fullpath
	if D is _D:D=os.path.join(A.project_path,_F)
	elif len(D)==0:D=os.path.join(A.project_path,_F)
	return{_B:1,_K:{'basic':{_M:A.notebook_id,_I:A.name,_P:A.slug,_Q:A.description,_T:A.is_expose_notebook,_W:A.is_public_notebook,_X:A.is_exec_code_display,_U:A.has_password,_h:A.notebook_venv,_L:A.project_path,_V:D},_g:{_i:A.lumino_layout}}}
def sparta_079a2e73ac(json_data,user_obj):
	I=user_obj;A=json_data;logger.debug('Save notebook');logger.debug(A);logger.debug(A.keys());N=A['isNew']
	if not N:return sparta_034c48e650(A,I)
	C=datetime.now().astimezone(UTC);J=str(uuid.uuid4());G=A[_Y];E=_D
	if G:E=A[_j];E=qube_98ef18f3d2.sparta_18bc87529f(E)
	O=A[_Z];P=A[_I];Q=A[_Q];D=A[_H];D=sparta_ff0e80d635(D);R=A[_k];S=A[_l];G=A[_Y];T=A[_m];U=A.get('notebookVenv',_D);B=A[_P]
	if len(B)==0:B=A[_I]
	K=slugify(B);B=K;L=1
	while Notebook.objects.filter(slug=B).exists():B=f"{K}-{L}";L+=1
	H=_D;F=A.get(_n,_D)
	if F is not _D:
		try:
			F=F.split(',')[1];V=base64.b64decode(F);D=sparta_4333278bd8()[_o];M=os.path.join(D,_p,_q,_K);os.makedirs(M,exist_ok=_A);H=str(uuid.uuid4());W=os.path.join(M,f"{H}.png")
			with open(W,'wb')as X:X.write(V)
		except:pass
	Y=Notebook.objects.create(notebook_id=J,name=P,slug=B,description=Q,is_expose_notebook=R,is_public_notebook=S,has_password=G,password_e=E,is_exec_code_display=T,lumino_layout=O,project_path=D,notebook_venv=U,thumbnail_path=H,date_created=C,last_update=C,last_date_used=C,spartaqube_version=sparta_f7bf9a61de());Z=ShareRights.objects.create(is_admin=_A,has_write_rights=_A,has_reshare_rights=_A,last_update=C);NotebookShared.objects.create(notebook=Y,user=I,share_rights=Z,is_owner=_A,date_created=C);return{_B:1,_M:J}
def sparta_034c48e650(json_data,user_obj):
	G=user_obj;B=json_data;logger.debug('Save notebook update_notebook_view');logger.debug(B);logger.debug(B.keys());L=datetime.now().astimezone(UTC);H=B[_G];I=Notebook.objects.filter(notebook_id__startswith=H,is_delete=_C).all()
	if I.count()==1:
		A=I[I.count()-1];H=A.notebook_id;M=sparta_fd87ef2187(G)
		if len(M)>0:J=NotebookShared.objects.filter(Q(is_delete=0,user_group__in=M,notebook__is_delete=0,notebook=A)|Q(is_delete=0,user=G,notebook__is_delete=0,notebook=A))
		else:J=NotebookShared.objects.filter(is_delete=0,user=G,notebook__is_delete=0,notebook=A)
		N=_C
		if J.count()>0:
			T=J[0];O=T.share_rights
			if O.is_admin or O.has_write_rights:N=_A
		if N:
			K=B[_Z];U=B[_I];V=B[_Q];W=B[_k];X=B[_l];Y=B[_Y];Z=B[_m];C=B[_P]
			if A.slug!=C:
				if len(C)==0:C=B[_I]
				P=slugify(C);C=P;R=1
				while Notebook.objects.filter(slug=C).exists():C=f"{P}-{R}";R+=1
			D=_D;E=B.get(_n,_D)
			if E is not _D:
				E=E.split(',')[1];a=base64.b64decode(E)
				try:
					b=sparta_4333278bd8()[_o];S=os.path.join(b,_p,_q,_K);os.makedirs(S,exist_ok=_A)
					if A.thumbnail_path is _D:D=str(uuid.uuid4())
					else:D=A.thumbnail_path
					c=os.path.join(S,f"{D}.png")
					with open(c,'wb')as d:d.write(a)
				except:pass
			logger.debug('lumino_layout_dump');logger.debug(K);logger.debug(type(K));A.name=U;A.description=V;A.slug=C;A.is_expose_notebook=W;A.is_public_notebook=X;A.is_exec_code_display=Z;A.thumbnail_path=D;A.lumino_layout=K;A.last_update=L;A.last_date_used=L
			if Y:
				F=B[_j]
				if len(F)>0:F=qube_98ef18f3d2.sparta_18bc87529f(F);A.password_e=F;A.has_password=_A
			else:A.has_password=_C
			A.save()
	return{_B:1,_M:H}
def sparta_3ea8ff6bbc(json_data,user_obj):
	E=json_data;B=user_obj;F=E[_G];C=Notebook.objects.filter(notebook_id__startswith=F,is_delete=_C).all()
	if C.count()==1:
		A=C[C.count()-1];F=A.notebook_id;G=sparta_fd87ef2187(B)
		if len(G)>0:D=NotebookShared.objects.filter(Q(is_delete=0,user_group__in=G,notebook__is_delete=0,notebook=A)|Q(is_delete=0,user=B,notebook__is_delete=0,notebook=A))
		else:D=NotebookShared.objects.filter(is_delete=0,user=B,notebook__is_delete=0,notebook=A)
		H=_C
		if D.count()>0:
			J=D[0];I=J.share_rights
			if I.is_admin or I.has_write_rights:H=_A
		if H:K=E[_Z];A.lumino_layout=K;A.save()
	return{_B:1}
def sparta_8f53f21aed(json_data,user_obj):
	A=user_obj;G=json_data[_G];B=Notebook.objects.filter(notebook_id=G,is_delete=_C).all()
	if B.count()>0:
		C=B[B.count()-1];E=sparta_fd87ef2187(A)
		if len(E)>0:D=NotebookShared.objects.filter(Q(is_delete=0,user_group__in=E,notebook__is_delete=0,notebook=C)|Q(is_delete=0,user=A,notebook__is_delete=0,notebook=C))
		else:D=NotebookShared.objects.filter(is_delete=0,user=A,notebook__is_delete=0,notebook=C)
		if D.count()>0:F=D[0];F.is_delete=_A;F.save()
	return{_B:1}
def sparta_db46a726c2(notebook_id,user_obj,password_notebook=_D):
	J='debug';I='Invalid password';F=password_notebook;E=notebook_id;C=user_obj;logger.debug(_M);logger.debug(E);B=Notebook.objects.filter(notebook_id__startswith=E,is_delete=_C).all();D=_C
	if B.count()==1:D=_A
	else:
		K=E;B=Notebook.objects.filter(slug__startswith=K,is_delete=_C).all()
		if B.count()==1:D=_A
	logger.debug('b_found');logger.debug(D)
	if D:
		A=B[B.count()-1];L=A.has_password
		if A.is_expose_notebook:
			logger.debug('is exposed')
			if A.is_public_notebook:
				logger.debug('is public')
				if not L:logger.debug('no password');return{_B:1,_J:A}
				else:
					logger.debug('hass password')
					if F is _D:logger.debug('empty passord provided');return{_B:2,_E:'Require password',_J:A}
					else:
						try:
							if qube_98ef18f3d2.sparta_f2a6ad3bd9(A.password_e)==F:return{_B:1,_J:A}
							else:return{_B:3,_E:I,_J:A}
						except Exception as M:return{_B:3,_E:I,_J:A}
			elif C.is_authenticated:
				G=sparta_fd87ef2187(C)
				if len(G)>0:H=NotebookShared.objects.filter(Q(is_delete=0,user_group__in=G,notebook__is_delete=0,notebook=A)|Q(is_delete=0,user=C,notebook__is_delete=0,notebook=A))
				else:H=NotebookShared.objects.filter(is_delete=0,user=C,notebook__is_delete=0,notebook=A)
				if H.count()>0:return{_B:1,_J:A}
			else:return{_B:-1,J:1}
	return{_B:-1,J:2}
def sparta_9f456c809e(json_data,user_obj):A=sparta_ff0e80d635(json_data[_H]);return sparta_a3ffb5d42e(A)
def sparta_f9d35b88c7(json_data,user_obj):A=sparta_ff0e80d635(json_data[_H]);return sparta_82e779a082(A)
def sparta_5c235648b2(json_data,user_obj):
	C=user_obj;B=json_data;logger.debug('notebook_ipynb_set_entrypoint json_data');logger.debug(B);F=B[_G];D=Notebook.objects.filter(notebook_id__startswith=F,is_delete=_C).all()
	if D.count()==1:
		A=D[D.count()-1];F=A.notebook_id;G=sparta_fd87ef2187(C)
		if len(G)>0:E=NotebookShared.objects.filter(Q(is_delete=0,user_group__in=G,notebook__is_delete=0,notebook=A)|Q(is_delete=0,user=C,notebook__is_delete=0,notebook=A))
		else:E=NotebookShared.objects.filter(is_delete=0,user=C,notebook__is_delete=0,notebook=A)
		H=_C
		if E.count()>0:
			J=E[0];I=J.share_rights
			if I.is_admin or I.has_write_rights:H=_A
		if H:K=sparta_ff0e80d635(B['fullPath']);A.main_ipynb_fullpath=K;A.save()
	return{_B:1}
async def notebook_permission_code_exec_DEPREC(json_data):
	C=json_data;logger.debug('Callilng notebook_permission_code_exec')
	try:
		F=C[_G];D=Notebook.objects.filter(notebook_id__startswith=F,is_delete=_C)
		if await D.acount()>0:
			E=await D.afirst();G=C[_R];A=E.main_ipynb_fullpath
			if A is _D:A=os.path.join(E.project_path,_F)
			H=qube_d14205c11b.sparta_42867f3351(A);I=H['cells']
			for B in I:
				J=json.loads(B[_r][_s])
				if J[_R]==G:logger.debug(_t);logger.debug(B[_S][0]);return B[_S][0]
	except Exception as K:logger.debug('Except is:');logger.debug(K);return''
	return''
async def notebook_permission_code_exec(json_data):
	C=json_data;logger.debug('Calling notebook_permission_code_exec')
	try:
		F=C[_G];D=await sync_to_async(lambda:list(Notebook.objects.filter(notebook_id__startswith=F,is_delete=_C)),thread_sensitive=_C)()
		if len(D)>0:
			E=D[0];G=C[_R];A=E.main_ipynb_fullpath
			if A is _D:A=os.path.join(E.project_path,_F)
			H=qube_d14205c11b.sparta_42867f3351(A);I=H['cells']
			for B in I:
				J=json.loads(B[_r][_s])
				if J[_R]==G:logger.debug(_t);logger.debug(B[_S][0]);return B[_S][0]
	except Exception as K:logger.debug('Exception in notebook_permission_code_exec:');logger.debug(K);return''
	return''
def sparta_cef4fb0de5(json_data,user_obj):0
from django.core.management import call_command
from io import StringIO
def sparta_c3bdac576a(project_path,python_executable=_u):
	E=python_executable;B=project_path;A=_C
	try:
		H=os.path.join(B,_N)
		if not os.path.exists(H):A=_A;return _C,f"Error: manage.py not found in {B}",A
		F=os.environ.copy();F[_v]=_w;E=sys.executable;I=[E,_N,_x,'--dry-run'];C=subprocess.run(I,cwd=B,text=_A,capture_output=_A,env=F)
		if C.returncode!=0:A=_A;return _C,f"Error: {C.stderr}",A
		G=C.stdout;J='No changes detected'not in G;return J,G,A
	except FileNotFoundError as D:A=_A;return _C,f"Error: {D}. Ensure the correct Python executable and project path.",A
	except Exception as D:A=_A;return _C,str(D),A
def sparta_f36f40b028():
	A=os.environ.get('VIRTUAL_ENV')
	if A:return A
	else:return sys.prefix
def sparta_6ddd47fbb3():
	A=sparta_f36f40b028()
	if sys.platform=='win32':B=os.path.join(A,'Scripts','pip.exe')
	else:B=os.path.join(A,'bin','pip')
	return B
def sparta_8c893e0637(json_data,user_obj):
	D=sparta_ff0e80d635(json_data[_H]);A=D;B=os.path.join(sparta_4333278bd8()[_a],_K,_b);C=os.path.join(A,_O)
	if not os.path.exists(C):os.makedirs(C)
	shutil.copytree(os.path.join(B,_O),C,dirs_exist_ok=_A);logger.debug(f"Folder copied from {B} to {A}");shutil.copy2(os.path.join(B,_c),A);shutil.copy2(os.path.join(B,_d),A);return{_B:1}
def sparta_b46ec90edf(json_data,user_obj):
	A=sparta_ff0e80d635(json_data[_H]);A=os.path.join(A,_O);G,C,D=sparta_c3bdac576a(A);B=_A;E=1;F=''
	if D:
		E=-1;F=C;B;H=os.path.join(A,_N)
		if not os.path.exists(H):B=_C
	I={_B:E,'has_error':D,'has_pending_migrations':G,_y:C,_E:F,'has_django_init':B};return I
def sparta_346a370185(project_path,python_executable=_u):
	D=python_executable;C=project_path
	try:
		G=os.path.join(C,_N)
		if not os.path.exists(G):return _C,f"Error: manage.py not found in {C}"
		F=os.environ.copy();F[_v]=_w;D=sys.executable;H=[[D,_N,_x],[D,_N,'migrate']];B=[]
		for I in H:
			A=subprocess.run(I,cwd=C,text=_A,capture_output=_A,env=F)
			if A.stdout is not _D:
				if len(str(A.stdout))>0:B.append(A.stdout)
			if A.stderr is not _D:
				if len(str(A.stderr))>0:B.append(f"<span style='color:red'>Stderr:\n{A.stderr}</span>")
			if A.returncode!=0:return _C,'\n'.join(B)
		return _A,'\n'.join(B)
	except FileNotFoundError as E:return _C,f"Error: {E}. Ensure the correct Python executable and project path."
	except Exception as E:return _C,str(E)
def sparta_c88e8f34f3(json_data,user_obj):
	A=sparta_ff0e80d635(json_data[_H]);A=os.path.join(A,_O);B,C=sparta_346a370185(A);D=1;E=''
	if not B:D=-1;E=C
	return{_B:D,'res_migration':B,_y:C,_E:E}
def sparta_aeb5745a98(json_data,user_obj):return{_B:1}
def sparta_ce085ee1e9(json_data,user_obj):return{_B:1}