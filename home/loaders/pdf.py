from langchain_text_splitters import RecursiveCharacterTextSplitter
from home.utilities import VectorStoreRetriever, set_docstring
from home.loaders.desc import fetch_summarize
import openai
from langchain_core.tools import tool
from home.agent_structure.assistant import tool_set
import boto3
import PyPDF2
from io import BytesIO

tools = []
docs_list = []

def process_pdf_file(file_stream):
    """Extract text from all pages of the PDF and append to docs_list."""
    reader = PyPDF2.PdfReader(file_stream)
    combined_text = ""
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text = page.extract_text()
        combined_text += text + "\n"  # Concatenate text from all pages
    docs_list.append(combined_text)
    print(f"Combined text: {combined_text}")

def read(s3, BUCKET_NAME, FILE_KEY):
    """Retrieve and read the PDF file from S3."""
    try:
        # Get the object from S3
        response = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_KEY)
        
        # Read the content of the file into a BytesIO buffer
        file_stream = BytesIO(response['Body'].read())

        # Process the PDF file
        process_pdf_file(file_stream)

    except Exception as e:
        print(f"Error accessing or processing file: {e}")

def rag_pdf(file_key, k_value=2):
    """Process the PDF, split text into chunks, and set up document retrieval."""
    s3 = boto3.client('s3')

    print("file Key:", file_key)
    BUCKET_NAME = 'sentinal-customer-care'
    FILE_KEY = file_key

    read(s3, BUCKET_NAME, FILE_KEY)

    # Apply preprocessing
    combined_text = docs_list[0] if docs_list else ""
    
    # Split documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=500, chunk_overlap=50  # Adjusted chunk size
    )
    docs = [{"page_content": txt} for txt in text_splitter.split_text(combined_text)]
    print("Documents split into chunks:", docs)

    summary = fetch_summarize(combined_text)
    print("Document summary:", summary)
    
    retriever = VectorStoreRetriever.from_docs(docs, openai.Client())

    # Function to lookup policy
    def lookup_pdf(query: str, k_value: int) -> str:
        docs = retriever.query(query, k=k_value)
        return "\n\n".join([doc["page_content"] for doc in docs])
    
    lookup_pdf = set_docstring(summary)(lookup_pdf)
    lookup_pdf = tool(lookup_pdf)
    
    tools.append(lookup_pdf)
    tool_set(tools)

