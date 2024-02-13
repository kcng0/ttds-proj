import re
from nltk.stem import PorterStemmer
from xml.dom import minidom
from bs4 import BeautifulSoup
import json
import traceback
import os
import time
import threading
from collections import defaultdict
import math
from typing import DefaultDict, Dict

STOP_WORDS_FILE = "ttds_2023_english_stop_words.txt"
XML_FILES = ["sample.xml", "trec.sample.xml", "trec.5000.xml"]
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
NUM_OF_CORES = os.cpu_count()
SPECIAL_PATTERN = {
    'proximity': re.compile(r"#(\d+)\((\w+),\s*(\w+)\)"),
    'exact': re.compile(r"\"[^\"]+\""),
    'spliter': re.compile(r"(AND|OR|NOT|#\d+\(\w+,\s*\w+\)|\"[^\"]+\"|\'[^\']+\'|\w+|\(|\))")
}

lock = threading.Lock()

def read_file(file_name: str) -> str:
    with open(os.path.join(CURRENT_DIR, file_name), "r", encoding="utf8") as f:
        content = f.read()
    return content

def read_xml_file(file_name: str) -> minidom.Document:
    file = minidom.parse(file_name)
    return file

def get_stop_words(file_name: str = STOP_WORDS_FILE) -> list:
    assert os.path.exists(os.path.join(CURRENT_DIR, file_name)), f"File {file_name} does not exist"
    with open(os.path.join(CURRENT_DIR, file_name), "r") as f:
        stop_words = f.read()
    return stop_words.split("\n")

def remove_stop_words(tokens: list) -> list:
    assert os.path.exists(os.path.join(CURRENT_DIR, STOP_WORDS_FILE)), f"File {STOP_WORDS_FILE} does not exist"
    stop_words = get_stop_words(STOP_WORDS_FILE)
    return [token for token in tokens if token not in stop_words]

def tokenize(content: str) -> list:
    return re.findall(r"\w+", content)

def get_stemmed_words(tokens: list) -> list:
    # stemming
    stemmer = PorterStemmer()
    words = [stemmer.stem(token) for token in tokens]
    return words

def replace_non_word_characters(content: str) -> str:
    # replace non word characters with space
    return re.sub(r"[^\w\s]", " ", content)

def get_preprocessed_words(content: str, stopping: bool = True, stemming: bool = True) -> list:
    tokens = tokenize(content)
    tokens = [token.lower() for token in tokens]
    if stopping:
        tokens = remove_stop_words(tokens)
    if stemming:
        tokens = get_stemmed_words(tokens)
    return tokens

def preprocess_match(match: re.Match, stopping: bool = True, stemming: bool = True) -> str:
    word = match.group(0)
    if word in ["AND", "OR", "NOT"]:
        return word
    word = word.lower()
    
    stopwords = get_stop_words()
    if stopping and word in stopwords:
        return ""
    
    if stemming:
        stemmer = PorterStemmer()
        word = stemmer.stem(word)

    return word

def save_json_file(file_name: str, data: dict, output_dir: str = "result"):
    if not os.path.exists(os.path.join(CURRENT_DIR, output_dir)):
        os.mkdir(os.path.join(CURRENT_DIR, output_dir))
    with open(os.path.join(CURRENT_DIR, output_dir, file_name), "wb") as f:
        f.write(json.dumps(data).encode("utf8"))

def index_docs(docs_batches: minidom.Document, stopping: bool = True, stemming: bool = True, escape_char:bool = False, headline:bool = False) -> DefaultDict[str, Dict[str, list]]:
    local_index = defaultdict(dict)
    try:
        for doc in docs_batches:
            doc_id = doc.find("docno").text if not escape_char else doc.find("docno").decode_contents()
            doc_text = doc.find("text").text if not escape_char else doc.find("text").decode_contents()

            text_words = get_preprocessed_words(doc_text, stopping, stemming)
            if headline:
                headline = doc.find("headline").text if not escape_char else doc.find("headline").decode_contents()
                headline_words = get_preprocessed_words(headline, stopping, stemming)
                text_words = headline_words + text_words

            for position, word in enumerate(text_words):
                if doc_id not in local_index[word]:
                    local_index[word][doc_id] = []
                local_index[word][doc_id].append(position + 1)
    except:
        print("Error processing doc_id", doc_id)
        traceback.print_exc()
        exit()
    
    return local_index

