from home.agent import customer_support
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest
from home.mongo_models import Query


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
        chatbot_response = customer_support(input_data)
        # Return JSON response
        return JsonResponse({"response": chatbot_response})
    except Exception as e:
        # Log the exception for debugging
        print(f"Error: {str(e)}")
        return JsonResponse({"response": "Internal Server Error"}, status=500)
