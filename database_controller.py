
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import pandas as pd
import datetime
import PyPDF2
import uuid

#=============================================================================#

class DatabaseController():

    def __init__(self, database):
        self.database  = database

        self.time_zone = datetime.timezone(datetime.timedelta(hours=8))
        self.time_now  = datetime.datetime.now(tz=self.time_zone)
        self.time_end  = datetime.datetime(9999, 12, 31, 0, 0, 0, tzinfo=self.time_zone)

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size         = 800,   # 每塊的大小
            chunk_overlap      = 80,    # 每塊之間的重疊部分
            length_function    = len,   # 用於計算塊長度的函數
            is_separator_regex = False, # 是否使用正則表達式作為分隔符
            )

#-----------------------------------------------------------------------------#

    def calculate_existing_ids(self):

        existing_items = self.database.get(include=[])
        existing_ids   = set(existing_items["ids"])

        return existing_ids

#-----------------------------------------------------------------------------#

    def database_to_dataframes(self):

        data = self.database.get()

        df = pd.DataFrame({
            'ids'        : data['ids'],
            'page'       : [meta['page'] for meta in data['metadatas']],
            'source'     : [meta['source'] for meta in data['metadatas']],
            'size'       : [meta['size'] for meta in data['metadatas']],
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

    def add_PDF_to_chroma(self, file):

        start_date = self.time_now.strftime('%Y/%m/%d %H:%M:%S')
        end_date   = self.time_end.strftime('%Y/%m/%d %H:%M:%S')

        pdf = PyPDF2.PdfReader(file)

        current_version = self.get_current_version(pdf.stream.name)

        if current_version > 0:
            self.update_chroma_scd(pdf, start_date, current_version)

        self.add_to_chroma(pdf, start_date, end_date, current_version)

#-----------------------------------------------------------------------------#

    def get_current_version(self, source):

        version_list = self.database.get(where={"source": source})["metadatas"]
        
        if len(version_list):
            current_version = max(item['version'] for item in version_list)
        else:
            current_version = 0

        return current_version

#-----------------------------------------------------------------------------#

    def update_chroma_scd(self, pdf, start_date, current_version):

        old_documents = self.database.get(where={"source": pdf.stream.name})

        update_documents = []
        update_ids       = []

        for ids, original_metadata, original_documents in zip(old_documents["ids"], old_documents['metadatas'], old_documents['documents']):

            if original_metadata['version'] == current_version:

                updated_metedata = {
                "source"     : original_metadata['source'], 
                "page"       : original_metadata['page'], 
                "size"       : original_metadata['size'],
                "start_date" : original_metadata['start_date'],
                "end_date"   : start_date,
                "version"    : original_metadata['version'],
                "latest"     : False
                }

                update_document = Document(page_content=original_documents, metadata=updated_metedata)

                update_documents.append(update_document)

                update_ids.append(ids)

        self.database.update_documents(ids=update_ids, documents=update_documents)

#-----------------------------------------------------------------------------#

    def add_to_chroma(self, pdf, start_date, end_date, current_version):

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

    def rollback_chroma_scd(self, rollback_list):

        for rollback_source, rollback_version in rollback_list:

            version_list = self.database.get(where={"source": rollback_source})["metadatas"]

            all_versions = sorted(set(item['version'] for item in version_list), reverse=True)

            current_version = self.get_current_version(rollback_source)

            if rollback_version == current_version:

                end_date = self.time_end.strftime('%Y/%m/%d %H:%M:%S')

                rollback_documents = self.database.get(where={"source":rollback_source})

                update_documents = []
                update_ids       = []

                for ids, rollback_metadata, rollback_documents in zip(rollback_documents["ids"], rollback_documents['metadatas'], rollback_documents['documents']):

                    if rollback_metadata['version'] == all_versions[1]:

                        updated_metedata = {
                        "source"     : rollback_metadata['source'], 
                        "page"       : rollback_metadata['page'], 
                        "size"       : rollback_metadata['size'],
                        "start_date" : rollback_metadata['start_date'],
                        "end_date"   : end_date,
                        "version"    : rollback_metadata['version'],
                        "latest"     : True
                        }

                        updated_document = Document(page_content=rollback_documents, metadata=updated_metedata)

                        update_documents.append(updated_document)

                        update_ids.append(ids)

                self.database.update_documents(ids=update_ids, documents=update_documents)  
