from django.shortcuts import render
from home.loaders.url import rag_url
from home.loaders.pdf import rag_pdf
from django.http import JsonResponse
from home.utilities import upload_file_to_S3, KValueForm
from home.models import Company
from home.agent_structure.graph import graph_struct
from home.agent_structure.assistant import Assistant, assistant_set

# Global dictionary to store vectorstores
part_1_graph = []

def index(request):
    return render(request, 'main.html')

def chatbot(request):
    if request.method == 'POST':
        try:
            companyName = request.POST.get('companyName')
            companyLink = request.POST.get('companyLink')
            
            # Handle the k_value and temperature form submission
            form = KValueForm(request.POST)
            if form.is_valid():
                k_value = form.cleaned_data['k_value']
            else:
                return JsonResponse({"response": "Invalid k value"}, status=400)
            
            temperature = request.POST.get('temperature')
            if temperature is None:
                return JsonResponse({"response": "Temperature value is required"}, status=400)
            try:
                temperature = float(temperature)
                if not (0 <= temperature <= 1):
                    raise ValueError("Temperature must be between 0 and 1.")
            except ValueError:
                return JsonResponse({"response": "Invalid temperature value"}, status=400)

            print("companyName :", companyName)
            if not companyName:
                return JsonResponse({"response": "Company name is required"}, status=400)
            
            print(f"Received temperature value: {temperature}")

            company = Company(name=companyName, url=companyLink)
            company.save()
            
            rag_url(companyLink)

            # File Upload to S3
            uploaded_file = request.FILES["fileInput"]
            new_filename = upload_file_to_S3(uploaded_file)

            # Pass the user-provided k_value to the rag_pdf function
            rag_pdf(new_filename, k_value=k_value)

            # Graph structure processing
            x = graph_struct()
            part_1_graph.append(x)
            
            # Set up the assistant with the provided temperature
            assistant_runnable = assistant_set(temperature)
            assistant = Assistant(assistant_runnable)
            print("Assistant set up with temperature:", temperature)
            return JsonResponse({"response": "Form submitted successfully"})

        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({"response": "Internal Server Error"}, status=500)

    else:
        form = KValueForm()

    return render(request, 'chatbot.html', {'form': form})
