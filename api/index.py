import os
from dotenv import load_dotenv
import time
import datetime

import logging

from typing import Optional
from fastapi import FastAPI
import telegram
from pydantic import BaseModel
from telegram import Update, Bot
from telegram.ext import CommandHandler, MessageHandler, Updater, Filters, Dispatcher, CallbackContext
from deta import Deta

load_dotenv()

# TOKEN = os.environ.get("TELE_TOKEN")
TOKEN = os.getenv("TELE_TOKEN")
DETA_KEY = os.getenv("DETA_KEY")
ADMIN_IDs = [403875924]

logging.basicConfig(format="%(asctime)s - %(name)s - %(message)s", level=logging.INFO)

FIRST_MSG = """
Hello <a href="tg://user?id={user_id}">{name}</a>

<b>Welcome back</b>

Use /recordsales followed by sales info to save sales info
please follow the format /recordsales sales_item sales_quantity sales_revenu sales_date(dd/mm/yyyy)
e.g /recordsales chocolate_mocha 50 2000 07/05/2023


Use /recordexpense followed by expense info to save expense info
please follow the format /recordexpense expnse_name qunatity amount expense_date(dd/mm/yyyy)
e.g /recordexpense chocolate_sirup(250ml) 1 2500 07/05/2023


Use /todayssales to see todays sales

Use /todaysexpense to see todays expense

Use /salesdate followed by sales date to see specfifc date sales

Use /expensedate followed by expense date to see specfifc date expense

please use the format dd/mm/Y for date
e.g 07/05/2023
"""

app = FastAPI()

deta = Deta(DETA_KEY)

sales_db = deta.Base("Sales_DB")
expense_db = deta.Base("Expense_DB")

class TelegramWebhook(BaseModel):
    update_id: int
    message: Optional[dict]
    edited_message: Optional[dict]
    channel_post: Optional[dict]
    edited_channel_post: Optional[dict]
    inline_query: Optional[dict]
    chosen_inline_result: Optional[dict]
    callback_query: Optional[dict]
    shipping_query: Optional[dict]
    pre_checkout_querry: Optional[dict]
    poll: Optional[dict]
    poll_answer: Optional[dict]

def start(update, context):
    effective_user = update.effective_user
    if effective_user.id not in ADMIN_IDs:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Well, hello there!!")
        return
    admin = effective_user
    first_name = getattr(admin, "first_name", '')
    update.message.reply_html(text=FIRST_MSG.format(name=first_name, user_id=admin.id))

def record_sales(update, context):
    effective_user = update.effective_user
    if effective_user.id not in ADMIN_IDs:
        update.message.reply_text(text="What do you mean, I don't get it")
        return
    admin=effective_user
    sales_raw = str(context.args[0:])
    #  sales_raw data to be recorder like this 
    # /recordsales sales_item sales_quantity sales_revenu sales_date(dd/mm/yyyy)
    # /recordsales chocolate_mocha 50 2000 07/05/2023
    # sales info
    sales_=sales_raw.split(",")
    sales_item = sales_[0].replace("[", '').replace("'", '')
    sales_quantity = sales_[1].replace("'", '')
    sales_revenu = sales_[2].replace("'", '')
    sales_date = sales_[3].replace("]", '').replace("'", '').replace(" ", "")

    # admin info
    adminUserName = getattr(admin, "username", '')
    adminFirstName = getattr(admin, "first_name", '')
    adminRecordAt = datetime.datetime.now()

    sales_dict = {}
    sales_dict["item_name"]=sales_item
    sales_dict["quantity"]=sales_quantity
    sales_dict["revenu"]=sales_revenu
    sales_dict["date"]=sales_date

    sales_dict["admin_user_N"]=adminUserName
    sales_dict["admin_first_N"]=adminFirstName
    sales_dict["sales_record_at"]=adminRecordAt.strftime("%d/%m/%y, %H:%M")

    sales_db.put(sales_dict)
    update.message.reply_html("<b>Sales</b> info recorded successfully")


def record_expense(update, context):
    effective_user = update.effective_user
    if effective_user.id not in ADMIN_IDs:
        update.message.reply_text(text="What do you mean, I don't get it")
        return
    admin=effective_user
    expense_raw= str(context.args[0:])
    #  sales_raw data to be recorder like this 
    # /recordexpense expnse_name qunatity amount expense_date(dd/mm/yyyy)
    # /recordexpense chocolate_sirup(250ml) 1 2500 07/05/2023
    # expense info
    expense_=expense_raw.split(",")
    expense_name = expense_[0].replace("[", '').replace("'", '')
    expense_qunatity = expense_[1].replace("'", '')
    expense_amount = expense_[2].replace("'", '')
    expense_date = expense_[3].replace("]", '').replace("'", '').replace(" ", "")

    # admin info
    adminUserName = getattr(admin, "username", '')
    adminFirstName = getattr(admin, "first_name", '')
    adminRecordAt = datetime.datetime.now()

    expense_dict = {}
    expense_dict["exp_name"]=expense_name
    expense_dict["quantity"]=expense_qunatity
    expense_dict["amount"]=expense_amount
    expense_dict["date"]=expense_date

    expense_dict["admin_user_N"]=adminUserName
    expense_dict["admin_first_N"]=adminFirstName
    expense_dict["expense_record_at"]=adminRecordAt.strftime("%d/%m/%y, %H:%M")

    expense_db.put(expense_dict)
    update.message.reply_html("<b>expense</b> info recorded successfully")

