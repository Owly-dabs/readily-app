#!/usr/bin/env python3

import fire
from indexer import parse, main, search
from extractor import extract

if __name__ == "__main__":
    fire.Fire(
        {
            "parse": parse,
            "index": main,
            "search": search,
            "extract": extract,
        }
    )
