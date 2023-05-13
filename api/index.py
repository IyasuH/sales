import os
from dotenv import load_dotenv
import time
import datetime
import csv

import logging

from typing import Optional
from fastapi import FastAPI
import telegram
from pydantic import BaseModel
from telegram import Update, Bot
from telegram.ext import CommandHandler, MessageHandler, Updater, Filters, Dispatcher, CallbackContext
from deta import Deta
import command

from api.constants import *

load_dotenv()

# TOKEN = os.environ.get("TELE_TOKEN")
TOKEN = os.getenv("TELE_TOKEN")
DETA_KEY = os.getenv("DETA_KEY")
ADMIN_IDs = [403875924, 446194134, 972958641, 331259874]

logging.basicConfig(format="%(asctime)s - %(name)s - %(message)s", level=logging.INFO)


app = FastAPI()

deta = Deta(DETA_KEY)

sales_db = deta.Base("Sales_DB")
expense_db = deta.Base("Expense_DB")
respo_db = deta.Base("Respon_DB")
permission_request_db = deta.Base("Permission_DB")

# command.run(['chmod', '-R', '755', '/api'])

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
    """
    record sales info
    """
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
    """
    record expense info
    """
    effective_user = update.effective_user
    if effective_user.id not in ADMIN_IDs:
        update.message.reply_text(text="What do you mean, I don't get it")
        return
    admin=effective_user
    expense_raw= str(context.args[0:])
    #  expense_raw data to be recorder like this 
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
    """
    shows todays sales info
    """
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
    """
    shows todays expense info
    """
    effective_user = update.effective_user
    if effective_user.id not in ADMIN_IDs:
        update.message.reply_text(text="What do you mean, I don't get it")
        return
    expenses = expense_db.fetch({"date": today}).items
    if expenses == []:
        update.message.reply_text("No Expense 😌 Today")
        return
    for expense in  expenses:
        update.message.reply_text("Expenses: \n\tName: "+expense["exp_name"]+"\n\tQunatity: "+str(expense["quantity"])+"\n\tAmount: "+str(expense["amount"])+"\n\tDate: "+expense["date"]+"\n\tRecorder by: "+expense["admin_first_N"]+"\n\tRecorded At: "+expense["expense_record_at"])

def sales_date(update, context):
    """
    see sales info for specifc day
    """
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
    """
    see expense info for specifc day
    """
    effective_user = update.effective_user
    if effective_user.id not in ADMIN_IDs:
        update.message.reply_text(text="What do you mean, I don't get it")
        return
    # the date format should be 07/05/2023
    date = str(context.args[0:]).replace("['", '').replace("']",'').replace(" ", "")
    expenses = expense_db.fetch({"date":date}).items
    for expense in  expenses:
        update.message.reply_text("Expenses: \n\tName: "+expense["exp_name"]+"\n\tQunatity: "+str(expense["quantity"])+"\n\tAmount: "+str(expense["amount"])+"\n\tDate: "+expense["date"]+"\n\tRecorder by: "+expense["admin_first_N"]+"\n\tRecorded At: "+expense["expense_record_at"])

def record_todays_boss(update, context):
    """
    record todays boss info
    """
    effective_user = update.effective_user
    if effective_user.id not in ADMIN_IDs:
        update.message.reply_text(text="What do you mean, I don't get it")
        return
    # take the day as key so one day will have one boss
    # and first check if there is any before recording
    boss_query = respo_db.get(today)
    if boss_query == None:
        # No boss still now so record one
        boss = effective_user
        bossUserName = getattr(boss, "username", '')
        bossFirstName = getattr(boss, "first_name", '')

        boss_dict = {}
        boss_dict["key"]= today
        boss_dict["id"] = boss.id
        boss_dict["boss_user_N"] = bossUserName
        boss_dict["boss_first_N"] = bossFirstName
        boss_dict["said_at"] = datetime.datetime.now().strftime("%d/%m/%y, %H:%M")

        respo_db.put(boss_dict)
        update.message.reply_html(BOSS_AUTH_MSG.format(user_id=boss.id, name=bossFirstName))
    else:
        update.message.reply_html("Possition already taken")
        update.message.reply_html(WHO_THE_BOSS.fromat(user_id=boss_query["id"], name=boss_query["boss_first_N"]))

def show_todays_boss(update, context):
    """
    show todays boss info
    """
    effective_user = update.effective_user
    if effective_user.id not in ADMIN_IDs:
        update.message.reply_text(text="What do you mean, I don't get it")
        return
    # check if any boss for today and display who is he/she
    # if not promote to record one
    boss_query = respo_db.get(today)
    if boss_query == None:
        update.message.reply_html("""No one still now you can be todays boss using /amtheboss
        """
        )
    else:
        update.message.reply_html(WHO_THE_BOSS.format(user_id=boss_query["id"], name=boss_query["boss_first_N"]))

