from .config import logger
from teloxi import TeloxiClient,Storage,Account,Device
from dbflux import Sqlite
from itertools import cycle
from .config import Settings
import asyncio  
from typing import Tuple,Dict
from .utils import parse_phone

class AdvioTG:
    
    def __init__(self,settings:Settings=None,proxy:Tuple|Dict=None):
        
        self.settings   =   Settings() if not settings else settings
        self.sessions   =   Storage(Sqlite(self.settings._resolve_path(self.settings.sessions_path)))
        self.proxy      =   proxy
       
        
    
    
    
    

    async def register(self):
        
        devices={
            'A':Device.TelegramAndroid,
            'X':Device.TelegramAndroidX,
            'W':Device.TelegramWindows,
            'I':Device.TelegramIOS,
            'L':Device.TelegramLinux,
            'M':Device.TelegramMacOS,
            'MD':Device.TelegramMacosDesktop
        }
        device=lambda t: devices.get(t,Device.TelegramAndroid).Generate()
        
        try:
            while True:
                phone=input("Enter a valid phone number (or 'END' to cancel): ")
                if not phone :
                    continue
                if phone.upper()=='END':
                        break

                if not parse_phone(phone):
                        print("Invalid phone number format. Please try again.")
                        continue
                self.sessions.delete(conditions= [Account.session_id==phone, Account.status=='INACTIVE'])
                client=TeloxiClient(session_id=phone,device=device(self.settings.telegram), database=self.sessions,proxy=self.proxy)
                try:
                    await client.start(phone=phone)
                except Exception as e:
                    logger.error(f"<r>{e.__class__.__name__}: {e}</r>")

                    
        except KeyboardInterrupt:
            print("\nRegistration cancelled by user.")

    
   
    async  def get_login_code(self):
            def callback(message, code):

                if code:
                    
                    logger.success(f"<g>login code: {message}</g>")
                else:
                    logger.info(f"<y>{message}</y>")
                    
            
            try:
                while True:
                    phone=input("Enter a valid phone number (or 'END' to cancel): ")
                    if not phone :
                        continue
                    if phone.upper()=='END':
                            break

                    if not parse_phone(phone):
                            print("Invalid phone number format. Please try again.")
                            continue
                    accounts:list[Account]=self.sessions.get(conditions=[Account.session_id==phone, Account.status=='ACTIVE'])
                    if not accounts:
                        logger.error('<r>Account not found OR account is not active</r>')
                        continue
                    account=accounts[0]
                    try:
                        client=TeloxiClient(session_id=account.session_id, database=self.sessions,proxy=self.proxy)
                        await client.connect()
                        if not await client.is_user_authorized():
                            logger.error("<r>Account not authorized</r>")
                            continue
                        
                        await client.get_login_code(callback=callback)
                    except Exception as e:
                        logger.error(f"<r>{e.__class__.__name__}: {e}</r>")
                    finally:
                        await client.disconnect()
                        
            except KeyboardInterrupt:
                print("\nGet login code cancelled by user.")
            
    async def join_chats(self):
        pass

        
    

    
    
    
    
    
    
            
     

         
            
                

    
                
        
   


        
         
    
    