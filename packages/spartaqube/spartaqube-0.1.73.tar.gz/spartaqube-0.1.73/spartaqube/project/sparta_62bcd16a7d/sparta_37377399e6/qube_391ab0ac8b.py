import os
from project.sparta_62bcd16a7d.sparta_37377399e6.qube_9fcfa2fb70 import qube_9fcfa2fb70
from project.sparta_62bcd16a7d.sparta_37377399e6.qube_2c2402a1fc import qube_2c2402a1fc
from project.sparta_62bcd16a7d.sparta_37377399e6.qube_b7b84934f5 import qube_b7b84934f5
from project.sparta_62bcd16a7d.sparta_37377399e6.qube_155dcdd43f import qube_155dcdd43f
class db_connection:
	def __init__(A,dbType=0):A.dbType=dbType;A.dbCon=None
	def get_db_type(A):return A.dbType
	def getConnection(A):
		if A.dbType==0:
			from django.conf import settings as B
			if B.PLATFORM in['SANDBOX','SANDBOX_MYSQL']:return
			A.dbCon=qube_9fcfa2fb70()
		elif A.dbType==1:A.dbCon=qube_2c2402a1fc()
		elif A.dbType==2:A.dbCon=qube_b7b84934f5()
		elif A.dbType==4:A.dbCon=qube_155dcdd43f()
		return A.dbCon