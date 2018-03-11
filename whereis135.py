import telegram
from telegram.ext import Updater, CommandHandler
import pandas as pd

# Uncomment and paste token below
# mytoken = '<MY TOKEN HERE>'

updater = Updater(token = mytoken)
dispatcher = updater.dispatcher

custom_keyboard = [['/oldstreet', '/byng'],['/canarywharf', '/tfl']]
reply_markup_ = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard = True)
# reply_markup_ = telegram.ReplyKeyboardRemove()

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                  text="*How to use:* \n - /oldstreet for next 135 bus arriving at Old Street Stand B \n - /byng for next 135 bus arriving at Byng Street \n - /canarywharf for eastbound train updates \n - /tfl to generate URL for TfL website",
                  parse_mode=telegram.ParseMode.MARKDOWN,
                  reply_markup = reply_markup_)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

def tfl(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                  text="[TfL website](https://tfl.gov.uk/)",
                  parse_mode=telegram.ParseMode.MARKDOWN,
                  reply_markup = reply_markup_)

tfl_handler = CommandHandler('tfl', tfl)
dispatcher.add_handler(tfl_handler)


def oldstreet(bot, update):
    Data = pd.read_json('https://api.tfl.gov.uk/StopPoint/490015193S/Arrivals')
    L = Data.sort_values('timeToStation').reset_index().timeToStation
    if L.shape[0] == 1:
        a = 'Time to next bus: %.0fm%.0fs' % (L[0]//60, L[0]%60)
    elif L.shape[0] == 0:
        a = 'No bus coming. Take Uber perhaps?'
    else:
        a = 'Old Street next bus: %.0fm%.0fs, %.0fm%.0fs' % (L[0]//60, L[0]%60, L[1]//60, L[1]%60)
    bot.send_message(chat_id = update.message.chat_id, text = a, reply_markup = reply_markup_)

oldstreet_handler = CommandHandler('oldstreet', oldstreet)
dispatcher.add_handler(oldstreet_handler)

def byng(bot, update):
    Data = pd.read_json('https://api.tfl.gov.uk/StopPoint/490009545N/Arrivals')
    L = Data.loc[Data.lineId == '135'].sort_values('timeToStation').reset_index().timeToStation
    if L.shape[0] == 1:
        a = 'Time to next bus: %.0fm%.0fs' % (L[0]//60, L[0]%60)
    elif L.shape[0] == 0:
        a = 'No bus coming. Take Uber perhaps?'
    else:
        a = 'Byng Street next bus: %.0fm%.0fs, %.0fm%.0fs' % (L[0]//60, L[0]%60, L[1]//60, L[1]%60)
    bot.send_message(chat_id = update.message.chat_id, text = a, reply_markup = reply_markup_)

byng_handler = CommandHandler('byng', byng)
dispatcher.add_handler(byng_handler)

def canarywharf(bot, update):
    lineData = pd.read_json('https://api.tfl.gov.uk/Line/jubilee/Status?detail=true')
    lineStatus = (pd.DataFrame(lineData['lineStatuses'][0]).statusSeverityDescription)[0]
    paragraph = 'Jubilee line: %s\n' % (lineStatus)

    stationData = pd.read_json('https://api.tfl.gov.uk/Line/jubilee/Arrivals/940GZZLUCYF?direction=inbound')
    tab = stationData.sort_values('timeToStation').loc[:,['timeToStation', 'towards']]
    for i in range(tab.shape[0]):
        line = "%.0fm%.0fs (%s)\n" % (tab.iloc[i,:].values[0]//60, tab.iloc[i,:].values[0]%60, tab.iloc[i,:].values[1])
        paragraph += line

    bot.send_message(chat_id = update.message.chat_id, text = paragraph, reply_markup = reply_markup_)

    # bot.send_message(chat_id = update.message.chat_id, text = paragraph, reply_markup = reply_markup_)

canarywharf_handler = CommandHandler('canarywharf', canarywharf)
dispatcher.add_handler(canarywharf_handler)

updater.start_polling()
