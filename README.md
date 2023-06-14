# Chat Bot



## Getting started

Clone this to your computer with `git clone https://gitlab.com/cs-department-ecu/csci-4230-spring-2023/section-003/slack-discord-chat-bot/chat-bot.git`. This may require you to authenticate, this is with your gitlab username and your personal access token. You create your personal access token [here](https://gitlab.com/-/profile/personal_access_tokens)

This will create a new directory on your computer called 'chat bot'. I recommend importing this directory into vscode but you may use any ide you like.


## Making changes

In order to upload changes, here are some steps you need to take:

1. `git checkout main` to make sure you're in the main branch.
2. `git pull` to make sure you are up to date on all changes.
3. `git checkout -b new-branch-name` to create your new branch.
4. Make all your changes
5. `git add *` to add all files changes or `git add name-of-file` to add files individually
6. `git commit` to commit your changes, you will need to enter a commit message. Lets try to keep commit messages brief and to the point.
7. `git push origin your-branch-name` to push changes to gitlab.
8. Go to gitlab and you should see a message at the top of your screen regarding your changes with a button that says create merge request, press that button and follow the steps to create a merge request.
9. Then you're done! Either I (Ricky) or Andrew will look at your changes and either approve + merge it or reach out to you with questions and/or changes


## Running the bot

In order to run the bot, only a few things need to happen.

1. In your command line enter `pip3 install -r requirements.txt` to install dependencies
2. Change the BOT_KEY text in `config.py` to your discord bot api key.
3. In your command line enter `python3 main.py`

This should make the bot run, with any issues please reach out and we will assist :)


## Running tests

We have unit tests to test functionality of the bot.

1. In your command line enter `pip3 install -r requirements.txt` to install dependencies
2. Change the BOT_KEY text in `config.py` to your discord bot api key.
3. In your command line enter `python3 -m pytest`

This will run all the tests in our tests folder.


## Description

This is a multi-purpose discord chat bot that, as the name suggests, will have multiple purposes. This will have some basic discord server moderation tools, chat commands, and user interactions. We will also develop some ways to relay stock data as well as allow the discord server to buy/sell stocks. There will likely be more commands and as we come up with them they will be documented as well.

## Group Member Names

- Ricky Herget
- Andrew Edwards
- Carl Gaier
- Anu Shittu 
