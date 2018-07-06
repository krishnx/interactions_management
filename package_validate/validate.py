from logger_mod import Logger
import datetime, time
import re

class Validate(object):
    def __init__(self, info, conn_string):
        self.info = info
        self.conn_string = conn_string
        Logger.logger.debug("Validate() initialized.")

    def _rotate(self, l, n):
        """
        Rotate the array.
        :param l: the array
        :param n: the number of times to rotate the array.
        :return: rotated array
        """
        return l[-n:] + l[:-n]

    def _inspect_blank(self, input_value, input_name):
        """
        Check if the passed in data structure is empty
        :param input_value: a list / object / string
        :param input_name: the relevance of the passed in argument
        :return: Bool
        """
        if isinstance(input_value, str) and not input_value.strip():
            Logger.logger.debug("Received blank {0} field from the interaction.".format(input_name))
            return True
        elif isinstance(input_value, list) and not all(v for v in input_value):
            Logger.logger.debug("Blank(s) found in the list of {0}".format(input_name))
            return True
        elif input_value is None:
            Logger.logger.debug("Received blank {0} field from the interaction.".format(input_name))
            return True
        return False

    def _match_string(self, from_db, from_interaction, what):
        """
        Compare the string from DB and interaction
        :param from_db: input from DB
        :param from_interaction: input from interaction
        :param what: it's relevance
        :return: comparison result
        """
        fails = 0
        if not (from_db and from_interaction):
            return fails+1

        from_db = from_db.strip()
        from_interaction = from_interaction.strip()

        if from_db.lower() == from_interaction.lower():
            Logger.logger.debug("{0} matches".format(what))
        else:
            Logger.logger.error("{0} mis-matched: DB:{1} :: Interaction:{2}".format(what, from_db, from_interaction))
            fails += 1

        return fails

    def _match_region(self, region, region_id, interaction_region, dbh=None):
        """
        Compare he Country, State and City.
        :param region: Country / State / City
        :param region_id: it's id in the DB
        :param interaction_region: the name "country"/"state"/"city"
        :param dbh: DB handle
        :return: comparison result
        """
        fails = 0
        if self._inspect_blank(region, "region") or \
                self._inspect_blank(region_id, "region id") or \
                self._inspect_blank(interaction_region, "interaction region") or \
                self._inspect_blank(dbh, "DBH"):
            return fails+1

        region_name = None
        try:
            # Try-except block for the [0][0], if that fails, raise exception.
            region_name = dbh.execute_query(
                "select name from {0} where {0}Id = {1}".format(region, region_id))[0][0]
        except Exception as e:
            Logger.logger.error("For {0}: {1}".format(region, str(e)))

        fails += self._match_string(region_name, interaction_region, region)

        return fails

    def _convert_date_format(self, start_ts, end_ts, duration, input_pat='%Y-%M-%d', output_pat='%d/%M/%Y'):
        """
        The interactions have a timestamp format,
        split the date and time and convert it into the desired format.
        :param start_ts: start timestamp 2018[/-]05[/-]10THH:MM:SSZ
        :param end_ts: end timestamp 2018[/-]05[/-]10THH:MM:SSZ
        :param duration: integer - in minutes
        :param input_pat: the received format of timestamp
        :param output_pat: the desired format of timestamp
        :return: an array with [start_date, start_time, end_date, end_time]
        """
        start    = [ele.encode("ascii", "ignore") for ele in re.split(r'[TZ\s]+', start_ts)][:2]
        start[0] = datetime.datetime.strptime(start[0], input_pat).strftime(output_pat)
        end      = [ele.encode("ascii", "ignore") for ele in re.split(r'[TZ\s]+', end_ts)][:2]
        end[0]   = datetime.datetime.strptime(end[0], input_pat).strftime(output_pat)
        duration = [duration.encode("ascii", "ignore")]

        return start + end + duration

    def _epoch_convertor(self, date_str, time_str):
        """
        Convert he timestamp into epoch seconds.
        :param date_str: date string
        :param time_str: time string
        :return: epoch equivalent of the inputs
        """
        date_split_pat = re.compile(r'[\-\/]')
        date_attr = [0] * 3
        time_attr = [0] * 3
        date_str = date_str.strip()

        if not any(char.isdigit() for char in date_str):
            Logger.logger.error("Invalid date string received. Date: {0}".format(date_str))
            return False
        if time_str and not any(char.isdigit() for char in time_str):
            Logger.logger.error("Invalid time string received. Time: {0}".format(time_str))
            return False

        date_attr = map(int, re.split(date_split_pat, date_str))

        if time_str.upper().endswith('AM') or time_str.upper().endswith('PM'):
            time_attr = time_str[:-2].strip().split(":")
            if time_str.upper().endswith("PM") and int(time_attr[0]) < 12:
                time_attr[0] = int(time_attr[0]) + 12
                time_attr[1] = int(time_attr[1])
            else:
                time_attr = map(int, time_str[:-2].split(":"))

        return str(datetime.datetime(date_attr[2], date_attr[1], date_attr[0], time_attr[0], time_attr[1]))

    def _validate_duration(self, interaction, eventId, dbh=None):
        """
        package_validate the start, end date & time and the duration
        :param interaction: input from interaction
        :param eventId: input from DB
        :param dbh: DB handle
        :return: comparison result
        """
        fails = 0
        if self._inspect_blank(dbh, "DBH") or \
                self._inspect_blank(eventId, "event id") or \
                self._inspect_blank(interaction[0], 'start time') or \
                self._inspect_blank(interaction[2], 'end time') or \
                self._inspect_blank(interaction[4], 'duration'):
            return fails+1

        db_dates = dbh.execute_query(
            "select StartDate, EndDate from EventPeriod where EventId = {0};".format(eventId))

        if len(db_dates) < 1:
            Logger.logger.error("No duration found for Event id {0}".format(eventId))
            return fails+1

        Logger.logger.debug("times : {0}".format(", ".join(interaction)))
        pattern = '%Y-%m-%d %H:%M:%S'
        start_time_tuple = time.strptime(self._epoch_convertor(interaction[0], interaction[1]), pattern)
        end_time_tuple = time.strptime(self._epoch_convertor(interaction[2], interaction[3]), pattern)
        interaction_start_time = time.mktime(start_time_tuple)
        interaction_end_time = time.mktime(end_time_tuple)

        db_start_time = time.mktime(time.strptime(str(db_dates[0][0]), pattern))
        db_end_time = time.mktime(time.strptime(str(db_dates[0][1]), pattern))

        if db_start_time == interaction_start_time and db_end_time == interaction_end_time:
            Logger.logger.debug("Start and End date matched")
        else:
            Logger.logger.error("DB:{0}, {1} INTERACTION: {2}, {3}".
                               format(db_start_time, db_end_time, interaction_start_time, interaction_end_time))

        if (interaction_end_time - interaction_start_time) == (int(interaction[4])*60):
            Logger.logger.debug("Duration matched")
        else:
            Logger.logger.error("start: {0}, end: {1}, interaction: {2}".
                               format(interaction_start_time, interaction_end_time, interaction[3]))
            fails += 1

        return fails

    def _validate_address(self, interaction, eventId, dbh=None):
        """
        Compare the City State and Country of an interaction with the one in DB
        :param interaction: from the uploaded file.
        :param eventId: the associated event id in the DB
        :param dbh: DB handle
        :return: comparison result
        """
        fails = 0
        if self._inspect_blank(dbh, "DBH") or \
                self._inspect_blank(eventId, "event id") or \
                self._inspect_blank(interaction[2], "country") or \
                self._inspect_blank(interaction[1], "state") or \
                self._inspect_blank(interaction[0], "city"):
            fails += 1
            return fails

        address_id = dbh.execute_query(
            "select AddressId from EventToAddress where EventId = {0}".format(eventId))

        if len(address_id) > 0:
            address_id = address_id[0][0]
        else:
            Logger.logger.warn("No entries found for EventId {0} in EventToAddress db table.".format(eventId))
            return fails

        country_id, state_id, city_id =  dbh.execute_query(
            "select CountryId, StateId, CityId from Address where AddressId = {0}".format(address_id))[0]
        originating_region = dbh.execute_query(
            "select RawOriginatingRegion from EventInteraction where EventId = {0}".format(eventId)
        )
        country_name = dbh.execute_query(
            "select Name from Country where CountryId in (select CountryId from Address where AddressId in (select AddressId from EventToAddress where EventId = {0}))".format(eventId)
        )[0][0]

        state_name = dbh.execute_query("select Name from Region where RegionId = {0}".format(state_id))[0][0]

        fails += self._match_string(country_name, interaction[2], "Country")
        fails += self._match_string(originating_region, interaction[3], "Originating Region")
        fails += self._match_string(state_name, interaction[1], "State")
        fails += self._match_region("City", city_id, interaction[0], dbh)

        return fails

    def _validate_attendees(self, interaction, eventId, interaction_title="", dbh=None):
        """
        package_validate the Company, Expert, Investor and Broker participants
        :param interaction: from the uploaded file
        :param eventId: from the DB
        :param interaction_title: Title to trace the interaction in the DB.
        :param dbh: DB handle
        :return: Comparison result
        """
        fails = 0
        if self._inspect_blank(dbh, "DBH") or \
                self._inspect_blank(eventId, "event id"):
            return fails+1

        split_pat = re.compile(r'[\|\s\,\n\r]+')

        query = 'select * from InteractionCondensed where EventId = {0}'.format(eventId)
        if interaction_title:
            query +=  "and Title like '{0}'".format(interaction_title)
        attendees = dbh.execute_query(query)

        if not attendees:
            fails += 1
            Logger.logger.error("No rows found for attendees details in InteractionCondensed.")
            return fails

        # Investor Attendees
        attendees_attr = re.split(split_pat, attendees[0][3].strip())
        Logger.logger.debug("Attendees : {0}".format(", ".join(attendees_attr)))
        if not self._inspect_blank(interaction['investor'], "Investors"):
            fails += self._match_string(attendees_attr[0], interaction['investor'][0], "Investor First name")
            fails += self._match_string(attendees_attr[1], interaction['investor'][1], "Investor Last name")
            fails += self._match_string(attendees_attr[2], interaction['investor'][2], "Investor Email address")

        # Company Attendees
        company_expert_attendee_id = 1 # Company and Expert pariticipant attendies come under id 1
        company_attendees = dbh.execute_query(
            "select FirstName, LastName, Email from EventAttendee where EventId = {0} and ParticipantTypeId = {1};".format(eventId, company_expert_attendee_id))

        if len(company_attendees) > 0:
            if not self._inspect_blank(interaction['company'], "Companies") and len(interaction['company']) >= 3:
                fails += self._match_string(company_attendees[-1][0], interaction['company'][0], "Company First name")
                fails += self._match_string(company_attendees[-1][1], interaction['company'][1], "Company Last name")
                fails += self._match_string(company_attendees[-1][2], interaction['company'][2], "Company Email address")
                # self._match_string(company_attendees[0][8].split(',')[0], interaction['company'][3], "Company Title")
            else:
                Logger.logger.debug("Blank(s) in Company attendies.")

            # Expert Attendees.
            if interaction.has_key('expert'):
                fails += self._match_string(company_attendees[0][0], interaction['expert'][0], "Expert First name")
                fails += self._match_string(company_attendees[0][1], interaction['expert'][1], "Expert Last name")
                fails += self._match_string(company_attendees[0][2], interaction['expert'][2], "Expert Email address")

        # Broker Attendees
        if attendees[0][4]:
            broker_attendees_attr = re.split(split_pat, attendees[0][4].strip())
        else:
            broker_attendees_attr = ['']
        Logger.logger.debug("Broker attendees : {0}.".format(", ".join(broker_attendees_attr)))
        if not self._inspect_blank(interaction['broker'], "Brokers"):
            fails += self._match_string(broker_attendees_attr[0], interaction['broker'][0], "Broker First name")
            fails += self._match_string(broker_attendees_attr[1], interaction['broker'][1], "Broker Last name")
            fails += self._match_string(broker_attendees_attr[2], interaction['broker'][2], "Broker Email address")
            # self._match_string(broker_attendees_attr[3], interaction[35], "Broker Title")

        # Company name
        if not self._inspect_blank(interaction['company_name'], "Company name"):
            companies_tuple = dbh.execute_query("select * from EventInteractionCompany where EventId = {0};".format(eventId))
            company_names = [i.encode("utf-8") for i in filter(None, [company[3] for company in companies_tuple])]
            if interaction['company_name'].strip() in company_names:
                Logger.logger.debug("Company name matched")
            else:
                fails += 1
                Logger.logger.error("Company name mis-matched. {0} :: {1}".format(company_names, interaction['company_name']))

        # Meeting type from interactioncondensed table.
        fails += self._match_string(attendees[0][15], interaction['meeting_type'], "Meeting type") \
            if interaction.has_key('meeting_type') else 0

        return fails

    def _validate_miscellanous(self, interaction, eventId, dbh=None):
        """
        Compare the one's which are not covered above.
        :param interaction:
        :param eventId:
        :param dbh:
        :return:
        """
        fails = 0
        if not (dbh or interaction or eventId):
            fails += 1
            return fails

        # Investor Name - interaction[0]
        # Critical Errors / Reject reason - interaction[2]

        return fails