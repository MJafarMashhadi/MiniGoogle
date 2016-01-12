import json

import requests
from util import read_file, list_files


class ElasticAPI:

    def __init__(self, base_url, base_folder):
        """
        :param base_url: http://localhost:9200
        :param base_folder: ../retrievedDocs/index/
        :return:
        """
        import os
        self.base_url = base_url
        self.base_folder = os.path.normpath(base_folder)
        if self.base_folder[-1] != '/':
            self.base_folder += '/'
        if self.base_url[-1] == '/':
            self.base_url = self.base_url[:-1]

    def get_index_url(self, index_name, doc_type, doc_id):
        return '/'.join(map(str, [self.base_url, index_name, doc_type, doc_id]))

    def add_document_by_id(self, id, index_name, document_type):
        """
        reads document file from index location.
        :param id:
        :return: tuple <Success(bool), response details(dictionary)>
        """
        file_address = '{}{}.json'.format(self.base_folder, id)
        contents = read_file(file_address)

        if contents is None:
            return (False, None)
        else:
            return self.add_document(contents, index_name, document_type)

    def add_document(self, json_contents, index_name, document_type):
        """
        Add document based on json
        :param json_contents:
        :return: tuple <Success(bool), response details(dictionary)>
        """
        parsed = json.loads(json_contents)
        index_url = self.get_index_url(index_name, document_type, parsed['id'])
        elastic_response = requests.put(index_url, data=json_contents).json()
        return elastic_response['created'], elastic_response

    def bulk_add_documents_in_directory(self, folder, index_name, document_type, pattern='*.json'):
        """
        add documents in directory that their name matches given pattern

        :param folder: directory address
        :param index_name: name of index (e.g. articles)
        :param document_type: type of documents (e.g. paper)
        :param pattern: file name pattern (wildcard). default: *.json
        :return:
        """
        return self.bulk_add_documents_file_list(
            map(lambda name: self.base_folder+name, list_files(folder, pattern=pattern)),
            index_name, document_type)

    def bulk_add_documents_file_list(self, file_names, index_name, document_type):
        """
        add all documnets that their address is given in
        :param file_names:
        :param index_name:
        :param document_type:
        :return:
        """
        contents = filter(lambda x: x is not None, map(read_file, file_names))
        return self.bulk_add(contents, index_name, document_type)

    def bulk_add(self, documents, index_name, document_type):
        """
        Bulk add documents that their content is given.
        :param documents: Document contents in json formatted string.
        :param index_name:
        :param document_type:
        :return:
        """
        documents = map(lambda x: x.replace('\r?\n', ''), documents)
        document_ids = map(lambda js: js['id'], map(json.loads, documents))
        request_data = []
        for document, id in zip(documents, document_ids):
            header = json.dumps({'index': {'_id': id}})
            request_data += [header, document]

        bulk_request = requests.post('/'.join([self.base_url, index_name, document_type, '_bulk']), data='\n'.join(request_data))
        return bulk_request


