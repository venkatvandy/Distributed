'''msg_sliding_window = {}
from collections import deque

def store_msg_history(topic,message,history):
    que = deque()

    if topic in msg_sliding_window.keys():
        que.clear()
        for elements in msg_sliding_window[topic]:
            # print(elements)
            que.append(elements)
            # que=required_table[topic]
            # print("Queueeueue:",que)
        del (msg_sliding_window[topic])

    que.appendleft(message)
    if len(que) == int(history) +1 :
        que.pop()

    temp_list = []
    temp_list[:] = []

    for ele in que:
        temp_list.append(ele)

    msg_sliding_window[topic] = temp_list

    print(msg_sliding_window)

store_msg_history(5,"1",4)
store_msg_history(5,"2",4)
store_msg_history(5,"3",4)
store_msg_history(5,"4",4)
store_msg_history(5,"5",4)
store_msg_history(5,"6",4)
store_msg_history(5,"7",4)'''

'''list_of_subs = "10.0.0.1@10.0.0.2@10.0.0.3@10.0.0.4@10.0.0.5@10.0.0.6@10.0.0.7"
no_of_subs = list_of_subs.count('@')+1
subscribers = list()
for i in range(no_of_subs):
    subscribers.append(list_of_subs.split('@')[i])

print(subscribers[0])'''

list_of_subs = list()
no_of_subs=0
if(list_of_subs):
    no_of_subs = list_of_subs.count('@') +1
print(no_of_subs)