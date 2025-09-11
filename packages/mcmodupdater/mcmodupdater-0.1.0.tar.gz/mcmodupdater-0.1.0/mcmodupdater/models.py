# -*- coding: utf-8 -*-
"""
"""

from typing import (
    TypeVar,
    List
)

MOD = TypeVar("Mod")
MODFILE = TypeVar("ModFile")



class CurseForgeAPI:
    base = "https://api.curseforge.com"
    minecraftId = 432
    games = "/v1/games"
    mods_search = "/v1/mods/search"
    categories = "/v1/categories"
    getMod = "/v1/mods/MODID"  # GET
    getModFiles = "/v1/mods/MODID/files"  # GET
    getFile = "/v1/mods/MODID/files/FILEID"  # GET
    postGetFiles = "/v1/mods/files"  # POST
    postFingerprints = "/v1/fingerprints/432"  # POST
    mod_loader = {
        "forge": 1,
        "cauldron": 2,
        "liteloader": 3,
        "fabric": 4,
        "quilt": 5,
        "neoforge": 6,
    }
    gameVersionTypeId = {
        "forge": 3,
        "fabric": 73247,
        "quilt": 76692,
        "neoforge": 76994,
    }
    releaseType = {
        "release": 1,
        "beta": 2,
        "alpha": 3,
    }
    sortField = {
        "featured": 1,
        "popularity": 2,
        "lastupdated": 3,
        "name": 4,
        "author": 5,
        "totaldownloads": 6,
        "category": 7,
        "gameversion": 8,
        "earlyaccess": 9,
        "featuredreleased": 10,
        "releaseddate": 11,
        "rating": 12,
    }

    @staticmethod
    def getModLoaderId(
        modloader: str
    ) -> int:
        """
        """
        try:
            return CurseForgeAPI.mod_loader[modloader]
        except KeyError as e:
            return CurseForgeAPI.mod_loader["forge"]


# class Mod:
#     def __init__(
#         self,
#         name: str,
#         filename: str,
#         slug: str,
#         modId: int = None,
#         fileId: int = None,
#         releaseType: int = None,
#         modLoader: int = None,
#         version: str = None,
#         in_db: bool = False,
#     ) -> None:
#         """
#         """
#         self.name = name
#         self.filename = filename
#         self.slug = slug
#         self.modId = modId
#         self.fileId = fileId
#         self.releaseType = releaseType
#         self.modLoader = modLoader
#         self.version = version
#         self.in_db = in_db
#
#         self.fileFingerprint = 0
#         self.downloadUrl = None
#
#     def __lt__(self, other: MOD) -> bool:
#         """
#         """
#         return self.name < other.name
#
#     def __str__(self) -> str:
#         """
#         """
#         return "Slug: %s, FileId: %s, ReleaseType: %s" % (
#                         self.slug,
#                         str(self.fileId),
#                         self.releaseType
#                     )
#
#     def __repr__(self) -> str:
#         """
#         """
#         return "<[Mod: %s]>" % self.__str__()



class ModFile:
    def __init__(
        self,
        id: int = None,
        modId: int = None,
        displayName: str = None,
        fileName: str = None,
        releaseType: int = None,
        fileLength: int = None,
        downloadUrl: str = None,
        dependencies: List[MODFILE] = [],
        fileFingerprint: int = None,
    ) -> None:
        """
        """
        self.id = id
        self.modId = modId
        self.displayName = displayName
        self.fileName = fileName
        self.downloadUrl = downloadUrl
        self.fileFingerprint = fileFingerprint
        self.dependencies = dependencies
        self.fileLength = fileLength
        self.releaseType = releaseType
        self.is_download = False

    def size(self) -> str:
        """
        """
        if self.fileLength is None:
            return "%.3f" % (0)
        return "%.3f" % (self.fileLength / (1024 * 1024))

    def get_releaseType(
        self,
        value: int
    ) -> str:
        """
        """
        try:
            d = {v: k for k,v in CurseForgeAPI.releaseType.items()}
            return d[value]
        except KeyError as e:
            return None

    def get_fileName_downloadUrl(self) -> tuple:
        """
        """
        return self.fileName, self.downloadUrl

    def __lt__(self, other: MODFILE) -> bool:
        """
        """
        return self.modId < other.modId

    def __eq__(self, other: MODFILE) -> bool:
        """
        """
        return any([self.modId == other.modId, self.id == other.id])

    def __hash__(self) -> int:
        """
        """
        return hash(self.id) + hash(self.modId)

    def __str__(self) -> str:
        """
        """
        return "Name: %s, %s, %s mb" % (
                        self.fileName,
                        self.get_releaseType(self.releaseType),
                        self.size(),
                    )

    def __repr__(self) -> str:
        """
        """
        return "<[Mod: %s]>" % self.__str__()
