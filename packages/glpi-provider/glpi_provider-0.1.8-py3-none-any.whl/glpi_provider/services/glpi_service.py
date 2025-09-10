import json, requests
from glpi_provider.utils.url import url_transform


class GlpiServiceException(Exception):

    def __init__(self, message: str) -> None:
        self.message = message


class GlpiService:

    def __init__(
            self, 
            base_url: str, 
            user_token: str, 
            status_open: list, 
            requests_lib: requests = requests, 
            app_token: str=None
    ) -> None:
        self.base_url = url_transform(base_url)
        self._user_token = user_token
        self._app_token = app_token
        self._requests = requests_lib
        self._session_token: str = None
        self._ticket_open_status = status_open

    def create_session(self) -> None:
        self._create_session_token()
    
    def close_session(self) -> None:
        self._kill_session_token()

    def get_entity(self, entity_id: int) -> dict:
        url = f'{self.base_url}/apirest.php/entity/{entity_id}'
        return self._get(url)
    
    def get_entities(self) -> list:
        url = f'{self.base_url}/apirest.php/entity'
        return self._get(url)
    
    def get_locations(self) -> list:
        url = f'{self.base_url}/apirest.php/location'
        return self._get(url)

    def get_ticket(self, ticket_id: int) -> dict:
        url = f'{self.base_url}/apirest.php/ticket/{ticket_id}'
        return self._get(url)
    
    def get_tickets(self) -> list:
        url = f'{self.base_url}/apirest.php/ticket'
        return self._get(url)
    
    def get_open_tickets(self) -> dict:
        url = f'{self.base_url}/apirest.php/search/ticket/?range=0-50&order=DESC'
        index = 0

        for status in self._ticket_open_status:
            if index != 0:
                url += f'&criteria[{index}][link]=OR'

            url += f'&criteria[{index}][field]=12&criteria[{index}][searchtype]=equals&criteria[{index}][value]={status}'
            index += 1

        return self._get(url)
    
    def get_user(self, user_id: int) -> dict:
        url = f'{self.base_url}/apirest.php/user/{user_id}'
        return self._get(url)
    
    def get_users(self) -> list:
        url = f'{self.base_url}/apirest.php/user'
        return self._get(url)

    def add_comment(self, ticket_id: int, comment: str) -> dict:
        data = {
            'input': {
                "itemtype": "Ticket",
                "items_id": ticket_id,
                'content': comment, 
                'is_private': False
            }
        }
        headers = {
            'Session-Token': f'{self._get_session_token()}',
            'App-Token': self._app_token, 
            'Content-Type': 'application/json'
        }
        url = f'{self.base_url}/apirest.php/ticket/{ticket_id}/ITILFollowup/'
        response = requests.post(
            url,
            data=json.dumps(data),
            headers=headers
        )
        
        if response.status_code != 201:
            raise GlpiServiceException(f'Response status code {response.status_code}')
        
        return response.json()

    
    def get(self, url: str) -> requests.Response:
        url = f''

        if not self._session_token:
            raise GlpiServiceException('Session not initialized')

        headers = {
            'Session-Token': f'{self._get_session_token()}',
            'App-Token': self._app_token
        }
        response = self._requests.get(url, headers=headers)       
        return response
    
    def _get(self, url: str) -> dict:

        if not self._session_token:
            raise GlpiServiceException('Session not initialized')
        
        response = self.get(url)

        if response.status_code != 200:
            raise GlpiServiceException(f'Response status code {response.status_code}')
        
        return response.json()
    
    def _create_session_token(self) -> None:
        url = f'{self.base_url}/apirest.php/initSession/'
        headers = {
            'Authorization': f'user_token {self._user_token}',
            'App-Token': self._app_token
        }
        response = self._requests.get(url, headers=headers)

        if response.status_code != 200:
            raise GlpiServiceException(f'Response status code {response.status_code}')

        self._session_token = response.json().get('session_token')
    
    def _get_session_token(self) -> str:

        if not self._session_token:
            self._create_session_token()
            
        return self._session_token
    

    def _kill_session_token(self) -> None:

        if self._session_token:
            url = f'{self.base_url}/apirest.php/killSession/'
            headers = {
                'Session-Token': f'{self._get_session_token()}',
                'App-Token': self._app_token
            }
            response = self._requests.get(url, headers=headers)

            if response.status_code != 200:
                raise GlpiServiceException(f'Response status code {response.status_code}')

            self._session_token = None