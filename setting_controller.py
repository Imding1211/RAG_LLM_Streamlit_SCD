
import json

#=============================================================================#

class SettingController():

	def __init__(self):

		self.default_setting = {
		'default' : {
			'prompt'           : '{context}\n\n---\n\n根據以上資料用繁體中文回答問題: {question}\n',
			'LLM_models'       : 'gemma2:2b',
			'embedding_models' : 'all-minilm',
			},
		'customize' : {
			'prompt'           : '',
			'LLM_models'       : [],
			'embedding_models' : [],
			}
		}

		self.setting = self.load_setting()

#-----------------------------------------------------------------------------#

	def add_llm_model(self, model_name):

		if len(model_name) > 0:

			self.setting['customize']['LLM_models'].append(model_name)

			self.generate_setting(self.setting)

#-----------------------------------------------------------------------------#

	def remove_llm_model(self, model_name):

		if len(model_name) > 0:

			self.setting['customize']['LLM_models'].remove(model_name)

			self.generate_setting(self.setting)

#-----------------------------------------------------------------------------#

	def add_embedding_model(self, model_name):

		if len(model_name) > 0:

			self.setting['customize']['embedding_models'].append(model_name)

			self.generate_setting(self.setting)

#-----------------------------------------------------------------------------#

	def remove_embedding_model(self, model_name):

		if len(model_name) > 0:

			self.setting['customize']['embedding_models'].remove(model_name)

			self.generate_setting(self.setting)

#-----------------------------------------------------------------------------#

	def generate_setting(self, new_setting):
		with open('setting.json', 'w', encoding='utf-8') as setting_file:
			setting_file.write(json.dumps(new_setting, indent=4, ensure_ascii=False))

#-----------------------------------------------------------------------------#

	def generate_default_setting(self):
		with open('setting.json', 'w', encoding='utf-8') as setting_file:
			setting_file.write(json.dumps(self.default_setting, indent=4, ensure_ascii=False))

#-----------------------------------------------------------------------------#

	def load_setting(self):
		with open('setting.json', 'r', encoding='utf-8') as setting_file:
		    setting = json.load(setting_file)

		return setting

#-----------------------------------------------------------------------------#

	def reload_setting(self):
		with open('setting.json', 'r', encoding='utf-8') as setting_file:
		    self.setting = json.load(setting_file)
