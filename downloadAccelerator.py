import argparse
import os
import requests
import threading
import time

''' Downloader for a set of files '''
class Downloader:
    def __init__(self):
        ''' initialize the file where the list of URLs is listed, and the
        directory where the downloads will be stored'''
        self.args = None
        self.url = None
        self.threadNum = None
        self.fileName = None
        self.parse_arguments()

    def parse_arguments(self):
        ''' parse arguments, which include '-n' for number of threads'''
        parser = argparse.ArgumentParser(prog='Download Accelerator', description='A simple script that downloads a urls content using multiple threads', add_help=True)
        parser.add_argument('url', type=str, help='Specify the url you wish to use')
        parser.add_argument('-n', '--threads', type=int, action='store', help='Specify the number of threads you would like to use',default=10)
        args = parser.parse_args()
        self.url = args.url
        self.threadNum = args.threads
        self.fileName = self.getFileName(self.url)

        #print 'url: %s' % self.url
        #print 'threadNum: %d' % self.threadNum
        #print 'fileName: %s' % self.fileName

    def getFileName(self, url):
        fileName = 'index.html'

        if not url[-1] == '/':
            parsedUrl = url.split('/')
            fileName = parsedUrl[-1]

        return fileName

    def download(self):
        ''' download the file within the url '''
        r = requests.head(self.url)

        # find out the content-length based on the url.
        contentLength = int(r.headers['content-length'])
        #print 'contentLength: %d' % contentLength

        # split based on the number of threads
        bytesToDownload = contentLength / self.threadNum
        #print 'bytesToDownload: %d' % bytesToDownload

        beg_index = 0
        end_index = bytesToDownload - 1

        # create threads
        threads = []

        for x in xrange(self.threadNum):
            #print 'Starting index: %d. Ending Index: %d' % (beg_index, end_index)

            range_string = ""

            if x == self.threadNum - 1:
                range_string = 'Bytes=%d-' % beg_index
                #print 'Reached last thread.  range_string: %s' % range_string
            else:
                range_string = 'Bytes=%d-%d' % (beg_index, end_index)
                #print 'range_string: %s' % range_string

            d = DownThread(self.url, range_string)
            threads.append(d)

            beg_index = end_index + 1
            end_index += bytesToDownload

        for t in threads:
            t.start()

        elapsedTime = 0.0
        outFile = open(self.fileName, 'wb')
        for t in threads:
            time1 = time.time()

            t.join()
            outFile.write(t.dataReceived)

            time2 = time.time()
            elapsedTime = time2 - time1

        print '%s %d %d %f' % (self.url, self.threadNum, contentLength, elapsedTime)

''' Use a thread to download one file given by url and stored in filename'''
class DownThread(threading.Thread):
    def __init__(self,url,range_string):
        self.url = url
        self.range_string = range_string
        self.dataReceived = None
        threading.Thread.__init__(self)
        #self._content_consumed = False


    def run(self):
        headers = {'Range': self.range_string}

        #Downloading a specific range of bytes
        r = requests.get(self.url, headers=headers)

        # Save dataReceived on the object
        self.dataReceived = r.content
 
if __name__ == '__main__':
    d = Downloader()
    d.download()