def process_batch(docs_batch: list, pos_inverted_index: DefaultDict[str, Dict[str, list]], stopping: bool = True, stemming:bool = True, escape_char: bool = False, headline: bool = False):
    local_index = index_docs(docs_batch, stopping, stemming, escape_char, headline)
    try:
        lock.acquire()
        for word in local_index:
            for doc_id in local_index[word]:
                if word not in pos_inverted_index or doc_id not in pos_inverted_index[word]:
                    pos_inverted_index[word][doc_id] = []
                pos_inverted_index[word][doc_id] += local_index[word][doc_id]
    except:
        print("Error processing batch")
        traceback.print_exc()
        exit()
    finally:
        lock.release()
    
    
def positional_inverted_index(file_name: str, stopping: bool = True, stemming: bool = True, escape_char: bool = False, headline: bool = True) -> dict:
    assert os.path.exists(os.path.join(CURRENT_DIR, file_name)), f"File {file_name} does not exist"
    xml_text = read_file(file_name)
    doc_ids_set = set()
    soup = BeautifulSoup(xml_text, "html.parser")
    docs = soup.find_all("doc")
    doc_nos = soup.find_all("docno")
    for doc_no in doc_nos:
        doc_ids_set.add(doc_no.text)
    document_size = len(docs)
    batch_size = document_size // NUM_OF_CORES
    remainder = document_size % NUM_OF_CORES
    pos_inverted_index = defaultdict(dict)
    pos_inverted_index['document_size']['0'] = document_size
    pos_inverted_index['doc_ids_list'] = list(doc_ids_set)
    
    batches = [ docs[i * batch_size: (i + 1) * batch_size] for i in range(NUM_OF_CORES)]
    if remainder != 0:
        # append the remainder to the last batch
        batches[-1] += docs[-remainder:]
    
    threads = []
    for batch in batches:
        thread = threading.Thread(target=process_batch, args=(batch, pos_inverted_index, stopping, stemming, escape_char, headline))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    

    return pos_inverted_index

# save as binary file
def save_index_file(file_name: str, index: DefaultDict[str, dict[str, list]], output_dir: str = "binary_file"):
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
                f.write(f"\t{doc_id}: {','.join([str(pos) for pos in positions])}\n".encode("utf8"))
                

def load_binary_index(file_name: str, output_dir: str = "binary_file") -> dict:
    with open(os.path.join(CURRENT_DIR, output_dir, file_name), "rb") as f:
        data = f.read().decode("utf8")
    return json.loads(data)

def load_queries(file_name: str) -> list:
    query_lines = read_file(file_name).split("\n")
    queries = []
    for line in query_lines:
        if line == "":
            continue
        query_id, query_text = line.split(":")
        queries.append(query_text.strip())
    return queries

def handle_binary_operator(operator: str, left: list, right: list) -> list:
    # print("handle binary operator", operator, left, right)
    left = [] if left is None else left
    right = [] if right is None else right
    if operator == "AND":
        print("AND operation")
        return list(set(left) & set(right))
    elif operator == "OR":
        print("OR operation")
        return list(set(left) | set(right))

def handle_not_operator(operand: list, doc_ids_list: list) -> list:
    print("NOT operation")
    return list(set(doc_ids_list) - set(operand))

def get_doc_ids_from_string(string: str, inverted_index: dict, doc_ids_list: list, negate: bool = False) -> list:
    # check if string is a phrase bounded by double quotes 
    if string in inverted_index:
        if negate:
            return negate_doc_ids(list(inverted_index[string].keys()), doc_ids_list)
        else:
            return list(inverted_index[string].keys()) if inverted_index[string] else []

def get_doc_ids_from_pattern(pattern: str, inverted_index: dict, doc_ids_list: list, negate: bool = False):
    # pattern is of the form "A B"/"A B C" etc
    # retrieve words from the pattern
    doc_ids = []
    words = re.findall(r"\w+", pattern)
    # check if the word are in consecutive positions
    for doc_id in inverted_index[words[0]]:
        positions = inverted_index[words[0]][doc_id]
        for pos in positions:
            try:
                if all([pos + i in inverted_index[words[i]][doc_id] for i in range(1, len(words))]) and doc_id not in doc_ids:
                    doc_ids.append(doc_id)
            except:
                pass
    if negate:
        return negate_doc_ids(doc_ids, doc_ids_list)
    else:
        return doc_ids


def negate_doc_ids(doc_ids: list, doc_ids_list: list) -> list:
    return list(set(doc_ids_list) - set(doc_ids))

