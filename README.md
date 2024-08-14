# PS5 3.xx / 4.xx Kernel Exploit
https://mhm200533.github.io/mhm200533/document/en/ps5/
Modified ps5 host to load payloads from within the browser.

- Site hosted on Cloudflare's CDN: https://ps5jb.pages.dev
- This site is set up with automatic deployment, `deploy.py` is ran on each commit.


## Self-hosting setup
1. Run fakedns.py with `python fakedns.py` and set the DNS on your PS5 to your computers IP address. (this step is optional if youre using a proper web browser and not the user guide, but you should always use an update blocking dns)
    - By default domains containing `playstation`, `sonyentertainmentnetwork` and `scea` are blocked, this can be disabled with the `--no-ps-blocking` argument
    - By default `manuals.playstation.net` (user guide) is set to the current computers IP address, this can be disabled with the `--no-user-guide` argument
    - You can specify an optional dns config file like this `-c dns.conf`, rules specified here take priority over the above mentioned rules, so if you have a `dns.conf` file like this, `manuals.playstation.net` would get matched to the ip specified in the config file even if `--no-user-guide` is not specified:
      ```
      A manuals.playstation.net 192.168.1.2
      ```
    - More info with `--help`
    - If you get a message saying udp port 53 is in use open Services (`services.msc`), and disable then stop `Host Network Service` and `Internet Connection Sharing`
      - If this didnt work, open a powershell terminal and run this (may require powershell in admin mode)
        ```
        Get-Process -Id (Get-NetUDPEndpoint -LocalPort 53).OwningProcess
        ```
        you'll see an id column take note of the id then run this
        ```
        taskkill /F /PID <ID>
        ```

1. Create appcache for offline use by running `python appcache_manifest_generator.py`
    - You can disable caching by deleting `cache.appcache` files if they exist (located in root and `document/en/ps5`) and editing the `index.html`'s first line from
      ```
      <html manifest="cache.appcache">
      ```
      to
      ```˙
      <html>
