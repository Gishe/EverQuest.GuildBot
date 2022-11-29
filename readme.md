# EQ Guild Bot

## Features
- Perform regular guild dumps and notify remote discord channel of members who have logged on, logged off, joined the guild, or left the guild.
- Scan OpenDKP and notify when guild members have become inactive (e.g. 30 day raid attendance has dropped below a specified threshold).
- Buff players with requested buffs. Can be configured to only buff guild memebers.
- Observable log parser which can notify subscribed python functions when specific types of messages arrive.

## Limitations
- In order to interact with the game, this bot will force the EQ window to the foreground. The bot will only do this if there hasn't been input from your mouse/keyboard for a while, however, you will want to avoid any mouse/keyboard input while it is interacting with the EQ window. If possible, this will be updated in the future to communicate as a background process.
- For granular guild tracking functionality such as determining who has logged in vs who has logged off, this bot will need to be ran indefinitely. However, the bot could be enabled occasionally to perform a quick analysis of who has joined and left the guild since the last execution.

## Installation (Windows)

1. Install Python3.7+
2. (If using Powershell) Run the below command in Powershell as Adminsitrator to allow for execution of Python modules:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```
3. Clone down the repository
4. From within a terminal (Powershell, bash, etc), navigate to the cloned repository
5. Create and activate a new virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```
6. Install dependencies
```powershell
pip install -r requirements.txt
```
_Certain pip packages require redistributables such as C++ Build Tools to be installed. If you receive an error for a missage dependency, please install the dependency before rerunning the pip install command._

7. If you intend to output guild status reports to discord, create a file named `secrets.yaml` at the project root and include your webhook config.
```yaml
webhooks:
  discord:
    url: https://discord.com/api/webhooks/################/#######################################
```

## Configuration
The `config.yaml` at the project root can be used to change the bot's default behavior.

### Properties
Coming soon. Refer to example properties for now.

## Execution

1. Activate the virtual environment
```powershell
.\.venv\Scripts\activate
```

2. Run the bot
```powershell
python .\eq_bot\main.py
```
## Extending

### Log Input

To observe the log parser for a specific type of message, call the `observe_messages` function on startup in `main.py`.
```python
# Example log reader subscription. This will print all tells which are received.
player_log_reader.observe_messages(LogMessageType.TELL_RECEIVE, lambda message: message.print())
```