def record_todays_sales(update, context):
    """
    record todays sales info
    """
    effective_user = update.effective_user
    if effective_user.id not in ADMIN_IDs:
        update.message.reply_text(text="What do you mean, I don't get it")
        return
    admin=effective_user
    sales_raw = str(context.args[0:])
    # sales INFO
    # /recordsales sales_item sales_quantity sales_revenu
    # /recordsales chocolate_mocha 50 2000

    sales_=sales_raw.split(",")
    sales_item = sales_[0].replace("[", '').replace("'", '')
    sales_quantity = sales_[1].replace("'", '')
    sales_revenu = sales_[2].replace("]", '').replace("'", '').replace(" ", "")
    sales_date = today

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
    update.message.reply_html("<b>Todays Sales</b> info recorded successfully")


def record_todays_expesne(update, context):
    """
    record todays expense info
    """
    effective_user = update.effective_user
    if effective_user.id not in ADMIN_IDs:
        update.message.reply_text(text="What do you mean, I don't get it")
        return
    admin=effective_user
    expense_raw= str(context.args[0:])
    # expense INFO
    # /recordexpense expnse_name qunatity amount
    # /recordexpense chocolate_sirup(250ml) 1 2500

    expense_=expense_raw.split(",")
    expense_name = expense_[0].replace("[", '').replace("'", '')
    expense_qunatity = expense_[1].replace("'", '')
    expense_amount = expense_[2].replace("]", '').replace("'", '').replace(" ", "")
    expense_date = today

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
    
def help_me(update, context):
    """
    lists commands with their uses
    """
    effective_user = update.effective_user
    if effective_user.id not in ADMIN_IDs:
        update.message.reply_text(text="What do you mean, I don't get it")
        return
    update.message.reply_html(HELP_MSG)
    
def request_permision(update, context):
    """
    to requst permission for admin
    """
    user = update.effective_user
    startUser_dict = user.to_dict()
    startUser_dict["at"] = datetime.datetime.now().strftime("%d/%m/%y, %H:%M")
    startUser_dict["key"] = str(user.id)

    permission_request_db.put(startUser_dict)
    update.message.reply_html("Permission requested I will let you know soon")

def see_permission_req(update, context):
    effective_user = update.effective_user
    if effective_user.id != 403875924:
        update.message.reply_text(text="What do you mean, I don't get it")
        return
    per_requests = permission_request_db.fetch().items
    for per_request in per_requests:
        update.message.reply_text("First Name: "+per_request["first_name"]+"\nId: "+per_request["key"]+"\nAt: "+per_request["at"])

def monthly_sales(update, context):
    """
    to generate CSV or XL file that contains sales info for this month
    """
    effective_user = update.effective_user
    if effective_user.id not in ADMIN_IDs:
        update.message.reply_text(text="What do you mean, I don't get it")
        return

    sales = sales_db.fetch().items
    this_month = [["Item Name", "Quantity", "Revenu", "Date", "Recorded By", "Rrecord At"]]
    for sale in sales:
        if sale['date'][3:] == today[3:]:
            this_month.append([sale['item_name'], sale['quantity'], sale['revenu'], sale['date'], sale['admin_first_N'], sale['sales_record_at']])
    with open('This_month_sales.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(this_month)
        # writer.writerow(["Item Name", "Quantity", "Revenu", "Date", "Recorded By", "Rrecord At"])
        # for sale in sales:
        #     if sale['date'][3:] == today[3:]:
        #         writer.writerow([sale('item_name'), sale('quantity'), sale('revenu'), sale('date'), sale('admin_first_N'), sale('sales_record_at')])
    chat_id = update.message.chat_id
    document = open('This_month_sales.csv', 'rb')
    context.bot.send_document(chat_id, document)

def monthly_expense(update, context):
    """
    to generate CSV or XL file that contains expense info for this month
    """
    effective_user = update.effective_user
    if effective_user.id not in ADMIN_IDs:
        update.message.reply_text(text="What do you mean, I don't get it")
        return
    pass

def register_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('recordsales', record_sales))
    dispatcher.add_handler(CommandHandler('recordexpense', record_expense))

    dispatcher.add_handler(CommandHandler('recTodaySale', record_todays_sales))
    dispatcher.add_handler(CommandHandler('recTodaysExp', record_todays_expesne))

    dispatcher.add_handler(CommandHandler('todayssales', todays_sales))
    dispatcher.add_handler(CommandHandler('todaysexpense', todays_expense))

    dispatcher.add_handler(CommandHandler('salesdate', sales_date))
    dispatcher.add_handler(CommandHandler('expensedate', expense_date))

    dispatcher.add_handler(CommandHandler('amtheboss', record_todays_boss))
    dispatcher.add_handler(CommandHandler('whoistheboss', show_todays_boss))

    dispatcher.add_handler(CommandHandler('help_me', help_me))
    
    dispatcher.add_handler(CommandHandler('req_permission', request_permision))
    dispatcher.add_handler(CommandHandler('see_permission_req', see_permission_req))

    dispatcher.add_handler(CommandHandler('monthly_sales', monthly_sales))
    dispatcher.add_handler(CommandHandler('monthly_expense', monthly_expense))


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