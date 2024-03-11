import os, sys
import asyncio
import orjson

from datetime import datetime
from typing import List

FILENAME = os.path.basename(__file__)
BASEPATH = os.path.dirname(__file__)
UTILPATH = os.path.dirname(BASEPATH)

sys.path.append(UTILPATH)

# from common import get_preprocessed_words
from push_data_colwise import do_gather_task_push_value, do_push_value, func_summary
from module_summarizer import get_summaries_of_csv_file
from common import Logger
from basetype import RedisDocKeys

if __name__ == "__main__":
    logpath = os.path.join(UTILPATH, "logger.log")
    logger = Logger(logpath)

    logger.log_event("info", f"{FILENAME} - Start script")

    today = datetime.now()
    today_str = today.strftime("%Y%m%d")
    today_str_dash = today.strftime("%Y-%m-%d")

    folder_path = os.path.join(UTILPATH, "data", today_str)

    inputfile = os.path.join(folder_path, f"data_{today_str}.csv")
    outputpath = os.path.join(folder_path, f"summary.json")

    logger.log_event("info", f"{FILENAME} - Generating the summary")
    results = get_summaries_of_csv_file(
        inputfile, number_of_initial_sentences_to_skip=2
    )

    logger.log_event("info", f"{FILENAME} - Dumping the data into JSON")
    with open(outputpath, "wb") as file:
        file.write(orjson.dumps(results))

    logger.log_event("info", f"{FILENAME} - Updating the data on Redis")
    asyncio.run(do_gather_task_push_value(results, RedisDocKeys.summary, func_summary))
    logger.log_event("info", f"{FILENAME} - Done")
