import requests


class SearchAPI:

    def __init__(self, base_url):
        """
        :param base_url: http://localhost:9200
        :return:
        """
        self.base_url = base_url
        if self.base_url[-1] == '/':
            self.base_url = self.base_url[:-1]

    def get_search_url(self, index=None, doc_type=None):
        """
        Get url for sending search request. If index is
        :param index: name of one index or list of index names
        :param doc_type: name of one doc type or list of doctypes
        :return:
        """
        url_parts = [self.base_url]
        if index:
            if type(index) == list:
                index = ','.join(index)
            url_parts.append(index)

            if doc_type:
                if type(doc_type) == list:
                    doc_type = ','.join(doc_type)
                url_parts.append(doc_type)
        elif doc_type:
            raise Exception('Cannot search in a given type without knowing index name. yet.')

        url_parts.append('_search')

        return '/'.join(url_parts)

    def search(self, query, index=None, doc_type=None, size=1000):
        """
        :param query: A dictionary of query in fields
        :param index: name of one index or list of index names
        :param doc_type: name of one doc type or list of doctypes
        :param size: number of top docs returned. size of hits array in response
        :return: {took: 69, hits: { "total": 15, "hits": [{...}]} }
        """

        base_url = self.get_search_url(index, doc_type)
        query_string_items = []
        if type(query) != dict:
            query = {
                'abstract': query,
                'title': query,
            }
        for k,v in query.items():
            query_string_items.append('{}:{}'.format(k,v))

        query_string = ' <OR> '.join(query_string_items)
        query_url = '{}?q={}&size={}'.format(base_url, query_string, size)
        alpha = 0.8
        score_function = "(_score*{})+(_source.pageRank*100*{})".format(alpha, 1.0 - alpha)
        response_json = requests.post(query_url, json={
            "track_scores": True,
            "sort": {
                "_script": {
                    "type": "number",
                    "order": "desc",
                    "script": {"inline": score_function}
                }
            }
        }).json()
        return response_json
