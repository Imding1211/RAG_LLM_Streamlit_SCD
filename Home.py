
from langchain_community.embeddings.ollama import OllamaEmbeddings
from database_controller import DatabaseController
from setting_controller import SettingController
from query_controller import QueryController
from langchain_chroma import Chroma
import streamlit as st

#=============================================================================#

SettingController = SettingController()

PROMPT_TEMPLT   = SettingController.setting['selected']['prompt']
LLM_MODEL       = SettingController.setting['selected']['llm_model']
EMBEDDING_MODEL = SettingController.setting['selected']['embedding_model']
QUERY_NUM       = SettingController.setting['selected']['query_num']
CHROMA_PATH     = SettingController.setting['selected']['database']

#-----------------------------------------------------------------------------#

# 初始化Chroma向量存儲
database = Chroma(
    persist_directory  = CHROMA_PATH, 
    embedding_function = OllamaEmbeddings(model=EMBEDDING_MODEL)
    )

QueryController    = QueryController(database, LLM_MODEL, QUERY_NUM, PROMPT_TEMPLT)
DatabaseController = DatabaseController(database)

#=============================================================================#

st.set_page_config(layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "使用繁體中文回答問題", "source": None}]

    if len(DatabaseController.calculate_existing_ids()) == 0:
        info = "👈 Hi~ 資料庫是空的，請先到Database頁面點選上傳資料。"
        st.session_state.messages.append({"role": "assistant", "content": info, "source": None})

    else:
        info = "✋ Hi~ 請問想詢問什麼問題呢？"
        st.session_state.messages.append({"role": "assistant", "content": info, "source": None})

#=============================================================================#

st.title("資料查詢")

#-----------------------------------------------------------------------------#

for message in st.session_state.messages[1:]:

    if message["role"] == "user":
        with st.chat_message("user", avatar="🦖"):
            st.markdown(message["content"])

    else:
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(message["content"])

            if message["source"] is not None:
                st.caption(message["source"])

#-----------------------------------------------------------------------------#

if question := st.chat_input("輸入問題"):

    with st.chat_message("user", avatar="🦖"):
        st.markdown(question)

#-----------------------------------------------------------------------------#

    results, sources = QueryController.generate_results(question)

    prompt = QueryController.generate_prompt(question, results)
    
    source_info = "資料來源: " + ", ".join(sources)

    st.session_state.messages.append({"role": "user", "content": prompt, "source": None})

#-----------------------------------------------------------------------------#

    with st.chat_message("assistant", avatar="🤖"):
        response = st.write_stream(QueryController.ollama_generator(st.session_state.messages))
        st.caption(source_info)

    st.session_state.messages[-1]["content"] = question

    st.session_state.messages.append({"role": "assistant", "content": response, "source": source_info})
