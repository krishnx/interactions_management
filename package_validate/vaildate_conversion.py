import ConfigParser, os, datetime, argparse, re
from file_parser import ParseFile
from logger_mod import Logger
from dao import DAO
from validate import Validate
from validate_header import ValidateHeader

class DataToXML(Validate):
    """
    Prepare the XML content from the data retrieved from the input file.
    """
    def __init__(self, file, template, mapper, d):
        self.file = file
        self.template = template
        self.mapper = mapper
        self.d = d
        # super(DataToXML, self).__init__(params)

    def prepare_xml(self, content):
        """
        Iterate over the content and prepare the XML file.
        :param content: data from input file.
        :return: file path.
        """
        xml = {
            'clientinteraction': {
                'interactions': {
                    'investor': {
                        'investorName': '<investorName>' + content[0][0] + '</investorName>',
                        'all_interactions': [],
                    }
                },
                'updated': '<datetime>' + str(datetime.datetime.now()) + '</datetime><timezone>UTC</timezone>',
                'broker' : '<broker>KrishnX</broker>'
            }
        }

        interaction = {}
        for row in content:
            row = [i.strip() for i in row]
            if interaction.has_key(row[1]):
                interaction[row[1]]['brokerParticipants'].append(self._get_participants_attendies({
                    'firstName': row[25],
                    'lastName': row[26],
                    'email': row[27],
                    'title': row[28],
                    'roles': row[29]
                }, "broker"))
                interaction[row[1]]['investorParticipants'].append(self._get_participants_attendies({
                    'firstName': row[38],
                    'lastName': row[39],
                    'email': row[40],
                    'title': row[41],
                    'roles': row[42],
                    'status': row[43]
                }, "investor"))
                interaction[row[1]]['companies'].append(self._get_company_participants({
                    'companyName': row[17],
                    'identifiers': row[18],
                    'firstName': row[19],
                    'lastName': row[20],
                    'email': row[21],
                    'title': row[22],
                    'roles': row[23],
                    'status': row[24]
                }))
                interaction[row[1]]['thirdPartyParticipants'].append(self._get_participants_attendies({
                    'firstName': row[30],
                    'lastName': row[31],
                    'email': row[32],
                    'title': row[33],
                    'roles': row[34],
                    'company': row[35],
                    'bio': row[36],
                    'status': row[37]
                }, "thirdParty"))
                interaction[row[1]]['sectors'].append(self._get_sectors(row[12]))
                interaction[row[1]]['tags'].append(self._get_interaction_tag(row[44]))
            else:
                interaction[row[1]] = {}
                interaction[row[1]]['interactionID'] = self.__get_field_tag(row[1], "interactionID")
                interaction[row[1]]['interactionType'] = self.__get_field_tag(
                    self.__to_corpaxe(row[2], "EventType"),
                    "interactionType")
                interaction[row[1]]['interactionSubType'] = self.__get_field_tag(
                    self.__to_corpaxe(row[3], "MeetingType"),
                    "interactionSubType")
                interaction[row[1]]['interactionTitle'] = self.__get_field_tag(row[4], "interactionTitle")
                interaction[row[1]]['investorInteractionStatus'] = self.__get_field_tag(
                    self.__to_corpaxe(row[5], "Status"),
                    "investorInteractionStatus")
                interaction[row[1]]['start'] = self._get_date(row[6], "start", "%M/%d/%Y")
                interaction[row[1]]['startTime'] = self._get_time(row[6], row[7], "start")
                interaction[row[1]]['end'] = self._get_date(row[8], "end", "%M/%d/%Y")
                interaction[row[1]]['endTime'] = self._get_time(row[8], row[9], "end")
                if self.template == 'corpaxe':
                    interaction[row[1]]['duration'] = self.__get_field_tag("30", "duration")
                interaction[row[1]]['group'] = self.__get_field_tag(row[10], "group")
                interaction[row[1]]['originatingRegion'] = self._get_originating_region(row[11])
                interaction[row[1]]['location'] = self._get_location(row[13:17])
                interaction[row[1]]['sectors'] = [self._get_sectors(row[12])]
                interaction[row[1]]['brokerParticipants'] = [self._get_participants_attendies({
                    'firstName': row[25],
                    'lastName': row[26],
                    'email': row[27],
                    'title': row[28],
                    'roles': row[29]
                }, "broker")]
                interaction[row[1]]['investorParticipants'] = [self._get_participants_attendies({
                    'firstName': row[38],
                    'lastName': row[39],
                    'email': row[40],
                    'title': row[41],
                    'roles': row[42],
                    'status': row[43]
                }, "investor")]
                interaction[row[1]]['companies'] = [self._get_company_participants({
                    'companyName': row[17],
                    'identifiers': row[18],
                    'firstName': row[19],
                    'lastName': row[20],
                    'email': row[21],
                    'title': row[22],
                    'roles': row[23],
                    'status': row[24]
                })]
                interaction[row[1]]['thirdPartyParticipants'] = [self._get_participants_attendies({
                    'firstName': row[30],
                    'lastName': row[31],
                    'email': row[32],
                    'title': row[33],
                    'roles': row[34],
                    'company': row[35],
                    'bio': row[36],
                    'status': row[37]
                }, "thirdParty")]
                interaction[row[1]]['tags'] = [self._get_interaction_tag(row[44])]
        # TODO: readership, interactionDescription, source, initiator, region, comment

        for intrxn in interaction:
            temp = []
            for entity in interaction[intrxn]:
                if (entity.endswith('articipants') or entity in ['companies', 'sectors', "tags"]) and isinstance(interaction[intrxn][entity], list):
                    # If the first element itself is None, that means no sector value was present in the XL.
                    if not interaction[intrxn][entity][0]:
                        interaction[intrxn][entity] = "<{0}/>".format(entity)
                    else:
                        interaction[intrxn][entity] = "<{0}>{1}</{0}>".format(entity, os.linesep.join(interaction[intrxn][entity]))
                temp.append(interaction[intrxn][entity])
            interaction[intrxn] = os.linesep.join(temp)

        xml['clientinteraction']['interactions']['investor']['all_interactions'] = [
            "<{0}>{1}</{0}>".format("interaction", interaction[ele]) for ele in interaction
            ]

        return xml

    def _write_to_file(self, xml, filename):
        if not xml:
            Logger.logger.error("Blank xml received.")
            return

        with open(filename, 'w') as jhol:
            jhol.write(self._to_string(xml))

    def __to_corpaxe(self, data, what):
        result = ""
        if self._inspect_blank(data, what):
            return result

        for key_tup in self.mapper[what]:
            if data in key_tup:
                result = self.mapper[what][key_tup][0]

        return result

    def _to_string(self, xml):
        result = ""
        for x in xml:
            if isinstance(xml[x], dict):
                result += "<{0}>{1}</{0}>".format(x, self._to_string(xml[x]))
            elif isinstance(xml[x], list):
                if x == 'all_interactions':
                    result += os.linesep.join(xml[x])
                else:
                    result += "<{0}>{1}</{0}>".format(x, os.linesep.join(xml[x]))
            else:
                try:
                    result += xml[x]
                except TypeError:
                    result += str(xml[x])

        return result

    def _get_interaction_tag(self, data):
        if self._inspect_blank(data, "interaction tag"):
            return

        result = filter(None, [ent.strip() for ent in re.split(r'[\s;,|]+', data)])
        return os.linesep.join(["<tag>{0}</tag>".format(tag) for tag in result])

    def _change_date_format(self, data, form='%Y-%M-%d'):
        if self._inspect_blank(data, "date"):
            return
        return datetime.datetime.strptime(data, form).strftime('%d-%M-%Y')

    def _get_date(self, data, what, form='%Y-%M-%d'):
        if self._inspect_blank(data, "date"):
            return """
                <{0}/>
            """.format(what)

        return """
        <{0}>{1}</{0}>
        """.format(what, datetime.datetime.strptime(data, form).strftime('%Y-%M-%d'))

    def _get_time(self, date_str, time_str, what):
        if self._inspect_blank(date_str, "date string") or self._inspect_blank(time_str, "time str"):
            return """
            <{0}Time>
                <datetime/>
                <timezone/>
            </{0}Time>
            """
        dMY_date = self._change_date_format(date_str, "%M/%d/%Y")
        result = self._epoch_convertor(dMY_date, time_str.strip())
        return """
        <{0}Time>
            <datetime>{1}</datetime>
            <timezone>UTC</timezone>
        </{0}Time>
        """.format(what, result)

    def _get_originating_region(self, data):
        if self._inspect_blank(data, "originating region"):
            return """
                <originatingRegion/>
            """

        return """
            <originatingRegion>{0}</originatingRegion>
        """.format(data)

    def __get_resolved_country(self, data):
        if self._inspect_blank(data, "country name"):
            return """
                <country/>
            """

        query = "select Name from Country where Code3 like '{0}' or Code like '{0}'".format(data, data[:2])
        resolved_name = self.d.execute_query(query)[0][0]

        return """
            <country>{0}</country>
        """.format(resolved_name)

    def __get_resolved_city(self, data, country):
        if self._inspect_blank(data, "City"):
            return """
                <city/>
            """
        query =  "select CountryId from Country where Name like '{0}'".format(country)
        country_id = self.d.execute_query(query)
        query = "select Name from City where (Code = '{0}' or Name = '{0}')".format(data)
        if len(country_id) > 0:
            query += " and CountryId = {0}".format(country_id[0][0])
        resolved_name = self.d.execute_query(query)

        if len(resolved_name) < 1:
            return """
                <city/>
            """

        return """
            <city>{0}</city>
        """.format(resolved_name[0][0])

    def __get_resolved_state(self, data):
        if self._inspect_blank(data, "state"):
            return "<state/>"

        result = self.d.execute_query("select Name from Region where Code like '{0}'".format(data))
        if len(result) < 1:
            return "<state/>"

        return """
            <{0}>{1}</{0}>
        """.format("state", result[0][0])

    def __get_resolved_addresstype(self, data):
        if self._inspect_blank(data, "addressType"):
            return """
                <type>N/A</type>
            """
        result = self.__to_corpaxe(data, "LocationType")

        return """
            <type>{0}</type>
        """.format(result)

    def __get_resolved_blah(self, data, what):
        # Please do something here. :|
        if self._inspect_blank(data, "blah for now"):
            return """
                <{0}/>
            """.format(what)

        return """
            <{0}>{1}</{0}>
        """.format(what, data)

    def _get_location(self, data):
        if len(data) < 1:
            return """
                <location>
                    <address>
                        <type/>
                        <streetAddress/>
                        <city/>
                        <state/>
                        <country/>
                    </address>
                </location>
            """

        address_type = self.__get_resolved_addresstype("lol")
        street_address = self.__get_field_tag(data[0], "streetAddress")
        state = self.__get_resolved_state(data[2])
        country = self.__get_resolved_country(data[3])
        city = self.__get_resolved_city(data[1], re.sub(r'<[^>]+>', '', country).strip())

        return """
            <location>
                <address>
                    {0}{1}{2}{3}{4}
                </address>
            </location>
        """.format(address_type, street_address, city, state, country)

    def _get_sectors(self, data):
        if self._inspect_blank(data, "sector"):
            return

        result = filter(None, [ent.strip() for ent in re.split(r'[\s;,|]+', data)])
        return os.linesep.join(["<sector>{0}</sector>".format(sec) for sec in result])

    def __get_field_tag(self, data, what):
        if self._inspect_blank(data, what):
           return """
                <{0}/>
           """.format(what)
        return """
            <{0}>{1}</{0}>
        """.format(what, data)

    def _get_participants_attendies(self, data, what):
        # if self._inspect_blank(data, what + " pariticipants"):
        if len(data) < 1:
            return

        person = []
        for entity in data:
            if entity == 'roles' or entity == 'status':
                continue
            person.append(self.__get_field_tag(data[entity], entity))

        roles = os.linesep.join(
            ["<role>{0}</role>".format(self.__to_corpaxe(role, "Roles"))
             for role in filter(None, re.split(r'[,|\s;]+', data['roles']))
             ]
        )

        return """
            <participant>
                <person>
                    {0}
                </person>
                <roles>
                    {1}
                </roles>
                <status>{2}</status>
            </participant>
        """.format(os.linesep.join(person), roles, self.__to_corpaxe(data['status'], "Status") if data.has_key('status') else "")

    def _get_company_participants(self, data):
        # if self._inspect_blank(data, "company participants"):
        if len(data) < 1:
            return """
                <companies>
                    <company/>
                </companies>
            """
        participants_data = {}
        for entity in data:
            if entity == 'identifiers' or entity == 'companyName':
                continue
            participants_data[entity] = data[entity]

        company_participants = self.__get_field_tag(
            self._get_participants_attendies(participants_data, "company"),
            "companyParticipants"
        )

        return """
            <company>
                <companyName>{0}</companyName>
                <isPublic>{1}</isPublic>
                {2}
            </company>
        """.format(data['companyName'], data['identifiers'], company_participants)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-fn", "--filename",
                        type=str,
                        required=True,
                        help="The full file path with name which would be uploaded")
    parser.add_argument("-t", "--template",
                        type=str,
                        required=True,
                        help="the template format of the file.",
                        choices=["corpaxe",
                                 "markit",
                                 "markit(capital group)",
                                 "markit(blackrock)",
                                 "a2dealogic",
                                 "oneaccess",
                                 "bloomberg",
                                 "commcise"])
    args = parser.parse_args()
    if not (isinstance(args.template, str) and isinstance(args.filename, str)):
        parser.print_help()
        raise Exception("Invalid parameter(s).")

    config = ConfigParser.ConfigParser()
    config.read('config.ini')

    conn_string = ";".join([ele + "=" + config.get("MSSQL_DB_CONFIG_QA", ele.lower()) for ele in
                            ["DRIVER", "SERVER", "DATABASE", "UID", "PWD"]])
    d = DAO(conn_string)

    fp = ParseFile("xlsx", args.filename)
    content = fp.parse_file()

    mappings_file = ParseFile("xml", "/home/vauser/Project/fe_tc/files_oa/mappings/corpaxe/CorpAxeToOATypeRules.xml")
    mapping_content = mappings_file.parse_file()


    vh = ValidateHeader(content[0], args.template)
    if vh.is_file_valid():
        dx = DataToXML(args.filename, args.template)
        xml = dx.prepare_xml(content[1:])
        dx._write_to_file(config.get("XML", "dest"))
        Logger.logger.info("Done")
    else:
        Logger.logger.error("File does not comply with the template.")