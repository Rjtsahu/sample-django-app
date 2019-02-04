# food ordering management 
A simple POC app on Django framework

### What is this app ?
- This app demonstrate how to solve producer consumer problem using priority queuing in redis.
- It contains two user roles Manager and Delivery Agent
- A manager can create a task with priority as High/Medium/Low.
- A delivery agent can accept the highest priority task.
- Task can have various life cycle states viz. New->Accepted->Complted->Declined->Cancelled.
- Any event happening should be updated in realtime(websockets).

### Library and Framework used
- Django as web framework
- Django.db as ORM with postgres as database.
- Channels with channel_redis to perform realtime communication by using websocket and redis as channel layer.
- Redis datastore to store task queues with above priorities.

#

#### This is a simple app to demonstate how to work with django app with realtime communication.
###### Any improvements/suggestions are appreciable.
