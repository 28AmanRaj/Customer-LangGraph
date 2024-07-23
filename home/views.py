from django.shortcuts import render
from home.loaders.url import rag_url
from home.loaders.pdf import rag_pdf
from django.http import JsonResponse
from home.utilities import upload_file_to_S3
from home.models import Company
from home.agent_structure.graph import graph_struct

# Global dictionary to store vectorstores
part_1_graph = []

def index(request):
    return render(request, 'main.html')

def chatbot(request):
    if request.method == 'POST':
        try:
            companyName = request.POST.get('companyName')
            companyLink = request.POST.get('companyLink')

            print("companyName :",companyName)
            if not companyName:
                return JsonResponse({"response": "Company name is required"}, status=400)

            #value(companyName, companyLink)

            company = Company(name=companyName, url=companyLink)
            company.save()
            
            rag_url(companyLink)
            #graph()

            print('A')

         
            #File Upload to S3
            uploaded_file = request.FILES["fileInput"]
            print('B')

            new_filename = upload_file_to_S3(uploaded_file)

            print('D')
            rag_pdf(new_filename)

            print("E")
            x = graph_struct()
            print('x',x)
            print("graph",part_1_graph)
            part_1_graph.append(x)
            print("F")
            return JsonResponse({"response": "Form submitted successfully"})

        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({"response": "Internal Server Error"}, status=500)

    return render(request, 'chatbot.html')
'''
def services(request):
    return HttpResponse("this is services page")
'''