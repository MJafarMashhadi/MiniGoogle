__author__ = 'mjafar'


class Node:
    authors = []
    articles = []
    parent = None
    similarity_value = 0

    def __init__(self, param1, param2=None, similarity=0):
        """
        Two ways of initializing,
          1. for leaf nodes, pass one author and leave second parameter
          2. for merge nodes, pass two nodes
        :param authors:
        :param node2:
        :return:
        """
        if param2:
            # Merge two nodes
            self.authors = param1.authors | param2.authors
            # from functools import reduce
            # self.articles = reduce(lambda x,y: x|y, (set(a.get_papers()) for a in authors))
            self.articles = param1.articles | param2.articles
            param1.parent = param2.parent = self
            self.children = (param1, param2)
            self.similarity_value = similarity
        else:
            # Leaf node
            self.authors = {param1}
            self.articles = set(param1.get_papers())
            self.children = None

    def similarity(self, node):
        return len(self.articles & node.articles)

    def get_similarity_ratio(self):
        return self.similarity_value * 100.0 / len(self.articles)

    def __str__(self):
        if not self.children:
            author_ = self.authors.pop()
            return 'Node <author={}, |papers|={}>'.format(author_.name, len(author_.papers))
        else:
            return 'Node <similarity={}>'.format(self.similarity_value)


def first(nodes, candidates):
    if type(candidates) != list:
        candidates = list(candidates)
    return candidates[0]


class Dendogram:
    nodes = []
    root_node = None

    def __init__(self, authors):
        if type(authors) != list:
            authors = list(authors)

        self.nodes = [Node(author) for author in authors]

    def cluster(self, choose_function=first):
        nodes = self.nodes.copy()
        while len(nodes) > 1:
            similarities = {}
            for i in range(0, len(nodes)):
                for j in range(i + 1, len(nodes)):
                    similarities.update({(i, j): nodes[i].similarity(nodes[j])})

            max_value = max(similarities.values())
            candidates = filter(lambda key: similarities[key] == max_value, similarities.keys())
            selected_key = choose_function(nodes, candidates)
            i = selected_key[0]
            j = selected_key[1]
            new_node = Node(nodes[i], nodes[j], similarities[selected_key])
            if j < i:
                i, j = j, i

            del nodes[i], nodes[j-1]  # j-1 bara inke hamzaman delete nemikone
            nodes.append(new_node)

        self.root_node = nodes[0]

    def get_clusters(self, min_similarity_measure=0.2):
        """
        Thanks to vahid :-D

        :param min_similarity_measure:
        :return:
        """
        q = [self.root_node]
        clusters = list()
        while len(q) > 0:
            n = q.pop()
            print(n.get_similarity_ratio())
            if n.children:
                if n.get_similarity_ratio() < min_similarity_measure:
                    clusters.append(n)
                else:
                    q += n.children
            else:
                clusters.append(n)

        return clusters



def main():
    from .author import Author
    authors = [
        Author({'name': '', 'papers': [1, 2, 3, 4]}),
        Author({'name': '', 'papers': [4, 5, 6, 7]}),
        Author({'name': '', 'papers': [1, 2, 6, 7]}),
        Author({'name': '', 'papers': [8, 9, 10, 21]}),
        Author({'name': '', 'papers': [2]}),
        Author({'name': '', 'papers': [16, 45, 11]}),
        Author({'name': '', 'papers': [11, 15, 22, 44]}),
        Author({'name': '', 'papers': [12, 22, 32, 42]}),
    ]

    for author in authors:
        author.name = ' '.join(map(str, author.papers))

    d = Dendogram(authors)
    d.cluster()

    q = [d.root_node]
    while len(q) > 0:
        n = q.pop()
        print('Node: ', n)
        if n.children:
            q += list(n.children)

if __name__ == '__main__':
    main()
