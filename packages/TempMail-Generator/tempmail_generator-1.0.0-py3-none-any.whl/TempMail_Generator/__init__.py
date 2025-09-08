from .server import Backend
from .process import APIProcess,Config


class TempMailGenerator:
    def __init__(self):
        Config.load()

    def add_api(key_list:list[str]|str,new_host:str=None,new_base:str=None):
        if isinstance(key_list,str):
            key_list = [key_list]
        Config.CONFIG["rapid_api_keys"] += [k.strip() for k in key_list.split(" ")]
        Config.CONFIG["rapid_api_keys"] = list(set(Config.CONFIG["rapid_api_keys"]))

        if new_host:
            Config.CONFIG["api_host"] = new_host.strip()

        if new_base:
            Config.CONFIG["api_base_url"] = new_base.strip()
        Config.save_config()

    def generate():
        return APIProcess.generate_email()
    
    def start_server(self,debug:bool = False, host:str=None, port:int=None):
        Backend().run(debug=debug, host=host, port=port)
