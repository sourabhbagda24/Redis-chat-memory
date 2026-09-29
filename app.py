import time
from chat_memory import add_message,get_recent_messages
from chat_memory_ttl import add_message,get_recent_messages

if __name__=="__main__":
    user_id ="sourabh"

    add_message(user_id,"hii")
    add_message(user_id,"how's u")
    add_message(user_id,"r u okay")


    messages =get_recent_messages(user_id)

    print("recent chat history")
    print("recen")
    for i in messages:
        print("-",i)

    print("/n waiting for time fo dlt...")
    time.sleep(20)  

    print("/n after ttl expiry:")
    messages =get_recent_messages(user_id) 
    print(messages) 