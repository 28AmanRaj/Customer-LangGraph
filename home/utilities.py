import uuid
import boto3
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode
import numpy as np
from home.models import File
from django import forms

from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def upload_file_to_S3(uploaded_file):
    try:
        # Generate a new filename using a UUID
        new_filename = uuid.uuid4().hex + "." + uploaded_file.name.rsplit('.', 1)[1].lower()

        # S3 bucket details
        Bucket_name = "sentinal-customer-care"  # Replace with your S3 bucket name
        s3 = boto3.resource("s3")

        # Upload the file to the specified S3 bucket
        s3.Bucket(Bucket_name).upload_fileobj(uploaded_file, new_filename)
        print('File uploaded successfully to S3.')

        # Create a file record
        file_record = File(
            original_filename=uploaded_file.name,
            filename=new_filename,
            bucket=Bucket_name,
            region="eu-north-1"  # Replace with your S3 bucket region
        )

        # Save the file record
        file_record.save()
        print("S3 upload and file record save were successful.")

        return new_filename

    except NoCredentialsError:
        print("Error: AWS credentials not available.")
    except PartialCredentialsError:
        print("Error: Incomplete AWS credentials provided.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    return None


def handle_tool_error(state) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }


def create_tool_node_with_fallback(tools: list):
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
        )

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


# def _print_event(event: dict, _printed: set, max_length=1500):
#     current_state = event.get("dialog_state")
#     if current_state:
#         print("Currently in: ", current_state[-1])
#     message = event.get("messages")
#     if message:
#         if isinstance(message, list):
#             message = message[-1]
#         if message.id not in _printed:
#             msg_repr = message.pretty_repr(html=True)
#             if len(msg_repr) > max_length:
#                 msg_repr = msg_repr[:max_length] + " ... (truncated)"
#             print(msg_repr)
#             _printed.add(message.id)

def _print_event(event: dict, _printed: set, max_length=1500):
    current_state = event.get("dialog_state")
    if current_state:
        print("Currently in: ", current_state[-1])
    message = event.get("messages")
    if message:
        if isinstance(message, list):
            message = message[-1]
        if message.id not in _printed:
            msg_repr = message.pretty_repr(html=True)
            if len(msg_repr) > max_length:
                msg_repr = msg_repr[:max_length] + " ... (truncated)"
            print(msg_repr)
            _printed.add(message.id)
            return msg_repr  # Return the message representation
    return ""
def set_docstring(docstring):
        def decorator(func):
            func.__doc__ = docstring
            return func
        return decorator

# This is to take K value input


class KValueForm(forms.Form):
    k_value = forms.IntegerField(label='Number of Documents to Retrieve', min_value=1)
    temperature = forms.FloatField(label='Temperature for Summarization', min_value=0.0, max_value=1.0, initial=0.7)