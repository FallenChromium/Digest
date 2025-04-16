import requests
import json
from time import sleep

sources_str = '''
[
  {
    "name": "Artificial Intelligence",
    "source_type": "webpage",
    "parser_id": "tchan",
    "update_frequency": 3600,
    "config": {
      "channel_name": "Artificial_intelligence_in",
      "limit": 16
    },
    "enabled": true
  },
  {
    "name": "Deep Learning & AI",
    "source_type": "webpage",
    "parser_id": "tchan",
    "update_frequency": 3600,
    "config": {
      "channel_name": "DeepLearning_ai",
      "limit": 16
    },
    "enabled": true
  },
  {
    "name": "Machine Learning World",
    "source_type": "webpage",
    "parser_id": "tchan",
    "update_frequency": 3600,
    "config": {
      "channel_name": "ml_world",
      "limit": 16
    },
    "enabled": true
  },
  {
    "name": "Data Science & Machine Learning",
    "source_type": "webpage",
    "parser_id": "tchan",
    "update_frequency": 3600,
    "config": {
      "channel_name": "datasciencej",
      "limit": 16
    },
    "enabled": true
  },
  {
    "name": "Best AI Tools",
    "source_type": "webpage",
    "parser_id": "tchan",
    "update_frequency": 3600,
    "config": {
      "channel_name": "BestAITools",
      "limit": 16
    },
    "enabled": true
  },
  {
    "name": "The Art of Programming",
    "source_type": "webpage",
    "parser_id": "tchan",
    "update_frequency": 3600,
    "config": {
      "channel_name": "TheArtOfProgramming",
      "limit": 16
    },
    "enabled": true
  },
  {
    "name": "Python",
    "source_type": "webpage",
    "parser_id": "tchan",
    "update_frequency": 3600,
    "config": {
      "channel_name": "Python",
      "limit": 16
    },
    "enabled": true
  },
  {
    "name": "Coding News",
    "source_type": "webpage",
    "parser_id": "tchan",
    "update_frequency": 3600,
    "config": {
      "channel_name": "CodingNews",
      "limit": 16
    },
    "enabled": true
  },
  {
    "name": "Programming Challenges",
    "source_type": "webpage",
    "parser_id": "tchan",
    "update_frequency": 3600,
    "config": {
      "channel_name": "prograchallenges",
      "limit": 16
    },
    "enabled": true
  },
  {
    "name": "GitHub Repos",
    "source_type": "webpage",
    "parser_id": "tchan",
    "update_frequency": 3600,
    "config": {
      "channel_name": "github_repos",
      "limit": 16
    },
    "enabled": true
  },
  {
    "name": "Tech Guide",
    "source_type": "webpage",
    "parser_id": "tchan",
    "update_frequency": 3600,
    "config": {
      "channel_name": "TechGuide",
      "limit": 16
    },
    "enabled": true
  },
  {
    "name": "Linuxgram",
    "source_type": "webpage",
    "parser_id": "tchan",
    "update_frequency": 3600,
    "config": {
      "channel_name": "linuxgram",
      "limit": 16
    },
    "enabled": true
  },
  {
    "name": "Android ResId",
    "source_type": "webpage",
    "parser_id": "tchan",
    "update_frequency": 3600,
    "config": {
      "channel_name": "AndroidResId",
      "limit": 16
    },
    "enabled": true
  },
  {
    "name": "Data Science Jobs",
    "source_type": "webpage",
    "parser_id": "tchan",
    "update_frequency": 3600,
    "config": {
      "channel_name": "datasciencej",
      "limit": 16
    },
    "enabled": true
  },
  {
    "name": "FrontEnd World",
    "source_type": "webpage",
    "parser_id": "tchan",
    "update_frequency": 3600,
    "config": {
      "channel_name": "front_end_first",
      "limit": 16
    },
    "enabled": true
  }
]
'''

# API configuration
API_ENDPOINT = "http://localhost:8000/api/v1/sources"  # Replace with your actual API endpoint
HEADERS = {
    "Content-Type": "application/json",
}
REQUEST_DELAY = 0.5  # Delay between requests in seconds to avoid rate limiting

def insert_sources():
    # Parse the JSON string
    try:
        sources = json.loads(sources_str)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return
# Insert each source one by one
    for index, source in enumerate(sources, 1):
        try:
            response = requests.post(
                API_ENDPOINT,
                headers=HEADERS,
                json=source
            )
            
            if response.status_code == 200:
                print(f"Successfully inserted {index}/{len(sources)}: {source['name']}")
            else:
                print(f"Failed to insert {source['name']}. Status code: {response.status_code}, Response: {response.text}")
            
            # Add delay between requests
            sleep(REQUEST_DELAY)
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed for {source['name']}: {e}")
            continue

if __name__ == "__main__":
    insert_sources()