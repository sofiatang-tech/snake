import praw
import requests
import os

# =============================
# TODO: Replace with your Reddit credentials
CLIENT_ID = "EYxZdgQ-a8m4ipgZf-aS8A"
CLIENT_SECRET = "Z2WHK7vLcsZ0m6m4vqJgX-clPuHt7w"
USER_AGENT = "RecipeFinderBot/1.0 by u/Training_Quiet_9828"
# =============================

# Initialize Reddit instance
reddit = praw.Reddit(client_id=CLIENT_ID,
                     client_secret=CLIENT_SECRET,
                     user_agent=USER_AGENT)

# Create folder to save images
if not os.path.exists("recipe_images"):
    os.makedirs("recipe_images")

print("🍽️ Reddit Recipe Finder — type a topic to search (or 'exit' to quit)\n")

# Main input loop
while True:
    topic = input("Enter a recipe topic: ").strip().lower()
    if topic in ("exit", "quit"):
        print("\n👋 Exiting Recipe Finder. Have a great day!")
        break
    if not topic:
        print("⚠️ Please enter a topic.")
        continue

    print("\n" + "#" * 60)
    print(f"Searching for topic: {topic.capitalize()}")

    subreddit = reddit.subreddit("recipes")
    found_post = None

    # Search top 10 posts matching topic
    for submission in subreddit.search(topic, limit=10):
        if submission.link_flair_text and "recipe" in submission.link_flair_text.lower():
            found_post = submission
            break

    if not found_post:
        print(f"No recipe found for topic '{topic}'. Try another one!\n")
        continue

    print(f"Recipe Name: {found_post.title}")

    author_name = found_post.author.name if found_post.author else "[deleted]"
    print(f"Posted by: u/{author_name}")

    found_post.comments.replace_more(limit=0)
    if found_post.comments:
        top_comment = found_post.comments[0].body
        print(f"\nRecipe Text:\n{top_comment}")
    else:
        print("No recipe text found in comments.")

    # Download image if available
    image_url = found_post.url
    if any(image_url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png"]):
        image_path = os.path.join("recipe_images", f"{topic.replace(' ', '_')}.jpg")
        response = requests.get(image_url)
        with open(image_path, "wb") as f:
            f.write(response.content)
        print(f"Saved local file: {image_path}")
    else:
        print("No image found for this recipe.")

    print("\nDone! You can search another topic or type 'exit' to quit.\n")

