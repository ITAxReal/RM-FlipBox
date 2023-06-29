from ABCProvider import ABCProvider
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote


def get_filename(link: str) -> str:
     return link.split('file=', 1)[1]
 
 
class RMPatreon(ABCProvider):
     
     BASE_URL = "https://rogue-master.net/"
     LOGIN_URI = "login.php"
     
     def __init__(self, username: str, password: str) -> None:
          self.sess = requests.Session()
          self.sess.headers = {
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
               'Accept-Language': 'en-US,en;q=0.9',
               'Cache-Control': 'max-age=0',
               'Connection': 'keep-alive',
               'Origin': 'https://rogue-master.net',
               'Referer': 'https://rogue-master.net/?sesh=1',
               'Sec-Fetch-Dest': 'document',
               'Sec-Fetch-Mode': 'navigate',
               'Sec-Fetch-Site': 'same-origin',
               'Sec-Fetch-User': '?1',
               'Upgrade-Insecure-Requests': '1',
               'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
          }
          try:
               self.sess.post(urljoin(self.BASE_URL, self.LOGIN_URI), data={'un': username, 'pw': password, 'Submit': "View Builds"})
               resp = self.sess.get(self.BASE_URL + '?sesh=1')
               if "A password has been emailed to all our Patreon members." in resp.text:
                    self.close()
                    raise RuntimeError("Auth failed")
               if not resp.text:
                    self.close()
                    raise RuntimeError("Something went wrong")               
          except requests.RequestException as e:
               self.close()
               raise requests.RequestException(f"Connection error: {e}")
          self._content = BeautifulSoup(resp.text, "html.parser")
          self._lastver = self._content.body.h2.text.split(': ')[1] # type: ignore
          self._builds = {i.text.split(' (')[0]: {'type': 'p' if i.parent.name == 'span' else 'c', 'link': unquote(i['href'].split('?url=', 1)[1].split('&', 1)[0])} for i in self._content.find_all('a') if 'Web Installer' in i.text}
          self._astver = self._content.body.hr.next.text.split('ts_', 1)[1].split('.zip', 1)[0] # type: ignore | Yes, no ASSver :)
          self._astlink = self._content.body.hr.next['href'] # type: ignore
     
     def close(self) -> None:
          """Closes sessions and connections"""
          self.sess.close()
     
     @property
     def latest_version(self) -> str:
          """[property] String that contains latest firmware version
          format: RM[mmdd]-xxxx
          """
          return self._lastver
     
     @property
     def assets_version(self) -> str:
          """[property] String that contains latest assets version
          format: [mmdd]-xxxx
          """
          return self._astver
     
     @property
     def builds(self) -> list:
          """[property] List of all available builds (includes custom)"""
          return list(self._builds.keys())
     
     @property
     def popular_builds(self) -> list:
          """[property] List of popular builds
          """
          return [i for i in self._builds if self._builds[i]['type'] == 'p']
     
     @property
     def custom_builds(self) -> list:
          """[property] List of custom builds
          """
          return [i for i in self._builds if self._builds[i]['type'] == 'c']
     
     #TODO
     def download_build(self, build, path):
          link = self._builds.get(build, None)
          if not link:
               raise ValueError(f"Build {build} not presented in this provider")
          link = link['link']
          file = get_filename(link)
     
     #TODO
     def download_assets(self, path):
          file = get_filename(self._astlink) # type: ignore


# DEBUG (Only for development)
if __name__ == '__main__':
     import os
     from dotenv import load_dotenv
     load_dotenv('../../../.env')
     prov = RMPatreon(os.getenv('RM_USER'), os.getenv('RM_PWD')) # type: ignore
     pass
