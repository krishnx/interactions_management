import xml.etree.ElementTree as ET

class Mapper(object):
    def __init__(self, file_path):
        self.file_path = file_path

    def get_mapping_content(self):
        tree = ET.parse(self.file_path)
        root = tree.getroot()
        result = {}
        for item in root.findall('OneWayMapper'):

            # empty news dictionary
            result[item.attrib['Name']] = {}
            for b in item.findall('./BundleMap'):
                from_tup = []
                to_tup = []
                for fs in b.findall('./From/string'):
                    from_tup.append(fs.text)
                for ts in b.findall('./To/string'):
                    to_tup.append(ts.text)
                result[item.attrib['Name']][tuple(from_tup)] = to_tup

        return result