__author__ = 'mjafar'


class Author:
    def __init__(self, data):
        self.name = str(data['Name']).strip()
        self.papers = map(lambda pdata: pdata[1] if len(pdata[1]) < len(pdata[0]) else pdata[1], data['Article'])

    def get_papers(self):
        return list(self.papers)
