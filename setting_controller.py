
import json

#=============================================================================#

class SettingController():

	def __init__(self):

		self.default_setting = {
		    "selected": {
		        "prompt": "{context}\n\n---\n\n根據以上資料用繁體中文回答問題: {question}\n",
		        "llm_model": "gemma2:2b",
		        "embedding_model": "all-minilm"
		    },
		    "options": {
		        "llm_model": ["gemma2:2b", "jcai/llama3-taide-lx-8b-chat-alpha1:Q4_K_M"],
		        "embedding_model": ["all-minilm"]
		    }
		}

		self.reload_setting()

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

	def add_llm_model(self, model_name):

		if len(model_name) > 0:

			self.setting['options']['llm_models'].append(model_name)

			self.generate_setting(self.setting)

#-----------------------------------------------------------------------------#

	def remove_llm_model(self, model_name):

		if len(model_name) > 0:

			self.setting['options']['llm_models'].remove(model_name)

			self.generate_setting(self.setting)

#-----------------------------------------------------------------------------#

	def add_embedding_model(self, model_name):

		if len(model_name) > 0:

			self.setting['options']['embedding_models'].append(model_name)

			self.generate_setting(self.setting)

#-----------------------------------------------------------------------------#

	def remove_embedding_model(self, model_name):

		if len(model_name) > 0:

			self.setting['options']['embedding_models'].remove(model_name)

			self.generate_setting(self.setting)

#-----------------------------------------------------------------------------#

	def generate_setting(self, new_setting):
		with open('setting.json', 'w', encoding='utf-8') as setting_file:
			setting_file.write(json.dumps(new_setting, indent=4, ensure_ascii=False))

#-----------------------------------------------------------------------------#

	def reload_setting(self):
		with open('setting.json', 'r', encoding='utf-8') as setting_file:
		    self.setting = json.load(setting_file)
