
from .http_client.client_interface import HTTPClientInterface
from fastapi import HTTPException
import requests
import logging
import json
from .....config.logs_config import info_logger

        


class HTTPClient():
   
    
    def __init__(self, client:HTTPClientInterface, params = None) -> None:
        self.client = client
        self.params = params
        self.__headers={'Content-type':'application/json',
            'Api-Token': self.params['Api-Token']}
    
    def new_post_request(self):
        try:
            response = requests.post(url=self.client['url'],
                                headers=self.__headers,
                                data = json.dumps(self.client['body']),
                                timeout=(6, 120))
        except requests.exceptions.RequestException:
            detail= 'Something went wrong while sending letter, please try again later.'
            info_logger.error(detail)
            raise HTTPException(status_code=400, detail = detail)
        if response.status_code != 200:
            detail= 'Something went wrong after letter has sent'
            info_logger.error(detail)
            raise HTTPException(status_code=response.status_code, detail=detail)
        return response.content
    
    
    
    def new_get_request(self):
        response = None
        try:
            response = requests.get(url=self.client['url'],
                                headers=self.__headers,
                                params = {"id":self.client['letter_id']},
                                timeout=(6, 120))
        except requests.exceptions.RequestException:
            detail= 'Something went wrong while getting status, please try again later.'
            info_logger.error(detail)
            raise HTTPException(status_code=400, detail=detail)
        if response.status_code != 200:
            detail= 'Letter not found'
            info_logger.error(detail)
            raise HTTPException(status_code=response.status_code, detail=detail)
        elif response is not None:
            return response.json()
        else: return response