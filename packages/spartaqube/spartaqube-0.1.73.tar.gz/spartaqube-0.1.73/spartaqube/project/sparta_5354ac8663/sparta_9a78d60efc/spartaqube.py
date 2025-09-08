_P='append'
_O='connector_id'
_N='Invalid chart type. Use an ID found in the DataFrame get_plot_types()'
_M='You do not have the rights to access this object'
_L='utf-8'
_K='data'
_J='slug'
_I='dispo'
_H='table_name'
_G='100%'
_F='widget_id'
_E=False
_D='res'
_C=True
_B='api_service'
_A=None
import os,json,uuid,base64,pickle,pandas as pd,urllib.parse
from IPython.core.display import display,HTML
import warnings
warnings.filterwarnings('ignore',message='Consider using IPython.display.IFrame instead',category=UserWarning)
from datetime import datetime,timedelta
import pytz
UTC=pytz.utc
from project.models import UserProfile,PlotDBChart,PlotDBChartShared,PlotDBPermission,DataFrameShared,DataFramePermission
from project.sparta_5354ac8663.sparta_9a78d60efc.qube_7a5a12db7c import sparta_020f5bfb89
from project.sparta_5354ac8663.sparta_82fa1097b7.qube_4a8aaacb65 import convert_to_dataframe,convert_dataframe_to_json,process_dataframe_components
from project.sparta_5354ac8663.sparta_82fa1097b7.qube_3713da2649 import sparta_416d6d8c82
from project.sparta_5354ac8663.sparta_6b03b9aba1 import qube_951781f614 as qube_951781f614
from project.sparta_5354ac8663.sparta_c0f904d512 import qube_ac67c5d252 as qube_ac67c5d252
def sparta_fd87ef2187(user_obj):
	A=qube_ac67c5d252.sparta_3530108797(user_obj)
	if len(A)>0:B=[A.user_group for A in A]
	else:B=[]
	return B
