# -*- coding: utf-8 -*-
"""
`PathClass` in charge of managing the paths.
"""

import os
import shutil
import platformdirs

from typing import Tuple


class PathClass:

    __sep = os.path.sep

    @classmethod
    @property
    def separator(cls) -> str:
        """
        """
        return cls.__sep

    @classmethod
    @property
    def get_home(cls) -> str:
        """
        """
        return cls.expanduser("~")

    def get_desktop() -> str:
        """
        """
        return platformdirs.user_desktop_dir()

    def user_config_dir(
        name: str
    ) -> str:
        return platformdirs.user_config_dir(name)

    def openfile(
        path: str
    ) -> None:
        """
        """
        os.startfile(path)

    def absolute_path(
        path: str
    ) -> str:
        """
        """
        return os.path.abspath(path=path)

    def delete_file(
        path: str
    ) -> bool:
        """
        """
        return os.remove(path)

    def delete_directory(
        path: str
    ) -> bool:
        """
        """
        try:
            shutil.rmtree(path=path)
            return True
        except Exception as e:
            print(e)
            return False

    def is_file(
        path: str
    ) -> bool:
        """
        """
        return os.path.isfile(path)

    def is_dir(
        path: str
    ) -> bool:
        """
        """
        return os.path.isdir(path)

    def listdir(
        path: str = ""
    ) -> None:
        """
        """
        if path != "":
            return os.listdir(path)
        return os.listdir()

    def dirname(
        path: str
    ) -> str:
        """
        """
        return os.path.dirname(path)

    def basename(
        path: str
    ) -> str:
        """
        """
        return os.path.basename(path)

    def splitext(
        path: str
    ) -> Tuple[str]:
        """
        """
        return os.path.splitext(PathClass.basename(path))

    def expanduser(
        path: str
    ) -> str:
        return os.path.expanduser(path)

    def join(
        *path: str
    ) -> str:
        """
        """
        # return os.path.join(f"{os.path.sep}".join(*path))
        return os.path.join(*path)

    def exists(
        path: str
    ) -> bool:
        """
        """
        return os.path.exists(path)

    def realpath(
        path: str
    ) -> str:
        """
        """
        return os.path.realpath(path)

    def makedirs(
        path: str
    ) -> bool:
        try:
            os.makedirs(path)
        except FileExistsError:
            pass
        return PathClass.exists(path)
