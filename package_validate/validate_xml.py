from dao import DAO
from logger_mod import Logger
import datetime, time
import re
from validate import Validate as V_Abs

class Validate(V_Abs):

    def _get_value(self, data):
        if not data:
            return ''
        return data.encode("ascii", "ignore")

    def _get_participants(self, data):
        """
        From the data, extract the participant's info.
        :param data: a list or a dict containing pariticapnts' info
        :return: array  [0] - first name
                        [1] - last name
                        [2] - email address
        """
        participants = []
        if isinstance(data['participant'], list):
            for person in data['participant']:
                participants.append(self._get_value(person['person']['firstName']))
                participants.append(self._get_value(person['person']['lastName']))
                participants.append(self._get_value(person['person']['email']))
        else:
            participants.append(self._get_value(data['participant']['person']['firstName']))
            participants.append(self._get_value(data['participant']['person']['lastName']))
            participants.append(self._get_value(data['participant']['person']['email']))

        return participants

    def _get_company_participants(self, data):
        """
        From data, extract company participants info
        :param data: a list or a dict containing company's pariticapnts' info
        :return: array  [0] - first name
                        [1] - last name
                        [2] - email address
        """
        if data.has_key('company'):
            if isinstance(data['company'], list):
                result = []
            else:
                result = self._get_participants(data['company']['companyParticipants'])
        else:
            result = []

        return result

    def _get_company_name(self, data):
        """
        Parse the nested structure and extract the company name.
        :param data: a dict containing company' name info
        :return: a string with company name
        """
        if data.has_key('company'):
            if isinstance(data['company'], list):
                result = ""
            else:
                result = data['company']['companyName']
        else:
            result = ""

        return result

    def _get_address(self, interaction):
        """
        Get the Country, State and City values from the data.
        :param interaction: regions->region key has the country name
                            if not, location will have country, state and city
        :return: array  [0] - city
                        [1] - state
                        [2] - country
        """
        result = [''] * 4
        if interaction.has_key('regions'):
            result[2] = interaction['regions']['region']
            result[1] = 'state'
            result[0] = interaction['location']['address']['city']
        else:
            result[2] = interaction['location']['address']['country']
            result[1] = interaction['location']['address']['state']
            result[0] = interaction['location']['address']['city']

        return result

    def _validate_interaction(self, interaction):
        """
        This is a granular interaction. Iterate over it and compare the data points
        Interaction format:
        {u'clientinteraction': {u'@xmlns': u'http://oneaccess.io/corporateaccess/clientinteraction/2.1.1',
                        u'@xmlns:xsd': u'http://www.w3.org/2001/XMLSchema',
                        u'@xmlns:xsi': u'http://www.w3.org/2001/XMLSchema-instance',
                        u'broker': u'ROKOLabs',
                        u'interactions': {u'investor': {u'interaction': [{u'brokerParticipants': {u'participant': [{u'person': {u'email': u'Broker@email.com',
                                                                                                                                u'firstName': u'George',
                                                                                                                                u'lastName': u'Notter',
                                                                                                                                u'title': u'Analyst'},
                                                                                                                    u'roles': {u'role': u'SellsideAnalyst'},
                                                                                                                    u'status': u'Confirmed'},
                                                                                                                   {u'person': {u'email': u'Broker2@email.com',
                                                                                                                                u'firstName': u'Shanelle',
                                                                                                                                u'lastName': u'Trinidad',
                                                                                                                                u'title': u'Research Sales'},
                                                                                                                    u'roles': {u'role': u'SellsideAnalyst'},
                                                                                                                    u'status': u'Confirmed'}]},
                                                                          u'comments': {u'comment': [u'comment1',
                                                                                                     u'comment2']},
                                                                          u'companies': {u'company': {u'companyName': u'APPLE',
                                                                                                      u'companyParticipants': {u'participant': {u'person': {u'email': u'CompanyPersonemail@email.com',
                                                                                                                                                            u'firstName': u'Sergei',
                                                                                                                                                            u'lastName': u'Brin',
                                                                                                                                                            u'phone': u'322223',
                                                                                                                                                            u'title': u'some title'},
                                                                                                                                                u'roles': {u'role': u'HeadOfBusiness'},
                                                                                                                                                u'status': u'Confirmed'}},
                                                                                                      u'identifiers': {u'identifier': {u'#text': u'APPL',
                                                                                                                                       u'@type': u'Ticker'}},
                                                                                                      u'isPublic': u'true'}},
                                                                          u'duration': u'10',
                                                                          u'end': u'2016-11-30',
                                                                          u'endTime': {u'datetime': u'2016-11-30T20:30:00-04:00',
                                                                                       u'timezone': u'US/Eastern'},
                                                                          u'initiator': u'Broker',
                                                                          u'interactionDescription': u'testinteraction descritiption',
                                                                          u'interactionID': u'1040025130',
                                                                          u'interactionSubType': u'1x1',
                                                                          u'interactionTitle': u'TEST1 (AnalystMarketing)',
                                                                          u'interactionType': u'AnalystMarketing',
                                                                          u'investorParticipants': {u'participant': {u'person': {u'email': u'ekater.inasemyonov.a654@gmail.com',
                                                                                                                                 u'firstName': u'Ken0812',
                                                                                                                                 u'lastName': u'Chang0812',
                                                                                                                                 u'title': u'investortitle'},
                                                                                                                     u'roles': {u'role': u'PortfolioManager'},
                                                                                                                     u'status': u'Attended'}},
                                                                          u'location': {u'address': {u'city': u'New York',
                                                                                                     u'country': u'USA',
                                                                                                     u'postalCode': u'212121',
                                                                                                     u'state': u'New York',
                                                                                                     u'streetAddress': u'New street',
                                                                                                     u'type': u'Offsite'}},
                                                                          u'originatingRegion': u'North America',
                                                                          u'parentID': u'1040025130',
                                                                          u'sectors': {u'sector': u'45'},
                                                                          u'start': u'2016-11-28',
                                                                          u'startTime': {u'datetime': u'2016-11-28T12:00:00-04:00',
                                                                                         u'timezone': u'US/Eastern'},
                                                                          u'thirdPartyParticipants': {u'participant': {u'person': {u'email': u'expert@email.com',
                                                                                                                                   u'firstName': u'Ken1',
                                                                                                                                   u'lastName': u'Chang1',
                                                                                                                                   u'title': u'experttitle'},
                                                                                                                       u'roles': {u'role': u'IndustryExpert'},
                                                                                                                       u'status': u'Attended'}}},
                                                                         {u'brokerParticipants': {u'participant': [{u'person': {u'email': u'Broker@email.com',
                                                                                                                                u'firstName': u'George',
                                                                                                                                u'lastName': u'Notter',
                                                                                                                                u'title': u'Analyst'},
                                                                                                                    u'roles': {u'role': u'SellsideSales'},
                                                                                                                    u'status': u'Confirmed'},
                                                                                                                   {u'person': {u'email': u'Broker2@email.com',
                                                                                                                                u'firstName': u'Shanelle',
                                                                                                                                u'lastName': u'Trinidad',
                                                                                                                                u'title': u'Research Sales'},
                                                                                                                    u'roles': {u'role': u'SellsideSales'},
                                                                                                                    u'status': u'Confirmed'}]},
                                                                          u'comments': {u'comment': [u'comment1',
                                                                                                     u'comment2']},
                                                                          u'companies': {u'company': {u'companyName': u'APPLE',
                                                                                                      u'companyParticipants': {u'participant': {u'person': {u'email': u'CompanyPersonemail@email.com',
                                                                                                                                                            u'firstName': u'Sergei',
                                                                                                                                                            u'lastName': u'Brin',
                                                                                                                                                            u'phone': u'322223',
                                                                                                                                                            u'title': u'some title'},
                                                                                                                                                u'roles': {u'role': u'HeadOfBusiness'},
                                                                                                                                                u'status': u'Confirmed'}},
                                                                                                      u'identifiers': {u'identifier': {u'#text': u'APPL',
                                                                                                                                       u'@type': u'Ticker'}},
                                                                                                      u'isPublic': u'true'}},
                                                                          u'duration': u'10',
                                                                          u'end': u'2016-11-30',
                                                                          u'endTime': {u'datetime': u'2016-11-30T20:30:00-04:00',
                                                                                       u'timezone': u'US/Eastern'},
                                                                          u'initiator': u'Investor',
                                                                          u'interactionDescription': u'testinteraction descritiption',
                                                                          u'interactionID': u'1040025129',
                                                                          u'interactionSubType': u'1x1',
                                                                          u'interactionTitle': u'TEST1 (Conference)',
                                                                          u'interactionType': u'Conference',
                                                                          u'investorParticipants': {u'participant': {u'person': {u'email': u'ekater.inasemyonov.a654@gmail.com',
                                                                                                                                 u'firstName': u'Ken0812',
                                                                                                                                 u'lastName': u'Chang0812',
                                                                                                                                 u'title': u'investortitle'},
                                                                                                                     u'roles': {u'role': u'PortfolioManager'},
                                                                                                                     u'status': u'Attended'}},
                                                                          u'location': {u'address': {u'city': u'New York',
                                                                                                     u'country': u'USA',
                                                                                                     u'postalCode': u'212121',
                                                                                                     u'state': u'New York',
                                                                                                     u'streetAddress': u'New street',
                                                                                                     u'type': u'Onsite'}},
                                                                          u'originatingRegion': u'North America',
                                                                          u'parentID': u'1040025129',
                                                                          u'sectors': {u'sector': u'45'},
                                                                          u'start': u'2016-11-28',
                                                                          u'startTime': {u'datetime': u'2016-11-28T12:00:00-04:00',
                                                                                         u'timezone': u'US/Eastern'},
                                                                          u'thirdPartyParticipants': {u'participant': {u'person': {u'email': u'expert@email.com',
                                                                                                                                   u'firstName': u'Ken1',
                                                                                                                                   u'lastName': u'Chang1',
                                                                                                                                   u'title': u'experttitle'},
                                                                                                                       u'roles': {u'role': u'IndustryExpert'},
                                                                                                                       u'status': u'Attended'}}}
								u'investorName': u'ROKOLabs'}},
                        u'updated': {u'datetime': u'2016-05-09T16:43:49.3823692Z',
                                     u'timezone': u'Etc/UTC'}}}
        :param interaction: a dict containing interaction
        :return: failed counts
        """
        fails = 0

        d = DAO(self.conn_string)
        interaction_title = self._get_value(interaction['interactionTitle'])
        Logger.logger.debug("Starting for interaction title: {0}".format(interaction_title))
        file_attr = d.execute_query(
            'select FileId from "File" where FileName like \'{0}\''.format(self.info['file_name']))
        Logger.logger.debug(file_attr)

        if len(file_attr) < 1:
            raise Exception(
                "File {0} is not present in the DB. Please try uploading again or check if something broke".format(
                    self.info['file_name'])
            )

        event_id_from_event_interaction = d.execute_query(
            'select EventId from EventInteraction where SellSideInteractionFileId = {0};'.format(file_attr[0][0]))
        event_id_from_event = d.execute_query(
            'select EventId from Event where OrgId = {0} and Title like \'{1}\';'.format(self.info['org_id'],
                                                                                         interaction_title))

        # EventId at 0th index
        if len(event_id_from_event_interaction) > 0:
            Logger.logger.debug("Event id {0} from EventInteraction Table".format(event_id_from_event_interaction[0][0]))
            event_id = event_id_from_event_interaction[0][0]
        elif len(event_id_from_event) > 0:
            Logger.logger.debug("Event id {0} from Event Table".format(event_id_from_event[0][0]))
            event_id = event_id_from_event[0][0]
        else:
            Logger.logger.error("No Event found in database.")
            return fails + 1

        if interaction.has_key('startTime') and interaction.has_key('endTime') and interaction.has_key('duration'):
            fails = self._validate_duration(self._convert_date_format(
                interaction['startTime']['datetime'],
                interaction['endTime']['datetime'],
                interaction['duration']),
                event_id, d)
        else:
            Logger.logger.error("No duration details found in interaction.")

        fails += self._validate_attendees({
            'broker': self._get_participants(interaction['brokerParticipants']) if interaction.has_key(
                'brokerParticipants') else ['']*3,
            'investor': self._get_participants(interaction['investorParticipants']) if interaction.has_key(
                'investorParticipants') else ['']*3,
            'expert': self._get_participants(interaction['thirdPartyParticipants']) if interaction.has_key(
                'thirdPartyParticipants') else ['']*3,
            'company': self._get_company_participants(interaction['companies']) if interaction.has_key(
                'companies') else ['']*3,
            'company_name': self._get_company_name(interaction['companies']) if interaction.has_key('companies') else ""
        }, event_id, interaction_title, d)

        fails += self._validate_address(self._get_address(interaction), event_id, d) if interaction.has_key('location') else 0

        event_interaction = d.execute_query(
            "select * from EventInteraction where EventId = {0};".format(event_id))
        for ei in event_interaction:
            # interaction_status = d.execute_query(
            #     "select EventStatus from EventStatus where EventStatusId = {0}".format(ei[9]))[0][0]
            # fails += self._match_string(interaction_status, interaction[1], "Platform Status")
            fails += self._match_string(ei[29], interaction['interactionID'], "Interaction ID") if interaction.has_key('interactionID') else 0
            fails += self._match_string(ei[27], interaction['interactionType'], "Interaction type") if interaction.has_key('interactionType') else 0
            fails += self._match_string(ei[28], interaction['interactionSubType'],
                                        "Meeting type / Interaction sub-type")  if interaction.has_key('interactionSubType') else 0
            fails += self._match_string(ei[13], interaction['initiator'], "Interaction intiator") if interaction.has_key('initiator') else 0

        return fails

    def validate_content(self):
        """
        If file_content is a list, iterate over this list and compare the data points
        :return: failed counts
        """
        fails = 0

        if isinstance(self.info['file_content']['clientinteraction']['interactions']['investor']['interaction'], list):
            for interaction in self.info['file_content']['clientinteraction']['interactions']['investor']['interaction']:
                fails += self._validate_interaction(interaction)

        else:
            fails += self._validate_interaction(self.info['file_content']['clientinteraction']['interactions']['investor']['interaction'])

        if not fails:
            return True

        return False
