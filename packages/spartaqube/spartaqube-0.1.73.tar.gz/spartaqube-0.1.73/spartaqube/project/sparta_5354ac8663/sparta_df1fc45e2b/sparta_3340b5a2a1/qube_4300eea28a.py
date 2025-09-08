_A='gpt-3.5-turbo'
from openai import OpenAI
from typing import Optional,AsyncGenerator
from spartaqube_app.secrets import sparta_1c1a070836
from project.sparta_5354ac8663.sparta_df1fc45e2b.qube_9e508cfc86 import LLMGenerator
from project.sparta_5354ac8663.sparta_df1fc45e2b.qube_34b32d54de import sparta_995fd3e7aa,sparta_1c358d5682
class OpenAIGeneratorLLM(LLMGenerator):
	def __init__(A,system_prompt,api_key,user_obj,model=_A,mode='notebook-kernel'):
		B=api_key;super().__init__(system_prompt,B,user_obj,model,mode);A.available_models=[_A,'gpt-4o']
		if not A.cf_stream:
			if not B:raise ValueError('OpenAI API key is required. Either pass it to the constructor or set OPENAI_API_KEY environment variable.')
			A.client=OpenAI(api_key=B)
		A.ini_msg=[{'role':'system','content':A.system_prompt}];A.messages=A.ini_msg.copy()
	def construct_generator(A,system_prompt):A.llm_generator_spartaqube_api=OpenAIGeneratorLLM(system_prompt,api_key=A.api_key,user_obj=A.user_obj,model=A.model,mode='spartaqube-api-context')
	def clear_chatbot_spartaqube_api_rag_context(A):
		B=''
		if A.is_local_system_prompt:
			try:from project.sparta_5354ac8663.sparta_df1fc45e2b.sq_prompt import get_spartaqube_api_context_rag as C;B=C()
			except:pass
		A.construct_generator(B)
	async def spartaqube_api_context_rag(A,prompt):
		if A.llm_generator_spartaqube_api is None:
			B=''
			if A.is_local_system_prompt:
				try:from project.sparta_5354ac8663.sparta_df1fc45e2b.sq_prompt import get_spartaqube_api_context_rag as C;B=C()
				except:pass
			A.construct_generator(B)
		return await A.llm_generator_spartaqube_api.stream_spartaqube_api_context(prompt)
	def restore_llm_spartaqube_api(A,messages):
		B=''
		if A.is_local_system_prompt:
			try:from project.sparta_5354ac8663.sparta_df1fc45e2b.sq_prompt import get_spartaqube_api_context_rag as C;B=C()
			except:pass
		A.construct_generator(B);A.llm_generator_spartaqube_api.messages=messages