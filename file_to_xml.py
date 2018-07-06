from dao import DAO
from logger_mod import Logger
import argparse, ConfigParser, os
from file_parser import ParseFile
from package_validate.validate_header import ValidateHeader
from package_validate.vaildate_conversion import DataToXML
from package_validate.validate_xml import Validate
from mappings import Mapper

if __name__ == '__main__':
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
    parser.add_argument("-o", "--org_id",
                        type=int,
                        help="The Sell side org id",
                        required=True)

    try:
        args = parser.parse_args()
    except:
        Logger.logger.error(parser.print_help())
        exit(0)

    if not (isinstance(args.template, str) and isinstance(args.filename, str) and os.path.exists(args.filename)):
        parser.print_help()
        raise Exception("Invalid parameter(s).")

    if args.template.lower() == 'markit(capital group)':
        template = "markit_cg"
    elif args.template.lower() == 'markit(blackrock)':
        template = "markit_blackrock"
    else:
        template = args.template.lower()

    config = ConfigParser.ConfigParser()
    config.read('config.ini')

    conn_string = ";".join([ele + "=" + config.get("MSSQL_DB_CONFIG_QA", ele.lower()) for ele in
                            ["DRIVER", "SERVER", "DATABASE", "UID", "PWD"]])
    d = DAO(conn_string)

    fp = ParseFile("xlsx", args.filename)
    content = fp.parse_file()

    vh = ValidateHeader(content[0], args.template)
    if vh.is_file_valid():

        mapping_content_fp = os.path.join(config.get("BASE", "base_dir_path"),
                                       config.get("CLIENTS_RULES", template))
        mapper = Mapper(mapping_content_fp).get_mapping_content()

        dx = DataToXML(args.filename, args.template, mapper, d)
        xml = dx.prepare_xml(content[1:])
        xml_file = config.get("XML", "dest")
        dx._write_to_file(xml, xml_file)
        xml_content = ParseFile("xml", xml_file).parse_file()

        vld = Validate({'file_name': args.filename.split(os.sep)[-1],
                       'file_content': xml_content,
                       'org_id': args.org_id}, conn_string)
        if vld.validate_content():
            Logger.logger.info("Success")
        else:
            Logger.logger.info("Failed")
        Logger.logger.info("Done")
    else:
        Logger.logger.error("File does not comply with the template.")