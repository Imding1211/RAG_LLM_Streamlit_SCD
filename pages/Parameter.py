
from setting_controller import SettingController
import streamlit as st

#=============================================================================#

SettingController = SettingController()

selected_prompt    = SettingController.setting['selected']['prompt']
selected_query_num = SettingController.setting['selected']['query_num']
selected_database  = SettingController.setting['selected']['database']

#=============================================================================#

def change_query_num():
	SettingController.change_query_num(st.session_state.query_num)

#-----------------------------------------------------------------------------#

def change_database():
	SettingController.change_database(st.session_state.database)
	
#=============================================================================#

st.set_page_config(layout="wide")

#=============================================================================#

st.title("參數")

query_num_container = st.container(border=True)

query_num_container.slider("資料檢索數量",
	1, 10, selected_query_num, 
	on_change=change_query_num,
	key="query_num",
	)

database_container = st.container(border=True)

database_container.text_input("資料庫名稱", 
	selected_database.split('/')[-1],
	key="database",
	)

if database_container.button("確認"):
	SettingController.change_database(st.session_state.database)
	st.toast('資料庫名稱已更新。')

prompt_container = st.container(border=True)

prompt_container.text_area("自訂提示詞", 
	selected_prompt,
	height=200,
	key="prompt",
	)

prompt_warning = prompt_container.empty()

if prompt_container.button("更新"):
	
	if "{context}" not in st.session_state.prompt and "{question}" not in st.session_state.prompt:
		prompt_warning.warning('提示詞必須包含{context}與{question}。', icon="⚠️")

	elif "{context}" not in st.session_state.prompt:
		prompt_warning.warning('提示詞必須包含{context}。', icon="⚠️")

	elif "{question}" not in st.session_state.prompt:
		prompt_warning.warning('提示詞必須包含{question}。', icon="⚠️")

	else:
		SettingController.change_prompt(st.session_state.prompt)
		st.toast('提示詞已更新。')

