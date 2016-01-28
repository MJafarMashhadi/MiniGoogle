__author__ = 'mjafar'


class Author:
    def __init__(self, data):
        self.name = data['name']
        self.id = data['id']
        self.papers = data['papers']

    def get_papers(self):
        return self.papers
