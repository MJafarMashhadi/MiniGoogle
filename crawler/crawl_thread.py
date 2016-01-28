import threading
import sys


class CrawlThread(threading.Thread):
    def __init__(self, c):
        threading.Thread.__init__(self)
        self.crawler = c

    def run(self):
        while self.crawler.numberOfVisitedPage < self.crawler.n and len(self.crawler.queue) > 0:
            self.crawler.lockQueue.acquire()
            currentURL = self.crawler.queue.pop(0)
            self.crawler.lockQueue.release()
            try:
                self.crawler.crawlPage(currentURL)
                print(self.crawler.numberOfVisitedPage.__str__() + ' : ' + currentURL)
            except:
                print('Error : ' + currentURL)
                print (sys.exc_info())
                with open("retrievedDocs/afterCrawl/ERROR.txt", "a") as ErrorFile:
                    ErrorFile.write(currentURL + '\n')
