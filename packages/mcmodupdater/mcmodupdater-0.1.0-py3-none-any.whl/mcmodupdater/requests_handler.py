# -*- coding: utf-8 -*-
"""
"""

from mcmodupdater.models import CurseForgeAPI


import requests
import json

from typing import (
    Union,
    List,
)


class RequestData:

    ERROR_CODE_ = 777

    @staticmethod
    def __get(
        api_key: str,
        url: str,
        params: dict = {},
    ) -> requests.Response:
        """
        """
        try:
            headers = RequestData.__headers(api_key)
            req = requests.get(url, headers=headers, params=params)
            return req
        except Exception as e:
            fake_response = requests.Response()
            fake_response.status_code = RequestData.ERROR_CODE_
            fake_response._content = str(e).encode("utf-8")
            fake_response.url = url
            fake_response.is_fake = True
            return fake_response

    @staticmethod
    def __post(
        api_key: str,
        url: str,
        body: dict,
    ) -> requests.Response:
        """
        """
        headers = RequestData.__headers(api_key)
        headers["Content-Type"] = "application/json"

        try:
            res = requests.post(
                            url,
                            headers=headers,
                            json=body
                        )
            return res
        except Exception as e:
            fake_response = requests.Response()
            fake_response.status_code = RequestData.ERROR_CODE_
            fake_response._content = str(e).encode("utf-8")
            fake_response.url = url
            fake_response.is_fake = True
            return fake_response

    @staticmethod
    def __headers(
        api_key: str
    ) -> dict:
        """
        """
        return {
          "Accept": "application/json",
          "x-api-key": api_key
        }

    @staticmethod
    def search_mod(
        api_key: str,
        version: str,
        modloader: str,
        name: str,
        sortField: str = "lastupdated",
        index: int = 0,
    ) -> list:
        """
        """
        results = []

        url = CurseForgeAPI.base + CurseForgeAPI.mods_search,
        params={
                "gameId": 432,  # minecraft
                # "gameVersion": version,
                "gameVersions": [version, modloader],
                "modLoaderType": CurseForgeAPI.mod_loader[modloader],
                "classId": 6,
                # "slug": name,
                "searchFilter": name,
                "sortField": CurseForgeAPI.sortField[sortField],
                "sortOrder": "desc",
                "index": index,
                "pageSize": 50,
            }

        req = RequestData.__get(api_key, url, params)

        if req.status_code == 200:
            data = req.json()
            results += data["data"]

            pageSize = data["pagination"]["pageSize"]
            total = data["pagination"]["totalCount"]

            if int(total) > int(pageSize):
                for i in range(1, total // pageSize + 1):
                    params["index"] = pageSize * i
                    req = RequestData.__get(api_key, url, params)
                    if req.status_code == 200:
                        results += req.json()["data"]

        return results


    @staticmethod
    def get_file(
        modId: int,
        fileId: int,
        api_key: str
    ) -> dict:
        """
        """
        url = CurseForgeAPI.getFile
        url = url.replace("MODID", str(modId))
        url = url.replace("FILEID", str(fileId))

        url = CurseForgeAPI.base + url

        req = RequestData.__get(api_key, url)

        if req.status_code == 200:
            return res.json()["data"]
        else:
            return {}

    @staticmethod
    def get_files(
        api_key: str,
        filesIds: list,
    ) -> list:
        """
        """
        # print(filesIds)
        body = {"fileIds": filesIds}
        url = CurseForgeAPI.base + CurseForgeAPI.postGetFiles
        req = RequestData.__post(api_key, url, body)
        if req.status_code == 200:
            return req.json()["data"]
        return []

    @staticmethod
    def get_files_by_fingerprints(
        api_key: str,
        fingerprints: List[int],
    ) -> dict:
        """
        Request information about mods using fingerprints, maximum 100/request.
        """
        if isinstance(fingerprints, int):
            fingerprints = [fingerprints]

        # print(api_key, fingerprints)

        body = {
            "gameId": 432,
            "fingerprints": fingerprints
        }
        url = CurseForgeAPI.base + CurseForgeAPI.postFingerprints

        req = RequestData.__post(api_key, url, body)
        if req.status_code == 200:
            return req.json()["data"]
        else:
            return {}

    @staticmethod
    def getModFiles(
        api_key: str,
        modId: int,
        gameVersion: str,
        modLoaderType: int,
        index: int = 0,
    ) -> dict:
        """
        """
        results = []

        endpoint = CurseForgeAPI.getModFiles.replace("MODID", str(modId))
        url = CurseForgeAPI.base + endpoint

        params = {
            "modId": modId,
            "gameVersion": gameVersion,
            "modLoaderType": modLoaderType,
            "index": index,
            "pageSize": 50,
        }

        req = RequestData.__get(api_key, url, params)

        if req.status_code == 200:
            data = req.json()
            results += data["data"]

            pageSize = data["pagination"]["pageSize"]
            total = data["pagination"]["totalCount"]

            if int(total) > int(pageSize):
                for i in range(1, total // pageSize + 1):
                    params["index"] = pageSize * i
                    req = RequestData.__get(api_key, url, params)
                    if req.status_code == 200:
                        results += req.json()["data"]

        return {modId: results}

    @staticmethod
    def getMod(
        api_key: str,
        modid: int
    ) -> dict:
        """
        """
        data = {}
        endpoint = CurseForgeAPI.getMod.replace("MODID", str(modid))
        url = CurseForgeAPI.base + endpoint

        req = RequestData.__get(api_key, url)

        if req.status_code == 200:
            data = req.json()["data"]
        return data

    @staticmethod
    def download_file(
        url: str,
    ) -> bytes:
        """
        """
        data = bytes()
        with requests.get(url, stream=True) as req:
            for chunk in req.iter_content(chunk_size=8192):
                if chunk:
                    data += chunk
                else:
                    print(url)
        return data
