HELP_MSG = """Here is the help
<b>To be todays boss</b>
(boss is the one who is responsible to control things at cafe)
Use /amtheboss

<b>To see todays boss</b>
Use /whoistheboss

<b>To record sales</b>
Use /recordsales followed by sales info to save sales info

please follow the format /recordsales sales_item sales_quantity sales_revenu sales_date(dd/mm/yyyy)

e.g /recordsales chocolate_mocha 50 2000 07/05/2023

day format DON'T FORGOT the zeros
e.g 07/05/2023


<b>To record expense</b>
Use /recordexpense followed by expense info to save expense info

please follow the format /recordexpense expnse_name qunatity amount expense_date(dd/mm/yyyy)

e.g /recordexpense chocolate_sirup(250ml) 1 2500 07/05/2023

day format DON'T FORGOT the zeros
e.g 07/05/2023


<b>To record todays sales</b>
Use /recTodaySale followed by todays sales info - to record todays sales info

please follow the format /recTodaySale sales_item sales_quantity sales_revenu

e.g /recTodaySale chocolate_mocha 50 2000


<b>To record todays expesne</b>
Use /recTodaysExp followed by todays expense info - to record todays expense info

please follow the format /recTodaysExp expnse_name qunatity amount

e.g /recTodaysExp chocolate_sirup(250ml) 1 2500


<b>To see todays sales</b>
Use /todayssales to see todays sales

<b>To see todays expense</b>
Use /todaysexpense to see todays expense


<b>To see sales for specific day</b>

day format DON'T FORGOT the zeros
e.g 07/05/2023

Use /salesdate followed by sales date to see specfifc date sales

<b>To see expense for specific day</b>

day format DON'T FORGOT the zeros
e.g 07/05/2023

Use /expensedate followed by expense date to see specfifc date expense

Or you can contact me at @IyasuHa
"""


BOSS_AUTH_MSG = """
Well done <a href="tg://user?id={user_id}">{name}</a> 

Now you are the <b>BOSS</b> keep up the sales

And don't forget to record sales and expense info at the end of the day

using /recTodaySale (followed by sales info) for sales

/recTodaysExp (followed by expense info) for expenses

/help_me for more info
"""

WHO_THE_BOSS = """
Todays Boss is <a href="tg://user?id={user_id}">{name}</a>
"""

FIRST_MSG = """
Hello <a href="tg://user?id={user_id}">{name}</a>

<b>Welcome back</b>
This bot is to control our sales, expense and responsible person at the cafe

TEST VERSION

<b>To record todays sales</b>
Use /recTodaySale followed by todays sales info - to record todays sales info

<b>To record todays expesne</b>
Use /recTodaysExp followed by todays expense info - to record todays expense info

<b>To be todays boss</b>
Use /amtheboss

<b>To see todays boss</b>
Use /whoistheboss

Use /todayssales to see todays sales

Use /todaysexpense to see todays expense

Use /help_me to see all commands
"""
