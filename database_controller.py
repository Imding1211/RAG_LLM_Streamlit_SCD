
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

        self.SCD_update_chroma(pdf, start_date)

        self.add_to_chroma(pdf, start_date, end_date)

#-----------------------------------------------------------------------------#

    def SCD_update_chroma(self, pdf, start_date):

        old_documents = self.database.get(where={"source": pdf.stream.name})

        old_ids = old_documents["ids"]

        if len(old_ids):

            update_documents = []

            for original_metadata, original_documents in zip(old_documents['metadatas'], old_documents['documents']):
                
                updated_metedata = {
                "source"     : original_metadata['source'], 
                "page"       : original_metadata['page'], 
                "size"       : original_metadata['size'],
                "start_date" : original_metadata['start_date'],
                "end_date"   : start_date,
                "latest"     : False
                }

                updated_document = Document(page_content=original_documents, metadata=updated_metedata)

                update_documents.append(updated_document)

            self.database.update_documents(ids=old_ids, documents=update_documents)

#-----------------------------------------------------------------------------#

    def add_to_chroma(self, pdf, start_date, end_date):

        for page in range(len(pdf.pages)):
            
            content = pdf.pages[page].extract_text()

            metadata = {
            "source"     : pdf.stream.name, 
            "page"       : page + 1, 
            "size"       : pdf.stream.size,
            "start_date" : start_date,
            "end_date"   : end_date,
            "latest"     : True
            }

            documents = self.text_splitter.create_documents([content], [metadata])

            ids = [str(uuid.uuid4()) for _ in range(len(documents))]

            if len(documents):
                self.database.add_documents(documents, ids=ids)

