try:
    import requests, os, sys, json, time, threading, copy
    from colorama import Fore, Style
    from rgbprint import gradient_print
except ModuleNotFoundError as error:
    os.system("pip install requests colorama rgbprint")
    os.execv(sys.executable, [sys.executable] + [sys.argv[0]] + sys.argv[1:])


settings = json.load(open("settings.json", "r"))
collectable_types = [
    8, 42, 43, 44, 45, 46, 47, 41, 64, 65, 68, 67, 66, 69, 72, 70, 71
]


class Client:
    def __init__(self):
        self.client = {
            "cookie": settings["COOKIE"],
            "auth": "abcabcabc",
            "name": "abcabcabc",
            "id": 0
        }
        self.ready = False
        self.session = requests.session()
        self.session.cookies['.ROBLOSECURITY'] = self.client["cookie"]
        
        self.token = None
        self.results = []
        self.last_transaction_id = None
        self.verify_cookie()
        while self.ready != True:
            time.sleep(1)

        self.infinite_thread(self.set_token, 200)
        

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
        

    


    def fetch_inv(self, assettype, cursor="", data=[]):
        try:
            print(f"Fetching inventory for asset type {assettype} with cursor: {cursor}")
            conn = self.session.get(f'https://inventory.roblox.com/v2/users/{self.client["id"]}/inventory/{assettype}?cursor={cursor}&limit=50&sortOrder=Desc')  # Reducimos el límite a 50
            if conn.status_code == 200:
                conn_data = conn.json()
                data = data + conn_data["data"]
                
                if conn_data["nextPageCursor"] is not None:
                    return self.fetch_inv(assettype, conn_data["nextPageCursor"], data)

                return data
            elif conn.status_code == 429:
                print("Rate limit hit, sleeping for 5 seconds...")
                time.sleep(5)
                return self.fetch_inv(assettype, cursor, data)

            else:
                print(f"Failed to fetch inventory. Status code: {conn.status_code}")
                return data

        except Exception as error:
            print(f"Error fetching inventory: {error}")
            time.sleep(5)
            return self.fetch_inv(assettype, cursor, data)

        except:
            time.sleep(5)
            return self.fetch_inv(assettype, cursor, data)

    def get_collectibleItemId(self, assetId, retries=5):
        try:
            print(f"Attempting to fetch collectibleItemId for assetId: {assetId}, retries left: {retries}")
            headers = {"x-csrf-token": self.token}
            conn = self.session.get(f"https://economy.roblox.com/v2/assets/{assetId}/details", headers=headers)

            if conn.status_code == 200:
                data = conn.json()
                print(f"Successfully fetched data for assetId: {assetId}")

                
                return {
                    "name": data.get("Name"),
                    "collectibleItemId": data.get("CollectibleItemId"),
                    "id": data.get("AssetId"),
                    "CreatorTargetId": data.get("Creator", {}).get("CreatorTargetId"),
                    "collectibleProductId": data.get("CollectibleProductId"),
                }

            elif retries > 0:
                print(f"Failed to fetch details for assetId {assetId}, status code: {conn.status_code}. Retrying...")
            
                return self.get_collectibleItemId(assetId, retries - 1)
            else:
                print(f"Max retries reached for assetId: {assetId}. Skipping...")
                return None

        except Exception as error:
            print(f"Error fetching collectibleItemId for assetId {assetId}: {error}")
            if retries > 0:
                
                return self.get_collectibleItemId(assetId, retries - 1)
            else:
                print(f"Max retries reached for assetId: {assetId} due to error. Skipping...")
                return None
    

    def get_thumb(self, assetId):
        try:
            print(f"Fetching thumbnail for assetId: {assetId}")
            conn = self.session.get(f"https://thumbnails.roblox.com/v1/assets?assetIds={assetId}&size=420x420&format=Png&isCircular=false")
            if conn.status_code == 200:
                data = conn.json()
                if data["data"]:
                    thumbnail_url = data["data"][0]["imageUrl"]
                    print(f"Thumbnail for assetId {assetId} fetched successfully: {thumbnail_url}")
                    return thumbnail_url
                else:
                    print(f"No thumbnail found for assetId: {assetId}")
                    return None
            else:
                print(f"Failed to fetch thumbnail for assetId: {assetId}, status code: {conn.status_code}")
                return None

        except Exception as error:
            print(f"Error fetching thumbnail for assetId {assetId}: {error}")
            return None
        

    def isoffale(self, assetId):
        try:
            print(f"Fetching isOffSale for assetId: {assetId}")
            conn = self.session.post(
            f"https://catalog.roblox.com/v1/catalog/items/details", 
            json={"items": [{"itemType": "Asset", "id": assetId}]}
            )
            if conn.status_code == 200:
                data = conn.json()
                if data["data"]:
                    has_resellers = data["data"][0].get("hasResellers", False)
                    print(f"Fetch for assetId {assetId} fetched successfully: {'Resellable' if has_resellers else 'Not resellable'}")
                    return has_resellers
                else:
                    print(f"Can't fetch for assetId: {assetId}")
                    return None
            elif conn.status_code == 429:
                print("Rate limit hit, sleeping for 10 seconds...")
                time.sleep(10)
                return self.isoffale(assetId) 
            else:
                print(f"Failed to fetch details for assetId: {assetId}, status code: {conn.status_code}")
                return False

        except Exception as error:
            print(f"Error fetching isOffSale for assetId {assetId}: {error}")
            return None

    def save_results_to_json(self):
        try:
            with open('items_data.json', 'w') as json_file:
                json.dump(self.results, json_file, indent=4)
            print("Item details saved to items_data.json")
        except Exception as error:
            print(f"Error saving results: {error}")
        


    def main(self):
        for assettype in collectable_types:
            inventory_data = self.fetch_inv(assettype)

            if inventory_data:
                print(f"Data for asset type {assettype}: {len(inventory_data)} items found")

                for item in inventory_data:
                    assetId = item.get("assetId")
                    if assetId:
                        print(f"Fetching details for assetId: {assetId}")
                        details = self.get_collectibleItemId(assetId)

                        if details:
                            if details["CreatorTargetId"] == 1:  
                                print(f"Skipping item with assetId {assetId} due to creatorId being 1")
                                continue
                            if details["collectibleItemId"] is None or details["collectibleProductId"] is None:  
                                print(f"Skipping item with assetId {assetId} due to missing collectibleProductId or CollectibleItemId")
                                continue

                            thumbnail = self.get_thumb(assetId)
                            resellable = self.isoffale(assetId)
                            details["thumbnail"] = thumbnail
                            details["resellable"] = resellable

                            self.results.append(details)
                            print(details)

            else:
                print(f"No data found for asset type {assettype}")
        
        self.save_results_to_json() 
    
    def infinite_thread(self, func, _time):
        def _func():
            while True:
                func()
                time.sleep(_time)
        threading.Thread(target=_func,).start()

if __name__ == "__main__":
    client = Client()  
    client.verify_cookie()  
    if client.ready:
        client.main()  