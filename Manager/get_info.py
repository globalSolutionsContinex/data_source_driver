import csv


class FileInfoExtractor:

    def __init__(self, descriptor):
        self.descriptor = descriptor
        self.CSV = 'csv'
        self.PLAIN = 'plain'

    def process_file(self, file_name):
        product_list = []
        product_error_list = []
        if self.descriptor.data_descriptor['info_type'] is self.CSV:
            self.generate_product_list(file_name, self.descriptor.data_descriptor['encode'], self.get_csv_reader, self.get_csv_row, product_list, product_error_list )
        elif self.descriptor.data_descriptor['info_type'] is self.PLAIN:
            self.generate_product_list(file_name, self.descriptor.data_descriptor['encode'], self.get_plain_txt_reader, self.get_plain_text_row, product_list, product_error_list)
        return [product_list, product_error_list]

    def get_csv_reader(self, file):
        return csv.reader(file, delimiter=self.descriptor.data_descriptor['delimiter'])

    @staticmethod
    def get_csv_row(line, value, row, key):
            row[key] = str(line[value[0]].strip())

    @staticmethod
    def get_plain_txt_reader(file):
        return file

    @staticmethod
    def get_plain_text_row(line, value, row, key):
        if value[2] is 'N':
            row[key] = int(line[value[0]:value[1]].strip())
        else:
            row[key] = line[value[0]:value[1]].strip()

    def generate_product_list(self, file_name, enconding, reader, get_row, product_list, product_error_list):
        num_line = 1
        with open(file_name, 'r', encoding=enconding) as file:
            file_reader = reader(file)
            for line in file_reader:
                if len(line) == 0:
                    product_error_list.append([num_line, "linea vacia"])
                elif self.descriptor.data_descriptor['headers'] and num_line == 1:
                    self.generate_file_descriptor(line)
                else:
                    row = {}
                    for key, value in self.descriptor.file_descriptor.items():
                        try:
                            get_row(line, value, row, key)
                        except Exception as ex:
                            product_error_list.append([num_line, line, row, str(ex), key, value])
                            row = {}
                            break
                    if bool(row):
                        product_list.append(row)
                num_line += 1

    def generate_file_descriptor(self, line):
        self.descriptor.file_descriptor = {}
        for i, value in enumerate(line):
            self.descriptor.file_descriptor[value] = (i, 'A')
