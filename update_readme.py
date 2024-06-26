import feedparser

RSS_FEED_URL = "https://medium.com/feed/@ElliottFairhall"
MAX_POSTS = 5

def fetch_medium_posts():
    feed = feedparser.parse(RSS_FEED_URL)
    posts = []
    for entry in feed.entries[:MAX_POSTS]:
        posts.append(f"- [{entry.title}]({entry.link})")
    return posts

def update_readme(posts):
    with open("README.md", "r") as file:
        lines = file.readlines()

    with open("README.md", "w") as file:
        in_blog_section = False
        for line in lines:
            if line.strip() == "<!-- BLOG-POST-LIST:START -->":
                in_blog_section = True
                file.write(line)
                for post in posts:
                    file.write(f"{post}\n")
            elif line.strip() == "<!-- BLOG-POST-LIST:END -->":
                in_blog_section = False
            if not in_blog_section:
                file.write(line)

if __name__ == "__main__":
    posts = fetch_medium_posts()
    update_readme(posts)
