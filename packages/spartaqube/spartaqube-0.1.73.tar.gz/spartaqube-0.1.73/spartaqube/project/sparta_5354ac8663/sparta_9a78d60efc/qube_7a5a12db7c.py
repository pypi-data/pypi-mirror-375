_F='output'
_E=False
_D=None
_C='res'
_B='utf-8'
_A='name'
import os,sys,json,ast,re,base64,uuid,hashlib,socket,cloudpickle,websocket,subprocess,threading
from random import randint
import pandas as pd
from pathlib import Path
from cryptography.fernet import Fernet
from subprocess import PIPE
from datetime import datetime,timedelta
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.cache import cache
from django.conf import settings as conf_settings
from asgiref.sync import sync_to_async
import pytz
UTC=pytz.utc
from spartaqube_app.path_mapper_obf import sparta_4333278bd8
from project.models import UserProfile,NewPlotApiVariables,NotebookShared,DashboardShared
from project.sparta_5354ac8663.sparta_c0f904d512 import qube_ac67c5d252 as qube_ac67c5d252
from project.sparta_5354ac8663.sparta_b8b7994f57 import qube_6ee1b476a3 as qube_6ee1b476a3
from project.sparta_5354ac8663.sparta_6b03b9aba1 import qube_951781f614 as qube_951781f614
from project.sparta_5354ac8663.sparta_82fa1097b7.qube_4a8aaacb65 import convert_to_dataframe,convert_dataframe_to_json,sparta_ff0e80d635
from project.sparta_5354ac8663.sparta_82fa1097b7.qube_3713da2649 import sparta_416d6d8c82,sparta_19443989ab
from project.logger_config import logger
def sparta_ac377b6fea(file_path=_D,text=_D,b_log=True):
	if text is _D:return
	if file_path is _D:file_path='C:\\Users\\benme\\Desktop\\LOG_DEBUG.txt'
	try:
		mode='a'if os.path.exists(file_path)and os.path.getsize(file_path)>0 else'w'
		with open(file_path,mode,encoding=_B)as file:
			if mode=='a':file.write('\n')
			file.write(text)
		if b_log:logger.debug(f"Successfully wrote/appended to {file_path}")
	except Exception as e:
		if b_log:logger.debug(f"Error writing to file: {e}")
def sparta_e525f2fe2b():keygen_fernet='spartaqube-api-key';key=keygen_fernet.encode(_B);key=hashlib.md5(key).hexdigest();key=base64.b64encode(key.encode(_B));return key.decode(_B)
def sparta_c7be5838c9():keygen_fernet='spartaqube-internal-decoder-api-key';key=keygen_fernet.encode(_B);key=hashlib.md5(key).hexdigest();key=base64.b64encode(key.encode(_B));return key.decode(_B)
def sparta_1585e86531(f,str_to_encrypt):data_to_encrypt=str_to_encrypt.encode(_B);token=f.encrypt(data_to_encrypt).decode(_B);token=base64.b64encode(token.encode(_B)).decode(_B);return token
def sparta_ed6916bdd9(api_token_id):
	if api_token_id=='public':
		try:return User.objects.filter(email='public@spartaqube.com').all()[0]
		except:return
	try:
		f_private=Fernet(sparta_c7be5838c9().encode(_B));api_key=f_private.decrypt(base64.b64decode(api_token_id)).decode(_B).split('@')[1];user_profile_set=UserProfile.objects.filter(api_key=api_key,is_banned=_E).all()
		if user_profile_set.count()==1:return user_profile_set[0].user
		return
	except Exception as e:logger.debug('Could not authenticate api with error msg:');logger.debug(e);return
def sparta_130ad5a0ee(user_obj):
	userprofile_obj=UserProfile.objects.get(user=user_obj);api_key=userprofile_obj.api_key
	if api_key is _D:api_key=str(uuid.uuid4());userprofile_obj.api_key=api_key;userprofile_obj.save()
	return api_key
async def get_api_key_async_DEPREC(user_obj):
	userprofile_obj=await UserProfile.objects.aget(user=user_obj);api_key=userprofile_obj.api_key
	if api_key is _D:api_key=str(uuid.uuid4());userprofile_obj.api_key=api_key;await userprofile_obj.asave()
	return api_key
async def get_api_key_async(user_obj):
	userprofile_obj=await sync_to_async(lambda:UserProfile.objects.get(user=user_obj),thread_sensitive=_E)()
	if userprofile_obj.api_key is _D:userprofile_obj.api_key=str(uuid.uuid4());await sync_to_async(userprofile_obj.save,thread_sensitive=_E)()
	return userprofile_obj.api_key
