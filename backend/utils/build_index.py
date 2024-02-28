import re
import orjson
import traceback
import os
import time
import threading
from collections import defaultdict
from typing import DefaultDict, Dict, List
from common import (
    read_binary_file,
    get_preprocessed_words,
    load_batch_from_news_source,
    save_json_file,
    load_json_file,
    get_indices_for_news_data,
)
from basetype import (
    InvertedIndex,
    InvertedIndexMetadata,
    NewsArticleData,
    NewsArticlesFragment,
    NewsArticlesBatch,
    default_dict_list,
)
from constant import Source, CHILD_INDEX_PATH, GLOBAL_INDEX_PATH
from datetime import date
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

CURRENT_DIR = os.getcwd()
NUM_OF_CORES = os.cpu_count() or 1


def process_batch(
    fragment_list: List[NewsArticlesFragment],
    inverted_index: InvertedIndex,
    stopping: bool = True,
    stemming: bool = True,
) -> None:
    local_index = defaultdict(dict)
    for fragment in fragment_list:
        for article in fragment.articles:
            doc_id = article.doc_id
            doc_text = article.title + "\n" + article.content
            text_words = get_preprocessed_words(doc_text, stopping, stemming)
            for position, word in enumerate(text_words):
                if doc_id not in local_index[word]:
                    local_index[word][doc_id] = []
                local_index[word][doc_id].append(position + 1)
    try:
        for word in local_index:
            for doc_id in local_index[word]:
                inverted_index.index[word][doc_id] += local_index[word][doc_id]
    except:
        print("Error processing batch")
        traceback.print_exc()
        exit()


def positional_inverted_index(
    news_batch: NewsArticlesBatch,
    stopping: bool = True,
    stemming: bool = True,
) -> InvertedIndex:
    doc_ids = news_batch.doc_ids
    document_size = len(doc_ids)
    inverted_index_meta = InvertedIndexMetadata(
        document_size=document_size, doc_ids_list=doc_ids
    )

    inverted_index = InvertedIndex(
        meta=inverted_index_meta, index=defaultdict(default_dict_list)
    )

    # cut the fragments into batches
    for source, fragments in news_batch.fragments.items():
        curr_time = time.time()
        batch_size = len(fragments) // NUM_OF_CORES
        remainder = len(fragments) % NUM_OF_CORES
        batches = [
            fragments[i * batch_size : (i + 1) * batch_size]
            for i in range(NUM_OF_CORES)
        ]
        if remainder != 0:
            # append the remainder to the last batch
            batches[-1] += fragments[-remainder:]

        with ThreadPoolExecutor(max_workers=NUM_OF_CORES) as executor:
            futures = [
                executor.submit(
                    process_batch, batch, inverted_index, stopping, stemming
                )
                for batch in batches
            ]

        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"Error processing batch: {e}")
                traceback.print_exc()
                exit()

        print(
            f"Time taken for processing {source}: {time.time() - curr_time:.2f} seconds"
        )

    return inverted_index


# save as binary file
def save_index_file(
    file_name: str,
    index: DefaultDict[str, Dict[str, list]],
    output_dir: str = "binary_file",
):
    if not os.path.exists(os.path.join(CURRENT_DIR, output_dir)):
        os.mkdir(os.path.join(CURRENT_DIR, output_dir))
    # sort index by term and doc_id in int
    index_output = dict(sorted(index.items()))
    for term, record in index_output.items():
        if term == "document_size" or term == "doc_ids_list":
            continue
        index_output[term] = dict(sorted(record.items(), key=lambda x: int(x[0])))

    with open(os.path.join(CURRENT_DIR, output_dir, file_name), "wb") as f:
        for term, record in index_output.items():
            if term == "document_size" or term == "doc_ids_list":
                continue
            f.write(f"{term} {len(record)}\n".encode("utf8"))
            for doc_id, positions in record.items():
                f.write(
                    f"\t{doc_id}: {','.join([str(pos) for pos in positions])}\n".encode(
                        "utf8"
                    )
                )


def load_binary_index(file_name: str, output_dir: str = "binary_file") -> dict:
    with open(os.path.join(CURRENT_DIR, output_dir, file_name), "rb") as f:
        data = f.read().decode("utf8")
    return orjson.loads(data)


def merge_inverted_indices(
    global_index: DefaultDict[str, DefaultDict[str, List[int]]],
    child_index: DefaultDict[str, DefaultDict[str, List[int]]],
):

    if not global_index:
        global_index.update(child_index)
        return

    child_index_set = set(child_index.keys())
    global_index_set = set(global_index.keys())
    new_keys = child_index_set - global_index_set
    common_keys = child_index_set & global_index_set

    # the docID must be new!
    for key in new_keys:
        global_index[key] = child_index[key]

    for key in common_keys:
        for doc_id in child_index[key]:
            if doc_id not in global_index[key]:
                global_index[key][doc_id] = child_index[key][doc_id]
            elif doc_id in global_index[key]:
                print(
                    "WARNING: Trying to add new documents under the same doc ID!",
                    key,
                    doc_id,
                )


