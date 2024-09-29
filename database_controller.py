
from langchain_text_splitters import RecursiveCharacterTextSplitter
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

        pdf = PyPDF2.PdfReader(file)

        start_date = self.time_now.strftime('%Y/%m/%d %H:%M:%S')
        end_date   = datetime.datetime(9999, 12, 31, 0, 0, 0, tzinfo=self.time_zone).strftime('%Y/%m/%d %H:%M:%S')

        for page in range(len(pdf.pages)):
            
            content = pdf.pages[page].extract_text()

            metadata = {
            "source"     : pdf.stream.name, 
            "page"       : page+1, 
            "size"       : pdf.stream.size,
            "start_date" : start_date,
            "end_date"   : end_date,
            "latest"     : True
            }

            documents = self.text_splitter.create_documents([content], [metadata])

            ids = [str(uuid.uuid4()) for _ in range(len(documents))]

            if len(documents):
                self.database.add_documents(documents, ids=ids)
