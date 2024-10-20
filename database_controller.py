
from langchain_text_splitters import RecursiveCharacterTextSplitter
from setting_controller import SettingController
from langchain_core.documents import Document
import pandas as pd
import datetime
import humanize
import PyPDF2
import uuid

#=============================================================================#

class DatabaseController():

    def __init__(self, database):
        self.database  = database

        self.time_zone = datetime.timezone(datetime.timedelta(hours=8))
        self.time_now  = datetime.datetime.now(tz=self.time_zone)
        self.time_end  = datetime.datetime(9999, 12, 31, 0, 0, 0, tzinfo=self.time_zone)

        self.SettingController = SettingController()

        chunk_size    = self.SettingController.setting['text_splitter']['chunk_size']
        chunk_overlap = self.SettingController.setting['text_splitter']['chunk_overlap']

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size         = chunk_size,    # 每塊的大小
            chunk_overlap      = chunk_overlap, # 每塊之間的重疊部分
            length_function    = len,           # 用於計算塊長度的函數
            is_separator_regex = False,         # 是否使用正則表達式作為分隔符
            )

#-----------------------------------------------------------------------------#

    def calculate_existing_ids(self):

        existing_items = self.database.get(include=[])
        existing_ids   = set(existing_items["ids"])

        return existing_ids
            
#-----------------------------------------------------------------------------#

    def get_version_list(self, source):

        version_data = self.database.get(where={"source": source})["metadatas"]

        version_list = sorted(set(item['version'] for item in version_data), reverse=True)

        if not len(version_list):
            version_list = [0]

        return version_list

#-----------------------------------------------------------------------------#

    def database_to_dataframes(self):

        data = self.database.get()

        df = pd.DataFrame({
            'ids'        : data['ids'],
            'page'       : [meta['page'] for meta in data['metadatas']],
            'source'     : [meta['source'] for meta in data['metadatas']],
            'size'       : [humanize.naturalsize(meta['size'], binary=True) for meta in data['metadatas']],
            'start_date' : [meta['start_date'] for meta in data['metadatas']],
            'end_date'   : [meta['end_date'] for meta in data['metadatas']],
            'version'    : [meta['version'] for meta in data['metadatas']],
            'latest'     : [meta['latest'] for meta in data['metadatas']],
            'documents'  : data['documents']
        })

        return df

#-----------------------------------------------------------------------------#

    def clear_database(self, delete_ids):
        if delete_ids:
            self.database.delete(ids=delete_ids)

#-----------------------------------------------------------------------------#

    def add_chroma(self, pdf, start_date, end_date, current_version):

        for page in range(len(pdf.pages)):
            
            content = pdf.pages[page].extract_text()

            metadata = {
            "source"     : pdf.stream.name, 
            "page"       : page + 1, 
            "size"       : pdf.stream.size,
            "start_date" : start_date,
            "end_date"   : end_date,
            "version"    : current_version + 1,
            "latest"     : True
            }

            documents = self.text_splitter.create_documents([content], [metadata])

            ids = [str(uuid.uuid4()) for _ in range(len(documents))]

            if len(documents):
                self.database.add_documents(documents, ids=ids)

#-----------------------------------------------------------------------------#

    def update_chroma(self, source_name, date, latest, current_version):

        old_documents = self.database.get(where={"source": source_name})

        new_documents = []
        new_ids       = []

        for ids, old_metadata, old_document in zip(old_documents["ids"], old_documents['metadatas'], old_documents['documents']):

            if old_metadata['version'] == current_version:

                updated_metedata = {
                "source"     : old_metadata['source'], 
                "page"       : old_metadata['page'], 
                "size"       : old_metadata['size'],
                "start_date" : old_metadata['start_date'],
                "end_date"   : date,
                "version"    : old_metadata['version'],
                "latest"     : latest
                }

                new_documents.append(Document(page_content=old_document, metadata=updated_metedata))
                new_ids.append(ids)

        self.database.update_documents(ids=new_ids, documents=new_documents)

#-----------------------------------------------------------------------------#

    def add_database(self, file):

        start_date = self.time_now.strftime('%Y/%m/%d %H:%M:%S')
        end_date   = self.time_end.strftime('%Y/%m/%d %H:%M:%S')

        pdf = PyPDF2.PdfReader(file)

        current_version = self.get_version_list(pdf.stream.name)[0]

        if current_version > 0:
            self.update_chroma(pdf.stream.name, start_date, False, current_version)

        self.add_chroma(pdf, start_date, end_date, current_version)

#-----------------------------------------------------------------------------#

    def rollback_database(self, rollback_list):

        end_date = self.time_end.strftime('%Y/%m/%d %H:%M:%S')

        for rollback_source, rollback_version in rollback_list:

            version_list = self.get_version_list(rollback_source)

            if rollback_version == version_list[0] and len(version_list) > 1:

                self.update_chroma(rollback_source, end_date, True, version_list[1])

