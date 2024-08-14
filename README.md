# PS5 3.xx / 4.xx Kernel Exploit

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
      ```
      by doing this you wont get cache related toasts/notifications
    - If you disable caching after you had already loaded the page with the cache manifest, its a good idea to run the appcache remover payload, however it shouldnt be necessary
1. Run web server with `python host.py` for user guide use or `python simple_server.py` if you're using something like leefuls site.
    - You can add your own payloads by putting them into the `payloads` folder and editing the `payload_map.js` file
    - Re-run `appcache_manifest_generator.py` after adding payloads or changing files, if you're using caching

You can also watch Modded Warfare's video on setting this host up: https://www.youtube.com/watch?v=gjkaL1pTOQs


---
## Summary
This repo contains an experimental WebKit ROP implementation of a PS5 kernel exploit based on **TheFlow's IPV6 Use-After-Free (UAF)**, which was [reported on HackerOne](https://hackerone.com/reports/1441103). The exploit strategy is for the most part based on TheFlow's BSD/PS4 PoC with some changes to accommodate the annoying PS5 memory layout (for more see *Research Notes* section). It establishes an arbitrary read / (semi-arbitrary) write primitive. This exploit and its capabilities have a lot of limitations, and as such, it's mostly intended for developers to play with to reverse engineer some parts of the system.

With latest stability improvements, reliability is at about 80%. This document will contain research info about the PS5, and this exploit will undergo continued development and improvements as time goes on.

Those interested in contributing to PS5 research/dev can join a discord I have setup [here](https://discord.gg/kbrzGuH3F6).

Exploit should now support the following firmwares:

- 3.00
- 3.10
- 3.20
- 3.21
- 4.00
- 4.02
- 4.03
- 4.50
- 4.51




## Currently Included

- Obtains arbitrary read/write and can run a basic RPC server for reads/writes (or a dump server for large reads) (must edit your own address/port into the exploit file on lines 673-677)
- Enables debug settings menu (note: you will have to fully exit settings and go back in to see it).
- Gets root privileges




## Limitations
- This exploit achieves read/write, **but not code execution**. This is because we cannot currently dump kernel code for gadgets, as kernel .text pages are marked as eXecute Only Memory (XOM). Attempting to read kernel .text pointers will panic!
- As per the above + the hypervisor (HV) enforcing kernel write protection, this exploit also **cannot install any patches or hooks into kernel space**, which means no homebrew-related code for the time being.
- Clang-based fine-grained Control Flow Integrity (CFI) is present and enforced.
- Supervisor Mode Access Prevention/Execution (SMAP/SMEP) cannot be disabled, due to the HV.
- The write primitive is somewhat constrained, as bytes 0x10-0x14 must be zero (or a valid network interface).
  - Though due to newer work using pipes, full arbitrary read/write is now possible




## How to use

1. Configure fakedns via `dns.conf` to point `manuals.playstation.net` to your PCs IP address
2. Run fake dns: `python fakedns.py -c dns.conf`
3. Run HTTPS server: `python host.py`
4. Go into PS5 advanced network settings and set primary DNS to your PCs IP address and leave secondary at `0.0.0.0`
   1. Sometimes the manual still won't load and a restart is needed, unsure why it's really weird
5. Go to user manual in settings and accept untrusted certificate prompt, run
6. Optional: Run rpc/dump server scripts (note: address/port must be substituted in binary form into exploit.js).



## Future work
- [x] ~~Fix-up sockets to exit browser cleanly (top prio)~~
- [x] ~~Write some data patches (second prio)~~
  - [x] ~~Enable debug settings~~
  - [x] ~~Patch creds for uid0~~
  - [x] ~~Jailbreak w/ cr_prison overwrite~~
- [x] ~~Improve UAF reliability~~
- [x] ~~Improve victim socket reliability (third prio)~~
- [x] ~~Use a better / more consistent leak target than kqueue~~ (no longer necessary)
- [x] Make ELF loader support relocations
  - [ ] Add support for more relocations and possibly full dynamic linkage?




## Using ELF Loader

To use the ELF loader, run the exploit until completion. Upon completion it'll run a server on port `:9020`. Connect and send your ELF to the PS5 over that port and it'll run it. Assuming the ELF doesn't crash the browser, it can continue to run ELFs forever.



## Exploit Stages
This exploit works in 5 stages, and for the most part follows the same exploit strategy as theflow's poc.
1) Trigger the initial UAF on `ip6_pktopts` and get two sockets to point to the same `pktopts` / overlap (master socket <-> overlap spray socket)
2) Free the `pktopts` on the master socket and fake it with an `ip6_rthdr` spray containing a tagged `tclass` overlap.
3) Infoleak step. Use `pktopts`/`rthdr` overlap to leak a kqueue from the 0x200 slab and `pktopts` from the 0x100 slab.
4) Arbitrary read/write step. Fake `pktopts` again and find the overlap socket to use `IPV6_RTHDR` as a read/write primitive.
4) Cleanup + patch step. Increase refcount on corrupted sockets for successful browser exit + patch data to enable debug menu and patch ucreds for uid0.
4) Run ELF loader server that will accept and load/run ELFs. Currently WIP, does not support relocations at the moment.



## Stability Notes
Stability for this exploit is at about ~~30%~~ 80-90%, and has two potential points of failure. In order of observed descending liklihood:
1) *Stage 1* fails to reclaim the UAF, causing immediate crash or latent corruption that causes crash.
2) *Stage 4* fails to find a victim socket



## Research Notes
- ~~It appears based on various testing and dumping with the read primitive, that the PS5 has reverted back to 0x1000 page size compared to the PS4's 0x4000.~~
  - After further research, the page size is indeed still 0x4000, however due to some insane allocator changes, different slabs can be allocated in the same virtual page.

- It also seems on PS5 that adjacent pages rarely belong to the same slab, as you'll get vastly different data in adjacent pages. Memory layout seems more scattered.
- Often when the PS5 panics (at least in webkit context), there will be awful audio output as the audio buffer gets corrupted in some way.
- Sometimes this audio corruption persists to the next boot, unsure why.
- Similar to PS4, the PS5 will require the power button to be manually pressed on the console twice to restart after a panic.
- It is normal for the PS5 to take an absurd amount of time to reboot from a panic if it's isolated from the internet (unfortunately). Expect boot to take 3-4 minutes.



## Contributors / Special Thanks
- [Andy Nguyen / theflow0](https://twitter.com/theflow0) - Vulnerability and exploit strategy
- [ChendoChap](https://github.com/ChendoChap) - Various help with testing and research
- [Znullptr](https://twitter.com/Znullptr) - Research/RE
- [sleirsgoevy](https://twitter.com/sleirsgoevy) - Research/RE + exploit strat ideas
- [bigboss](https://twitter.com/psxdev) - Research/RE
- [flatz](https://twitter.com/flat_z) - Research/RE + help w/ patches
- [zecoxao](https://twitter.com/notzecoxao) - Research/RE
- [SocracticBliss](https://twitter.com/SocraticBliss) - Research/RE
- laureeeeeee - Background low-level systems knowledge and assistance



## Thanks to testers

- Dizz (4.50/4.51)