def sparta_34b08015f3(user_obj,domain_name):api_key=sparta_130ad5a0ee(user_obj);random_nb=str(randint(0,1000));data_to_encrypt=f"apikey@{api_key}@{random_nb}";f_private=Fernet(sparta_c7be5838c9().encode(_B));private_encryption=sparta_1585e86531(f_private,data_to_encrypt);data_to_encrypt=f"apikey@{domain_name}@{private_encryption}";f_public=Fernet(sparta_e525f2fe2b().encode(_B));public_encryption=sparta_1585e86531(f_public,data_to_encrypt);return public_encryption
def sparta_152b30c4fb(json_data,user_obj):api_key=sparta_130ad5a0ee(user_obj);domain_name=json_data['domain'];public_encryption=sparta_34b08015f3(user_obj,domain_name);return{_C:1,'token':public_encryption}
def sparta_063652c532(json_data,user_obj):userprofile_obj=UserProfile.objects.get(user=user_obj);api_key=str(uuid.uuid4());userprofile_obj.api_key=api_key;userprofile_obj.save();return{_C:1}
def sparta_68d5cb9a14():plot_types=sparta_416d6d8c82();plot_types=sorted(plot_types,key=lambda x:x['Library'].lower(),reverse=_E);return{_C:1,'plot_types':plot_types}
def sparta_47dc57a6fb(json_data):logger.debug('DEBUG get_plot_options json_data');logger.debug(json_data);plot_type=json_data['plot_type'];plot_input_options_dict=sparta_19443989ab(plot_type);plot_input_options_dict[_C]=1;return plot_input_options_dict
def sparta_a3ee3d1f4e(code):
	tree=ast.parse(code)
	if isinstance(tree.body[-1],ast.Expr):last_expr_node=tree.body[-1].value;last_expr_code=ast.unparse(last_expr_node);return last_expr_code
	else:return
def sparta_222f4141cc(json_data,user_obj):
	A='errorMsg';user_code_example=json_data['userCode'];resp=_D;error_msg=''
	try:
		logger.debug('EXECUTE API EXAMPLE DEBUG DEBUG DEBUG');api_key=sparta_130ad5a0ee(user_obj);core_api_path=sparta_4333278bd8()['project/core/api'];ini_code='import os, sys\n';ini_code+=f'sys.path.insert(0, r"{str(core_api_path)}")\n';ini_code+='from spartaqube import Spartaqube as Spartaqube\n';ini_code+=f"Spartaqube('{api_key}')\n";user_code_example=ini_code+'\n'+user_code_example;exec(user_code_example,globals());last_expression_str=sparta_a3ee3d1f4e(user_code_example)
		if last_expression_str is not _D:
			last_expression_output=eval(last_expression_str)
			if last_expression_output.__class__.__name__=='HTML':resp=last_expression_output.data
			else:resp=last_expression_output
			resp=json.dumps(resp);return{_C:1,'resp':resp,A:error_msg}
		return{_C:-1,A:'No output to display. You should put the variable to display as the last line of the code'}
	except Exception as e:return{_C:-1,A:str(e)}
def sparta_5cc41e0502(json_data,user_obj):
	session_id=json_data['session'];new_plot_api_variables_set=NewPlotApiVariables.objects.filter(session_id=session_id).all();logger.debug(f"gui_plot_api_variables with session_id {session_id}");logger.debug(new_plot_api_variables_set)
	if new_plot_api_variables_set.count()>0:
		new_plot_api_variables_obj=new_plot_api_variables_set[0];pickled_variables=new_plot_api_variables_obj.pickled_variables;unpickled_data=cloudpickle.loads(pickled_variables.encode('latin1'));notebook_variables=[]
		for notebook_variable in unpickled_data:
			notebook_variables_df=convert_to_dataframe(notebook_variable)
			if notebook_variables_df is not _D:0
			else:notebook_variables_df=pd.DataFrame()
			notebook_variables.append(convert_dataframe_to_json(notebook_variables_df))
		logger.debug(notebook_variables);return{_C:1,'notebook_variables':notebook_variables}
	return{_C:-1}
