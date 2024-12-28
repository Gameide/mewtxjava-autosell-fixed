# MewtXJava Autosell Fixed Version

> What is it?
- It gathers all the UGC Limiteds you have and sells all the one that are out of its holding period according to your settings.

## Credits 
- [Mewt](https://discord.gg/mewt) // Unsupported
- [Java](https://discord.gg/javaw) // Unsupported
- [Gameide](https://discord.gg/vAENGUKjVe) // Supported
- [ChatGPT](https://chatgpt.com) // 24/7 Support
  
- [Original Repository](https://github.com/workframes/mewtxjava-autosell)

## Requirements
- [Python](https://www.python.org/downloads/)
- [requests](https://pypi.org/project/requests/)
- [colorama](https://pypi.org/project/colorama/)
- [rgbprint](https://pypi.org/project/rgbprint/)

## Disclaimer
If you do plan on using this, and if something goes wrong and you loose robux. You will not be refunded as you are using this by your own choice.

## Installation
Grab the latest version from [here](https://github.com/Gameide/mewtxjava-autosell-fixed/releases)

You must start first the `getitemdetails.py` to fetch all your resellable items, after that, you can now start `main.py`

If you are running this on `Mac OS` run it using `main.py`, if you are running it on `Windows` you can run it with either `start.bat` or `main.py`

## Settings Documentation
- `COOKIE`
    * The `.ROBLOXSECURITY` of the acount you want to sell items on.
- `SELL_METHOD`
    * What sell method you want to use, here are the following options and what it does.
        * `UNDERCUT`
            * Sells your item for 1 robux under the most recent price. It will constantly update the price to 1 robux under as well every 5 minutes.
        * `CUSTOM`
            * Sells your items according to the prices you set in `CUSTOM_VALUES`. 
- `CUSTOM_VALUES`
    * These are the custom prices that will be used to for the sell method `CUSTOM` While using this only the items included in custom values will be resold. Example:
        * ```json
            "CUSTOM_VALUES": {
                "13345169760": 40
            }
            ```
- `WHITELIST`
    * It will **ONLY** resell only the items listed in there, it will apply for all selling methods and will also follow the `BLACKLIST`
- `BLACKLIST_ITEMID` 
    * If a item is in this list, it will not put it up for resale.
- `CREATORS_BLACKLIST`
    * If a CreatorID or GroupID is on this list, items made by them will not be put up for resale.
- `WEBHOOK`
    * If you have this enabled it will send notfications when a item sells.
    - `ENABLED`
        * `true` to enabled the feature
        * `false` to disable the feature
    - `URL`
        * If you have enabled you must have a discord webhook.
## Example Settings
```json
{
    "SELL_METHOD": "UNDERCUT",
    "CUSTOM_VALUES": {
        "13599801260": 60
    },
    "WHITELIST":[
        13345169760
    ],
    "BLACKLIST": [
        13636293210
    ],
    "BLACKLIST_ITEMID": [
        17598614110
    ],
    "CREATORS_BLACKLIST": [
        34670457
    ],
    "WEBHOOK": {
        "ENABLED": true,
        "URL": "https://discord.com/api/webhooks/abc/abc"
    }
}
```

## Still having trouble? 
* Join the discord server mentioned in [Credits](https://github.com/Gameide/mewtxjava-autosell-fixed#credits) and they will be happy to help you!
* Any suggestions? Let me know in the discord server.
