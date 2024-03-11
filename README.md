# ttds-proj
Python version: 3.12.1

# Create virtual environment(pyenv):
cd backend
python -m venv .venv

# Activate virtual environment(pyenv):
windows: .venv\Scripts\activate
linux: source .venv/bin/activate

# Create virtual environment(conda):
cd backend
conda create -n ttds-proj python=3.12.1

# Activate virtual environment(conda):
conda activate ttds-proj

# Install requirements:

### Windows Requirements
 Visual Studio 2022 Community ed. ([install](https://visualstudio.microsoft.com/downloads/)) and installing "Desktop development with C++" having checked the optional features of MSVC and Windows 11 SDK. 

### Linux Requirements
`sudo apt update` and `sudo apt install build-essential`.

## General Requirements (only after OS requirements)
pip install -r requirements.txt



# docker build:
docker build -t fastapi:latest .

# docker run:
docker run -d -p 8080:8080 fastapi

# deployment:
create commit to branch "deploy"

# folder structure:
.github/workflows
- build.yml (CI/CD)
- backend
    - data (put your data here if you want to build index from csv in local, ignored in git)
        - bbc
            - bbc_data_{date}_{index}.csv
        - gbn
            - gbn_data_{date}_{index}.csv
        - ind
            - ind_data_{date}_{index}.csv
        - tele
            - tele_data_{date}_{index}.csv
    - routers
        - \_\_init\_\_.py
        - api.py
        - {api_name}.py
    - utils
        - \_\_init\_\_.py
        - basetype.py (data structure)
        - build_index.py (build index from csv)
        - common.py (common functions)
        - constant.py (constant values(path, enums, etc))
        - pull_index.py (playground for pulling)
        - push_index.py (utils for pushing inverted index to db)
        - query_engine.py (query engine(boolean, tf-idf, etc))
        - query_suggestion.py (query suggestion when typing)
        - redis_utils.py (redis utils)
        - sentiment_analyzer.py (sentiment analysis class and utils)
        - spell_checker.py (spell checker class and utils)
        - summarizer.py (utils for getting summaries for documents)
        - ttds_2023_english_stop_words.txt (stop words)
    - \_\_init\_\_.py
    - .dockerignore
    - .gitignore
    
    - .env
    - deploy.py
    - main.py
    - requirements.txt
- frontend (react-app content)
    - public
    - src (js components)
    - .env.development (env for dev)
    - .env.production (env for prod)
    - .gitignore
    - package-lock.json (npm package lock)
    - package.json (npm package)
    - README.md
- temp (any temporary files that are not merged to backend/frontend)
current_doc_id.txt (Just for crash recovery for local batch processing, not used in production)
dockerfile (build docker image)
