# MTG Spoiler Scraper
*Developed in 2019*

Web scraper which notifies user when new Magic the Gathering spoilers are released

## How it works
Once started, the tool scrapes the [Mythic Spoiler site](https://www.mythicspoiler.com/newspoilers.html) for new Magic the Gathering spoilers every minute. When it sees that new spoilers have been added to the site, it sends an IFTTT notification to the user's phone to notify them and waits for a couple minutes to allow changes to the page to settle before resuming checking for new spoilers.

## Tool parameters
The tool has globals to set the hours of the day that it notifies the user and whether to notify the user on weekends. The default selections are to notify the user 8:00a-4:30p on weekdays only.
