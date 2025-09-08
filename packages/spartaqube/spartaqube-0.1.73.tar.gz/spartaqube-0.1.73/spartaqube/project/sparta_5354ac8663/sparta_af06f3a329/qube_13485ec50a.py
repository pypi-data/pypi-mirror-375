_A='utf-8'
import os,json,base64,hashlib,random
from cryptography.fernet import Fernet
def sparta_2cfaecd2a1():A='__API_AUTH__';A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_b906fce8cf(objectToCrypt):A=objectToCrypt;C=sparta_2cfaecd2a1();D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_7e4c8cb9b3(apiAuth):A=apiAuth;B=sparta_2cfaecd2a1();C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_94a49827dd(kCrypt):A='__SQ_AUTH__'+str(kCrypt);A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_76d880a922(objectToCrypt,kCrypt):A=objectToCrypt;C=sparta_94a49827dd(kCrypt);D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_a8ea7601bb(objectToDecrypt,kCrypt):A=objectToDecrypt;B=sparta_94a49827dd(kCrypt);C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_7bc73cadb0(kCrypt):A='__SQ_EMAIL__'+str(kCrypt);A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_6fa9be3a59(objectToCrypt,kCrypt):A=objectToCrypt;C=sparta_7bc73cadb0(kCrypt);D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_8f3e03639a(objectToDecrypt,kCrypt):A=objectToDecrypt;B=sparta_7bc73cadb0(kCrypt);C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_db98259cbf(kCrypt):A='__SQ_KEY_SSO_CRYPT__'+str(kCrypt);A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_983234b80b(objectToCrypt,kCrypt):A=objectToCrypt;C=sparta_db98259cbf(kCrypt);D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_a4a3da22c4(objectToDecrypt,kCrypt):A=objectToDecrypt;B=sparta_db98259cbf(kCrypt);C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_bfa339f0e2():A='__SQ_IPYNB_SQ_METADATA__';A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_e7a7c062d5(objectToCrypt):A=objectToCrypt;C=sparta_bfa339f0e2();D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_2a7cfa1821(objectToDecrypt):A=objectToDecrypt;B=sparta_bfa339f0e2();C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)