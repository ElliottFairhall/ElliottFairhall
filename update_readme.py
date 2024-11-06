"""
===================================================
Filename: update_readme.py
Created Date: 09-09-2024
Author: Elliott Fairhall
Email: elliott@elliottfairhall.dev
Version: 1.0

Purpose:
--------
This script automates the process of updating the README.md file in a GitHub repository 
with the latest blog posts from Medium and Data Flakes personal website RSS feeds. 
It checks for new posts, ensures the connections to the feeds are valid, and updates 
the README.md only if new posts are found. The script is designed to run within a 
GitHub Action workflow.

Revision History:
-----------------
09-09-2024: Redesign of solution to meet new standards. (Elliott Fairhall)
05-11-2024: Implemented more error handling and ensured that tests are completed before continuing. (Elliott Fairhall)
===================================================
"""

import feedparser
import logging
import requests

# Constants for the RSS feed URLs and the maximum number of posts to display
MEDIUM_RSS_FEED_URL = "https://medium.com/feed/@ElliottFairhall"
DATA_FLAKES_RSS_FEED_URL = "https://www.data-flakes.dev/rss-featured.xml"
MAX_POSTS = 5
TIMEOUT = 10  # Timeout for connection testing (in seconds)

# Set up logging for debugging and error handling
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_connection(url):
    """
    Test if a URL is reachable by making a HEAD request.
    
    Parameters:
    url (str): The URL to test.

    Returns:
    bool: True if the URL is reachable, False otherwise.
    """
    try:
        response = requests.head(url, timeout=TIMEOUT)
        if response.status_code == 200:
            logging.info(f"Successfully connected to {url}")
            return True
        else:
            logging.error(f"Failed to connect to {url}. Status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to {url}: {str(e)}")
        return False

def fetch_posts_from_feed(feed_url):
    """
    Fetches and parses posts from an RSS feed URL.
    
    Parameters:
    feed_url (str): The URL of the RSS feed to fetch posts from.

    Returns:
    list: A list of formatted strings containing post titles and URLs.
    """
    try:
        # Parse the RSS feed
        feed = feedparser.parse(feed_url)
        posts = []

        # Check for parsing errors
        if feed.bozo:
            logging.error(f"Error parsing feed {feed_url}: {feed.bozo_exception}")
            return posts

        # Extract and format posts (limit to MAX_POSTS)
        for entry in feed.entries[:MAX_POSTS]:
            posts.append(f"- [{entry.title}]({entry.link})")
        logging.info(f"Successfully fetched {len(posts)} posts from {feed_url}")
        return posts

    except Exception as e:
        logging.error(f"Failed to fetch posts from {feed_url}: {str(e)}")
        return []

def update_readme(medium_posts, data_flakes_posts):
    """
    Updates the README.md file with the fetched blog posts.

    Parameters:
    medium_posts (list): List of Medium blog posts.
    data_flakes_posts (list): List of Data Flakes blog posts.
    """
    try:
        with open("README.md", "r") as file:
            content = file.read()

        # Markers in README.md to indicate where to insert the blog posts
        start_marker = "<!-- BLOG-POST-LIST:START -->"
        end_marker = "<!-- BLOG-POST-LIST:END -->"
        start_index = content.find(start_marker) + len(start_marker)
        end_index = content.find(end_marker)

        if start_index == -1 or end_index == -1:
            logging.error("Blog post markers not found in README.md.")
            return

        # Build the new content to insert
        new_content = content[:start_index] + "\n"

        if medium_posts:
            new_content += "### Latest Medium Posts\n"
            new_content += "\n".join(medium_posts) + "\n\n"

        if data_flakes_posts:
            new_content += "### Latest Data Flakes Posts\n"
            new_content += "\n".join(data_flakes_posts) + "\n"

        new_content += content[end_index:]

        with open("README.md", "w") as file:
            file.write(new_content)

        logging.info("README.md successfully updated with the latest blog posts.")

    except Exception as e:
        logging.error(f"Failed to update README.md: {str(e)}")

if __name__ == "__main__":
    # Initialize lists to hold the posts
    medium_posts = []
    data_flakes_posts = []

    # Fetch Medium posts if the connection is successful
    if test_connection(MEDIUM_RSS_FEED_URL):
        medium_posts = fetch_posts_from_feed(MEDIUM_RSS_FEED_URL)
    else:
        logging.warning("Skipping Medium feed due to connection issues.")

    # Fetch Data Flakes posts if the connection is successful
    if test_connection(DATA_FLAKES_RSS_FEED_URL):
        data_flakes_posts = fetch_posts_from_feed(DATA_FLAKES_RSS_FEED_URL)
    else:
        logging.warning("Skipping Data Flakes feed due to connection issues.")

    # Update README.md if there are new posts
    if medium_posts or data_flakes_posts:
        logging.info("Updating README with new posts.")
        update_readme(medium_posts, data_flakes_posts)
    else:
        logging.info("No new posts available from either Medium or Data Flakes. Skipping README update.")
