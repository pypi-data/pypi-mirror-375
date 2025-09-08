import os,sys,getpass,platform
from project.sparta_5354ac8663.sparta_82fa1097b7.qube_0e647c534b import sparta_fba3132a9a,sparta_5cf63b95a7
def sparta_c4b5d73e17(full_path,b_print=False):
	B=b_print;A=full_path
	try:
		if not os.path.exists(A):
			os.makedirs(A)
			if B:print(f"Folder created successfully at {A}")
		elif B:print(f"Folder already exists at {A}")
	except Exception as C:print(f"An error occurred: {C}")
def sparta_2ed668cbe3():
	if sparta_5cf63b95a7():A='/app/APPDATA/local_db/db.sqlite3'
	else:C=sparta_fba3132a9a();B=os.path.join(C,'data');sparta_c4b5d73e17(B);A=os.path.join(B,'db.sqlite3')
	return A