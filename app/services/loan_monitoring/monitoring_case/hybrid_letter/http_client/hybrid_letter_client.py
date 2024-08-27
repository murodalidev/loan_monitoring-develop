
from .client_interface import HTTPClientInterface
from ......config.config import HYBRID_API, HYBRID_API_TEST, HYBRID_API_TOKEN



class HybridLetterClient(HTTPClientInterface):
    __get_region_api = '/api/v1/pochta/region'
    __get_area_api = '/api/v1/pochta/area'
    __get_by_id = '/api/v1/pochta/id/mail'
    __send_letter = '/api/v1/pochta/send/content'
    __get_by_period = '/api/v1/pochta/send/mail'
    __API_TOKEN = HYBRID_API_TOKEN
    def __init__(self, body = None, letter_id = None):
         self.body = body
         self.letter_id = letter_id
    def get_api_token(self):
        return {"Api-Token": self.__API_TOKEN}
    
    
    
    def get_region(self):
        return {"url": HYBRID_API + self.__get_region_api,
                "method": "GET"}
        
        
    def get_area(self):
        return {"url": HYBRID_API + self.__get_area_api,
                "method": "GET"}
        
        
    def get_by_id(self):
        return {"url": HYBRID_API + self.__get_by_id,
                "letter_id": self.letter_id,
                "method": "GET"}
        
        
    def get_by_period(self):
        return {"url": HYBRID_API + self.__get_by_period,
                "method": "GET"}
        
        
    def send_letter(self):
        return {"url": HYBRID_API + self.__send_letter,
                "method": "POST",
                "body": self.body}