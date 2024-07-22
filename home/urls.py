from django.urls import path
from home import views,ai,data

urlpatterns = [
    path("", views.index , name = 'home'),
    path("chatbot", views.chatbot , name = 'chatbot'),
    path("process",ai.process_input,name = "QuerySolver"),
    #path("submit",data.handle_form_submission, name = "Data")
]
 