_M='Error Final'
_L='zipName'
_K='Except2'
_J='file > '
_I='rmdir /S /Q "{}"'
_H='folderPath2MoveArr'
_G='filesPath2MoveArr'
_F='filePath'
_E='path'
_D='fileName'
_C='errorMsg'
_B='projectPath'
_A='res'
import os,shutil,zipfile,io,uuid
from distutils.dir_util import copy_tree
from project.sparta_5354ac8663.sparta_c0f904d512 import qube_ac67c5d252 as qube_ac67c5d252
from project.sparta_5354ac8663.sparta_82fa1097b7 import qube_4a8aaacb65 as qube_4a8aaacb65
from project.sparta_5354ac8663.sparta_d58392c7f1 import qube_3a003c75c0 as qube_3a003c75c0
from project.logger_config import logger
def sparta_21e57c3548():return str(uuid.uuid4())
def sparta_dc2faa3137(app_id):
	B=coreApps.get_app_folder_default_path();A=os.path.join(B,app_id)
	if not os.path.exists(A):os.makedirs(A)
	return A
def sparta_7884a9c2ee(project_path):
	A=project_path
	try:
		if not os.path.exists(A):os.makedirs(A)
		return{_A:1}
	except Exception as B:return{_A:-1,_C:str(B)}
def sparta_3cc61ee375(path):
	with open(path,'a'):os.utime(path,None)
def sparta_161aff7626(json_data,userObj):
	A=json_data;logger.debug('CREATE RESOURCE');logger.debug(A);C=A[_B];D=sparta_7884a9c2ee(C)
	if D[_A]==-1:return D
	F=A['createResourceName'];G=A['createType']
	try:
		B=os.path.join(C,F)
		if int(G)==1:
			if not os.path.exists(B):os.makedirs(B)
		elif not os.path.exists(B):sparta_3cc61ee375(B)
		else:return{_A:-1,_C:'A file with this name already exists'}
	except Exception as E:logger.debug('Exception create new resource');logger.debug(E);return{_A:-1,_C:str(E)}
	return{_A:1}
def sparta_1c9ef740c9(json_data,userObj):
	A=json_data;E=A[_B];C=A['folder_location'];H=A[_G];I=A[_H]
	for B in H:
		J=B[_E];F=B[_D];G=os.path.join(J,F);D=os.path.join(C,F)
		if E in D:
			try:logger.debug(f"Move from\n{G}\nto\n{D}");shutil.move(G,D)
			except Exception as K:logger.debug('Exception move 1');logger.debug(K)
	for B in I:
		L=B[_E]
		if E in C:
			try:shutil.move(L,C)
			except:pass
	return{_A:1}
def sparta_3c8c9d83b3(json_data,user_obj,file_obj_to_upload):
	D=file_obj_to_upload;B=json_data;A=B[_B];E=sparta_7884a9c2ee(A)
	if E[_A]==-1:return E
	F=B[_E];C=B['dragoverElem'];logger.debug('dragover_elem ');logger.debug(C)
	if len(C)>0:J=C
	if len(F)>0:
		A=os.path.join(A,F)
		if not os.path.exists(A):os.makedirs(A)
	G=os.path.join(A,D.name)
	with open(G,'wb')as H:H.write(D.read())
	I={_A:1};return I
def sparta_34b39f9e19(json_data,userObj):A=json_data[_B];B=qube_3a003c75c0.get_folder_and_files_recursively_from_path(A);C={_A:1,'folderStructure':B};return C
def sparta_a94fd7514d(json_data,userObj):
	A=json_data
	try:
		C=A[_B];D=A[_D];B=A[_F];E=A['sourceCode']
		if C in B:
			B=os.path.join(B,D)
			with open(B,'w')as F:F.write(E)
		return{_A:1}
	except Exception as G:return{_A:-1,_C:str(G)}
def sparta_950209ca9c(json_data,userObj):
	A=json_data;I=A[_B];F=A[_D];B=A[_F];G=A['editName'];J=int(A['renameType'])
	if I in B:
		if J==1:
			H=os.path.dirname(B);C=os.path.join(H,F);D=os.path.join(H,G)
			try:os.rename(C,D)
			except Exception as E:return{_A:-1,_C:str(E)}
		else:
			C=os.path.join(B,F);D=os.path.join(B,G)
			try:os.rename(C,D)
			except Exception as E:return{_A:-1,_C:str(E)}
	return{_A:1}
def sparta_c0b8f3011b(json_data,userObj):
	B=json_data;D=B[_B];E=B[_D];A=B[_F];F=int(B['typeDelete'])
	if D in A:
		if F==1:
			try:os.rmdir(A)
			except:
				try:os.system(_I.format(A))
				except:
					try:shutil.rmtree(A)
					except Exception as C:return{_A:-1,_C:str(C)}
		else:
			A=os.path.join(A,E)
			try:os.remove(A)
			except Exception as C:return{_A:-1,_C:str(C)}
	return{_A:1}
def sparta_ee2f582727(json_data,userObj):
	B=json_data;F=B[_G];G=B[_H];H=B[_B]
	for A in F:
		I=A[_D];E=A[_E]
		if H in E:
			J=os.path.join(E,I)
			try:os.remove(J)
			except Exception as C:return{_A:-1,_C:str(C)}
	for A in G:
		D=A[_E];logger.debug(f"Delete folder {D}")
		try:os.system(_I.format(D))
		except:
			try:shutil.rmtree(D)
			except Exception as C:return{_A:-1,_C:str(C)}
	return{_A:1}
def sparta_9c7e5dcd80(json_data,userObj):
	A=json_data;C=A[_B];D=A[_D];B=A[_F]
	if C in B:E=os.path.join(B,D);return{_A:1,'fullPath':E}
	return{_A:-1}
def sparta_d5f9ba6c96(json_data,userObj):
	A=json_data;logger.debug('DOWNLOAD FOLDER DEBUG');logger.debug(A);B=A[_B];E=A['folderName']
	def C(zf,folder):
		D=folder
		for E in os.listdir(D):
			logger.debug(_J+str(E));A=os.path.join(D,E)
			if os.path.isfile(A):zf.write(A,A.split(B)[1])
			elif os.path.isdir(A):
				try:C(zf,A)
				except Exception as F:logger.debug(_K);logger.debug(F)
		return zf
	try:
		D=io.BytesIO()
		with zipfile.ZipFile(D,mode='w',compression=zipfile.ZIP_DEFLATED)as F:C(F,B)
		return{_A:1,'zip':D,_L:E}
	except Exception as G:logger.debug(_M);logger.debug(G)
	return{_A:-1}
def sparta_beb06bf02c(json_data,userObj):
	B=json_data[_B];D='app'
	def C(zf,folder):
		D=folder
		for E in os.listdir(D):
			logger.debug(_J+str(E));A=os.path.join(D,E)
			if os.path.isfile(A):zf.write(A,A.split(B)[1])
			elif os.path.isdir(A):
				try:C(zf,A)
				except Exception as F:logger.debug(_K);logger.debug(F)
		return zf
	try:
		A=io.BytesIO()
		with zipfile.ZipFile(A,mode='w',compression=zipfile.ZIP_DEFLATED)as E:C(E,B)
		return{_A:1,'zip':A,_L:D}
	except Exception as F:logger.debug(_M);logger.debug(F)
	return{_A:-1}