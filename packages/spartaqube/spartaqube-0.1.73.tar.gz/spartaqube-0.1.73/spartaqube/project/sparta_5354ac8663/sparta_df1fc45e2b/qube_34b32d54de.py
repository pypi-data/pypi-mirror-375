import os,json,ast
def sparta_d02ce93b53():B='openai';A='anthropic';return{'gpt-3.5-turbo':B,'gpt-4o':B,'claude-3-opus-20240229':A,'claude-3-sonnet-20240229':A,'claude-3-haiku-20240307':A}
def sparta_517e85b40b(line):
	try:ast.parse(line);return True
	except SyntaxError:return False
def sparta_1c358d5682(code):A=code.splitlines();B=[A for A in A if sparta_517e85b40b(A.strip())];return'\n'.join(B)
def sparta_995fd3e7aa(variable_list):
	E='type';D='name';B=['You have access to the following Python variables in your workspace:\n']
	for A in variable_list:
		if A.get('is_df'):F=A['preview'].splitlines()[-1].strip();C=f"- `{A[D]}`: a **{A[E]}** with shape {F}. \n  Columns: {A['df_columns']}.";B.append(C)
		else:C=f"- `{A[D]}`: a **{A[E]}**.";B.append(C)
	return'\n'.join(B)