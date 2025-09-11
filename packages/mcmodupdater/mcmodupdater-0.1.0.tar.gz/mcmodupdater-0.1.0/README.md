# mcmodupdater

Automates the task of updating mods.

In case of errors, it will generate a report with the address of the mod project that could not be updated.

> [!IMPORTANT]
> You need a CurseForge API key, go to `https://docs.curseforge.com/rest-api/`, follow the instructions to create a account and gets your key and store carefully.
>

> ![NOTE]
> Some mods, due to their license, do not display the download URLs for the version you are looking for, in which case you will have to visit and download these mods manually.
> In these cases, `mcmodupdater` will show you the address of the mod project with this situation so you can download it manually.
>
> Downloaded mods are stored on the *desktop* in the “mods_updated” directory.
> If the mod update fails, a report (txt) will be generated on the *desktop* with the name “failed_mod_updates.txt,” which will contain the name of the mod project and its URL.


# Installation

```bash
$ pip install mcmodupdater
```


# Usage - CLI

```text
$ mcmodupdater --help
usage: mcmodupdater [-h] -k KEY_API [-p PATH] [-m {forge,cauldron,liteloader,fabric,quilt,neoforge}] [-v VERSION] [--only-release] [--report-failed]

Update mods automatically from CurseForge API.

optional arguments:
  -h, --help            show this help message and exit
  -k KEY_API, --key-api KEY_API
                        Key of CurseForge API. Remember to use single quotes. https://docs.curseforge.com/rest-api/.
  -p PATH, --path PATH  Mods directory path.
  -m {forge,cauldron,liteloader,fabric,quilt,neoforge}, --modloader {forge,cauldron,liteloader,fabric,quilt,neoforge}
                        Modloader used by mods.
  -v VERSION, --version VERSION
                        Version used by mods. For example: '1.21.8', '1.21'.
  --only-release        Only mods with status 'release'. Default is 'True', 'release', 'alpha' and 'beta' are included.
  --report-failed       Some mods cannot be updated; you will get the URL of the official website to try manual download.

Automates the tedious task of updating mods, ;).
```


```bash
$ mcmodupdater -k 'api_key_string' -p DIRECTORY_MODS -m forge -v 1.21.8 --report-failed
```
