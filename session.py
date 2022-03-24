import requests
import logging as log
import tracemalloc
from config import dest

class RequestSession(): 
    def __init__(self): 
        self.session = requests.Session()
        self.cookies = self.session.cookies
    
    def update_cookies(self, cookies):
        self.cookies = cookies

    def download_file(self, name, url):
        name = name+".mp4"
        #tracemalloc.start()
        response = self.session.get(url, stream=True)
        log.warning(f"Obtained recording URL response with status code: {response.status_code}")

        with open(f"{dest}{name}",'wb') as f: 
            log.warning(f"Downloading {name}.....")
            f.write(response.content)
            log.warning("Finished downloading.")
        
        #print(tracemalloc.get_traced_memory())
        #tracemalloc.stop()
    
    def close(self): 
        self.session.close()
        

   
    


