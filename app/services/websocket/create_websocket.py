from ...common.commit import commit_object, flush_object
from ...schemas.notification_schemas import CreateNotification
from ...common.dictionaries import notification_dictionary
from ...services.loan_monitoring.notification.notification_crud import Notificaton_class
from typing import List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self,websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    async def connectSoc(self, client_id, websocket: WebSocket):
        await websocket.accept()
        
        self.active_connections.append({client_id:websocket})

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def direct_disconnect(self,client_id, websocket: WebSocket):
        for item in self.active_connections.copy():
            if item.get(client_id) == websocket:
                self.active_connections.remove(item)
                break
        
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            connect = list(connection.values())
            await connect[0].send_text(message)

    async def local_broadcast(self,users, message):
        for user in users:
            for d in self.active_connections:
                if user['id'] in d:
                    connection = d[user['id']]
                    await connection.send_text(message)

    
    # async def create_notification(self, from_user:int, to_user: int, db_session):
    #     data = CreateNotification()
    #     data.from_user_id = from_user
    #     data.to_user_id = to_user
    #     data.notification_type = notification_dictionary.notification_type['monitoring']
    #     data.body = notification_dictionary.notification_body['appoint_responsible']
    #     data.url = f'{3453}'+':'+ f'{345}'
        
    #     notifiaction = Notificaton_class(data)
    #     notifiaction.create_notification(db_session)
    #     commit_object(db_session)
    #     await self.send_direct_message(to_user, 'True')
    
    async def send_direct_message(self, client_id:int, message: str):
        
        for d in self.active_connections:
            if client_id in d:
                connection = d[client_id]
                await connection.send_text(message)
                
                
    # connection = [d[client_id] for d in self.active_connections if client_id in d]
        # print(connection)
        # if connection != []:
        #     await connection[0].send_text(message)
        # else: print('user doesnt exists')
        
        
manager = ConnectionManager()