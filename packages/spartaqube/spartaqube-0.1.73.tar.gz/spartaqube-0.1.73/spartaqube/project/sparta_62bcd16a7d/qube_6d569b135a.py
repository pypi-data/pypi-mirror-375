import time
from project.logger_config import logger
def sparta_64e6481909():
	B=0;A=time.time()
	while True:B=A;A=time.time();yield A-B
TicToc=sparta_64e6481909()
def sparta_a217f66f0b(tempBool=True):
	A=next(TicToc)
	if tempBool:logger.debug('Elapsed time: %f seconds.\n'%A);return A
def sparta_c7d9bb3ba0():sparta_a217f66f0b(False)