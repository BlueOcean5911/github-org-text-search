# Script for searching text in github organization

## Install python libraries

```
    pip install -r requirements.txt
```

## Run the scripts

Retrieve all repositories from your targtted organization.

```
    python scripts/get_all_repo_names_from_organization.py --org-name organization_name --output-dir output
```

Search text in your targtted organization

```
    python scripts/search_text_in_organization.py --org-name organization_name --output-dir output --search-string sha256
```

## Introduction for scripts

### get_all_repo_names_from_organization.py

This script is for getting all repo names in organization with given its name.

### search_text_in_organization.py

This script is for searching text in all repos of organization
