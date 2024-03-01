from symspellpy import SymSpell, Verbosity
import os
import pandas as pd
from tqdm import tqdm

def create_spell_checking_txt(data_path, outlet_folders, output_corpus_path):
    for outlet_folder in outlet_folders:
        # Construct the path to the current outlet folder
        folder_path = os.path.join(data_path, outlet_folder)
        # List all files in the current outlet folder
        all_file_paths = os.listdir(folder_path)

        # Iterate over each file in the current outlet folder
        for file_name in tqdm(all_file_paths, desc=outlet_folder):
            # Construct the full path to the current file
            file_path = os.path.join(folder_path, file_name)
            # Ensure the file is a CSV before attempting to read it
            if file_path.endswith(".csv"):
                df = pd.read_csv(file_path)
                content_series = df["content"]
                doc_id_series = df["doc_id"]
                for index, article in enumerate(content_series):
                    try:
                        # Open the file in append mode and write the article string
                        with open(output_corpus_path, 'a', encoding='utf-8') as file:
                            file.write(article + "\n")  # Add a newline to separate articles
                    except Exception as e:
                        pass

def create_spell_checker_dictionary(corpus_path, output_dictionary_path):
    # Create a SymSpell instance
    sym_spell_instance = SymSpell()

    # Load the dictionary
    dictionary_path = "C:/Users/Asus/Desktop/ttds-proj/backend/utils/frequency_dictionary_en_82_765.txt"
    sym_spell_instance.load_dictionary(dictionary_path, 0, 1)

    # Load the corpus
    corpus_path = "C:/Users/Asus/Desktop/ttds-proj/backend/utils/corpus.txt"
    with open(corpus_path, "r", encoding="utf-8") as file:
        corpus = file.read()

    # Create a dictionary from the corpus
    sym_spell_instance.create_dictionary(corpus)

    # Save the dictionary
    sym_spell_instance.save_pickle(output_dictionary_path)

def correct_spelling(text, sym_spell_instance):
    # Perform spelling correction on the query
    # max_edit_distance dictates how far the algorithm should look for corrections
    # ignore_non_words=True allows the algorithm to skip words without corrections or those considered as proper nouns
    suggestions = sym_spell_instance.lookup_compound(text, max_edit_distance=2, ignore_non_words=True)

    # Print out the corrected query
    corrected_query = suggestions[0].term if suggestions else text
    return corrected_query
                    


if __name__ == "__main__":
    data_path = "C:/Users/Asus/Desktop/ttds-proj/backend/data/"
    outlet_folders = ["bbc", "gbn", "ind", "tele"]
    output_corpus_path = "C:/Users/Asus/Desktop/ttds-proj/backend/utils/corpus.txt"

    # create_spell_checking_txt(data_path, outlet_folders, output_corpus_path)