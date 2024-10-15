
from langchain_community.embeddings.ollama import OllamaEmbeddings
from database_controller import DatabaseController
from setting_controller import SettingController
from langchain_chroma import Chroma
import streamlit as st
import pandas as pd
import ollama

#=============================================================================#

CHROMA_PATH = "chroma"

#=============================================================================#

SettingController = SettingController()

selected_llm = SettingController.setting['selected']['llm_model']

llm_models = SettingController.setting['options']['llm_model']

selected_llm_index = llm_models.index(selected_llm)

selected_embedding = SettingController.setting['selected']['embedding_model']

embedding_models = SettingController.setting['options']['embedding_model']

selected_embedding_index = embedding_models.index(selected_embedding)

#-----------------------------------------------------------------------------#

EMBEDDING_MODEL = SettingController.setting['selected']['embedding_model']

database = Chroma(
    persist_directory  = CHROMA_PATH, 
    embedding_function = OllamaEmbeddings(model=EMBEDDING_MODEL)
    )

DatabaseController = DatabaseController(database)

if len(DatabaseController.calculate_existing_ids()) == 0:
	embedding_model_disabled = False
else:
	embedding_model_disabled = True

models = ollama.list()

#=============================================================================#

def change_llm_model():
	SettingController.change_llm_model(st.session_state.llm_model)

#-----------------------------------------------------------------------------#

def change_embedding_model():
	SettingController.change_embedding_model(st.session_state.embedding_model)

#-----------------------------------------------------------------------------#

@st.dialog("新增語言模型")
def add_llm_model():
    llm_model = st.text_input("輸入模型名稱")
    if st.button("新增"):
        SettingController.add_llm_model(llm_model)
        st.rerun()

#-----------------------------------------------------------------------------#

@st.dialog("新增嵌入模型")
def add_embedding_model():
    llm_model = st.text_input("輸入模型名稱")
    if st.button("新增"):
        SettingController.add_embedding_model(llm_model)
        st.rerun()

#-----------------------------------------------------------------------------#

@st.dialog("移除語言模型")
def remove_llm_model():
    llm_model = st.selectbox("選擇模型", llm_models)
    if st.button("移除"):
        SettingController.remove_llm_model(llm_model)
        st.rerun()

#-----------------------------------------------------------------------------#

@st.dialog("移除嵌入模型")
def remove_embedding_model():
    llm_model = st.selectbox("選擇模型", embedding_models)
    if st.button("移除"):
        SettingController.remove_embedding_model(llm_model)
        st.rerun()

#=============================================================================#

st.set_page_config(layout="wide")

if "selected_LLM_model" not in st.session_state:
    st.session_state.selected_LLM_model = ""

if "selected_embedding_model" not in st.session_state:
    st.session_state.selected_embedding_model = ""

#=============================================================================#

st.title("模型")

st.selectbox("請選擇語言模型", 
	llm_models, 
	on_change=change_llm_model, 
	key='llm_model', 
	index=selected_llm_index)

st.selectbox("請選擇嵌入模型", 
	embedding_models, 
	on_change=change_embedding_model, 
	key='embedding_model', 
	index=selected_embedding_index,
	disabled=embedding_model_disabled)

col1, col2 = st.columns([9,1])

df = pd.DataFrame(models['models'])

col1.dataframe(df)

if col2.button("新增語言模型"):
	add_llm_model()

if col2.button("移除語言模型"):
	remove_llm_model()

if col2.button("新增嵌入模型"):
	add_embedding_model()

if col2.button("移除嵌入模型"):
	remove_embedding_model()