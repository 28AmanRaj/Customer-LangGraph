
from langchain_text_splitters import RecursiveCharacterTextSplitter
import numpy as np
import openai
from langchain_core.tools import tool
from home.lgraph.AgentState import tool_set
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
    class VectorStoreRetriever:
        def __init__(self, docs: list, vectors: list, oai_client):
            self._arr = np.array(vectors)
            self._docs = docs
            self._client = oai_client
        print("5")
        @classmethod
        def from_docs(cls, docs, oai_client):
            embeddings = oai_client.embeddings.create(
                model="text-embedding-3-small", input=[doc["page_content"] for doc in docs]
            )
            vectors = [emb.embedding for emb in embeddings.data]
            return cls(docs, vectors, oai_client)
        print("6")
        def query(self, query: str, k: int = 5) -> list[dict]:
            embed = self._client.embeddings.create(
                model="text-embedding-3-small", input=[query]
            )
            # "@" is just a matrix multiplication in python
            scores = np.array(embed.data[0].embedding) @ self._arr.T
            k = min(k, len(scores))
            top_k_idx = np.argpartition(scores, -k)[-k:]
            top_k_idx_sorted = top_k_idx[np.argsort(-scores[top_k_idx])]
            return [
                {**self._docs[idx], "similarity": scores[idx]} for idx in top_k_idx_sorted
            ]

    print("7")
    retriever = VectorStoreRetriever.from_docs(docs, openai.Client())

    # Function to lookup policy
    @tool
    def lookup_pdf(query: str) -> str:
        """Check to see if the content is relevant to users query and use to answer the question."""
        docs = retriever.query(query, k=2)
        return "\n\n".join([doc["page_content"] for doc in docs])
    
    tools.append(lookup_pdf)
    tool_set(tools)

