import ConfigParser
import argparse
import os, re

from selenium import webdriver, common

from package_upload.upload_file import UploadFile
from package_validate.validate_xml import Validate as V_XML
from package_validate.validate_xlsx import Validate as V_XL
from file_parser import ParseFile
from logger_mod import Logger
from mail_mod import Mailer

if __name__ == '__main__':
    config = ConfigParser.ConfigParser()
    config.read('config.ini')

    parser = argparse.ArgumentParser(prog=os.path.basename(__file__),
                                     usage='%(prog)s [-o ORG_ID -fn <path_to_file> [-ct {"Interaction", "Readership"}] [-u {0 to compare the data points from the file with the db, 1 to package_upload the file and then compare with db}]]')
    parser.add_argument("-o", "--org_id",
                        type=int,
                        help="The Sell side org id",
                        required=True)
    parser.add_argument("-fn", "--filename",
                        type=str,
                        help="name of the file to be uploaded",
                        required=True)
    parser.add_argument("-ct", "--content_type",
                        type=str,
                        help="Content type. Either Interaction or Readership. Default is Interaction.",
                        nargs='?',
                        const="Interaction",
                        choices=['interaction', 'readership'],
                        default="Interaction")
    parser.add_argument("-u", "--upload",
                        type=int,
                        help="1 to package_upload the specified file, 0 to compare the file's data with Database, default is 0.",
                        nargs='?',
                        const=0,
                        choices=[0,1],
                        default=0)
    args = parser.parse_args()

    # package_validate the file extension
    file_ext = args.filename.split('.')[-1].lower()
    file_ext_pat = re.compile(r'^(xlsx?|xml|csv)$', re.IGNORECASE)
    if not (re.match(file_ext_pat, file_ext) and
                isinstance(args.org_id, int) and
                isinstance(args.filename, str)):
        parser.print_help()
        raise Exception('invalid parameters.')

    # Verify the file path
    file_path = os.path.join(config.get("BASE", "base_dir_path"), args.filename)
    if not (os.path.exists(file_path) and os.path.isfile(file_path)):
        raise Exception("Invalid file path. {0}".format(file_path))

    Logger.logger.info('Starting the test case.')
    Logger.logger.debug('''with params:
        org_id: {0}
        filename: {1}
        content_type: {2}'''.format(args.org_id, args.filename, args.content_type))

    # package_upload file from GUI
    if args.upload == 1:
        base_url = config.get('BASE', 'base_url').strip()
        browser = webdriver.Chrome()
        try:
            browser.maximize_window()
        except common.exceptions.WebDriverException:
            Logger.logger.warn("Not able to maximize the window size.")
        except:
            Logger.logger.error("Some thing broke.")

        browser.get(base_url + config.get('BASE', 'sellside_dashboard_url').format(args.org_id))

        # Initiate package_upload
        uf = UploadFile(args.org_id, file_path, args.content_type)
        success = uf.upload(browser, config)
    else:
        success = True

    # File parsing and data comparison with DB starts
    if success:
        # Prepare the connection string for DB
        conn_string = ";".join([ele + "=" + config.get("MSSQL_DB_CONFIG_QA", ele.lower()) for ele in
                                ["DRIVER", "SERVER", "DATABASE", "UID", "PWD"]])

        # Parse the file.
        file_content = ParseFile(file_ext, file_path)
        content = file_content.parse_file()
        if len(content) < 1:
            Logger.logger.error("Execution stopped as failed to fetch the content")
            exit(1)

        # package_validate the content.
        if file_ext == 'xlsx' or file_ext == 'xls' or file_ext == 'csv':
            v = V_XL({'file_name': args.filename.split(os.sep)[-1],
                      'file_content': content,
                      'org_id': args.org_id
                      },
                     conn_string)
        elif file_ext == 'xml':
            v = V_XML({'file_name': args.filename.split(os.sep)[-1],
                       'file_content': content,
                       'org_id': args.org_id},
                      conn_string)
        else:
            raise Exception("Invalid file extension. {0}".format(file_ext))

        if v.validate_content():
            Logger.logger.info("Success")
        else:
            Logger.logger.error("Failed")

        mailer = Mailer(
            [config.get("MAILER", "to")],
            config.get("MAILER", "subject"),
            config.get("MAILER", "success_body"),
            files=[file.strip() for file in config.get("MAILER", "attachments").split(",")],
            cc=[cc.strip() for cc in config.get("MAILER", "cc").split(",")],
            bcc=[bcc.strip() for bcc in config.get("MAILER", "bcc").split(",")],
            sender=config.get("MAILER", "sender")
        )
        # Uncomment this before checking-in or mails are not sent via Jenkins: TODO
        # mailer.send_email()
    else:
        Logger.logger.error("Execution stopped as login failed.")