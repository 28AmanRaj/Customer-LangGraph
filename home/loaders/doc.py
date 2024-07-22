import re
import requests
import numpy as np
import openai
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.tools import tool
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

tools = []

'''response = requests.get(
    "https://storage.googleapis.com/benchmarks-artifacts/travel-db/swiss_faq.md"
)
response.raise_for_status()
faq_text = response.text

docs = [{"page_content": txt} for txt in re.split(r"(?=\n##)", faq_text)]
'''
'''
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
docs_splits = [WebBaseLoader('https://www.lenovo.com/in/en/services/').load()]
docs_list = [item for sublist in docs_splits for item in sublist]

text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=100, chunk_overlap=50
)
docs = text_splitter.split_documents(docs_list)
''' 
def rag_url(url):
    docs_splits = [WebBaseLoader(url).load()]
    docs_list = [item for sublist in docs_splits for item in sublist]

    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=100, chunk_overlap=50
    )
    docs = text_splitter.split_documents(docs_list)
    print("1")
    # Add to vectorDB

    print("doc_splits :",docs)

    class VectorStoreRetriever:
        print("2")
        def __init__(self, docs: list, vectors: list, oai_client):
            self._arr = np.array(vectors)
            self._docs = docs
            self._client = oai_client
        
        print("3")
        @classmethod
        def from_docs(cls, docs, oai_client):
            print("4")
            '''embeddings = oai_client.embeddings.create(
                model="text-embedding-3-small", input=[docs]
            )
            print("5")
            vectors = [emb.embedding for emb in embeddings.data]'''

            vectors = [Chroma.from_documents(
                documents=docs,
                collection_name="rag-chroma",
                embedding=OpenAIEmbeddings(),
            )]

            print("6")
            return cls(docs, vectors, oai_client)
        
        def query(self, query: str, k: int = 5) -> list[dict]:
            embed = self._client.embeddings.create(
                model="text-embedding-3-small", input=[query]
            )
            # "@" is just a matrix multiplication in python
            scores = np.array(embed.data[0].embedding) @ self._arr.T
            top_k_idx = np.argpartition(scores, -k)[-k:]
            top_k_idx_sorted = top_k_idx[np.argsort(-scores[top_k_idx])]
            return [
                {**self._docs[idx], "similarity": scores[idx]} for idx in top_k_idx_sorted
            ]


    retriever = VectorStoreRetriever.from_docs(docs, openai.Client())


    @tool
    def lookup_policy(query: str) -> str:
        """Consult the company policies to check whether certain options are permitted.
        Use this before making any flight changes performing other 'write' events."""
        docs = retriever.query(query, k=2)
        return "\n\n".join([doc["page_content"] for doc in docs])
    
    tools.append(lookup_policy)
    print("tools: ",tools)