import re
import sys

from igit.util import shell
from more_termcolor import colors


class Repo:
    _url = ''
    _weburl = ''
    _host = ''
    _name = ''
    
    @property
    def url(self) -> str:
        if not self._url:
            self._url = shell.runquiet('git remote get-url origin')
        return self._url
    
    @property
    def host(self) -> str:
        if not self._host:
            if 'bitbucket' in self.url:
                self._host = 'bitbucket'
            elif 'github' in self.url:
                self._host = 'github'
            else:
                raise NotImplementedError(f"repo.weburl: not github nor bitbucket. {self.url}")
        return self._host
    
    @property
    def weburl(self) -> str:
        """bitbucket.org/cashdash/reconciliation-testing-tools"""
        if not self._weburl:
            
            isbitbucket = self.host == 'bitbucket'
            if isbitbucket:
                regex = r'bitbucket.org.*(?=\.git)\b'
            elif self.host == 'github':
                regex = r'github.com.*(?=\.git)\b'
            else:
                print(colors.yellow(f'repo.weburl unspecific self.host: {self.host}'))
                regex = fr'{self.host}.com.*(?=\.git)\b'
            match = re.search(regex, self.url)
            if not match:
                sys.exit(colors.red(f"regex: {regex} no match to self.url: '{self.url}'"))
            weburl = match.group()
            if isbitbucket and ':cashdash' in self.url:
                weburl = weburl.replace(':cashdash', '/cashdash')
            self._weburl = weburl
        return self._weburl
    
    @property
    def name(self) -> str:
        if not self._name:
            regex = r'(?<=/)[\w\d.-]*(?=\.git)'
            match = re.search(regex, self.url)
            if not match:
                sys.exit(colors.red(f"regex: {regex} no match to self.url: '{self.url}'"))
            self._name = match.group()
        return self._name
