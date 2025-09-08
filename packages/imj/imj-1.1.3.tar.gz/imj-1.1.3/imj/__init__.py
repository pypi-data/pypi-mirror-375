import requests

BASE = 'https://i.marcusj.org'

class IMJ(object):
    def __init__(self, img_id: str, key: str, base_url: str=BASE, disp_url: str=BASE):
        self.id = img_id
        self.base = base_url
        self.disp = disp_url
        self.key = key

    @property
    def viewer(self) -> str:
        return f"{self.disp}/view/{self.id}"
    
    @property
    def url(self) -> str:
        return f"{self.disp}/image/{self.id}"
    
    def shorten(self):
        return requests.get(f"{self.base}/shorten/{self.id}").url.replace(self.base, self.disp)
    
    def delete(self):
        return requests.get(f"{self.base}/delete/{self.id}?key={self.key}").text

def upload_file(fn: str) -> IMJ:
    r = requests.post(f"{BASE}/upload", files={
        'image': open(fn, 'rb')
    })
    return IMJ(*(r.url.split('/')[-1].split('?key=')))

def upload(raw: bytes, fn: str='image.png', mimetype: str='image/png') -> IMJ:
    r = requests.post(f"{BASE}/upload", files={
        'image': (
            fn,
            raw,
            mimetype,
        )
    })
    return IMJ(*(r.url.split('/')[-1].split('?key=')))

def delete(img_id: str, key: str) -> str:
    return requests.get(f"{BASE}/delete/{img_id}?key={key}").text