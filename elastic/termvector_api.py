# $ind"1993692/_termvectors?pretty=true" -d '{"fields": ["abstract"], "offsets":false,"payloads":false,"positions":false}'
import requests
import json


class TermVectorAPI:

    def __init__(self, base_url):
        """
        :param base_url: http://localhost:9200
        :return:
        """
        self.base_url = base_url
        if self.base_url[-1] == '/':
            self.base_url = self.base_url[:-1]

    def get_term_vector_url(self, index, doc_type, doc_id):
        """
        Get url for sending search request. If index is
        :param index: name of one index
        :param doc_type: name of one doc type
        :param doc_id: id of document
        :return:
        """
        return '/'.join([self.base_url, index, doc_type, str(doc_id), '_termvectors'])

    def get_term_vector(self, index, doc_type, doc_id):
        """
        :param index: name of one index
        :param doc_type: name of one doc type
        :param doc_id: id of document
        :return:
        """
        query_url = self.get_term_vector_url(index, doc_type, doc_id=doc_id)
        response_json = requests.post(query_url, data=json.dumps({
            'fields': ['abstract'],
            'offsets': False,
            'payloads': False,
            'positions': False,
        })).json()['term_vectors']['abstract']['terms']
        result = {}
        for term in response_json:
            result[term] = response_json[term]['term_freq']

        return result

if __name__ == '__main__':
    from settings import INDEX_NAME, DOCUMENT_TYPE
    api = TermVectorAPI('http://localhost:9200')
    print(api.get_term_vector(INDEX_NAME, DOCUMENT_TYPE, 1993692))