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

### How to Run?
- Use python3 and install all requirements : `pip install -r requirements.txt`
- Host/install redis server and save 'REDIS_CONNECTION' as environment variable.
  For example if you have hosted redis in your local system then : 'REDIS_CONNECTION' = `redis://127.0.0.1:6379`
- Similarly add environment variable with key 'DJANGO_SECRECT_KEY' and 'DATABASE_URL' where first one is random secret key,which second should be valid database URI for example : `postgres://user:password@127.0.0.1:5432/test_database`
- Run migrations `python manage.py makemigrations` and `python manage.py migrate`
- Run server `python manage.py runserver`
- This will run application in localhost:8000

#

#### This is a simple app to demonstate how to work in django app with realtime communication.
###### Any improvements/suggestions are appreciable.
