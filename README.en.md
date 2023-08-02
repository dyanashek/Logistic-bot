# Telegram logistic
## Change language: [English](README.en.md)
***
Bot to help in the implementation of logistics.
## [DEMO](README.demo.md)
## Functionality:
1. The administrator controls the users who have access to the bot
2. Distribution of routes to drivers based on the database of google tables
3. Transferring information from drivers to google spreadsheets
4. Making changes to running routes, notifying drivers about the changes made
5. Validation of the correct filling of tables
6. Work with an unlimited number of sheets
## Commands:
**For convenience, it is recommended to add these commands to the side menu of the bot using [BotFather](https://t.me/BotFather).**
- connect - calls the button to connect with the administrator

**Commands available only to the administrator:**
- allow - a command that provides drivers with access to the bot, after a space from the command, you must specify the user's nickname in the telegram (eg /allow username);
- disallow - a command that deprives drivers of access to the bot, after a space from the command, you must specify the user's nickname in telegrams (eg /disallow username)
- all_users - a command that displays a list of all users with access status
- send_routes - a command that sends routes to drivers, you must specify the name of the sheet with information about routes (eg /send_routes routes) separated by a space. **IMPORTANT:** removes all previous routes from the database, unfinished routes are grayed out in google sheets.
- update_routes - a command that allows you to make changes to previously added routes (changes in addresses, their order, adding new ones, etc.), you must specify the name of the sheet with information about routes separated by a space (eg /update_routes routes). **IMPORTANT:** if changes are made to an address that has already been visited by the driver or to which the driver is heading, then the driver's route will remain unchanged, the administrator will receive a warning that the route has not been changed.
- stop - a command that interrupts the execution of the route in the driver, after a space, you must specify the route identifier from the google table (e.g. /stop 123, used when you need to interrupt the route and completely update it (after using the /stop command and adding a new route with a unique identifier you should use the update_routes command)
- help - a command that displays a hint for using

## Installation and use:
- Install dependencies:
```sh
pip install -r requirements.txt
```
- in the .env file specify:\
   - Bot telegram token: **TELEBOT_TOKEN**=TOKEN\
   - Bot ID: **BOT_ID**=ID (first digits from bot token, before :)\
   - Manager ID: **MANAGER_ID**=MANAGER_ID; will have the right to execute the /update command, he will receive notifications - to receive notifications, the manager needs to activate the bot from his account (press the "start" button)
   > To determine the user ID, you need to send any message from the corresponding account to the next [bot] (https://t.me/getmyid_bot). Value contained in **Your user ID** - User ID
   - Manager username - the "administrator" button will enter the specified profile when using the /connect command: **MANAGER_USERNAME**=example (specified without @)\
   - Google spreadsheet name: **SPREAD_NAME**=logistic (don't use spaces and "_" - underscores)\
   - Name of the sheet on which the bot enters information: **LIST_BOT**=bot (do not use spaces and "_" - underscores in the name)
- get file with credentials (connection parameters):\
https://console.cloud.google.com/ \
https://www.youtube.com/watch?v=bu5wXjz2KvU - instruction from 00:00 to 02:35\
Save the resulting file in the root of the project, with the name **service_account.json**
- provide service e-mail with access to the table (instruction in the video at the link above)
- run the project:
```sh
python3 main.py
```
## Recommendations for use:
- in the name of the table and sheets do not use spaces and underscores
- a sheet with information filled in by the bot must contain 152 columns (unique ID, full name + 25 sets of fields for addresses)
- the order of the displayed information on the sheet with information filled in by the bot (the title is generated automatically):
     1. unique route ID, must not be repeated
     2. Name
     3. Address #1
     4. Time and date of arrival
     5. Message from the driver
     6. Status
     7. Time and date of departure
     8. Loading work
> then steps 3 to 8 are repeated
- the order of information on the sheet filled in by the logistician (the title must be formed independently):
     1. unique route ID (should be unique for the entire time of using the bot, you can use **only numbers**) (the title must contain the word "ID" - not case sensitive)
     2. Nickname of the driver in telegram (filled without @) (the title must contain the word "TELEGRAM" - not case sensitive)
     3. Full name of the driver (the title must contain the word "Name" - not case sensitive)
     4. Address №1 (header must contain the word "Address" - not case sensitive)
     5. Phone number №1 (the title should contain the word "Phone" - not case sensitive)
     6. Message №1 (title must contain the word "Message" - case insensitive)
> then paragraphs 4,5,6 are repeated (none of them can be omitted), if the phone or message is filled, the address cannot be empty.
- the bot starts filling from the first empty line (the check is carried out on column A) - do not leave this column empty at the top of the table
- do not create additional columns, do not enter information that is not provided for in the terms of reference - may affect the correct operation

## Features of use:
1. Each button needs to be pressed only once, after that the bot starts processing the data, upon completion of the process, changing the displayed information
2. No more than 25 addresses can be added to one route
3. Providing users with access to the bot occurs by specifying a nickname in telegrams
4. Options for adding points to the end of the route and changing the order are combined into one command /update_routes
5. If necessary, completely stop the route, use the /stop command
6. The /update_routes command eliminates the need for a personal update of information for each driver
7. To connect with the administrator, the driver needs to use the /connect command
8. The administrator needs to wait for a response to the entered command before entering the next