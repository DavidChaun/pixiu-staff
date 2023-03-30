import glob
from PyPDF2 import PdfReader as pdf_reader
import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import TokenTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.chains import ChatVectorDBChain
from langchain.document_loaders import DirectoryLoader
from langchain.docstore.document import Document
from typing import List, Any
from dotenv import load_dotenv
import jieba as jb
import openpyxl


load_dotenv()
if not os.path.exists('./db'):
    os.mkdir('./db')

openai_api_key = os.getenv("OPENAI_API_KEY")


def init_cut_file() -> None:
    file_list = glob.glob('./data/*')
    for file_path in file_list:
        if file_path.endswith("txt") or file_path.endswith("md"):
            with open(file_path, "r", encoding='utf-8') as f:
                data = f.read()
        elif file_path.endswith("pdf"):
            data = ''
            reader = pdf_reader(file_path)
            num_pages = len(reader.pages)
            for page_num in range(num_pages):
                # 获取指定页的PDF页面对象
                page = reader.pages[page_num]

                # 提取页面文本内容
                text = page.extract_text()
                # 输出文本内容
                data = data + text
        elif file_path.endswith("xls") or file_path.endswith("xlsx"):
            # 文本不够连续，
            data = ''
            workbook = openpyxl.load_workbook(file_path)
            sheet = workbook.active
            for row in sheet.iter_rows(values_only=True):
                # tuple row
                data = data + " ".join([str(r1) for r1 in row]) + '\n'
        else:
            data = ''

        # 对中文文档进行分词处理
        cut_data = " ".join([w for w in list(jb.cut(data))])
        # 分词处理后的文档保存到data文件夹中的cut子文件夹中
        file_name_with_ext = os.path.basename(file_path)
        file_name = os.path.splitext(file_name_with_ext)[0]
        cut_file = f"./db/cut_{file_name}.txt"
        with open(cut_file, 'w') as f:
            f.write(cut_data)
            f.close()


def load_cut_file() -> List[Document]:
    # 加载文档
    loader = DirectoryLoader('./db', glob='**/*.txt')
    docs = loader.load()
    # 文档切块
    text_splitter = TokenTextSplitter(chunk_size=1000, chunk_overlap=0)
    return text_splitter.split_documents(docs)


def get_chroma_db(doc_texts: List[Document]) -> Chroma:
    # 调用openai Embeddings
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    # 向量化
    vectordb = Chroma.from_documents(doc_texts, embeddings, persist_directory="./db")
    return vectordb


def vector_chain():
    has_init = os.path.exists('./success_init')

    if not has_init:
        init_cut_file()

    dom = load_cut_file()
    vectordb = get_chroma_db(dom)
    if not has_init:
        vectordb.persist()
        with open('./success_init', 'w') as f:
            f.write('1')
            f.close()

    return ChatVectorDBChain.from_llm(ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo"),
                               vectordb, return_source_documents=True)


chain = vector_chain()


def get_answer(question):
    chat_history = []
    result = chain({"question": question, "chat_history": chat_history})
    return result["answer"]

