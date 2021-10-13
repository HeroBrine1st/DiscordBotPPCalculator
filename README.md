# DiscordBotPPCalculator
[osu-tools](https://github.com/ppy/osu-tools) wrapper for discord

# Getting started

1. Clone or download this repository (you can do it with green "Code" button)
2. Meet the requirements of [osu-tools](https://github.com/ppy/osu-tools)
3. Open main.py file and find this:
  ```
  CLIENT_ID = ""
  CLIENT_SECRET = ""
  DISCORD_BOT_TOKEN = ""
  NUMBER_OF_TASKS_AT_THE_SAME_TIME = 5
  NICKNAME_REGEX = re.compile(r"^[A-Za-z0-9 _]+$")
  GET_COMMAND = lambda nickname: ["dotnet", "PerformanceCalculator.dll", "profile", nickname, CLIENT_ID, CLIENT_SECRET]  # Second value can accept path
  ```
  Change what you need

4. Run bot
