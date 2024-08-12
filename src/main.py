import feedparser
import re
import json
from datetime import datetime

rss_url = "https://dev.events/rss.xml"

feed = feedparser.parse(rss_url)

# sort by latest published date
sorted_feed = sorted(
    feed.entries, key=lambda entry: entry.published_parsed, reverse=True
)


def parse_summary(summary):
    summary = summary.split("is happening on")[-1].split("More information:")[0]
    pattern = "Online|in"
    matches = re.search(pattern, summary)

    event_date = summary[: matches.start()].strip()
    event_date = re.sub(r",\s*$", "", event_date)

    if re.search(r"\band\b", summary) or re.search(r"\bin\b", summary):
        location = summary[matches.end() + 1 :].strip()
    elif "Online" in summary:
        location = summary[matches.start() : matches.end() + 1].strip()
    location = re.sub(r".\s*$", "", location)

    return event_date, location


events = []
for event in sorted_feed:
    result = dict()
    result["title"] = event["title"]
    result["event_date"], result["location"] = parse_summary(event["summary"])
    result["link"] = event["link"]
    result["published"] = event["published"]
    # event["published_parsed"]
    result["category"] = event["tags"][0]["term"]
    result["type"] = event["tags"][1]["term"]
    events.append(result)

india_events = []
usa_events = []
online = []
for event in events:
    if re.search(r"\bIndia\b", event["location"]):
        india_events.append(event)
    if re.search(r"\bUnited States\b", event["location"]):
        usa_events.append(event)
    if re.search(r"\bOnline\b", event["location"]):
        online.append(event)


events_data = [india_events, usa_events, online]
events_path = ["events/india.json", "events/usa.json", "events/online.json"]
for i, filepath in enumerate(events_path):

    """
    # save by event date
    data = sorted(
        events_data[i],
        key=lambda event: datetime.strptime(event["event_date"], "%B %d, %Y"),
    )
    """

    # save by published time
    data = events_data[i]

    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)
