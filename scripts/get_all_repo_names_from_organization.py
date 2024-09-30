import os
import requests
import json
import argparse
from dotenv import load_dotenv
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
        'type': 'all',  # Include both public and private repos
        'per_page': 100  # Maximum number of results per page
    }

    repos = []
    while True:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        repos.extend(response.json())

        # Check for pagination
        if 'Link' in response.headers:
            links = response.headers['Link']
            if 'rel="next"' in links:
                params['page'] = params.get('page', 1) + 1
            else:
                break
        else:
            break

    return repos

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    
    parser.add_argument("--org-name", type=str, default="kk-digital", )
    parser.add_argument("--output-dir", type=str, default="output", )
    args = parser.parse_args()
    
    GITHUB_API_URL = os.getenv(key='GITHUB_API_URL')
    ORG_NAME = args.org_name
    REPOS_JSON_FNAME = os.path.join(args.output, f"{ORG_NAME}_repos.json")
    TOKEN = os.getenv(key='TOKEN')
    
    try:
        repositories = get_all_repositories(ORG_NAME, TOKEN)
        print(f"Total repositories found: {len(repositories)}")
        for repo in repositories:
            print(f"- {repo['name']} (Private: {repo['private']}) - {repo['html_url']}")
        with open(REPOS_JSON_FNAME, "w") as f:
            json.dump(repositories, f, indent=4)

    except Exception as e:
        print(f"An error occurred: {e}")
