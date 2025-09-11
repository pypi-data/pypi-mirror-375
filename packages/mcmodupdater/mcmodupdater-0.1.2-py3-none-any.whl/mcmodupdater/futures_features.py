# -*- coding: utf-8 -*-
"""
Futures tasks
"""


    def from_file(
        self,
        file: str,
        version: str,
        filters: list = [],
        only_release: bool = True
    ) -> dict:
        """
        """
        if PathClass.is_file(file) is False:
            return

        data = load_data(file)
        modelsData = self.to_model(
                            data=data,
                            filters=filters,
                        )

        modelsData.sort()

        mods = []

        for i in range(0, len(modelsData), 5):
            # print("Chunk ", 0 + i, 5 + i)
            # print(modelsData[0 + i : 5 + i])
            # if i == 120:
            for item in modelsData[0 + i : 5 + i]:
                print(item)

                x = self.search_mod(
                    name=item.name,
                    version=version,
                    only_release=only_release
                )
                # mods.append(x)
                if len(x) == 0:
                    print(item.name, len(x))
                sleep(1)




    def search_mod(
        self,
        name: str,
        version: str = "last",
        only_release: bool = True
    ) -> dict:
        """
        """
        # name = name.lower()

        results = RequestData.search_mod(
            api_key=self.api_key,
            version=version,
            modloader=self.modloader,
            name=name,
            sortField="lastupdated",
        )

        # print(len(results))
        mod_matches = []

        for item in results:
            for it in item["latestFilesIndexes"]:
                if name == it["filename"]:
                    # print(it["filename"])
                    if it["gameVersion"] == version:
                        if "modLoader" in it:
                            # print(">", item["name"])
                            mod = ModFile(
                                name=item["name"],
                                filename=it["filename"],
                                slug=item["slug"],
                                modId=item["id"],
                                fileId=it["fileId"],
                                modLoader=it["modLoader"],
                                releaseType=it["releaseType"],
                                version=it["gameVersion"],
                            )
                            mod_matches.append(mod)

        if len(mod_matches) == 0:
            print(name)




        # for item in results:
        #     n = item["name"].lower().replace(" ", "")
        #     # print(n, get_names_flat(n))
        #     if name in get_names_flat(n):
        #         for it in item["latestFilesIndexes"]:
        #             if it["gameVersion"] == version:
        #                 if "modLoader" in it:
        #                     # print(item["name"])
        #                     mod = ModFile(
        #                         name=item["name"],
        #                         filename=it["filename"],
        #                         slug=item["slug"],
        #                         modId=item["id"],
        #                         fileId=it["fileId"],
        #                         modLoader=it["modLoader"],
        #                         releaseType=it["releaseType"],
        #                         version=it["gameVersion"],
        #                     )
        #                     mod_matches.append(mod)
        #
        # files = []
        # for mod in mod_matches:
        #     if mod.releaseType is not None:
        #         if only_release:
        #             if int(mod.releaseType) == CurseForgeAPI.releaseType["release"]:
        #                 files.append(mod)
        #         else:
        #             files.append(mod)

                # print(files)
                # matches[item["name"]] = files
        # return files


    def to_model(
        self,
        data: list,
        # filepath: str,
        filters: list = []
    ) -> list:
        """
        """
        filters = filters + default_filters
        # data = load_data(path=filepath)
        data_clean = clear_data(
                            data=data,
                            custom_filters=filters,
                        )
        return get_models(data_clean)
