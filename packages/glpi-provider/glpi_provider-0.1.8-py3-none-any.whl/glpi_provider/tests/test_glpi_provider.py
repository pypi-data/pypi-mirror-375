from unittest import TestCase
from unittest.mock import MagicMock
from glpi_provider.models import Entity, Ticket, User
from glpi_provider.providers.glpi_provider import GlpiProvider
from glpi_provider.tests.constants.entities_responses import ENTITY_RESPONSE, ENTITIES_RESPONSE
from glpi_provider.tests.constants.tickets_responses import TICKET_REPONSE, TICKETS_RESPONSE, TICKET_OPEN_RESPONSE
from glpi_provider.tests.constants.users_responses import USER_RESPONSE, USERS_RESPONSE


class GlpiProviderTestCase(TestCase):

    def test_get_user(self):
        service = MagicMock()
        service.get_user.return_value = USER_RESPONSE
        provider = GlpiProvider(service)
        user = provider.get_user(user_id=8)
        self.assertEqual(type(user), User)
    
    def test_get_users(self):
        service = MagicMock()
        service.get_users.return_value = USERS_RESPONSE
        provider = GlpiProvider(service)
        users = provider.get_users()
        self.assertEqual(len(users), 16)

    def test_parser_user_data(self):
        expected_data = {
            "id": 8,
            "last_name": "Alves",
            "first_name": "Tatianno",
            "mobile": ""
        }
        service = MagicMock()
        provider = GlpiProvider(service)
        user_data = provider._parser_user_data(USER_RESPONSE)
        self.assertDictEqual(user_data, expected_data)
    
    def test_get_entity(self):
        service = MagicMock()
        service.get_entity.return_value = ENTITY_RESPONSE
        provider = GlpiProvider(service)
        entity = provider.get_entity(entity_id=8)
        self.assertEqual(type(entity), Entity)
    
    def test_get_entities(self):
        service = MagicMock()
        service.get_entities.return_value = ENTITIES_RESPONSE
        provider = GlpiProvider(service)
        entities = provider.get_entities()
        self.assertEqual(len(entities), 16)

    def test_parser_entity_data(self):
        expected_data = {
            'id': 6, 
            'name': 'XXXXXXXX - DESENTUPIDORA LTDA - EPP', 
            'address': 'R MARIA XDXXXXXXXXXX, 15\r\nJD OSASCO', 
            'postcode': 'XXXXXXXX', 
            'town': 'OSASCO', 
            'state': 'SP', 
            'country': 'BRASIL', 
            'phonenumber': '11 XXXXXXXXXX', 
            'admin_email': 'tatianno.alves@gnew.com.br', 
            'admin_email_name': 'Tatianno'
        }
        service = MagicMock()
        provider = GlpiProvider(service)
        entity_data = provider._parser_entity_data(ENTITY_RESPONSE)
        self.assertDictEqual(entity_data, expected_data)
    
    def test_get_ticket(self):
        service = MagicMock()
        service.get_ticket.return_value = TICKET_REPONSE
        provider = GlpiProvider(service)
        ticket = provider.get_ticket(ticket_id=8)
        self.assertEqual(type(ticket), Ticket)
    
    def test_get_tickets(self):
        service = MagicMock()
        service.get_tickets.return_value = TICKETS_RESPONSE
        provider = GlpiProvider(service)
        tickets = provider.get_tickets()
        self.assertEqual(len(tickets), 16)

    def test_parser_entity_data(self):
        expected_data = {'id': 6, 'content': None, 'date_creation': '2019-03-23 11:15:14'}
        service = MagicMock()
        provider = GlpiProvider(service)
        ticket_data, entity_id = provider._parser_ticket_data(ENTITY_RESPONSE)
        self.assertDictEqual(ticket_data, expected_data)
        self.assertEqual(entity_id, 0)

    def test_parser_open_ticket_data(self):
        expected_data = {
            'id': 12835,
            'content': "VERIFICAR CONSISTENCIAS DE UMA CONSULTA PASSADA PELO CLIENTE. CONTATO:",
            'owner_id': 8,
            'status_id': 4,
            'entity': "GNEW > CASTIQUINI & OLIVEIRA LTDA - ME > UNIMED PRESIDENTE PRUDENTE"
        }
        service = MagicMock()
        provider = GlpiProvider(service)
        ticket_data = provider._parser_open_ticket_data(TICKET_OPEN_RESPONSE)
        self.assertDictEqual(ticket_data, expected_data)