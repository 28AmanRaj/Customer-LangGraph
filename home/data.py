from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from pathlib import Path
from django.http import HttpRequest
from django.http import JsonResponse
from home.mongo_models import Company

@csrf_exempt 
def handle_form_submission(request: HttpRequest):
    try:
        companyName = request.POST.get('body')
        #companyLink = request.POST.get('companyLink')
        
        print("copany name is :",companyName)

        #company = Company(name = companyName, url = companyLink)
        company = Company(name = companyName)
        company.save()
        

        '''        
        # Define the base directory
        base_dir = Path("C:/Users/Sarthak/Desktop/AI Agents/CustomerSupport/docs")
        
        # Ensure the directory exists
        base_dir.mkdir(parents=True, exist_ok=True)
        
        # Construct the full file path, ensuring filename is treated as string
        file_location = base_dir / str(fileInput.name)

        try:
            # Write the file to disk
            with default_storage.open(file_location, 'wb+') as destination:
                for chunk in fileInput.chunks():
                    destination.write(chunk)
            print(f"File saved at {file_location}")
            
            # Set global variables (consider alternatives to using globals)
            global company, url, file, file_loc
            company = companyName
            url = companyLink
            file = fileType
            file_loc = file_location

            return HttpResponse("File uploaded successfully")
        except Exception as e:
            print(f"Failed to save file: {e}")
            return HttpResponse("Failed to save file", status=500)
            '''
    except Exception as e:
        # Log the exception for debugging
        print(f"Error: {str(e)}")
        return JsonResponse({"response": "Internal Server Error"}, status=500)
