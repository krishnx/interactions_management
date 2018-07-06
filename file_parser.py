import os
from logger_mod import Logger
from json import loads, dumps
import argparse
import ConfigParser
import csv
import xlrd
import xmltodict
# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')

class ParseFile(object):
    def __init__(self, file_type, file_path):
        self.content = []
        self.file_type = file_type
        self.file_path = file_path

    def parse_file(self):
        """
        depending upon the file type, parse and return the content
        :return: parsed file's content
        """
        if self.file_type.lower() == 'xlsx' or self.file_type.lower() == 'xls':
            content = self._parse_xlsx()
        elif self.file_type.lower() == 'csv':
            content = self._parse_csv()
        else:
            content = self._parse_xml()

        return content
            
    def _parse_xlsx(self):
        """
        parse the XLSX file.
        TODO: Check if xls file can be parsed with this utility or not.
        :return: parsed file's content in array format
        """
        book = xlrd.open_workbook(self.file_path)
        sheet = book.sheets()[0]
        rows = []
        offset = -1
        for i, row in enumerate(range(sheet.nrows)):
            if i <= offset:  # (Optionally) skip headers
                continue
            r = []
            for j, col in enumerate(range(sheet.ncols)):
                try:
                    r.append(str(sheet.cell_value(i, j)).encode("utf-8", "ignore"))
                except UnicodeEncodeError:
                    r.append(sheet.cell_value(i, j).encode('ascii', 'ignore').decode('ascii'))
                except:
                    r.append(str(sheet.cell_value(i, j)))

            rows.append(r)

        Logger.logger.debug("Parsed the {0} file: {1}".format(self.file_type, self.file_path))
        return rows
        
    def _parse_csv(self):
        """
        Parse the CSV file
        :return: parsed file's content in array format
        """
        rows = []
        with open(self.file_path, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if isinstance(row, str):
                    # note: this removes the character and encodes back to string.
                    row = row.decode('ascii', 'ignore').encode('ascii')
                elif isinstance(row, unicode):
                    row = row.encode('ascii', 'ignore')
                rows.append(row)

        Logger.logger.debug("Parsed the {0} file: {1}".format(self.file_type, self.file_path))
        return rows[1:]

    def _parse_xml(self):
        """
        Parse the XML file. By default,
        :return: parsed file's content in dictionary format.
        """
        with open(self.file_path) as fd:
            doc = fd.read()

        Logger.logger.debug("Parsed the {0} file: {1}".format(self.file_type, self.file_path))
        return loads(dumps(xmltodict.parse(doc)))


if __name__ == "__main__":

    config = ConfigParser.ConfigParser()
    config.read('config.ini')

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--type", type=str, help="The file type either, XLSX or CSV or XML.", required=True)
    parser.add_argument("-fn", "--filename", type=str, help="name of the file to be uploaded", required=True)
    args = parser.parse_args()
    
    base_dir_path = config.get('BASE', 'base_dir_path').strip()
    file_path = os.path.join(base_dir_path, args.filename)
    if not (os.path.exists(file_path) or args.type.lower() == 'xslx' or args.type.lower() == 'csv' or args.type.lower() == 'xml'):
        parser.print_help()
        raise Exception('invalid parameters.')

    file_parser = ParseFile(args.type, file_path)
    content = file_parser.parse_file()
    for ele,val in content.iteritems():
        print ele, val