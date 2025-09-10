from glpi_provider.models import Entity, Ticket, User
from glpi_provider.services.glpi_service import GlpiService
from glpi_provider.settings import BASE_URL, APP_TOKEN, USER_TOKEN, TICKET_STATUS


class GlpiProviderException(Exception):

    def __init__(self, message: str) -> None:
        self.message = message


class GlpiProvider:

    def __init__(self, service:GlpiService=None) -> None:
        self.service = service if service else GlpiService(
            base_url=BASE_URL, 
            user_token=USER_TOKEN, 
            status_open=TICKET_STATUS,
            app_token=APP_TOKEN
        )
    
    def add_comment(self, ticket_id: int, comment: str) -> None:
        self.service.add_comment(ticket_id, comment)
    
    def get_entity(self, entity_id: int) -> Entity:
        entity_data = self._parser_entity_data(self.service.get_entity(entity_id))
        return self._create_entity(entity_data)
    
    def get_entities(self) -> list[Entity]:
        entities = []

        for data in self.service.get_entities():
            entity_data = self._parser_entity_data(data)
            entities.append(self._create_entity(entity_data))
        
        return entities
    
    def get_locations(self):
        data = self.service.get_locations()
        return data

    def get_ticket(self, ticket_id: int) -> Ticket:
        ticket_data, entity_id = self._parser_ticket_data(self.service.get_ticket(ticket_id))
        return self._create_ticket(ticket_data, entity_id)
    
    def get_tickets(self) -> list[Ticket]:
        tickets = []

        for data in self.service.get_tickets():
            ticket_data, entity_id = self._parser_ticket_data(data)
            tickets.append(self._create_ticket(ticket_data, entity_id))
        
        return tickets
    
    def get_open_tickets(self) -> list[dict]:
        tickets = []

        for data in self.service.get_open_tickets().get('data', []):
            tickets.append(self._parser_open_ticket_data(data))
        
        return tickets
    
    def get_user(self, user_id: int) -> User:
        user_data = self._parser_user_data(self.service.get_user(user_id))
        return self._create_user(user_data)
    
    def get_users(self) -> list[User]:
        users = []

        for data in self.service.get_users():
            user_data = self._parser_user_data(data)
            users.append(self._create_user(user_data))
        
        return users
    
    def create_session(self) -> None:
        self.service.create_session()

    def close_session(self) -> None:
        self.service.close_session()
    
    def _create_entity(self, entity_data: dict) -> Entity:
        return Entity(**entity_data)
    
    def _create_ticket(self, ticket_data: dict, entity_id: int, user_id: int=None) -> Ticket:
        entity = self.get_entity(entity_id)
        user = self.get_user(user_id) if user_id else None
        ticket_data['entity'] = entity
        ticket_data['user'] = user
        return Ticket(**ticket_data)
    
    def _create_user(self, user_data: dict) -> User:
        return User(**user_data)

    def _parser_entity_data(self, data: dict) -> dict:
        self._validate_data_before_parser(data)
        return {
            'id': data.get('id'),
            'name': data.get('name'),
            'address': data.get('address'),
            'postcode': data.get('postcode'),
            'town': data.get('town'),
            'state': data.get('state'),
            'country': data.get('country'),
            'phonenumber': data.get('phonenumber'),
            'admin_email': data.get('admin_email'),
            'admin_email_name': data.get('admin_email_name')
        }
    
    def _parser_ticket_data(self, data: dict) -> tuple[dict, int]:
        self._validate_data_before_parser(data)
        return (
            {
                'id': data.get('id'),
                'content': data.get('content'),
                'date_creation': data.get('date_creation'),
            },
            data.get('entities_id')
        )
    
    def _parser_open_ticket_data(self, data: dict) -> tuple[int, int]:
        self._validate_data_before_parser(data)
        ticket_data = {
            'id': data.get("2"),
            'content': data.get("1"),
            'owner_id': data.get("5"),
            'status_id': data.get("12"),
            'entity': data.get("80")
        }
        return ticket_data
    
    def _parser_user_data(self, data: dict) -> dict:
        self._validate_data_before_parser(data)
        return {
            'id': data.get('id'),
            'last_name': data.get('realname'),
            'first_name': data.get('firstname'),
            'mobile': data.get('mobile')
        }

    def _validate_data_before_parser(self, data: dict) -> None:
        if type(data) != dict:
            raise GlpiProviderException('Parser data error')