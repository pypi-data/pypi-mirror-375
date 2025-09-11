# -*- coding: utf-8 -*-
"""
"""

from mcmodupdater.main import ModUpdater

from mcmodupdater.utils import check_version_format


import argparse


def main():
    main_parser = argparse.ArgumentParser(
        prog="mcmodupdater",
        description="Update mods automatically from CurseForge API.",
        epilog="Automates the tedious task of updating mods, ;)."
    )

    main_parser.add_argument(
        "-k",
        "--key-api",
        type=str,
        required=True,
        help="Key of CurseForge API. Remember to use single quotes. https://docs.curseforge.com/rest-api/.",
    )

    main_parser.add_argument(
        "-p",
        "--path",
        help="Mods directory path.",
    )

    main_parser.add_argument(
        "-m",
        "--modloader",
        default="forge",
        choices=[
            "forge", "cauldron", "liteloader", "fabric", "quilt", "neoforge"
        ],
        help="Modloader used by mods.",
    )

    main_parser.add_argument(
        "-v",
        "--version",
        help="Version used by mods. For example: '1.21.8', '1.21'.",
    )

    main_parser.add_argument(
        "--only-release",
        default=False,
        action="store_true",
        help="Only mods with status 'release'. Default is 'True', 'release', 'alpha' and 'beta' are included.",
    )

    main_parser.add_argument(
        "--report-failed",
        default=False,
        action="store_true",
        help="Some mods cannot be updated; you will get the URL of the official website to try manual download.",
    )

    args = main_parser.parse_args()

    key_api = args.key_api
    path = args.path
    modloader = args.modloader
    version = args.version
    only_release = args.only_release
    report_failed = args.report_failed

    if not check_version_format(version=version):
        print("The argument `-v|--version` is not in the correct format.")
        return

    try:
        with ModUpdater(
            api_key=key_api,
            modloader=modloader,
            auto_report=report_failed,
        ) as updater:
            data = updater.from_path(
                                path=path,
                                version=version,
                                only_release=only_release
                            )
            updater.download_files(modfiles=data)
            if report_failed:
                if updater.some_errors():
                    report_data = updater.report_failed_updates()

                    msg = "-- Manual update is required."
                    msg += " Visit the links to download the corresponding mod. --\n"
                    print(msg)
                    for name, link  in report_data:
                        print(f"{name},  {link}")
                    print()

    except (Exception, KeyboardInterrupt) as e:
        print(e)



if __name__ == '__main__':
    main()
