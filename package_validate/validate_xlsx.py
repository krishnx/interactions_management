from dao import DAO
from logger_mod import Logger
import re
from .validate import Validate as V_Abs

class Validate(V_Abs):

    def _validate_aggregated_content(self):
        """
        package_validate the aggregated content of the file_content.
        Interaction format:
        0 - Investor Name
        1 - Status
        2 - Critical Errors / Reject reason
        3 - Interaction ID
        4 - Interaction Type
        5 - Meeting Type
        6 - Interaction Title
        7 - StartDate
        8 - StartTime
        9 - EndDate
        10 - EndTime
        11 - Duration
        12 - Initiated By
        13 - Group
        14 - Region
        15 - OriginatingRegion
        16 - Sectors
        17 - Location Type
        18 - Street Address
        19 - City
        20 - State
        21 - Country
        22 - Company Name | Identifier
        23 - Company Attendee Name | Title | Role
        24 - Broker Analyst Name | Email
        25 - Broker SalesPerson Name | Email
        26 - Broker Specialist Sales Name | Email
        27 - Broker MacroStrategist Name | Email
        28 - Other Broker Attendees Name | Email |Role
        29 - Expert Attendee Name | Role
        30 - Investor Attendee Name | Email
        31 - Investor Attendee Status
        32 - Comments
        33 - Tag
        34 - Parent ID
        :return: failed counts
        """
        fails = 0
        d = DAO(self.conn_string)
        file_attr = d.execute_query(
            'select FileName from "File" where FileName like \'{0}\''.format(self.info['file_name']))
        Logger.logger.debug(file_attr)

        for interaction in self.info['file_content']:
            Logger.logger.info("Starting for interaction title: {0}".format(interaction[6]))
            event_attr = d.execute_query(
                'select * from Event where OrgId = {0} and Title like \'{1}\';'.format(self.info['org_id'],
                                                                                       interaction[6]))

            if len(event_attr) < 1:
                Logger.logger.error("No Event attribute found.")
                continue
            else:
                Logger.logger.debug("Event attribute length: {0}".format(len(event_attr[0])))

            # EventId at 0th index
            event_id = event_attr[0][0]
            fails += self._validate_duration(interaction[7:12], event_id, d)
            fails += self._validate_address(interaction[19:22] + [interaction[15]], event_id, d)
            # fails += self._validate_miscellanous(interaction[:7], event_id, d)

            split_pat = re.compile(r'[\|\s\,\n\r]+')
            fails += self._validate_attendees(
                {'company': re.split(split_pat, interaction[23].strip()),
                 'investor': re.split(split_pat, interaction[30].strip()),
                 'broker': re.split(split_pat, interaction[24].strip()),
                 'company_name': re.split(r'\|', interaction[22])[0]
                },
                event_id, interaction[6], d)

            event_interaction = d.execute_query(
                "select * from EventInteraction where EventId = {0};".format(event_id))

            for ei in event_interaction:
                interaction_status = d.execute_query(
                    "select EventStatus from EventStatus where EventStatusId = {0}".format(ei[9]))[0][0]
                fails += self._match_string(interaction_status, interaction[1], "Platform Status")
                fails += self._match_string(ei[29], interaction[3], "Interaction ID")
                fails += self._match_string(ei[11], interaction[4], "Interaction type")
                fails += self._match_string(ei[12], interaction[5], "Meeting type / Interaction sub-type") # meeting type or sub type, are interchagably used.
                fails += self._match_string(ei[13], interaction[12], "Interaction intiator")


        return fails

    def _validate_flattened_content(self):
        """
        package_validate the flattened content of the file_content.
        Interaction format:
        0 - Investor Name
        1 - Status
        2 - Critical Errors / Reject reason
        3 - Interaction ID
        4 - Interaction Type
        5 - Meeting Type
        6 - Interaction Title
        7 - Status
        8 - Start Date
        9 - Start Time
        10 - End Date
        11 - End Time
        12 - Duration
        13 - Initiated by
        14 - Group
        15 - Region
        16 - Originating Region
        17 - Sectors
        18 - Location
        19 - Street Address
        20 - City
        21 - State
        22 - Country
        23 - Company Name
        24 - Identifier
        25 - Company Attendee First Name
        26 - Company Attendee LastName
        27 - Company Attendee Email
        28 - Company Attendee Title
        29 - Company Attendee Role
        30 - Company Attendee Status
        31 - Broker Attendee First Name
        32 - Broker Attendee Last Name
        33 - Broker Attendee Email
        34 - Broker Attendee Title
        35 - Broker Attendee Role
        36 - Broker Attendee Status
        37 - Expert Attendee First Name
        38 - Expert Attendee Last Name
        39 - Expert Attendee Email
        40 - Expert Attendee Title
        41 - Expert Attendee Role
        42 - Expert Attendee Status
        43 - Investor Attendee First Name
        44 - Investor Attendee Last Name
        45 - Investor Attendee Email
        46 - Investor Attendee Title
        47 - Investor Attendee Role
        48 - Investor Attendee Status
        49 - Comments
        50 - Tag
        51 - Parent ID
        :return: failed counts
        """
        fails = 0
        d = DAO(self.conn_string)
        file_attr = d.execute_query(
            'select FileName from "File" where FileName like \'{0}\''.format(self.info['file_name']))
        Logger.logger.debug(file_attr)

        for interaction in self.info['file_content']:
            Logger.logger.info("Starting for interaction title: {0}".format(interaction[6]))
            event_attr = d.execute_query(
                'select * from Event where OrgId = {0} and Title like \'{1}\';'.format(self.info['org_id'],
                                                                                       interaction[6]))

            if len(event_attr) < 1:
                Logger.logger.error("No Event attribute found.")
                continue
            else:
                Logger.logger.debug("Event attribute length: " + str(len(event_attr)))

            # Event description at index 40 starting from 0.
            # self._match_string(event_attr[-1][40], interaction[7], "Description")

            # EventId at 0th index
            event_id = event_attr[0][0]
            fails += self._validate_duration(interaction[8:14], event_id, d)
            fails += self._validate_address(interaction[20:23] + [interaction[15]], event_id, d)
            fails += self._validate_attendees(
                {'company': interaction[25:29],
                 'investor': interaction[43:46],
                 'broker': interaction[31:34],
                 'company_name':interaction[23],
                 'meeting_type': interaction[5]},
                event_id, interaction[6], d)

            event_interaction = d.execute_query(
                "select * from EventInteraction where EventId = {0};".format(event_id))

            for ei in event_interaction:
                interaction_status = d.execute_query(
                    "select EventStatus from EventStatus where EventStatusId = {0}".format(ei[9]))[0][0]
                fails += self._match_string(interaction_status, interaction[1], "Platform Status")
                fails += self._match_string(ei[29], interaction[3], "Interaction ID")
                fails += self._match_string(ei[11], interaction[4], "Interaction type")
                fails += self._match_string(ei[12], interaction[5], "Meeting type / Interaction sub-type")
                fails += self._match_string(ei[13], interaction[13], "Interaction intiator")

        return fails

    def _validate_generic_content(self):
        """
        package_validate all the attributes of an interaction
        Interaction format:
        0 - Investor Name
        1 - Platform Status
        2 - Critical Errors / Reject reason
        3 - Interaction ID
        4 - Interaction Type
        5 - Meeting Type
        6 - Interaction Title
        7 - Interaction Description
        8 - Interaction Status
        9 - Start Date
        10 - Start Time
        11 - End Date
        12 - End Time
        13 - Duration
        14 - Initiated by
        15 - Group
        16 - Region
        17 - Originating Region
        18 - Sectors
        19 - Location
        20 - Street Address
        21 - City
        22 - State
        23 - Country
        24 - Company Name
        25 - Identifier
        26 - Company Attendee First Name
        27 - Company Attendee LastName
        28 - Company Attendee Email
        29 - Company Attendee Title
        30 - Company Attendee Role
        31 - Company Attendee Status
        32 - Broker Attendee First Name
        33 - Broker Attendee Last Name
        34 - Broker Attendee Email
        35 - Broker Attendee Title
        36 - Broker Attendee Role
        37 - Broker Attendee Status
        38 - Expert Attendee First Name
        39 - Expert Attendee Last Name
        40 - Expert Attendee Email
        41 - Expert Attendee Title
        42 - Expert Attendee Role
        43 - Expert Attendee Company
        44 - Expert Attendee Bio
        45 - Expert Attendee Status
        46 - Investor Attendee First Name
        47 - Investor Attendee Last Name
        48 - Investor Attendee Email
        49 - Investor Attendee Title
        50 - Investor Attendee Role
        51 - Investor Attendee Status
        52 - Broker Report ID
        53 - Published Date
        54 - Published Time
        55 - Page Count
        56 - Asset Type
        57 - Asset Class
        58 - ContractID
        59 - Comments
        60 - Tag
        61 - Parent ID
        :return: failed counts
        """
        fails = 0
        d = DAO(self.conn_string)
        file_attr = d.execute_query(
            'select FileId from "File" where FileName like \'{0}\''.format(self.info['file_name']))
        Logger.logger.debug(file_attr)

        if len(file_attr) < 1:
            raise Exception(
                "File {0} is not present in the DB. Please try uploading again or check if something broke".format(self.info['file_name'])
            )

        for interaction in self.info['file_content']:
            Logger.logger.info("Starting for interaction title: {0}".format(interaction[6]))
            event_id_from_event_interaction = d.execute_query(
                'select * from EventInteraction where SellSideInteractionFileId = {0};'.format(file_attr[0][0]))
            event_attr = d.execute_query(
                'select * from Event where OrgId = {0} and Title like \'{1}\';'.format(self.info['org_id'],
                                                                                                    interaction[6]))

            if len(event_attr) < 1:
                Logger.logger.error("No Event attribute found.")
                continue
            else:
                Logger.logger.debug("Event attribute length: " + str(len(event_attr)))

            # Event description at index 40 starting from 0.
            fails += self._match_string(event_attr[-1][40], interaction[7], "Description")

            # EventId at 0th index
            if len(event_id_from_event_interaction) > 0:
                event_id = event_id_from_event_interaction[0][0]
            else:
                event_id = event_attr[0][0]

            fails += self._validate_duration(interaction[9:14], event_id, d)
            fails += self._validate_address(interaction[21:24] + [interaction[17]], event_id, d)
            fails += self._validate_attendees(
                {'company': interaction[26:33],
                 'investor': interaction[46:49],
                 'broker': interaction[32:35],
                 'expert': interaction[38:41],
                 'company_name': interaction[24],
                 'meeting_type': interaction[5]},
                event_id, interaction[6], d)

            event_interaction = d.execute_query(
                "select * from EventInteraction where EventId = {0};".format(event_id))

            for ei in event_interaction:
                interaction_status = d.execute_query(
                    "select EventStatus from EventStatus where EventStatusId = {0}".format(ei[9]))[0][0]
                fails += self._match_string(interaction_status, interaction[1], "Platform Status")
                fails += self._match_string(ei[29], interaction[3], "Interaction ID")
                fails += self._match_string(ei[11], interaction[4], "Interaction type")
                fails += self._match_string(ei[12], interaction[5], "Meeting type / Interaction sub-type")
                fails += self._match_string(ei[13], interaction[14], "Interaction intiator")

        return fails

    def validate_content(self):
        """
        Check the content size and call the appropriate function
        :return: if, nothing failed, return True, else False
        """
        fails = 0

        doc_length = len(self.info['file_content'][0])
        Logger.logger.debug("Document length: {0}".format(doc_length))

        if doc_length == 52:
            fails = self._validate_flattened_content()
        elif doc_length == 35:
            fails = self._validate_aggregated_content()
        else:
            fails = self._validate_generic_content()

        if fails > 0:
            Logger.logger.error("Total number of fails: {0}".format(fails))
            return False
        else:
            Logger.logger.info("All tests passed.")

        return True