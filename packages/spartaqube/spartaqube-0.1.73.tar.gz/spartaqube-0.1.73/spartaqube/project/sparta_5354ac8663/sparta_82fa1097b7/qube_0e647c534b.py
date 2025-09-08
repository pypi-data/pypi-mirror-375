_A='windows'
import os,platform,getpass
def sparta_5cf63b95a7():
	try:A=str(os.environ.get('IS_REMOTE_SPARTAQUBE_CONTAINER','False'))=='True'
	except:A=False
	return A
def sparta_0368e4aa96():
	A=platform.system()
	if A=='Windows':return _A
	elif A=='Linux':return'linux'
	elif A=='Darwin':return'mac'
	else:return
def sparta_fba3132a9a():
	if sparta_5cf63b95a7():return'/spartaqube'
	A=sparta_0368e4aa96()
	if A==_A:B=f"C:\\Users\\{getpass.getuser()}\\SpartaQube"
	elif A=='linux':B=os.path.expanduser('~/SpartaQube')
	elif A=='mac':B=os.path.expanduser('~/Library/Application Support\\SpartaQube')
	return B