def sparta_a04ab90d5e(json_data,user_obj):widget_id=json_data['widgetId'];return qube_6ee1b476a3.sparta_a04ab90d5e(user_obj,widget_id)
def sparta_020f5bfb89(json_data,user_obj):
	A='api_service';api_service=json_data[A];print(A);print(api_service)
	if api_service=='get_status':output=sparta_fa5f24532f()
	elif api_service=='get_status_ws':return sparta_99d33c9ec1()
	elif api_service=='get_connectors':return sparta_9e8c7f04b9(json_data,user_obj)
	elif api_service=='get_connector_tables':return sparta_b90b73d355(json_data,user_obj)
	elif api_service=='get_data_from_connector':return sparta_df7d3cd85a(json_data,user_obj)
	elif api_service=='get_widgets':output=sparta_f7ed9fffe9(user_obj)
	elif api_service=='has_widget_id':return sparta_5a33f41066(json_data,user_obj)
	elif api_service=='get_widget_data':return sparta_37e27bb8e6(json_data,user_obj)
	elif api_service=='get_plot_types':return sparta_416d6d8c82()
	elif api_service=='put_df':return sparta_6d64e9b205(json_data,user_obj)
	elif api_service=='drop_df':return sparta_daae8a454c(json_data,user_obj)
	elif api_service=='drop_dispo_df':return sparta_a77141d141(json_data,user_obj)
	elif api_service=='get_available_df':return sparta_6d4bee4134(json_data,user_obj)
	elif api_service=='get_df':return sparta_eaa6e6dc76(json_data,user_obj)
	elif api_service=='has_dataframe_slug':return sparta_b19c5b70ae(json_data,user_obj)
	return{_C:1,_F:output}
def sparta_fa5f24532f():return 1
def sparta_9e8c7f04b9(json_data,user_obj):
	A='db_connectors';keys_to_retain=['connector_id',_A,'db_engine'];res_dict=qube_6ee1b476a3.sparta_3fae7ef16a(json_data,user_obj)
	if res_dict[_C]==1:res_dict[A]=[{k:d[k]for k in keys_to_retain if k in d}for d in res_dict[A]]
	return res_dict
def sparta_b90b73d355(json_data,user_obj):res_dict=qube_6ee1b476a3.sparta_dfe537363d(json_data,user_obj);return res_dict
def sparta_df7d3cd85a(json_data,user_obj):res_dict=qube_6ee1b476a3.sparta_47175a5b73(json_data,user_obj);return res_dict
def sparta_f7ed9fffe9(user_obj):return qube_6ee1b476a3.sparta_c439e755fa(user_obj)
def sparta_5a33f41066(json_data,user_obj):return qube_6ee1b476a3.sparta_6f2184dbef(json_data,user_obj)
def sparta_37e27bb8e6(json_data,user_obj):return qube_6ee1b476a3.sparta_9060ef4754(json_data,user_obj)
def sparta_6d64e9b205(json_data,user_obj):return qube_951781f614.sparta_b6bef797b9(json_data,user_obj)
def sparta_daae8a454c(json_data,user_obj):return qube_951781f614.sparta_aa27ab7547(json_data,user_obj)
def sparta_a77141d141(json_data,user_obj):return qube_951781f614.sparta_df41abda94(json_data,user_obj)
def sparta_6d4bee4134(json_data,user_obj):return qube_951781f614.sparta_bad6205770(json_data,user_obj)
def sparta_eaa6e6dc76(json_data,user_obj):return qube_951781f614.sparta_5f8321cb12(json_data,user_obj)
def sparta_b19c5b70ae(json_data,user_obj):return qube_951781f614.sparta_e48fdab00d(json_data,user_obj)
def sparta_c269f2302c(json_data,user_obj):date_now=datetime.now().astimezone(UTC);session_id=str(uuid.uuid4());pickled_data=json_data['data'];NewPlotApiVariables.objects.create(user=user_obj,session_id=session_id,pickled_variables=pickled_data,date_created=date_now,last_update=date_now);return{_C:1,'session_id':session_id}
def sparta_4becc85369():return sparta_416d6d8c82()
def sparta_e427e40f40():cache.clear();return{_C:1}
def sparta_99d33c9ec1():
	global is_wss_valid;is_wss_valid=_E
	try:
		api_path=sparta_4333278bd8()['api']
		with open(os.path.join(api_path,'app_data_asgi.json'),'r')as json_file:loaded_data_dict=json.load(json_file)
		ASGI_PORT=int(loaded_data_dict['default_port'])
	except:ASGI_PORT=5664
	logger.debug('ASGI_PORT');logger.debug(ASGI_PORT)
	def on_open(ws):global is_wss_valid;is_wss_valid=True;ws.close()
	def on_error(ws,error):global is_wss_valid;is_wss_valid=_E;ws.close()
	def on_close(ws,close_status_code,close_msg):
		try:logger.debug(f"Connection closed with code: {close_status_code}, message: {close_msg}");ws.close()
		except Exception as e:logger.debug(f"Except: {e}")
	ws=websocket.WebSocketApp(f"ws://127.0.0.1:{ASGI_PORT}/ws/statusWS",on_open=on_open,on_close=on_close);ws.run_forever()
	if ws.sock and ws.sock.connected:logger.debug('WebSocket is still connected. Attempting to close again.');ws.close()
	else:logger.debug('WebSocket is properly closed.')
	return{_C:1,_F:is_wss_valid}
