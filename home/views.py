import uuid
import boto3
from django.shortcuts import render, HttpResponse
from concurrent.futures import ThreadPoolExecutor
from home.mongo_models import Company
from home.loaders.url import rag_url
from home.loaders.pdf import rag_pdf
from django.http import JsonResponse
#from home.agent import value
from home.models import File
#from home.langagent import graph

# Global dictionary to store vectorstores

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
        
            new_filename = uuid.uuid4().hex + "." + uploaded_file.name.rsplit('.', 1)[1].lower()
        
            Bucket_name = "sentinal-customer-care"  # Replace with your S3 bucket name
            s3 = boto3.resource("s3")
            s3.Bucket(Bucket_name).upload_fileobj(uploaded_file, new_filename)
            print('c')
            file_record = File(
                original_filename=uploaded_file.name,
                filename=new_filename,
                bucket=Bucket_name,
                region="eu-north-1"  # Replace with your S3 bucket region
            )
            file_record.save()
            print('D')
            rag_pdf(new_filename)

            print("E")
            return JsonResponse({"response": "Form submitted successfully"})

        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({"response": "Internal Server Error"}, status=500)

    return render(request, 'chatbot.html')
'''
def services(request):
    return HttpResponse("this is services page")
'''