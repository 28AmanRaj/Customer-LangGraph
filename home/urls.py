from django.urls import path
from home import agent, views

urlpatterns = [
    path("", views.index , name = 'home'),
    path("chatbot", views.chatbot , name = 'chatbot'),
    path("process",agent.process_input,name = "QuerySolver"),
    #path("submit",data.handle_form_submission, name = "Data")
]
 