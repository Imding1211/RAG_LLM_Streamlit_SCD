
import json

#=============================================================================#

class SettingController():

	def __init__(self):

		self.default_setting = {
		    "selected": {
		        "prompt": "{context}\n\n---\n\n根據以上資料用繁體中文回答問題: {question}\n",
		        "llm_model": "gemma2:2b",
		        "embedding_model": "all-minilm",
		        "query_num": 5,
		        "database": "database/chroma"
		    },
		    "text_splitter": {
		        "chunk_size": 150,
		        "chunk_overlap": 50
		    },
		    "options": {
		        "llm_model": [
		            "gemma2:2b"
		        ],
		        "embedding_model": [
		            "all-minilm"
		        ]
		    }
		}

		self.load_setting()

#-----------------------------------------------------------------------------#

	def load_setting(self):
		with open('setting.json', 'r', encoding='utf-8') as setting_file:
		    self.setting = json.load(setting_file)

#-----------------------------------------------------------------------------#

	def generate_setting(self, new_setting):
		with open('setting.json', 'w', encoding='utf-8') as setting_file:
			setting_file.write(json.dumps(new_setting, indent=4, ensure_ascii=False))

#-----------------------------------------------------------------------------#

	def generate_default_setting(self):
		with open('setting.json', 'w', encoding='utf-8') as setting_file:
			setting_file.write(json.dumps(self.default_setting, indent=4, ensure_ascii=False))

#-----------------------------------------------------------------------------#

	def change_llm_model(self, model_name):

		if len(model_name) > 0:

			self.setting['selected']['llm_model'] = model_name

			self.generate_setting(self.setting)

#-----------------------------------------------------------------------------#

	def change_embedding_model(self, model_name):

		if len(model_name) > 0:

			self.setting['selected']['embedding_model'] = model_name

			self.generate_setting(self.setting)

#-----------------------------------------------------------------------------#

	def change_query_num(self, query_num):

		self.setting['selected']['query_num'] = query_num

		self.generate_setting(self.setting)

#-----------------------------------------------------------------------------#

	def change_database(self, database):

		self.setting['selected']['database'] = 'database/'+database

		self.generate_setting(self.setting)

#-----------------------------------------------------------------------------#

	def change_text_splitter(self, chunk_size, chunk_overlap):

		self.setting['text_splitter']['chunk_size'] = int(chunk_size)

		self.setting['text_splitter']['chunk_overlap'] = int(chunk_overlap)

		self.generate_setting(self.setting)

#-----------------------------------------------------------------------------#

	def change_prompt(self, prompt):

		self.setting['selected']['prompt'] = prompt

		self.generate_setting(self.setting)

#-----------------------------------------------------------------------------#

	def add_llm_model(self, model_name):

		if len(model_name) > 0:

			self.setting['options']['llm_model'].append(model_name)

			self.generate_setting(self.setting)

#-----------------------------------------------------------------------------#

	def add_embedding_model(self, model_name):

		if len(model_name) > 0:

			self.setting['options']['embedding_model'].append(model_name)

			self.generate_setting(self.setting)

#-----------------------------------------------------------------------------#

	def remove_llm_model(self, model_name):

		if len(model_name) > 0:

			self.setting['options']['llm_model'].remove(model_name)

			self.generate_setting(self.setting)

#-----------------------------------------------------------------------------#

	def remove_embedding_model(self, model_name):

		if len(model_name) > 0:

			self.setting['options']['embedding_model'].remove(model_name)

			self.generate_setting(self.setting)