class Spartaqube:
	_instance=_A
	def __new__(A,*B,**C):
		if A._instance is _A:A._instance=super().__new__(A);A._instance._initialized=_E
		return A._instance
	def __init__(A,api_token_id=_A):
		B=api_token_id
		if A._initialized:return
		A._initialized=_C
		if B is _A:
			try:B=os.environ['api_key']
			except:pass
		A.api_token_id=B;A.user_obj=UserProfile.objects.get(api_key=B).user
	def test(A):print('test')
	def get_widget_data(A,widget_id):B={_B:'get_widget_data',_F:widget_id};return sparta_020f5bfb89(B,A.user_obj)
	def sparta_6f2184dbef(A,widget_id):B={_B:'has_widget_id',_F:widget_id};return sparta_020f5bfb89(B,A.user_obj)
	def get_widget(E,widget_id,width=_G,height=500):
		F=widget_id;A=PlotDBChart.objects.filter(plot_chart_id__startswith=F,is_delete=_E).all();B=_E
		if A.count()==1:B=_C
		else:
			I=F;A=PlotDBChart.objects.filter(slug__startswith=I,is_delete=_E).all()
			if A.count()==1:B=_C
		if B:
			C=A[A.count()-1];G=sparta_fd87ef2187(E.user_obj)
			if len(G)>0:D=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=G,plot_db_chart__is_delete=0,plot_db_chart=C)|Q(is_delete=0,user=user_obj,plot_db_chart__is_delete=0,plot_db_chart=C))
			else:D=PlotDBChartShared.objects.filter(is_delete=0,user=E.user_obj,plot_db_chart__is_delete=0,plot_db_chart=C)
			if D.count()>0:H=str(uuid.uuid4());J=datetime.now().astimezone(UTC);PlotDBPermission.objects.create(plot_db_chart=D[0].plot_db_chart,token=H,date_created=J);return HTML(f'<iframe src="/plot-widget-token/{H}" width="{width}" height="{height}" frameborder="0" allow="clipboard-write"></iframe>')
		return _M
	def iplot(I,*B,width=_G,height=550):
		if len(B)==0:raise Exception('You must pass at least one input variable to plot')
		else:
			C=dict()
			for(E,D)in enumerate(B):
				if D is _A:continue
				F=convert_to_dataframe(D);C[E]=convert_dataframe_to_json(F)
			G=json.dumps(C);A=str(uuid.uuid4());H=f'''
                <form id="dataForm_{A}" action="plot-gui" method="POST" target="{A}">
                    <input type="hidden" name="data" value=\'{G}\' />
                </form>
                <iframe 
                    id="{A}"
                    name="{A}"
                    width="{width}" 
                    height="{height}" 
                    frameborder="0" 
                    allow="clipboard-write"></iframe>

                <script>
                    // Submit the form automatically to send data to the iframe
                    document.getElementById(\'dataForm_{A}\').submit();
                </script>
                ''';return HTML(H)
	def plot(V,*W,**A):
		I='width';H='chart_type';D=dict()
		for(J,F)in A.items():
			if F is _A:continue
			K=convert_to_dataframe(F);D[J]=convert_dataframe_to_json(K)
		E=_A
		if H not in A:
			if _F not in A:raise Exception("Missing chart_type parameter. For instance: chart_type='line'")
			else:E=0
		if E is _A:
			L=sparta_416d6d8c82(b_return_type_id=_C)
			try:M=json.loads(D[H])[_K][0][0];E=[A for A in L if A['ID']==M][0]['type_plot']
			except:raise Exception(_N)
		N=A.get(I,_G);O=A.get(I,'500');P=A.get('interactive',_C);G=A.get(_F,_A);Q={'interactive_api':1 if P else 0,'is_api_template':1 if G is not _A else 0,_F:G};R=json.dumps(Q);S=urllib.parse.quote(R);B=dict();B[_D]=1;B['notebook_variables']=D;B['type_chart']=E;B['override_options']=D.get('options',dict());T=json.dumps(B);C=str(uuid.uuid4());U=f'''
            <form id="dataForm_{C}" action="/plot-api/{S}" method="POST" target="{C}">
                <input type="hidden" name="data" value=\'{T}\' />
            </form>
            <iframe 
                id="{C}"
                name="{C}"
                width="{N}" 
                height="{O}" 
                frameborder="0" 
                allow="clipboard-write"></iframe>

            <script>
                // Submit the form automatically to send data to the iframe
                document.getElementById(\'dataForm_{C}\').submit();
            </script>
            ''';return HTML(U)
	def plot_documentation(B,chart_type='line'):
		A=chart_type;C=B.get_plot_types()
		if len([B for B in C if B['ID']==A])>0:D=f"api#plot-{A}";return D
		else:raise Exception(_N)
	def plot_template(B,*C,**A):
		if _F in A:return B.plot(*C,**A)
		raise Exception('Missing widget_id')
	def get_connector_tables(A,connector_id):B={_B:'get_connector_tables',_O:connector_id};return sparta_020f5bfb89(B,A.user_obj)
	def get_data_from_connector(I,connector_id,table=_A,sql_query=_A,output_format=_A,dynamic_inputs=_A):
		G=dynamic_inputs;F=output_format;E=sql_query;A={_B:'get_data_from_connector'};A[_O]=connector_id;A[_H]=table;A['query_filter']=E;A['bApplyFilter']=1 if E is not _A else 0;H=[]
		if G is not _A:
			for(J,K)in G.items():H.append({'input':J,'default':K})
		A['dynamic_inputs']=H;B=sparta_020f5bfb89(A,I.user_obj);C=_E
		if F is _A:C=_C
		elif F=='DataFrame':C=_C
		if C:
			if B[_D]==1:D=json.loads(B[_K])
			return pd.DataFrame(D[_K],index=D['index'],columns=D['columns'])
		return B
	def apply_method(B,method_name,*D,**C):A=C;A[_B]=method_name;return sparta_020f5bfb89(A,B.user_obj)
	def __getattr__(A,name):return lambda*B,**C:A.apply_method(name,*B,**C)
	def __setstate__(A,state):A.__dict__.update(state)
	def sparta_738a7bcc79(B,dispo):A=pickle.dumps(dispo);return base64.b64encode(A).decode(_L)
	def sparta_b6bef797b9(C,df,table_name,dispo=_A,mode=_P):
		A=dispo;B={_B:'put_df'};E=pickle.dumps(df);F=base64.b64encode(E).decode(_L);B['df']=F;B[_H]=table_name;B['mode']=mode;B[_I]=C.format_dispo(A)
		if mode not in[_P,'replace']:raise Exception("Mode should be: 'append' or 'replace'")
		if isinstance(A,pd.Series)or isinstance(A,pd.DatetimeIndex)or type(A).__name__=='ndarray'and type(A).__module__=='numpy':A=list(A);B[_I]=C.format_dispo(A)
		if isinstance(A,list):
			if len(A)!=len(df):raise Exception('If you want to use a list of dispo, it must have the same length at the dataframe')
		D=qube_951781f614.sparta_b6bef797b9(B,C.user_obj)
		if D[_D]==1:print('Dataframe inserted successfully!')
		return D
	def sparta_aa27ab7547(C,table_name,slug=_A):
		A={_B:'drop_df'};A[_H]=table_name;A[_J]=slug;B=qube_951781f614.sparta_aa27ab7547(A,C.user_obj)
		if B[_D]==1:print('Dataframe dropped successfully!')
		return B
	def sparta_b94f449727(C,id):
		A={_B:'drop_df_by_id'};A['id']=id;B=qube_951781f614.sparta_b94f449727(A,C.user_obj)
		if B[_D]==1:print(f"Dataframe dropped successfully for dispo!")
		return B
	def sparta_df41abda94(B,table_name,dispo,slug=_A):
		C=dispo;A={_B:'drop_dispo_df'};A[_H]=table_name;A[_I]=B.format_dispo(C);A[_J]=slug;D=qube_951781f614.sparta_df41abda94(A,B.user_obj)
		if D[_D]==1:print(f"Dataframe dropped successfully for dispo {C} !")
		return D
	def sparta_bad6205770(A):B={_B:'get_available_df'};return qube_951781f614.sparta_bad6205770(B,A.user_obj)
	def sparta_5f8321cb12(D,table_name,dispo=_A,slug=_A,b_concat=_C):
		A={_B:'get_df'};A[_H]=table_name;A[_I]=D.format_dispo(dispo);A[_J]=slug;B=qube_951781f614.sparta_5f8321cb12(A,D.user_obj)
		if B[_D]==1:
			F=pickle.loads(base64.b64decode(B['encoded_blob'].encode(_L)));E=[pickle.loads(A['df_blob']).assign(dispo=A[_I])for A in F]
			if b_concat:
				try:C=pd.concat(E);C=process_dataframe_components(C);return C
				except Exception as G:print('Could not concatenate all dataframes together with following error message:');raise str(G)
			else:return E
		return B
	def open_df(C,dataframe_id,width=_G,height=500):
		A=DataFrameShared.objects.filter(is_delete=0,user=C.user_obj,plot_db_chart__is_delete=0,plot_db_chart__plot_chart_id=widget_id)
		if A.count()>0:B=str(uuid.uuid4());D=datetime.now().astimezone(UTC);DataFramePermission.objects.create(dataframe_model=A[0].plot_db_chart,token=B,date_created=D);return HTML(f'<iframe src="/plot-dataframe-token/{B}" width="{width}" height="{height}" frameborder="0" allow="clipboard-write"></iframe>')
		return _M
	def sparta_e48fdab00d(A,slug):B={_B:'has_dataframe_slug',_J:slug};return sparta_020f5bfb89(B,A.user_obj)
	def open_data_df(F,data_df,name='',width=_G,height=600,detached=_E):
		A=str(uuid.uuid4());C=convert_dataframe_to_json(data_df);D=json.dumps(C);B=A
		if detached:B=name
		E=f'''
        <form id="dataForm_{A}" action="/plot-gui-df" method="POST" target="{A}">
            <input type="hidden" name="data" value=\'{D}\' />
            <input type="hidden" name="name" value=\'{name}\' />
        </form>
        <iframe 
            id="{A}"
            name="{B}"
            width="{width}" 
            height="{height}" 
            frameborder="0" 
            allow="clipboard-write"></iframe>
        <script>
            // Submit the form automatically to send data to the iframe
            document.getElementById(\'dataForm_{A}\').submit();
        </script>
        ''';return HTML(E)