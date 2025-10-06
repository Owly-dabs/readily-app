#!/usr/bin/env python3

import fire
from indexer import parse, main, search

if __name__ == "__main__":
    fire.Fire(
        {
            "parse": parse,
            "index": main,
            "search": search,
        }
    )
