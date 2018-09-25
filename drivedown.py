#!/usr/bin/env python3
#Copyright © 2018 Victor Oliveira <victor.oliveira@gmx.com>
#This work is free. You can redistribute it and/or modify it under the
#terms of the Do What The Fuck You Want To Public License, Version 2,
#as published by Sam Hocevar. See the COPYING file for more details.
'''
You provide links, DriveDown provide the files!
With this script, you can download files from Google
Drive using the CLI.
You can use as a library, or a command on terminal.
To download files, you can use Google Drive URL or
file ID directly.
See examples below.

Library:
import drivedown
url = 'https://drive.google.com/file/d/0B1Dx_Xbue-lud1dyOVYxenltems'
o = drivedown.DriveDown(url)
o.download()

Command:
python3 ./drivedown.py 'https://drive.google.com/file/d/0B1Dx_Xbue-lud1dyOVYxenltems'

Changelog:

1.0.1 - Minor fix to print filename when used as command
        Added infomation about file ID
1.0.0 - First release

Enjoy!
'''

from html.parser import HTMLParser
import urllib.request
import urllib.parse
import re

BUFFER_SIZE = 1024 * 8

__author__ = 'Victor Oliveira'
__version__ = '1.0.1'

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.tag = list()
        self.attrib = list()
    def handle_starttag(self, tag, attrib):
        self.tag.append(tag)
        self.attrib.append(attrib)

class DriveDown:
    def __init__(self, url):
        self.url = url
        self.urldirect = self._geturldirect()

    def _getfileid(self):
        '''Return the ID of file based on URL'''
        fileid = re.findall('[\w-]{28}', self.url)[0]
        return fileid

    def _geturldirect(self):
        '''Return direct download link'''
        urldirect = 'https://docs.google.com/uc?id={}'.format(self._getfileid())
        return urldirect

    def _acceptdownload(self):
        '''If the filesize is big, you need to confirm download
        This method does that'''
        self._cookie = self._req.getheader('Set-Cookie')
        html = self._req.read().decode()
        parser = MyHTMLParser()
        parser.feed(html)

        for i in parser.attrib:
            try:
                if 'uc-download-link' in i[0][1]:
                    urldown = i[2][1]
            except IndexError:
                pass

        urldown = urllib.parse.urljoin(self.urldirect, urldown)
        headers = {'Cookie' : self._cookie}

        self._req = urllib.request.Request(urldown, headers=headers)
        self._req = urllib.request.urlopen(self._req)

    def download(self):
        '''Download the file
        Return filename after sucessful download'''
        self._req = urllib.request.urlopen(self.urldirect)

        if not self._req.getheader('Content-Disposition'):
            self._acceptdownload()
        
        content = self._req.getheader('Content-Disposition')

        # Little fix to cut " symbol on filename
        content = ''.join(content.split('"'))

        filename = urllib.parse.parse_qs(content)['filename'][0]

        with open(filename, 'wb') as file:
            while True:
                buffer = self._req.read(BUFFER_SIZE)
                if buffer:
                    file.write(buffer)
                else:
                    break

        return filename

if __name__ == '__main__':
    import sys
    o = DriveDown(sys.argv[1])
    print(o.download())
