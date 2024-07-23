import shutil
import uuid
from home.utilities import _print_event
from home.lgraph.graph import tool_set2
# Update with the backup file so we can restart from the original place in each section
#shutil.copy(backup_file, db)
thread_id = str(uuid.uuid4())

config = {
    "configurable": {
        # The passenger_id is used in our flight tools to
        # fetch the user's flight information
        "passenger_id": "3442 587242",
        # Checkpoints are accessed by thread_id
        "thread_id": thread_id,
    }
}


 
# def customer_support(msg):
#     _printed = set()
#     print("1")
#     part_1_graph = tool_set2()
#     events = part_1_graph.stream(
#         {"messages": ("user", msg)}, config, stream_mode="values"
#     )
#     for event in events:
#         _print_event(event, _printed)
#         #return event

def customer_support(msg):
    _printed = set()
    part_1_graph = tool_set2()
    events = part_1_graph.stream(
        {"messages": ("user", msg)}, config, stream_mode="values"
    )
    response = ""
    for event in events:
        response += _print_event(event, _printed)
    return response

