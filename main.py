import requests, os, sys, json, time, threading, copy
from colorama import Fore, Style
from rgbprint import gradient_print

settings = json.load(open("settings.json", "r"))
collectable_types = [
    8, 42, 43, 44, 45, 46, 47, 41, 64, 65, 68, 67, 66, 69, 72, 70, 71
]
sell_methods = ["CUSTOM", "UNDERCUT"]

class MewtStyle():
    MAIN = f"\x1b[38;2;247;184;207m"

class Webhook:
    def __init__(self, webhook):
        self.webhook = webhook

    def post(self, buyer_name, buyer_id, item_name, item_id, item_thumbnail, price):
        payload = {
            "embeds": [
                {
                    "title": f"Sold {item_name}!",
                    "description": f"`earned`: **{price}**\n`buyer`: **[{buyer_name}](https://www.roblox.com/users/{buyer_id})**",
                    "url": f"https://www.roblox.com/catalog/{item_id}",
                    "color": 16234703,
                    "thumbnail": {
                        "url": item_thumbnail
                    }
                }
            ]
        }
        with requests.session() as session:
            session.post(self.webhook, json=payload)

class Client:
    def __init__(self):
        self.version = "1.0.2"
        self.title = (f"""
                                                                d8,                              
                                       d8P                     `8P                               
                                    d888888P                                      
  88bd8b,d88b  d8888b ?88   d8P  d8P  ?88'      ?88,  88P      d88   d888b8b  ?88   d8P d888b8b  
  88P'`?8P'?8bd8b_,dP d88  d8P' d8P'  88P        `?8bd8P'      ?88  d8P' ?88  d88  d8P'd8P' ?88  
 d88  d88  88P88b     ?8b ,88b ,88'   88b        d8P?8b,        88b 88b  ,88b ?8b ,88' 88b  ,88b 
d88' d88'  88b`?888P' `?888P'888P'    `?8b      d8P' `?8b       `88b`?88P'`88b`?888P'  `?88P'`88b
                                                                 )88                             
                                                                ,88P                             
                                                             `?888P
                      
                        fixed version, original code by frames & java - v{self.version}                              
                      """)

        self.ready = False    
        self.sell_method = settings["SELL_METHOD"]
        self.custom_values = settings["CUSTOM_VALUES"]
        self.whitelist = settings["WHITELIST"]
        self.blacklist = settings["BLACKLIST_ITEMID"]
        self.creatorsblacklist = settings["CREATORS_BLACKLIST"]
        self.webhook_enabled = settings["WEBHOOK"]["ENABLED"]
        self.webhook_url = settings["WEBHOOK"]["URL"]
        self.client = {
            "cookie": settings["COOKIE"],
            "auth": "abcabcabc",
            "name": "abcabcabc",
            "id": 0
        }
        self.inventory = {}
        self.last_transaction_id = None
        self.raw_inventory = []
        self.onsale = []
        self.mewt_collection = []
        self.mewt_collection_reversed = []
        

        self.id_to_name = {}
        self.collectable_id_to_name = {}

        self.collectable_instance_id_to_product_id = {}

        self.collectable_id_to_id = {}

        self.webhook = None

        self.session = requests.session()
        self.session.cookies['.ROBLOSECURITY'] = self.client["cookie"]

        self.resellable_count = 0
        self.logs = []

        if self.webhook_enabled:
            self.webhook = Webhook(self.webhook_url)

        if(self.sell_method not in sell_methods):
            print("Invalid sell method, accepted sale here are the accepted sell methods; " + ", ".join([value for value in sell_methods]))
            time.sleep(1)
            raise SystemExit
        
        if(self.sell_method == "CUSTOM" and len(self.custom_values) <= 0):
            print("You need add custom values to support your sell method")
            time.sleep(1)
            raise SystemExit


        self.verify_cookie()
        while self.ready != True:
            time.sleep(1)

        
        self.infinite_thread(self.update_status, 1)
        self.infinite_thread(self.set_token, 200)
        self.infinite_thread(self.fetch_mewt_collection, 10 * 60)

        self.logs.append(f"Logged in as {self.client['name']}({self.client['id']})")
        self.logs.append("Fetching inventory.")
        self.infinite_thread(self.update_inventory, 15 * 60)
        self.infinite_thread(self.sell_all_items, 5)
        self.infinite_thread(self.scan_recent_transactions, 3 * 60)

    def update_status(self):
        os.system('cls' if os.name=='nt' else 'clear')
        gradient_print(self.title, start_color=(0xFF6EA3), end_color=(0xF7B8CF))
        print(Fore.RESET + Style.RESET_ALL)
        print(Style.BRIGHT + f"> Current User: {MewtStyle.MAIN}{Style.BRIGHT}{self.client['name']}{Fore.WHITE}{Style.BRIGHT} ")
        print(Style.BRIGHT + f"> Resellable Items: {MewtStyle.MAIN}{Style.BRIGHT}{self.resellable_count}{Fore.WHITE}{Style.BRIGHT} ")
        print(Style.BRIGHT + f"> Sell Method: {MewtStyle.MAIN}{Style.BRIGHT}{self.sell_method}{Fore.WHITE}{Style.BRIGHT} ")
        print()
        print(Style.BRIGHT + f"> Logs: {MewtStyle.MAIN}{Style.BRIGHT}\n" + "\n".join(log for log in self.logs[-10:]) + f"{Fore.WHITE}{Style.BRIGHT}")

    
    def fetch_mewt_collection(self):
        try:
            with open("items_data.json", "r") as f:
                data = json.load(f)
            self.mewt_collection = {item["id"]: item for item in data}
            self.mewt_collection_reversed = {item["collectibleItemId"]: item for item in data}
            self.logs.append("Successfully fetched collectable items from local file")
        except Exception as e:
            self.logs.append(f"Error loading local file: {e}")
            time.sleep(5)
            return self.fetch_mewt_collection()
        
    def find_mewtdata_by_id(self, id):
        if len(self.mewt_collection) <= 0:
            time.sleep(1)
            return self.find_mewtdata_by_id(id)
        
        if id in self.mewt_collection:
            return self.mewt_collection[id]
        else:
            return None
        
    def find_mewtdata_by_collectable_item_id(self, collectibleItemId):
        if len(self.mewt_collection_reversed) <= 0:
            time.sleep(1)
            return self.find_mewtdata_by_id(collectibleItemId)
        
        if collectibleItemId in self.mewt_collection_reversed:
            return self.mewt_collection_reversed[collectibleItemId]
        else:
            return None

    def verify_cookie(self):
        conn = self.session.get("https://users.roblox.com/v1/users/authenticated")
        if(conn.status_code == 200):
            data = conn.json()
            self.client["id"] = data["id"]
            self.client["name"] = data["name"]
            self.ready = True
        else:
            print("Invalid cookie or please wait a minute and trying again")
            time.sleep(1)
            raise SystemExit

    def set_token(self):
        try:
            conn = self.session.post("https://friends.roblox.com/v1/users/1/request-friendship")
            if(conn.headers.get("x-csrf-token")):
                self.client["auth"] = conn.headers["x-csrf-token"]
                self.session.headers["x-csrf-token"] = conn.headers["x-csrf-token"]
        except:
            time.sleep(5)
            return self.set_token()
        
    def scan_recent_transactions(self):
        try:
            conn = self.session.get(f"https://economy.roblox.com/v2/users/{self.client['id']}/transactions?cursor=&limit=100&transactionType=Sale")
            if(conn.status_code == 200):
                conn_data = conn.json()
                data = conn_data["data"]
                if self.last_transaction_id is None:
                    self.last_transaction_id = data[0]["idHash"]
                    return 
                
                for sale in data:
                    if sale["idHash"] == self.last_transaction_id:
                        self.last_transaction_id = data[0]["idHash"] 
                        break 
                    
                    agentId = sale['agent']['id']
                    agentName = sale['agent']['name']
                    assetId = sale['details']['id']
                    assetName = sale['details']['name']
                    assetType = sale['details']['type']
                    amount = sale['currency']['amount']
                    if assetType != 'Asset':
                        continue

                    mewt_data = self.find_mewtdata_by_id(int(assetId))
                    
                    if not mewt_data:
                        continue

                    self.logs.append(f"{agentName} bought {assetName}, you earned {amount}!")
                    if self.webhook_enabled:
                        self.webhook.post(agentName, agentId, assetName, assetId, mewt_data["thumbnail"], amount)
            else:
                time.sleep(5)
                return self.scan_recent_transactions()

        except Exception as error:
            print(error)
            time.sleep(5)
            return self.scan_recent_transactions()
        
    def fetch_inventory(self, assettype, cursor = "", data = []):
        try:
            conn = self.session.get(f"https://inventory.roblox.com/v2/users/{self.client['id']}/inventory/{assettype}?cursor={cursor}&limit=100&sortOrder=Desc")
            if(conn.status_code == 200):
                conn_data = conn.json()
                data = data + conn_data["data"]

                if conn_data["nextPageCursor"] is not None:
                    return self.fetch_inventory(assettype, conn_data["nextPageCursor"], data)
                
                return data
            elif(conn.status_code == 429):
                time.sleep(5)
                return self.fetch_inventory(assettype, cursor, data)
        except:
            time.sleep(5)
            return self.fetch_inventory(assettype, cursor, data)

        
    def fetch_item_resellable(self, collectableItemId, cursor = "", data = []):
        try:
            conn = self.session.get(f"https://apis.roblox.com/marketplace-sales/v1/item/{collectableItemId}/resellable-instances?cursor={cursor}&ownerType=User&ownerId={self.client['id']}&limit=500")
            if(conn.status_code == 200):
                conn_data = conn.json()
                data = data + conn_data["itemInstances"]
                if conn_data["nextPageCursor"] is not None:
                    return self.fetch_item_resellable(collectableItemId, conn_data["nextPageCursor"], data)
                
                return data
            else:
                time.sleep(10)
                return self.fetch_item_resellable(collectableItemId, cursor, data)
        except:
            time.sleep(5)
            return self.fetch_item_resellable(collectableItemId, cursor, data)
        
    def fetch_item_details(self, items):
        try:
            conn = self.session.post("https://apis.roblox.com/marketplace-items/v1/items/details", json={ "itemIds": items })
            if(conn.status_code == 200):
                conn_data = conn.json()
                return conn_data
            else:
                time.sleep(5)
                return self.fetch_item_details(items)
        except:
            time.sleep(5)
            return self.fetch_item_details(items)
        
    def fetch_reseller(self, collectableItemId):
        try:
            conn = self.session.get(f"https://apis.roblox.com/marketplace-sales/v1/item/{collectableItemId}/resellers?limit=1")
            if(conn.status_code == 200):
                conn_data = conn.json()
                return conn_data["data"][0]
            else:
                time.sleep(5)
                return self.fetch_reseller(collectableItemId)
        except:
            time.sleep(5)
            return self.fetch_reseller(collectableItemId)
        
    def fetch_item_details_chunks(self, items):
        chunks = []
        data = []
        collectable_items = []

        for item in items:
            mewt_data = self.find_mewtdata_by_id(int(item))
            if mewt_data:
                collectable_items.append(mewt_data["collectibleItemId"])

        while len(collectable_items) > 0:
            chunks.append(collectable_items[:120])
            collectable_items = collectable_items[120:]

        for chunk in chunks:
            new_data = self.fetch_item_details(chunk)
            data = data + new_data

        return data
    

    def sell_item(self, price, collectibleItemId, collectibleInstanceId, collectibleProductId):
        try:
            payload = {
                "collectibleProductId": collectibleProductId,
                "isOnSale": True,
                "price": price,
                "sellerId": self.client["id"],
                "sellerType": "User",
            }
            conn = self.session.patch(f"https://apis.roblox.com/marketplace-sales/v1/item/{collectibleItemId}/instance/{collectibleInstanceId}/resale", json=payload)
            if(conn.status_code == 200):
                return True
            else:
                time.sleep(10)
                print(f"Something went wrong, {conn.status_code}")
                return self.sell_item(price, collectibleItemId, collectibleInstanceId, collectibleProductId)
        except:
            time.sleep(10)
            return self.sell_item(price, collectibleItemId, collectibleInstanceId, collectibleProductId)
        

    def sell_all_items(self):
        if(len(self.inventory) > 0):
            try:
                inventory = copy.deepcopy(self.inventory)
                price_cache = {}
        
                for collectibleItemId, collectibleInstanceIds in inventory.items():
                    for collectibleInstanceId in collectibleInstanceIds:
                        if collectibleInstanceId in self.onsale:
                            if collectibleInstanceId in self.inventory[collectibleItemId]:
                                self.inventory[collectibleItemId].remove(collectibleInstanceId)
                            continue

                        price = None

                        if self.sell_method == "CUSTOM":
                            id = str(self.collectable_id_to_id[collectibleItemId])
                            if not id in self.custom_values:
                                self.logs.append(f"Failed to sell {self.collectable_id_to_name[collectibleItemId]} due to no custom value for the item.")
                                self.resellable_count -= 1
                            else:
                                price = self.custom_values[id]
                        elif self.sell_method == "MEWTVALUES":
                            mewt_data = self.find_mewtdata_by_collectable_item_id(collectibleItemId)
                            if mewt_data["estimatedValue"] <= 0:
                                self.logs.append(f"Failed to sell {self.collectable_id_to_name[collectibleItemId]} due mewt value being too low")
                                self.resellable_count -= 1
                            else:
                                price = mewt_data["estimatedValue"] * self.mewtvalue_multiplier
                        elif self.sell_method == "UNDERCUT":
                            if collectibleItemId not in price_cache:
                                recent_seller = self.fetch_reseller(collectibleItemId)
                                if recent_seller["seller"]["sellerId"] == self.client["id"]:
                                    price_cache[collectibleItemId] = recent_seller["price"]
                                else:
                                    price_cache[collectibleItemId] = (recent_seller["price"] - 1)

                                price = price_cache[collectibleItemId]
                            
                        if price is not None:
                            success = self.sell_item(price, collectibleItemId, collectibleInstanceId, self.collectable_instance_id_to_product_id[collectibleInstanceId])
                            if success == True:
                                self.logs.append(f"Successfully put {self.collectable_id_to_name[collectibleItemId]} on sale for {price}")
                                self.onsale.append(collectibleInstanceId)
                                self.resellable_count -= 1
            except Exception as error:
                print(error)

    def update_inventory(self):
        self.resellable_count = 0
        self.inventory = {}
        can_resell_collectables = []

        if len(self.whitelist) > 0:
            item_details = self.fetch_item_details_chunks(self.whitelist)
            for item in item_details:
                mewt_data = self.find_mewtdata_by_id(item["itemTargetId"])
                if(mewt_data and mewt_data["CreatorTargetId"] not in self.creatorsblacklist and mewt_data["resellable"] == True):
                    if not item["itemTargetId"] in self.blacklist:
                        self.collectable_id_to_name[item["collectibleItemId"]] = item["name"]
                        self.id_to_name[item["itemTargetId"]] = item["name"]
                        self.collectable_id_to_id[item["collectibleItemId"]] = item["itemTargetId"]
                        if not item["collectibleItemId"] in can_resell_collectables:
                            can_resell_collectables.append(item["collectibleItemId"])
        elif self.sell_method == "CUSTOM":
            item_details = self.fetch_item_details_chunks(list(self.custom_values.keys()))
            for item in item_details:
                mewt_data = self.find_mewtdata_by_id(item["itemTargetId"])
                if(mewt_data and mewt_data["CreatorTargetId"] not in self.creatorsblacklist and mewt_data["resellable"] == True):
                    if not item["itemTargetId"] in self.blacklist:
                        self.collectable_id_to_name[item["collectibleItemId"]] = item["name"]
                        self.id_to_name[item["itemTargetId"]] = item["name"]
                        self.collectable_id_to_id[item["collectibleItemId"]] = item["itemTargetId"]
                        if not item["collectibleItemId"] in can_resell_collectables:
                            can_resell_collectables.append(item["collectibleItemId"])
        else:
            for assettype in collectable_types:
                inventory_data = self.fetch_inventory(assettype)
                self.raw_inventory.extend(inventory_data)

            for raw_item in self.raw_inventory:
                if not raw_item["assetId"] in self.blacklist:
                    mewt_data = self.find_mewtdata_by_id(raw_item["assetId"])
                    if(mewt_data and mewt_data["CreatorTargetId"] not in self.creatorsblacklist and mewt_data["resellable"] == True):
                        self.collectable_id_to_name[raw_item["collectibleItemId"]] = raw_item["assetName"]
                        self.id_to_name[raw_item["assetId"]] = raw_item["assetName"]
                        self.collectable_id_to_id[raw_item["collectibleItemId"]] = raw_item["assetId"]
                        if not raw_item["collectibleItemId"] in can_resell_collectables:
                            can_resell_collectables.append(raw_item["collectibleItemId"])

        self.logs.append(f"Found {len(can_resell_collectables)} different collectables that are resellable")
        for item in can_resell_collectables:
            resellable_data = self.fetch_item_resellable(item)
            total_instance_copies = 0 
            for instance in resellable_data:
                if instance["isHeld"] == False and instance["saleState"] == "OffSale":
                    if not item in self.inventory:
                        self.inventory[item] = []
                    self.resellable_count += 1
                    total_instance_copies += 1
                    self.collectable_instance_id_to_product_id[instance["collectibleInstanceId"]] = instance["collectibleProductId"]
                    self.inventory[item].append(instance["collectibleInstanceId"])
            self.logs.append(f"Loaded all resellable instances for {self.collectable_id_to_name[item]}; Copies: {total_instance_copies}")

        self.logs.append(f"Successfully updated inventory. Resellable: {self.resellable_count}")


    def infinite_thread(self, func, _time):
        def _func():
            while True:
                func()
                time.sleep(_time)
        threading.Thread(target=_func,).start()


if __name__ == '__main__':
    Client()
