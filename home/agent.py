import uuid
from home.utilities import _print_event
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest
from home.models import Query
from home.views import part_1_graph
from home.agent_structure.graph import graph_struct

thread_id = str(uuid.uuid4())

config = {
    "configurable": {
        # The passenger_id is used in our flight tools to
        # fetch the user's flight information
        #"passenger_id": "3442 587242",
        # Checkpoints are accessed by thread_id
        "thread_id": thread_id,
    }
}


 
def customer_support(part_1_grap,msg):
    _printed = set()
    print("1")
    events = part_1_grap.stream(
        {"messages": ("user", msg)}, config ,stream_mode="values"
    )
    for event in events:
        _print_event(event, _printed)
        #return event


@csrf_exempt
def process_input(request: HttpRequest):
    try:
        # Get the data from the request
        input_data = request.POST.get('msg')  # Assuming the input data is sent as a POST parameter named 'msg'

        # Log the received data
        print(f"Received data: {input_data}")
        
        query = Query(query = input_data)
        query.save() 

        # Assume process_query is a function that processes the user's message and returns a response
        #chatbot_response = customer_support(input_data, company, url, file_loc)
        chatbot_response = customer_support(part_1_graph[0],input_data)
        # Return JSON response
        return JsonResponse({"response": chatbot_response})
    except Exception as e:
        # Log the exception for debugging
        print(f"Error: {str(e)}")
        return JsonResponse({"response": "Internal Server Error"}, status=500)
    


# Update with the backup file so we can restart from the original place in each section
#shutil.copy(backup_file, db)