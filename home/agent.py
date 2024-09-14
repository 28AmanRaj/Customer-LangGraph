import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from home.models_mongo import Query
from home.views import part_1_graph
from home.utilities import _print_event
from mongoengine import DoesNotExist, QuerySet
import langsmith
from dotenv import load_dotenv
import os

# Initialize LangSmith client
load_dotenv()
api_key = os.getenv('LANGCHAIN_API_KEY')

langsmith_client = langsmith.Client(api_key=api_key)

def generate_thread_id():
    return str(uuid.uuid4())

def log_trace(message, thread_id, role):
    trace_metadata = {
        "thread_id": thread_id
    }
    # Log the trace with message, role (user or AI), and metadata
    print(f"Logging {role} message: {message} with metadata: {trace_metadata}")

def clean_chatbot_response(response):
    start_marker = "==================================\x1b[1m Ai Message \x1b[0m=================================="
    cleaned_response = response.replace(start_marker, "").strip()
    return cleaned_response

def customer_support(part_1_graph, msg, thread_id):
    _printed = set()
    print("Starting customer support function")
    print(f"Thread ID in customer_support: {thread_id}")
    
    try:
        if not isinstance(msg, dict) or "messages" not in msg:
            raise ValueError("Invalid message format")
        
        config = {
            'configurable': {
                'thread_id': thread_id
            }
        }
        
        events = part_1_graph.stream(msg, config, stream_mode="values")
    except Exception as e:
        print(f"Error during event streaming: {str(e)}")
        return "Error during event streaming"

    last_event = None
    for event in events:
        print("Processing event:", event)
        last_event = event

    if last_event:
        html_message = _print_event(last_event, _printed)
        return clean_chatbot_response(html_message)
    else:
        return "No events found"

@csrf_exempt
def process_input(request):
    try:
        input_data = request.POST.get('msg')
        thread_id = request.POST.get('thread_id')

        print(f"Received data: {input_data}, thread_id: {thread_id}")

        # Generate a new thread ID if not provided (indicating a new conversation)
        if not thread_id:
            thread_id = generate_thread_id()
            print(f"Generated new thread_id: {thread_id}")
            conversation_history = []
        else:
            # Retrieve conversation history for the provided thread ID
            try:
                previous_queries: QuerySet = Query.objects.filter(thread_id=thread_id)
                conversation_history = [{"role": "user", "content": query.query} for query in previous_queries]
                print(f"Retrieved conversation history for thread_id: {thread_id}")
            except DoesNotExist:
                conversation_history = []
                print(f"No previous conversation history found for thread_id: {thread_id}")

        # Save the current query
        query = Query(query=input_data, thread_id=thread_id)
        query.save()

        # Construct the conversation messages state
        messages_state = {"messages": conversation_history + [{"role": "user", "content": input_data}]}
        
        # Get chatbot response based on the document and thread ID
        chatbot_response = customer_support(part_1_graph[0], messages_state, thread_id)

        # Log user and chatbot messages
        log_trace(input_data, thread_id, "user")
        log_trace(chatbot_response, thread_id, "AI")

        print(f"Returning response with thread_id: {thread_id}")
        return JsonResponse({"response": chatbot_response, "thread_id": thread_id})
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({"response": "Internal Server Error"}, status=500)
