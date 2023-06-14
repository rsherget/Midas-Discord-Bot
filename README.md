# Chat Bot

# Midas Discord Bot

## About The Bot

This project was created by myself and two other group members (Andrew Edwards and Anu Shittu) for our software engineering capstone project. This bot idea came to be as we all use discord to communicate and we wanted to create something we could use in our discord server while also expanding our knowledge of using APIs and also just because it sounded fun. 

This is a self-hosted, multi-purpose discord bot with basic moderation capabilities as well as the ability to utilize chat-gpt and relay real-time stock data and make trades. It also has the ability to auto trade stocks where you pick the stock for the bot to monitor and if conditions are met then the bot will buy/sell the stock without further prompt from the user.

🔴 **PLEASE READ BEFORE USE!** 🔴 If used in a server with multiple people and you plan on using the trading aspects with real money not paper money, I advise you look up trading laws related to multiple people utilizing one trading account. We are computer science majors, not law majors so we have no idea what the law says about this. We recommend using a paper money account for this reason :)

## Getting started

Clone this to your computer with `git clone https://github.com/rsherget/Midas-Discord-Bot.git`.

In the `bot/config.py` file :

 - change the API_KEY to your Alpaca API Key
 - change the SECRET_KEY to your Alpaca API Secret Key
 - change the BOT_KEY to your Discord Bot Key
 - change the OPENAI_KEY to your OpenAI API Key

All Alpaca info, documentation, and key creation can be found [here](https://alpaca.markets/). Your Discord bot and key can be created [here](https://discord.com/developers/docs/intro). Your OpenAI key can be created [here](https://openai.com/blog/openai-api).


## Making changes

If you find this repo and want to make changes, then by all means do so! Follow the steps above to clone the repo to your computer and then follow these steps below:

1. `git checkout main` to make sure you're in the main branch.
2. `git pull` to make sure you are up to date on all changes.
3. `git checkout -b new-branch-name` to create your new branch.
4. Make all your changes.
5. `git add *` to add all files changes or `git add name-of-file` to add files individually.
6. `git commit` to commit your changes, you will need to enter a commit message. Lets try to keep commit messages brief and to the point.
7. `git push origin your-branch-name` to push changes to gitlab.
8. Go to github and create a pull request from your branch with your changes.
9. Then you're done! I will look at your changes and either approve + merge it or reach out to you with questions and/or changes.


## Running the bot

In order to run the bot, only a few things need to happen.

1. In your command line enter `brew install ta-lib` 
2. Next, enter 
```
export TA_INCLUDE_PATH="$(brew --prefix ta-lib)/include"
export TA_LIBRARY_PATH="$(brew --prefix ta-lib)/lib"
```
3. In your command line enter `pip3 install -r requirements.txt` to install dependencies
4. Change the BOT_KEY text in `config.py` to your discord bot api key.
5. In your command line enter `python3 main.py`

This should make the bot run, with any issues please reach out and I will assist :)


## Running tests

We have unit tests to test functionality of the bot.

1. In your command line enter `pip3 install -r requirements.txt` to install dependencies
2. Change the BOT_KEY text in `config.py` to your discord bot api key.
3. In your command line enter `python3 -m pytest`

This will run all the tests in our tests folder.

