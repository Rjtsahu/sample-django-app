from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from food_ordering.signals import ws_message, ws_connected, ws_disconnected
from channels.consumer import get_channel_layer
from django.db import connections

class WsConsumer(WebsocketConsumer):
    broadcast_group = 'broadcast'
    manager_group = 'manager'
    agent_group = 'agent'

    room_name: str
    client_id: str

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.client_id = self.scope['cookies']['sessionid']

        self.accept()
        print('client connected, sessionId:', self.client_id)

        self.send_message('you are now connected.')

        async_to_sync(self.channel_layer.group_add)(
            self.room_name,
            self.channel_name
        )

        # add user to single member group if that user is agent
        self.channel_layer.group_add(
            self.get_agent_group_name(self.scope['user'].id),
            self.channel_name)

        WsConsumer.group_send('New client connected clientId:' + self.client_id, self.room_name)
        ws_connected.send(sender=__class__, client_id=self.client_id, group_name=self.room_name)
        connections.close_all()

    def disconnect(self, code):
        print('disconnected client : ', self.client_id)

        async_to_sync(self.channel_layer.group_discard)(
            self.room_name,
            self.channel_name
        )

        self.channel_layer.group_discard(
            self.get_agent_group_name(self.scope['user'].id),
            self.channel_name)

        ws_disconnected.send(sender=__class__, client_id=self.client_id, group_name=self.room_name)
        connections.close_all()

    def receive(self, text_data=None, bytes_data=None):
        print('data received ', text_data)
        ws_message.send(sender=self.__class__, text_data=text_data, bytes_data=bytes_data)

    def send_message(self, msg):
        self.send(msg)

    @staticmethod
    def group_send(msg, group_name=broadcast_group):
        print('group name', group_name)
        print('message', group_name)
        try:
            layer = get_channel_layer()
            async_to_sync(layer.group_send)(
                group_name,
                {
                    'type': 'channel_send_handler',
                    'message': msg
                }
            )
        except Exception as e:
            print('error while group sending : ', e)
        connections.close_all()

    def channel_send_handler(self, event):
        message = event['message']
        self.send_message(message)

    @staticmethod
    def get_agent_group_name(user_id):
        return WsConsumer.agent_group + '_' + str(user_id)
