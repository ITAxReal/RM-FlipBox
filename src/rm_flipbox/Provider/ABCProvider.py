from abc import ABC

 
class ABCProvider(ABC):
    
    BASE_URL = None
    
    def __init__(self) -> None:
        raise NotImplementedError
    
    @property
    def latest_version(self) -> str:
        raise NotImplementedError
    
    @property
    def builds(self) -> list:
        raise NotImplementedError
    
    def close(self) -> None:
        raise NotImplementedError
    
    def download_build(self, build, path):
        raise NotImplementedError