def delta_encode_list(positions):
    """Convert a list of positions into a delta-encoded list."""
    if not positions:
        return []
    # The first position remains the same, others are differences from the previous one
    delta_encoded = [positions[0]] + [
        positions[i] - positions[i - 1] for i in range(1, len(positions))
    ]
    return delta_encoded


def delta_decode_list(delta_encoded):
    """Reconstruct the original list of positions from a delta-encoded list."""
    positions = [delta_encoded[0]] if delta_encoded else []
    for delta in delta_encoded[1:]:
        positions.append(positions[-1] + delta)
    return positions


# def save_delta_index_file(
#     file_name: str,
#     index: DefaultDict[str, Dict[str, list]],
#     output_dir: str = "binary_file",
# ):
#     if not os.path.exists(os.path.join(CURRENT_DIR, output_dir)):
#         os.mkdir(os.path.join(CURRENT_DIR, output_dir))
#     index_output = dict(sorted(index.items()))
#     with open(os.path.join(CURRENT_DIR, output_dir, file_name), "wb") as f:
#         for term, record in index_output.items():
#             if term == "document_size" or term == "doc_ids_list":
#                 continue
#             record = dict(sorted(record.items(), key=lambda x: int(x[0])))
#             f.write(f"{term} {len(record)}\n".encode("utf8"))
#             for doc_id, positions in record.items():
#                 # Apply delta encoding here
#                 delta_positions = delta_encode_positions(positions)
#                 # Convert delta-encoded positions back to strings for storage
#                 positions_str = ",".join(str(pos) for pos in delta_positions)
#                 f.write(f"\t{doc_id}: {positions_str}\n".encode("utf8"))


# def decode_positions(data):
#     """Recursively decode delta-encoded position lists in the index data."""
#     if isinstance(data, dict):
#         return {key: decode_positions(value) for key, value in data.items()}
#     elif isinstance(data, list) and all(isinstance(x, int) for x in data):
#         # Assuming the list is of integers, decode it if it's delta-encoded
#         return delta_decode_positions(data)
#     else:
#         return data


def encode_index(index: DefaultDict[str, Dict[str, list]]):
    for term, record in index.items():
        for doc_id, positions in record.items():
            index[term][doc_id] = delta_encode_list(positions)


def decode_index(index: DefaultDict[str, Dict[str, list]]):
    for term, record in index.items():
        for doc_id, positions in record.items():
            index[term][doc_id] = delta_decode_list(positions)


# def load_delta_encoded_index(file_name: str, output_dir: str = "binary_file") -> dict:
#     path = os.path.join(CURRENT_DIR, output_dir, file_name)
#     with open(path, "rb") as f:
#         data = orjson.loads(f.read().decode("utf8"))

#     # Apply delta decoding to the loaded data
#     index = decode_positions(data)
#     return index


def build_child_index(
    source: Source,
    date: date,
    interval=10,
):
    # file name format: {source_name}_{YYYY-MM-DD}_{start_number}_{end_number}.json
    time_str = date.strftime("%Y-%m-%d")
    pattern = re.compile(f"{source.value}_{time_str}_([0-9]+)_([0-9]+).json")
    last_index = -1
    if os.path.exists(CHILD_INDEX_PATH):
        child_index_file_list = [
            file for file in os.listdir(CHILD_INDEX_PATH) if pattern.match(file)
        ]
        print(child_index_file_list)
        for file in child_index_file_list:
            # split by .csv
            file_name = file.split(".")[0]
            # split by _
            file_info = file_name.split("_")
            if int(file_info[-1]) > last_index:
                last_index = int(file_info[-1])

    indices = get_indices_for_news_data(source.value, date)

    # prune the indices
    indices = [index for index in indices if index > last_index]

    # divide the indices into intervals
    indices_batches = [
        indices[i : i + interval] for i in range(0, len(indices), interval)
    ]
    for indices_batch in indices_batches:
        news_batch = load_batch_from_news_source(
            source, date, indices_batch[0], indices_batch[-1]
        )
        inverted_index = positional_inverted_index(news_batch)
        encode_index(inverted_index.index)
        save_json_file(
            f"{source.value}_{date}_{indices_batch[0]}_{indices_batch[-1]}.json",
            inverted_index.model_dump(),
            "index/child",
        )



if __name__ == "__main__":
    print("building")
    tasks = [
        # (Source.BBC, date(2024, 2, 17)),
        # (Source.IND, date(2024, 2, 18)),
        # (Source.GBN, date(2024, 2, 18)),
        (Source.TELE, date(2024, 2, 16))
    ]
    build_child_index(Source.TELE, date(2024, 2, 16))
    # with ProcessPoolExecutor(max_workers=4) as executor:
    #     executor.map(build_child_index, *zip(*tasks))
