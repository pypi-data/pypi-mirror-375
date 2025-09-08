import os,zipfile,pytz
UTC=pytz.utc
from django.conf import settings as conf_settings
def sparta_b8289a5b6a():
	B='APPDATA'
	if conf_settings.PLATFORMS_NFS:
		A='/var/nfs/notebooks/'
		if not os.path.exists(A):os.makedirs(A)
		return A
	if conf_settings.PLATFORM=='LOCAL_DESKTOP'or conf_settings.IS_LOCAL_PLATFORM:
		if conf_settings.PLATFORM_DEBUG=='DEBUG-CLIENT-2':return os.path.join(os.environ[B],'SpartaQuantNB/CLIENT2')
		return os.path.join(os.environ[B],'SpartaQuantNB')
	if conf_settings.PLATFORM=='LOCAL_CE':return'/app/notebooks/'
def sparta_4e56ec7616(userId):A=sparta_b8289a5b6a();B=os.path.join(A,userId);return B
def sparta_bf8f357a22(notebookProjectId,userId):A=sparta_4e56ec7616(userId);B=os.path.join(A,notebookProjectId);return B
def sparta_892af3cc82(notebookProjectId,userId):A=sparta_4e56ec7616(userId);B=os.path.join(A,notebookProjectId);return os.path.exists(B)
def sparta_39950e996c(notebookProjectId,userId,ipynbFileName):A=sparta_4e56ec7616(userId);B=os.path.join(A,notebookProjectId);return os.path.isfile(os.path.join(B,ipynbFileName))
def sparta_d617bb8f0d(notebookProjectId,userId):
	C=userId;B=notebookProjectId;D=sparta_bf8f357a22(B,C);G=sparta_4e56ec7616(C);A=f"{G}/zipTmp/"
	if not os.path.exists(A):os.makedirs(A)
	H=f"{A}/{B}.zip";E=zipfile.ZipFile(H,'w',zipfile.ZIP_DEFLATED);I=len(D)+1
	for(J,M,K)in os.walk(D):
		for L in K:F=os.path.join(J,L);E.write(F,F[I:])
	return E
def sparta_4e1af4c29d(notebookProjectId,userId):B=userId;A=notebookProjectId;sparta_d617bb8f0d(A,B);C=f"{A}.zip";D=sparta_4e56ec7616(B);E=f"{D}/zipTmp/{A}.zip";F=open(E,'rb');return{'zipName':C,'zipObj':F}