def evaluate_proximity_pattern(n: int, w1: str, w2: str, doc_ids_list: list, inverted_index: dict) -> list:
    # find all the doc_ids for w1 and w2
    doc_ids_for_w1 = get_doc_ids_from_string(w1, inverted_index, doc_ids_list)
    # find the doc_ids that satisfy the condition
    doc_ids = []
    for doc_id in doc_ids_for_w1:
        try:
            positions_for_w1 = inverted_index[w1][doc_id]
            positions_for_w2 = inverted_index[w2][doc_id]
            if any([abs(pos1 - pos2) <= int(n) for pos1 in positions_for_w1 for pos2 in positions_for_w2]):
                doc_ids.append(doc_id)
        except:
            pass
    return doc_ids

def evaluate_subquery(subquery: str, inverted_index: dict, doc_ids_list: list, special_patterns: dict[str, re.Pattern]) -> list:
    
    proximity_match = re.match(special_patterns['proximity'], subquery)
    exact_match = re.match(special_patterns['exact'], subquery)
    print("subquery", subquery)
    if proximity_match:
        n = proximity_match.group(1)
        w1 = proximity_match.group(2)
        w2 = proximity_match.group(3)
        print("Handle proximity pattern", n, w1, w2)
        return evaluate_proximity_pattern(n, w1, w2, doc_ids_list, inverted_index)
    else:
        # there is no NOT operator
        if exact_match:
            print("handle phrase", subquery[1:-1])
            return get_doc_ids_from_pattern(subquery[1:-1], inverted_index, doc_ids_list)
        else:
            print("handle word(s)", subquery)
            return get_doc_ids_from_string(subquery, inverted_index, doc_ids_list)

def read_boolean_queries(file_name: str) -> list:
    queries = []
    with open(os.path.join(CURRENT_DIR, file_name), "r") as f:
        for line in f.readlines():
            # split the query by the first space
            query_id, query = line.split(" ", 1)
            queries.append((query_id, query.strip()))
    return queries

def read_ranked_queries(file_name: str) -> list:
    queries = []
    with open(os.path.join(CURRENT_DIR, file_name), "r") as f:
        for line in f.readlines():
            # split the query by the first space
            query_id, query = line.split(" ", 1)
            queries.append((query_id, query.strip()))
        
    return queries

def calculate_tf_idf(inverted_index: dict, tokens: list, doc_id: str, docs_size: int) -> float:
    tf_idf_score = 0
    for token in tokens:
        if token not in inverted_index or doc_id not in inverted_index[token]:
            continue
        tf = 1 + math.log10(len(inverted_index[token][doc_id]))
        idf = math.log10(docs_size / len(inverted_index[token]))
        tf_idf_score += tf * idf
    return tf_idf_score


### Shunting Yard Algorithm
def precedence(operator: str) -> int:
    if operator == "NOT":
        return 3
    elif operator == "AND" or operator == "OR":
        return 2
    elif operator == "(" or operator == ")":
        return 1
    else:
        return -1

def associativity(operator: str) -> str:
    if operator == "NOT":
        return "right"
    else:
        return "left"

def is_operator(token: str) -> bool:
    return token in ["AND", "OR", "NOT"]

def infix_to_postfix(query: str, spliter: re.Pattern) -> list:
    tokens = re.findall(spliter, query)
    stack = []
    postfix = []
    for token in tokens:
        if is_operator(token):
            while stack and is_operator(stack[-1]) and \
                ((associativity(token) == "left" and precedence(token) <= precedence(stack[-1])) or \
                (associativity(token) == "right" and precedence(token) < precedence(stack[-1]))):
                postfix.append(stack.pop())
            stack.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                postfix.append(stack.pop())
            if stack and stack[-1] == '(':
                stack.pop()
        else:
            postfix.append(token)
    while stack:
        postfix.append(stack.pop())
    return postfix

def is_valid_query(query: str) -> bool:
    # check if the query is valid
    spliter = re.compile(r"(AND|OR|NOT|#\d+\(\w+,\s*\w+\)|\"[^\"]+\"|\'[^\']+\'|\w+|\(|\))")
    tokens = re.findall(spliter, query)
    prev_token = None
    parentheses_count = 0
    for token in tokens:
        if token == '(':
            parentheses_count += 1
        elif token == ')':
            parentheses_count -= 1
            if parentheses_count < 0:
                print("Parentheses count is less than 0")
                return False
        elif token == "NOT":
            if prev_token and (not is_operator(prev_token) or prev_token == '('):
                print("Invalid NOT position")
                return False
        elif is_operator(token):
            if prev_token and (prev_token == '(' or is_operator(prev_token)):
                print("Invalid operator position")
                return False
        else:
            # token is an operand
            if prev_token and prev_token == ')':
                print("Invalid operand position")
                return False
        prev_token = token
    if parentheses_count != 0:
        return False
    return True