today = datetime.datetime.now().strftime("%d/%m/%Y")

def todays_sales(update, context):
    effective_user = update.effective_user
    if effective_user.id not in ADMIN_IDs:
        update.message.reply_text(text="What do you mean, I don't get it")
        return
    sales = sales_db.fetch({"date": today}).items
    if sales == []:
        update.message.reply_text("No Sales 😞 Today")
        return
    for sale in sales:
        update.message.reply_text("Sales: \n\tItem Name: "+sale["item_name"]+"\n\tQunatity: "+str(sale["quantity"])+"\n\tRevenu: "+str(sale["revenu"])+"\n\tDate: "+sale["date"]+"\n\tRecorder by: "+sale["admin_first_N"]+"\n\tRecorded At: "+sale["sales_record_at"])

def todays_expense(update, context):
    effective_user = update.effective_user
    if effective_user.id not in ADMIN_IDs:
        update.message.reply_text(text="What do you mean, I don't get it")
        return
    expenses = expense_db.fetch({"date": today}).items
    if expenses == []:
        update.message.reply_text("No Expense 😌 Today")
        return
    for expense in  expenses:
        update.messgae.reply_text("Expenses: \n\tName: "+expense["exp_name"]+"\n\tQunatity: "+str(expense["quantity"])+"\n\tAmount: "+str(expense["amount"])+"\n\tDate: "+expense["date"]+"\n\tRecorder by: "+expense["admin_first_N"]+"\n\tRecorded At: "+expense["expense_record_at"])

def sales_date(update, context):
    effective_user = update.effective_user
    if effective_user.id not in ADMIN_IDs:
        update.message.reply_text(text="What do you mean, I don't get it")
        return
    # the date format should be 07/05/2023
    date = str(context.args[0:]).replace("['", '').replace("']",'').replace(" ", "")
    sales = sales_db.fetch({"date":date}).items
    if sales == []:
        update.message.reply_text("No sales at that day")
        return
    for sale in sales:
        update.message.reply_text("Sales: \n\tItem Name: "+sale["item_name"]+"\n\tQunatity: "+str(sale["quantity"])+"\n\tRevenu: "+str(sale["revenu"])+"\n\tDate: "+sale["date"]+"\n\tRecorder by: "+sale["admin_first_N"]+"\n\tRecorded At: "+sale["sales_record_at"])

def expense_date(update, context):
    effective_user = update.effective_user
    if effective_user.id not in ADMIN_IDs:
        update.message.reply_text(text="What do you mean, I don't get it")
        return
    # the date format should be 07/05/2023
    date = str(context.args[0:]).replace("['", '').replace("']",'').replace(" ", "")
    expenses = expense_db.fetch({"date":date}).items
    for expense in  expenses:
        update.messgae.reply_text("Expenses: \n\tName: "+expense["exp_name"]+"\n\tQunatity: "+str(expense["quantity"])+"\n\tAmount: "+str(expense["amount"])+"\n\tDate: "+expense["date"]+"\n\tRecorder by: "+expense["admin_first_N"]+"\n\tRecorded At: "+expense["expense_record_at"])


def register_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('recordsales', record_sales))
    dispatcher.add_handler(CommandHandler('recordexpense', record_expense))

    dispatcher.add_handler(CommandHandler('todayssales', todays_sales))
    dispatcher.add_handler(CommandHandler('todaysexpense', todays_expense))

    dispatcher.add_handler(CommandHandler('salesdate', sales_date))
    dispatcher.add_handler(CommandHandler('expensedate', expense_date))

def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    register_handlers(dispatcher)
    updater.start_polling()
    updater.idle()

@app.post("/webhook")
def webhook(webhook_data: TelegramWebhook):
    bot = Bot(token=TOKEN)
    update = Update.de_json(webhook_data.__dict__, bot)
    dispatcher = Dispatcher(bot, None, workers=4, use_context=True)
    register_handlers(dispatcher)
    dispatcher.process_update(update)
    return {"status":"okay"}

@app.get("/")
def index():
    return {"status":"okay"}