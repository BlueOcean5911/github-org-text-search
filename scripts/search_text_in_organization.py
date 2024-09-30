import os
import requests
import base64
import json
import argparse
from dotenv import load_dotenv
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
sys.path.insert(0, './')

load_dotenv()

def get_all_repositories(org_name, token):
    url = f"{GITHUB_API_URL}/orgs/{org_name}/repos"
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    params = {
        'type': 'all',
        'per_page': 100
    }

    repos = []
    while True:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        repos.extend(response.json())

        if 'Link' in response.headers:
            links = response.headers['Link']
            if 'rel="next"' in links:
                params['page'] = params.get('page', 1) + 1
            else:
                break
        else:
            break

    return repos

def is_python_file(file_path):
    # Check if the file extension indicates it's a python file
    text_extensions = ['.py']
    return any(file_path.endswith(ext) for ext in text_extensions)

def search_in_file(owner, org, repo, path):
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/contents/{path}"
    headers = {
        'Authorization': f'token {TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    content = response.json()['content']
    decoded_content = base64.b64decode(content).decode('utf-8')
    
    return decoded_content.splitlines()

def find_string_in_file(lines, org, repo, path):
    line_links = []
    
    for line_number, line in enumerate(lines, start=1):
        if SEARCH_STRING in line:
            line_link = f"https://github.com/{org}/{repo}/blob/main/{path}#L{line_number}"
            line_links.append(line_link)
    
    return line_links

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--org-name", type=str, default="kk-digital")
    parser.add_argument("--search-string", type=str, default="sha256")
    parser.add_argument("--output-dir", type=str, default="output")
    args = parser.parse_args()
    
    ORG_NAME = args.org_name
    TOKEN = os.getenv(key='TOKEN')
    SEARCH_STRING = args.search_string
    GITHUB_API_URL = os.getenv(key='GITHUB_API_URL')
    REPOS_JSON_FNAME = os.path.join(args.output, f"{ORG_NAME}_repos.json")
    SEARCH_RESULT_JSON_FNAME = os.path.join(
        args.output, 
        f"{ORG_NAME}_search_result({SEARCH_STRING}).json"
    )
    
    try:
        if os.path.isfile(REPOS_JSON_FNAME):
            with open(REPOS_JSON_FNAME) as f:
                repositories = json.load(f)
            print("Successfully loaded repositories from json file")
        else:
            repositories = get_all_repositories(ORG_NAME, TOKEN)
            with open(REPOS_JSON_FNAME, "w") as f:
                json.dump(REPOS_JSON_FNAME, f)
            print("Successfully fetched repositories using api")
        
        all_line_links = []
        total_len_repos = len(repositories)
        for id, repo in enumerate(repositories):
            repo_line_links = []
            print(f"Searching in repository({id + 1}/{total_len_repos}): {repo['name']}")
            try:
                contents_url = f"{GITHUB_API_URL}/repos/{repo['full_name']}/git/trees/main?recursive=1"
                contents_response = requests.get(contents_url, headers={'Authorization': f'token {TOKEN}'})
                contents_response.raise_for_status()
                files = contents_response.json()['tree']
            except Exception as e:
                print(f"Error in loading repo {repo['name']}", e)
                continue
            for file in tqdm(files):
                if file['type'] == 'blob' and is_python_file(file['path']):
                    path = file['path']
                    lines = search_in_file(repo['owner']['login'], ORG_NAME, repo['name'], path)
                    line_links = find_string_in_file(lines, ORG_NAME, repo['name'], path)
                    repo_line_links.extend(line_links)
            if len(repo_line_links) > 0:
              all_line_links.append({
                  "repo_name": repo['name'],
                  "repo_line_links": repo_line_links
              })

        print(f"Total line links found: {len(all_line_links)}")
        with open(SEARCH_RESULT_JSON_FNAME, "w") as f:
            json.dump(all_line_links, f, indent=4)

    except Exception as e:
        print(f"An error occurred: {e}")