def evaluate_boolean_query(query: str, inverted_index: dict, doc_ids_list: list, stopping: bool = True, stemming: bool = True, special_patterns: dict[str, re.Pattern] = SPECIAL_PATTERN) -> list:
    query = re.sub(r"(\w+)", lambda x: preprocess_match(x, stopping, stemming), query)
    query = " ".join([token.lower() if token not in ["AND", "OR", "NOT"] else token for token in query.split(" ")])
    if not is_valid_query(query):
        print("Invalid query: ", query)
        return []
    postfix = infix_to_postfix(query, special_patterns['spliter'])
    
    for token in postfix:
        token = re.sub(r"(\w+)", lambda x: preprocess_match(x, stopping, stemming), token)
    print("postfix", postfix)

    try:
        stack = []
        for token in postfix:
            if is_operator(token):
                if token == "NOT":
                    right = stack.pop()
                    result = handle_not_operator(right, doc_ids_list)
                else:
                    right = stack.pop()
                    left = stack.pop()
                    result = handle_binary_operator(token, left, right)
                stack.append(result)
            else:
                result = evaluate_subquery(token, inverted_index, doc_ids_list, special_patterns)
                stack.append(result)
        return stack.pop()

    except:
        # print the processing error term
        traceback.print_exc()
        exit()
        
def evaluate_ranked_query(queries: list, index: defaultdict, max_result: int = 150, stopping: bool = True, stemming:bool = True) -> list:
    results = []
    docs_size = int(index['document_size']['0'])
    for query_id, query in queries:
        words = get_preprocessed_words(query, stopping, stemming)
        print(words)
        doc_ids = set()
        for word in words:
            if word in index:
                doc_ids = doc_ids.union(set(index[word].keys()))
        
        doc_ids = list(doc_ids)
        scores = []
        for doc_id in doc_ids:
            scores.append((doc_id, calculate_tf_idf(index, words, doc_id, docs_size)))
        # sort by the score and the doc_id
        scores.sort(key=lambda x: (-x[1], x[0]))
        results.append((query_id, scores[:max_result]))
    return results

def save_boolean_queries_result(results: list, output_dir: str = "result"):
    if not os.path.exists(os.path.join(CURRENT_DIR, output_dir)):
        os.mkdir(os.path.join(CURRENT_DIR, output_dir))
    with open(os.path.join(CURRENT_DIR, output_dir, 'results.boolean.txt'), "w") as f:
        for query_id, result in results:
            for doc_id in result:
                f.write(f"{query_id},{doc_id}\n")
                
def save_ranked_queries_result(results: list, output_dir: str = "result"):
    if not os.path.exists(os.path.join(CURRENT_DIR, output_dir)):
        os.mkdir(os.path.join(CURRENT_DIR, output_dir))
    with open(os.path.join(CURRENT_DIR, output_dir, 'results.ranked.txt'), "w") as f:
        for query_id, result in results:
            for retrieved_doc_result in result:
                doc_id, score = retrieved_doc_result
                f.write(f"{query_id},{doc_id},{score:.4f}\n")

if __name__ == "__main__":
    # output_dir = ""
    custom_index_dir = 'index'
    start = time.time()
    index = positional_inverted_index(XML_FILES[2], stopping=True, stemming=True, escape_char=False, headline=True)
    print("Time taken to build index", time.time() - start)
    # save the index file which specifies the required format for submission
    save_index_file("index.txt", index, '')
    # save the custom index file
    save_json_file("index.json", index, custom_index_dir)

    ### loading index
    start = time.time()
    index = load_binary_index("index.json", custom_index_dir)
    print("Time taken to load index", time.time() - start)

    # ### processing boolean queries
    boolean_queries = read_boolean_queries("queries.boolean.txt")
    boolean_results = []
    doc_ids_list = index['doc_ids_list']
    start = time.time()
    for query in boolean_queries:
        query_id, query_text = query
        retrieved_docs = evaluate_boolean_query(query_text, index, doc_ids_list)
        retrieved_docs = [int(x) for x in retrieved_docs] if retrieved_docs else []
        retrieved_docs.sort()
        boolean_results.append((query_id, retrieved_docs))

    save_boolean_queries_result(boolean_results, '')
    print("Time taken to process boolean queries", time.time() - start)

    # ### processing ranked queries
    ranked_queries = read_ranked_queries("queries.ranked.txt")
    start = time.time()
    ranked_results = evaluate_ranked_query(ranked_queries, index)
    save_ranked_queries_result(ranked_results, '')
    print("Time taken to process ranked queries", time.time() - start)