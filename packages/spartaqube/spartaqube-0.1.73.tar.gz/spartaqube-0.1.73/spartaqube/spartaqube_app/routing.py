import importlib.metadata
from channels.routing import ProtocolTypeRouter,URLRouter
from django.urls import re_path as url
from django.conf import settings
from project.sparta_62bcd16a7d.sparta_4db29dfece import qube_9e2f2080de,qube_9fd54021fa,qube_a852153c3a,qube_e485211eab,qube_0e086f96d1,qube_1883767be4,qube_6e6e2e3e5b,qube_13da4fe415,qube_ed210fd0a0,qube_3feca720f3
from channels.auth import AuthMiddlewareStack
import channels
channels_ver=importlib.metadata.version('channels')
channels_major=int(channels_ver.split('.')[0])
def sparta_735d5a4de1(this_class):
	A=this_class
	if channels_major<=2:return A
	else:return A.as_asgi()
urlpatterns=[url('ws/statusWS',sparta_735d5a4de1(qube_9e2f2080de.StatusWS)),url('ws/notebookWS',sparta_735d5a4de1(qube_9fd54021fa.NotebookWS)),url('ws/wssConnectorWS',sparta_735d5a4de1(qube_a852153c3a.WssConnectorWS)),url('ws/pipInstallWS',sparta_735d5a4de1(qube_e485211eab.PipInstallWS)),url('ws/gitNotebookWS',sparta_735d5a4de1(qube_0e086f96d1.GitNotebookWS)),url('ws/xtermGitWS',sparta_735d5a4de1(qube_1883767be4.XtermGitWS)),url('ws/hotReloadLivePreviewWS',sparta_735d5a4de1(qube_6e6e2e3e5b.HotReloadLivePreviewWS)),url('ws/apiWebserviceWS',sparta_735d5a4de1(qube_13da4fe415.ApiWebserviceWS)),url('ws/apiWebsocketWS',sparta_735d5a4de1(qube_ed210fd0a0.ApiWebsocketWS)),url('ws/chatbotWS',sparta_735d5a4de1(qube_3feca720f3.ChatbotWS))]
application=ProtocolTypeRouter({'websocket':AuthMiddlewareStack(URLRouter(urlpatterns))})
for thisUrlPattern in urlpatterns:
	try:
		if len(settings.DAPHNE_PREFIX)>0:thisUrlPattern.pattern._regex='^'+settings.DAPHNE_PREFIX+'/'+thisUrlPattern.pattern._regex
	except Exception as e:print(e)