def sparta_5b4310d0f5(json_data,user_obj):
	I='displayText';H='Plot';G='-1';F='dict';E='popTitle';D='other';C='preview';B='popType';A='type';api_methods=[{_A:'Spartaqube().get_connectors()',A:1,B:F,C:'',D:'',E:'Get Connectors'},{_A:'Spartaqube().get_connector_tables("connector_id")',A:1,B:F,C:'',D:'',E:'Get Connector Tables'},{_A:'Spartaqube().get_data_from_connector("connector_id", table=None, sql_query=None, output_format=None)',A:1,B:F,C:'',D:'',E:'Get Connector Data'},{_A:'Spartaqube().get_plot_types()',A:1,B:'list',C:'',D:'',E:'Get Plot Type'},{_A:'Spartaqube().get_widgets()',A:1,B:F,C:'',D:'',E:'Get Widgets list'},{_A:'Spartaqube().iplot([var1, var2], width="100%", height=750)',A:1,B:H,C:'',D:G,E:'Interactive plot'},{_A:'Spartaqube().plot(\n    x:list=None, y:list=None, r:list=None, legend:list=None, labels:list=None, ohlcv:list=None, shaded_background:list=None, \n    datalabels:list=None, border:list=None, background:list=None, border_style:list=None, tooltips_title:list=None, tooltips_label:list=None,\n    chart_type="line", interactive=True, widget_id=None, title=None, title_css:dict=None, stacked:bool=False, date_format:str=None, time_range:bool=False,\n    gauge:dict=None, gauge_zones:list=None, gauge_zones_labels:list=None, gauge_zones_height:list=None,\n    dataframe:pd.DataFrame=None, dates:list=None, returns:list=None, returns_bmk:list=None,\n    options:dict=None, width=\'100%\', height=750\n)',A:1,B:H,C:'',D:G,I:'Spartaqube().plot(...)',E:'Programmatic plot'},{_A:'Spartaqube().get_available_df()',A:1,B:'List',C:'',D:G,E:'Get available dataframes'},{_A:'Spartaqube().get_df(table_name, dispo=None, slug=None)',A:1,B:'pd.DataFrame',C:'',D:G,E:'Get dataframe'},{_A:'Spartaqube().put_df(df:pd.DataFrame, table_name:str, dispo=None, mode="append")',A:1,B:F,C:'',D:G,E:'Insert a dataframe'},{_A:'Spartaqube().drop_df(table_name, slug=None)',A:1,B:F,C:'',D:G,E:'Drop dataframe'},{_A:'Spartaqube().drop_df_by_id(id=id)',A:1,B:F,C:'',D:G,E:'Drop dataframe (by id)'},{_A:'Spartaqube().drop_dispo_df(table_name, dispo, slug=None)',A:1,B:F,C:'',D:G,E:'Drop dataframe for dispo date'}];api_widgets_suggestions=[]
	if not user_obj.is_anonymous:
		api_get_widgets=sparta_f7ed9fffe9(user_obj)
		for widget_dict in api_get_widgets:widget_id_with_quote="'"+str(widget_dict['id'])+"'";widget_cmd=f"Spartaqube().get_widget({widget_id_with_quote})";api_widgets_suggestions.append({_A:widget_cmd,I:widget_dict[_A],E:widget_dict[_A],A:2,B:'Widget',C:widget_cmd,D:widget_dict['id']})
	autocomplete_suggestions_arr=api_methods+api_widgets_suggestions;return{_C:1,'suggestions':autocomplete_suggestions_arr}
def sparta_c271618aab(notebook_id):
	notebook_shared_set=NotebookShared.objects.filter(is_delete=0,notebook__is_delete=0,notebook__notebook_id=notebook_id)
	if notebook_shared_set.count()>0:return notebook_shared_set[0].user
def sparta_64f51d3e21(dashboard_id):
	dashboard_shared_set=DashboardShared.objects.filter(is_delete=0,dashboard__is_delete=0,dashboard__dashboard_id=dashboard_id)
	if dashboard_shared_set.count()>0:return dashboard_shared_set[0].user