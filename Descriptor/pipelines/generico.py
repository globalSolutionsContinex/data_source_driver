# ----------------------------------------------------------------------------------------------------
#
# Welcome to generico descriptor
# this descriptor updates prices and stock
# Autor: Stevenson Contreras
#
# ----------------------------------------------------------------------------------------------------
#
# Basic structure for canonical_descriptor
# 'attribute':{
#        'columns_file_descriptor': ['price'],
#        'columns_pattern': '{}',
#        'rules': [{
#                'lamb_func': lambda x,y: x= 10+y
#            }
#        ],
#        'default': 0
#  }

data_descriptor = {
    'name': 'master',
    'name_pattern': '',
    'info_type': 'csv',
    'encode': 'latin-1',
    'delimiter': ';',
    'retailer_id': '*',
    'headers': True,
    'method': 'upsert_method'
}

channel_descriptor = {
        'connection': 's3',
        'backup': False,
        'dir_path': 'files/',
        'processed_path': 'files_processed/'
}

file_descriptor = {}
