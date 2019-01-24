from django.dispatch import Signal

ws_message = Signal(providing_args=['text_data', 'bytes_data'])

ws_connected = Signal(providing_args=['client_id', 'group_name'])

ws_disconnected = Signal(providing_args=['client_id', 'group_name'])
