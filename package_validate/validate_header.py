import ConfigParser, os
from file_parser import ParseFile
from logger_mod import Logger

class ValidateHeader(object):
    """
    Validate the headers of the file with the template.
    """
    def __init__(self, file_headers, template):
        """
        Initialize the object with <params>
        :param file_headers: file's headers.
        :param template: corpaxe/
                         markit/
                         markit(capital group)/
                         markit(blackrock)/
                         a2dealogic/
                         oneaccess/
                         bloomberg/
                         commcise
        """
        self.file_headers = file_headers
        self.template = template

    def _get_template_header(self):
        """
        Read the template's headers
        :return: template headers
        """
        config = ConfigParser.ConfigParser()
        config.read("config.ini")

        if self.template.lower() == 'markit(capital group)':
            _path = os.path.join(config.get("BASE", "base_dir_path"), "files_oa/standard_templates", "markit",
                                 "template_capital_group.xlsx")
        elif self.template.lower() == 'markit(blackrock)':
            _path = os.path.join(config.get("BASE", "base_dir_path"), "files_oa/standard_templates", "markit",
                                 "template_blackrock.xlsx")
        else:
            _path = os.path.join(config.get("BASE", "base_dir_path"), "files_oa/standard_templates", self.template.lower(),
                                 "template.xlsx")

        fp = ParseFile("xlsx", _path)
        return fp.parse_file()

    def is_file_valid(self):
        """
        Compare the file with the template and return status
        :return: bool (status)
        """

        if len(self.file_headers) < 1:
            Logger.logger.error("File headers are invalid")
            return False
        else:
            return self.file_headers == self._get_template_header()[0]