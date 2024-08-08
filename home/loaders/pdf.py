
from langchain_text_splitters import RecursiveCharacterTextSplitter
from home.utilities import VectorStoreRetriever,set_docstring
from home.loaders.desc import fetch_summarize
import openai
from langchain_core.tools import tool
from home.agent_structure.assistant import tool_set
import boto3
import PyPDF2
from io import BytesIO

tools = []
docs_list=[]


def process_pdf_file(file_stream):
    # Use PyPDF2 to read and process the PDF file
    reader = PyPDF2.PdfReader(file_stream)
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text = page.extract_text()
        docs_list.append(text)
        print(f"Page {page_num+1}: {text}")

def read(s3,BUCKET_NAME,FILE_KEY):
    try:
        # Get the object from S3
        response = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_KEY)
        
        # Read the content of the file into a BytesIO buffer
        file_stream = BytesIO(response['Body'].read())

        # Process the PDF file
        process_pdf_file(file_stream)

    except Exception as e:
        print(f"Error accessing or processing file: {e}")



def rag_pdf(file_key):

    s3 = boto3.client('s3')

    print("file KEy",file_key)
    BUCKET_NAME = 'sentinal-customer-care'
    FILE_KEY = file_key

    read(s3,BUCKET_NAME,FILE_KEY)

    # Apply preprocessing
    #docs_list1 = [{'page_content': preprocess_text(docs_list[2])} for doc in docs_list]
    print("3")
    # Split documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=500, chunk_overlap=50  # Adjusted chunk size
    )
    #doc_splits = [text_splitter.split_text(preprocess_text(docs_list[2]))]
    for x in docs_list:
        docs = [{"page_content": txt} for txt in text_splitter.split_text(x)]
    print("4",docs)
    summary=fetch_summarize(docs)
    print("file summ===",summary)
    print("7")
    retriever = VectorStoreRetriever.from_docs(docs, openai.Client())

    # Function to lookup policy
    # @tool
    # def lookup_pdf(query: str) -> str:
    #     """Use this if a Question about password is asked."""
    #     docs = retriever.query(query, k=2)
    #     return "\n\n".join([doc["page_content"] for doc in docs])
    def lookup_pdf(query: str) -> str:
        # global summary
        # print("SUMMM1 :",summary)
        # f"""{summary}"""
        # print("SUMMM :",summary)
        docs = retriever.query(query, k=2)
        return "\n\n".join([doc["page_content"] for doc in docs])
    
    lookup_pdf = set_docstring(summary)(lookup_pdf)
    # print("set_docstring :",lookup_url)
    lookup_pdf = tool(lookup_pdf)    
    
    
    tools.append(lookup_pdf)
    tool_set(tools)

