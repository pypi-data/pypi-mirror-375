# -*- coding: utf-8 -*-
"""
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock


from time import sleep

from typing import Union


class ThreadExecutor:
    """
    """

    @staticmethod
    def status(
        operation: str,
        index: list,
        total: int,
        lock: Lock
    ) -> None:
        """
        """
        with lock:
            percent = (index[0] / total) * 100

            msg = f"\r\t{operation}:".ljust(22)
            msg += f"\t{index[0]}-{total}"
            msg += f"  ({percent:.2f}%)"
            print(msg, end="", flush=True)

            if index[0] >= total:
                print("\n")
                return

            index[0] = index[0] + 1
            sleep(0.2)

    @staticmethod
    def to_thread(
        function: callable,
        operation: str = None,
        single_queries: Union[bool, None] = False,
        workers: int = 1,
        *args,
        **kwargs,
    ) -> list:
        """
        10 queries
        """
        lock = Lock()
        index = [0]
        total = len(args[0])
        resultados = []

        if operation is not None:
            ThreadExecutor.status(
                                operation=operation,
                                index=index,
                                total=total,
                                lock=lock,
                            )

        i = 0
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = []
            for args_function in args[0]:

                if not isinstance(args_function, (list, tuple)):
                    args_function = [args_function]

                futures.append(
                    executor.submit(
                            function,
                            *args_function
                    )
                )

                if single_queries is None:
                    pass
                else:
                    if single_queries:
                        i+=1
                        if i % 10 == 0:
                            sleep(0.5)
                    else:
                        sleep(0.5)

            for future in as_completed(futures):

                result = future.result()
                resultados.append(result)

                if operation is not None:
                    ThreadExecutor.status(
                                        operation=operation,
                                        index=index,
                                        total=total,
                                        lock=lock,
                                    )

        return resultados
