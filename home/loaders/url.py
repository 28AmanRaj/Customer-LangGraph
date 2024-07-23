from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re
from bs4 import BeautifulSoup
import openai
from langchain_core.tools import tool
from home.agent_structure.assistant import tool_set
from home.utilities import VectorStoreRetriever

tools = []

def preprocess_text(text1):

    text = str(text1)
    # Remove HTML tags using BeautifulSoup
    soup = BeautifulSoup(text, 'html.parser')
    clean_text = soup.get_text(separator=' ')
    
    # Remove excessive whitespace, special characters, and multiple 'n's
    # Remove excessive whitespace and special characters
    clean_text = re.sub(r'\s+', ' ', clean_text)  # Replace multiple whitespace with a single space
    clean_text = re.sub(r'\xa0', ' ', clean_text)  # Remove non-breaking spaces
    clean_text = re.sub(r'\\r\\n', ' ', clean_text)  # Remove \r\n sequences
    clean_text = re.sub(r'\n+', ' ', clean_text)  # Remove multiple newlines
    clean_text = re.sub(r'n{2,}', ' ', clean_text)  # Remove multiple occurrences of 'n'
    clean_text = re.sub(r'[^a-zA-Z0-9\s,.]', '', clean_text)  # Remove other special characters

    return clean_text

def rag_url(url):
    print("2")
    url = [url]

    # Load documents
    docs = WebBaseLoader(url).load() 
    docs_list = [item for sublist in docs for item in sublist]
    # Enhanced preprocessing function

    # Apply preprocessing
    #docs_list1 = [{'page_content': preprocess_text(docs_list[2])} for doc in docs_list]
    print("3")
    # Split documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=500, chunk_overlap=50  # Adjusted chunk size
    )
    #doc_splits = [text_splitter.split_text(preprocess_text(docs_list[2]))]
    docs = [{"page_content": txt} for txt in text_splitter.split_text(preprocess_text(docs_list[2]))]
    print("4",docs)
    print("7")
    retriever = VectorStoreRetriever.from_docs(docs, openai.Client())

    # Function to lookup policy
    @tool
    def lookup_url(query: str) -> str:
        """Consult the company policies to check whether certain options are permitted.
        Use this before answering a relevant question."""
        docs = retriever.query(query, k=2)
        return "\n\n".join([doc["page_content"] for doc in docs])
    
    tools.append(lookup_url)
    tool_set(tools)









'''
# Generate unique IDs for each document chunk
ids = [str(uuid.uuid4()) for _ in doc_splits]

# Add to vectorDB
vectorstore = Chroma.from_texts(
    texts=doc_splits,
    collection_name="rag-chroma",
    embedding=OpenAIEmbeddings(),
    ids=ids  # Pass the generated IDs
)
retriever = vectorstore.as_retriever()
'''