import random
import os
import pandas as pd
import re
from openpyxl import Workbook, load_workbook
from telegram import Update, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackContext, MessageHandler, Filters, CommandHandler, CallbackQueryHandler, Updater

# تعداد کل سوال‌ها
NUM_QUESTIONS = 5

# مراحل مختلف مکالمه با کاربر
STAGE_NAME, STAGE_EMAIL, STAGE_PHONE, STAGE_QUESTION_1, STAGE_QUESTION_2, STAGE_QUESTION_3,STAGE_QUESTION_4,STAGE_QUESTION_5, STAGE_FINISH = range(1, NUM_QUESTIONS + 5)

# دیکشنری حاوی سوالات و گزینه‌ها
questions ={
    
    "سوال: نقش رله‌ها در تجهیزات برق چیست؟": {
        "گزینه‌ها": ["انتقال بارهای سنگین", "کنترل و مدیریت ترانسفورماتورها", "محافظت از تجهیزات برق در برابر جریان‌های بالا", "تنظیم ولتاژ خروجی باتری"],
        "گزینه صحیح": "محافظت از تجهیزات برق در برابر جریان‌های بالا",
        "امتیاز": 1,
    },
    "سوال : تعداد فازهای یک سیستم توزیع برق برای خانه‌ها عموماً چقدر است؟": {
        "گزینه‌ها": ["3 فاز", "1 فاز", "2 فاز", "4 فاز"],
        "گزینه صحیح": "1 فاز",
        "امتیاز": 1,
    },
    "سوال: مدار کوتاه در سیستم‌های برق به چه معناست؟": {
        "گزینه‌ها": ["دو سیم برق که به یکدیگر متصل شده‌اند", "افزایش جریان برق", "اتصال دو سیم برق به یک منبع", "کاهش ولتاژ برق"],
        "گزینه صحیح": "اتصال دو سیم برق به یک منبع",
        "امتیاز": 1,
    },
    "سوال 7: در یک سیستم توزیع برق سه فاز، چه تعداد سیم برق در کل مورد استفاده قرار می‌گیرد؟": {
        "گزینه‌ها": ["1 سیم", "2 سیم", "3 سیم", "4 سیم"],
        "گزینه صحیح": "3 سیم",
        "امتیاز": 1,
    },
    "سوال: ترانسفورماتور چه کاربردی دارد؟": {
        "گزینه‌ها": ["تبدیل ولتاژ برق", "محافظت از تجهیزات برقی", "تقویت جریان برق", "تبدیل جریان مستقیم به جریان متناوب (جواب درست)"],
        "گزینه صحیح": "تبدیل جریان مستقیم به جریان متناوب (جواب درست)",
        "امتیاز": 1,
    },
    "سوال: تابلوی برق چه کاربردی در ایستگاه‌های برق دارد؟": {
        "گزینه‌ها": ["نمایش ولتاژ برق", "کنترل دما", "کنترل و محافظت از تجهیزات برقی", "تولید انرژی برق"],
        "گزینه صحیح": "کنترل و محافظت از تجهیزات برقی",
        "امتیاز": 1,
    },
    "سوال: در تجهیزات برقی برای چه منظوری از جداسازی (ایزوله) استفاده می‌شوند؟": {
        "گزینه‌ها": ["اتصال تجهیزات برقی به یک منبع مشترک", "محافظت در برابر اتصال کوتاه", "جدا سازی تجهیزات برقی از منابع برق", "کنترل ولتاژ برق"],
        "گزینه صحیح": "جدا سازی تجهیزات برقی از منابع برق",
        "امتیاز": 1,
    },
    "سوال: رله حفاظتی در سیستم برق چه کاربردی دارد؟": {
        "گزینه‌ها": ["کنترل مصرف برق", "کاهش ولتاژ برق", "حفاظت در برابر جریان‌های اضافی و زیاد", "تنظیم ولتاژ برق"],
        "گزینه صحیح": "حفاظت در برابر جریان‌های اضافی و زیاد",
        "امتیاز": 1,
    },
    "سوال: کدام یک از موارد زیر یک مثال از منبع تغذیه‌های برق هستند؟": {
        "گزینه‌ها": ["باتری", "لامپ‌های ال ای دی", "رله‌ها", "ترانسفورماتورها"],
        "گزینه صحیح": "باتری",
        "امتیاز": 1,
    },
    "سوال: اصطلاح 'پیک ولتاژ' در برق به چه معناست؟": {
        "گزینه‌ها": ["ولتاژ برقی بالای معمول", "ولتاژ برقی پایین‌تر از معمول", "تغییر ناگهانی ولتاژ برق", "عدم وجود ولتاژ برق"],
        "گزینه صحیح": "تغییر ناگهانی ولتاژ برق",
        "امتیاز": 1,
    },
    "سوال: تجهیزات برقی چگونه در برابر خرابی‌ها محافظت می‌شوند؟": {
        "گزینه‌ها": ["با استفاده از موارد اضافی برق", "با نصب تجهیزات محافظتی مانند رله‌های حفاظتی", "با کاهش ولتاژ برق", "با افزایش جریان برق"],
        "گزینه صحیح": "با نصب تجهیزات محافظتی مانند رله‌های حفاظتی",
        "امتیاز": 1,
    },
    "سوال: محافظ‌های حرارتی چه کاربردی دارند؟": {
        "گزینه‌ها": ["افزایش دما", "کنترل و محافظت از دما", "کاهش دما", "اتصال دو سیم برق به یک منبع"],
        "گزینه صحیح": "کنترل و محافظت از دما",
        "امتیاز": 1,
    },
    "سوال: رله‌های حفاظتی برای چه منظوری استفاده می‌شوند؟": {
        "گزینه‌ها": ["کنترل ولتاژ برق", "محافظت در برابر جریان‌های اضافی و زیاد", "تولید انرژی برق", "تغییر ولتاژ برق"],
        "گزینه صحیح": "محافظت در برابر جریان‌های اضافی و زیاد",
        "امتیاز": 1,
    },
    "سوال: چه تجهیزات برقی می‌توانند در صورت نیاز از باتری استفاده کنند؟": {
        "گزینه‌ها": ["لامپ‌های روشنایی", "موتورها", "کامپیوترها", "تابلوهای برقی"],
        "گزینه صحیح": "کامپیوترها",
        "امتیاز": 1,
    },
    "سوال: چه عواملی باعث افت ولتاژ در شبکه برق می‌شوند؟": {
        "گزینه‌ها": ["بار زیاد در شبکه برق", "عملکرد نامناسب ترانسفورماتورها", "کاهش نیروی جریان", "افزایش توان مصرفی"],
        "گزینه صحیح": "عملکرد نامناسب ترانسفورماتورها",
        "امتیاز": 1,
    },
    "سوال: کدام یک از موارد زیر از ترانسفورماتورها در صنعت استفاده می‌شود؟": {
        "گزینه‌ها": ["افزایش ولتاژ برق", "کاهش ولتاژ برق", "تغییر نوع جریان برق", "ایجاد جریان مستقیم"],
        "گزینه صحیح": "تغییر نوع جریان برق",
        "امتیاز": 1,
    },
    "سوال: ولتاژ مستقیم و متناوب در چه کاربردهایی مورد استفاده قرار می‌گیرند؟": {
        "گزینه‌ها": ["ولتاژ مستقیم برای انتقال انرژی برق استفاده می‌شود و ولتاژ متناوب برای کاربردهای خانگی و صنعتی", "هر دو برای انتقال انرژی برق استفاده می‌شوند", "هر دو برای کاربردهای خانگی و صنعتی استفاده می‌شوند", "ولتاژ متناوب برای انتقال انرژی برق استفاده می‌شود و ولتاژ مستقیم برای کاربردهای خانگی و صنعتی"],
        "گزینه صحیح": "ولتاژ مستقیم برای انتقال انرژی برق استفاده می‌شود و ولتاژ متناوب برای کاربردهای خانگی و صنعتی",
        "امتیاز": 1,
    },
    "سوال: منظور از عمر مفید تجهیزات برقی چیست؟": {
        "گزینه‌ها": ["زمانی که تجهیزات برقی تولید می‌شوند", "زمانی که تجهیزات برقی در صنعت استفاده می‌شوند", "مدت زمان کارکرد موثر تجهیزات برقی قبل از احتیاج به تعمیر یا تعویض", "زمانی که تجهیزات برقی به طور کامل خراب می‌شوند"],
        "گزینه صحیح": "مدت زمان کارکرد موثر تجهیزات برقی قبل از احتیاج به تعمیر یا تعویض",
        "امتیاز": 1,
    },
    "سوال: اصطلاح 'جریان نامی' در برق به چه معناست؟": {
        "گزینه‌ها": ["بیشترین جریانی که یک تجهیز برقی می‌تواند تحمل کند", "کمترین جریانی که یک تجهیز برقی می‌تواند تحمل کند", "جریانی که برای کارکرد معمولی تجهیزات برقی نیاز است", "جریانی که برای کارکرد موقتی تجهیزات برقی نیاز است"],
        "گزینه صحیح": "جریانی که برای کارکرد معمولی تجهیزات برقی نیاز است",
        "امتیاز": 1,
    },
    "سوال: ترانسفورماتورها در صنعت برق چه کاربردی دارند؟": {
        "گزینه‌ها": ["کاهش جریان برق", "تغییر ولتاژ برق", "افزایش ولتاژ برق", "تنظیم دمای محیط"],
        "گزینه صحیح": "تغییر ولتاژ برق",
        "امتیاز": 1,
    },
    "سوال: الکتروموتورها در زمان راه اندازی چند برابر جریان نامی خود دریافت می کنند؟": {
        "گزینه‌ها": ["۶ برابر", "۵ تا ۷ برابر", "۴ برابر", "۲ تا ۳ برابر"],
        "گزینه صحیح": "۵ تا ۷ برابر",
        "امتیاز": 1,
    },
    "سوال: بهترین راه برای جلوگیری از افت فشار در کارگاه ها در زمان راه اندازی الکتروموتور چیست؟": {
        "گزینه‌ها": ["افزایش جریان ورودی", "استفاده از برق سه فاز در کارگاه", "استفاده از فیوز قوی تر","استفاده از سیم های قوی تر در سیم کشی کارگاه"],
        "گزینه صحیح": "استفاده از برق سه فاز در کارگاه",
        "امتیاز": 1,
    },
    "سوال: علت قطع و وصل ناگهانی برق تمام ساختمان چیست ؟": {
        "گزینه‌ها": ["بار قوی در مدار داخلی ساختمان", "بار قوی در شبکه بیرون ساختمان", "بار قوی در شبکه (داخل یا خارج ساختمان)", "اشکال در سیم کشی داخلی ساختمان"],
        "گزینه صحیح": " بار قوی در شبکه (داخل یا خارج ساختمان)",
        "امتیاز": 1,
    },
    "سوال: علت چشمک زدن لامپ کم مصرف در زمان خاموشی چیست؟": {
        "گزینه‌ها": ["محکم نبودن لامپ در هلدر", "مشکل مربوط به کلید برق است", "مدار داخلی لامپ اتصال دارد", "برق دزدی در مدار داخلی ساختمان"],
        "گزینه صحیح": "مشکل مربوط به کلید برق است",
        "امتیاز": 1,
    },
    "سوال: با اتصال یک وسیله الکتریکی مانند اتو به برق، روشنایی برای چند لحظه ضعیف می‌شود، علت چیست؟": {
        "گزینه‌ها": ["یکی بودن مدار پریز با مدار روشنایی", "افت فشار مدار", "استفاده از فیوز نامناسب", "ایجاد جریان مستقیم"],
        "گزینه صحیح": "یکی بودن مدار پریز با مدار روشنایی",
        "امتیاز": 1,
    },
    "سوال: چرا در انتقال برق استفاده از ولتاژ‌های متناوب را نسبت به ولتاژ‌های مستقیم ترجیح داده اند؟": {
        "گزینه‌ها": ["بار زیاد در شبکه برق", "عملکرد نامناسب ترانسفورماتورها", "امکان افزایش ولتاژ و کاهش تلفات در جریان متناوب", "هزینه کمتر انتقال"],
        "گزینه صحیح": "امکان افزایش ولتاژ و کاهش تلفات در جریان متناوب",
        "امتیاز": 1,
    },
    "سوال: دلیل الزام به جداسازی مدار پریزها و سیستم روشنایی در ساختمان چیست؟": {
        "گزینه‌ها": ["جلوگیری از افزایش بار در مدار", "عملکرد نامناسب فیوزها", "عملکرد صحیح تر چراغ ها و تجهیزات الکتریکی که به پریزها وصل می شوند", "افزایش توان مصرفی"],
        "گزینه صحیح": "عملکرد صحیح تر چراغ ها و تجهیزات الکتریکی که به پریزها وصل می شوند",
        "امتیاز": 1,
    },
    "سوال: لوله‌های فلکسیبل، به چه لوله‌هایی می‌گویند؟": {
        "گزینه‌ها": ["لوله انعطاف پذیر", "نوعی لوله PVC", "لوله های خرطومی فلزی", "لوله های خرطومی"],
        "گزینه صحیح": "لوله های خرطومی فلزی",
        "امتیاز": 1,
    },

    "سوال: فاصله مناسب کلیدهای ساختمان از کف چقدر است؟": {
        "گزینه‌ها": ["۱ متر", "۱۰۰ تا ۱۱۰ سانتی متر", "۱۲۰ سانتی متر", "۱۱۰ تا ۱۲۰ سانتی متر"],
        "گزینه صحیح": "۱۱۰ تا ۱۲۰ سانتی متر",
        "امتیاز": 1,
    },

    "سوال: فاصله مناسب قوطی برق از چهارچوب در چقدر است؟": {
        "گزینه‌ها": ["۱۵ تا ۲۵ سانتی متر", "۳۰ سانتی متر", "۳۰ تا ۴۰ سانتی متر", "۴۰ سانتی متر"],
        "گزینه صحیح": "۱۵ تا ۲۵ سانتی متر",
        "امتیاز": 1,
    },


    "سوال: فاصله مناسب پریزهای برق ، تلفن و آنتن از زمین چقدر است؟": {
        "گزینه‌ها": ["۵۰ سانتی متر", "۶۰ سانتی متر", "۵۰ تا ۶۰ سانتی متر", "۳۰ تا ۴۰ ساننتی متر"],
        "گزینه صحیح": "۳۰ تا ۴۰ ساننتی متر",
        "امتیاز": 1,
    },


    "سوال: حداقل فاصله بین لوله های آب و گاز از جعبه فیوز چقدر است؟": {
        "گزینه‌ها": ["۱۲۰ سانتی متر", "۱۰۰ سانتی متر", " ۵۰ سانتی متر", "۲ متر"],
        "گزینه صحیح": "۱۰۰ سانتی متر",
        "امتیاز": 1,
    },


    "سوال: فاصله مناسب جعبه فیوز از زمین چقدر است؟": {
        "گزینه‌ها": ["۱۰۰ تا ۱۲۰ سانتی متر", "۱۲۰ تا ۱۳۰ سانتی متر", "۱۵۰ تا ۱۷۰ سانتی متر", "۱۶۰ تا ۱۸۰ سانتی متر"],
        "گزینه صحیح": "۱۵۰ تا ۱۷۰ سانتی متر",
        "امتیاز": 1,
    },


    "سوال: فاصله مناسب آیفون تصویری و گوشی از کف چقدر است؟": {
        "گزینه‌ها": ["۱۱۰ تا ۱۲۰ سانتی متر", "۱۲۰ سانتی متر", "۱۴۰ تا ۱۵۰ سانتی متر", "۱۴۰ سانتی متر"],
        "گزینه صحیح": "۱۴۰ تا ۱۵۰ سانتی متر",
        "امتیاز": 1,
    },


    "سوال: نشانه فرسودگی سیم های ساختمان چیست؟": {
        "گزینه‌ها": ["سرخ بودن سیم", "زنگ زدگی یا رنگ پریدگی سیم", "رنگ پریدگی سیم", "زنگ زدگی سیم"],
        "گزینه صحیح": " زنگ زدگی یا رنگ پریدگی سیم",
        "امتیاز": 1,
    },


    "سوال: ظرفیت مناسب فیوزهای مربوط به سیستم روشنایی خانه چند آمپر است؟": {
        "گزینه‌ها": ["۳۰ آمپر", "حدود ۳۰ آمپر", " حدود ۱۰ آمپر", "حدود ۱۶ آمپر"],
        "گزینه صحیح": "حدود ۱۰ آمپر",
        "امتیاز": 1,
    },


    "سوال: ظرفیت ماسب فیوزهای مربوط به پریزهای برق چند آمپر است؟": {
        "گزینه‌ها": ["حدود ۱۶ آمپر", "حدود ۱۴ آمپر", "۱۰ آمپر", "۲۵ آمپر"],
        "گزینه صحیح": " حدود ۱۶ آمپر",
        "امتیاز": 1,
    },


    "سوال: ظرفیت مناسب فیوز کولرهای آبی چند آمپر است؟": {
        "گزینه‌ها": ["۱۶ آمپر", "حدود ۲۰ آمپر", "۳۰ آمپر", "حدود ۲۵ آمپر"],
        "گزینه صحیح": " حدود ۲۰ آمپر",
        "امتیاز": 1,
    },


    "سوال: چرا از سیم آلومینیومی در سیم کشی ساختمان استفاده می شود؟": {
        "گزینه‌ها": ["قیمت بالاتر آلومینیوم نسبت به مس", "افزایش حجم سیم در زمان جریان برق و شکنندگی بیشتر", "بروز آتش سوزی در ساختمان", "فرسودگی سریعتر"],
        "گزینه صحیح": "افزایش حجم سیم در زمان جریان برق و شکنندگی بیشتر",
        "امتیاز": 1,
    },


    "سوال: دلیل بروز آتش سوزی در سیم کشی های آلومینیومی چیست؟": {
        "گزینه‌ها": ["افزایش حجم سیم در زمان جریان برق", "شل شدن اتصالات", "جرقه زدن در محل اتصالات", "همه موارد"],
        "گزینه صحیح": "همه موارد",
        "امتیاز": 1,
    },



}


def save_data_to_excel(data):
    file_path = 'user_data.xlsx'

    # Create a new DataFrame with data
    df = pd.DataFrame(data)

    if not os.path.exists(file_path):
        # If the Excel file doesn't exist, save the DataFrame to a new file
        df.to_excel(file_path, index=False)
    else:
        # If the Excel file exists, append the DataFrame to the existing file
        existing_data = pd.read_excel(file_path)
        combined_data = pd.concat([existing_data, df], ignore_index=True)
        combined_data.to_excel(file_path, index=False)





def is_valid_email(email):
    # الگوی صحیح ایمیل
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)


def is_valid_phone(phone):
    # الگوی صحیح شماره تلفن
    pattern = r'^\d{11}$'
    return re.match(pattern, phone)


def get_random_question_and_keyboard():
    # انتخاب یک سوال به صورت تصادفی
    question, question_info = random.choice(list(questions.items()))

    # انتخاب گزینه‌ها به صورت تصادفی
    random_answers = random.sample(question_info["گزینه‌ها"], k=4)
    keyboard = [
        [InlineKeyboardButton(answer, callback_data=answer)] for answer in random_answers
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    return question, reply_markup


def start(update: Update, context: CallbackContext) -> int:
    context.user_data['امتیاز'] = 0  # مقداردهی اولیه امتیاز به صفر

    update.message.reply_text(
        "لطفاً نام خود را وارد کنید:",
        reply_markup=ReplyKeyboardRemove(),
    )
    return STAGE_NAME


def get_user_info(update: Update, context: CallbackContext) -> int:
    context.user_data['name'] = update.message.text

    update.message.reply_text(
        "لطفاً ایمیل خود را وارد کنید:",
        reply_markup=ReplyKeyboardRemove(),
    )
    return STAGE_EMAIL


def get_email(update: Update, context: CallbackContext) -> int:
    email = update.message.text

    if not is_valid_email(email):
        update.message.reply_text("ایمیل وارد شده معتبر نیست. لطفاً ایمیل معتبری وارد کنید:")
        return STAGE_EMAIL

    context.user_data['email'] = email

    update.message.reply_text(
        "لطفاً شماره تلفن ۱۱ رقمی خود را وارد کنید:",
        reply_markup=ReplyKeyboardRemove(),
    )
    return STAGE_PHONE


def get_phone(update: Update, context: CallbackContext) -> int:
    phone = update.message.text

    if not is_valid_phone(phone):
        update.message.reply_text("شماره تلفن وارد شده معتبر نیست. لطفاً شماره تلفن معتبری وارد کنید:")
        return STAGE_PHONE

    context.user_data['phone'] = phone

    # انتقال به مرحله پرسش سوال تستی اول
    question, keyboard = get_random_question_and_keyboard()
    context.user_data['question_1'] = question

    update.message.reply_text(question, reply_markup=keyboard)
    return STAGE_QUESTION_1


def question_1(update: Update, context: CallbackContext) -> int:
    user_answer = update.callback_query.data
    context.user_data['answer_1'] = user_answer

    # بررسی جواب سوال تستی اول
    question_info = questions[context.user_data['question_1']]
    if user_answer == question_info["گزینه صحیح"]:
        context.user_data['امتیاز'] = question_info["امتیاز"]

    # انتقال به مرحله پرسش سوال تستی دوم
    question, keyboard = get_random_question_and_keyboard()
    context.user_data['question_2'] = question

    update.callback_query.edit_message_text(question, reply_markup=keyboard)
    return STAGE_QUESTION_2


def question_2(update: Update, context: CallbackContext) -> int:
    user_answer = update.callback_query.data
    context.user_data['answer_2'] = user_answer

    # بررسی جواب سوال تستی دوم
    question_info = questions[context.user_data['question_2']]
    if user_answer == question_info["گزینه صحیح"]:
        context.user_data['امتیاز'] += question_info["امتیاز"]

    # انتقال به مرحله پرسش سوال تستی سوم
    question, keyboard = get_random_question_and_keyboard()
    context.user_data['question_3'] = question

    update.callback_query.edit_message_text(question, reply_markup=keyboard)
    return STAGE_QUESTION_3

def question_3(update: Update, context: CallbackContext) -> int:
    user_answer = update.callback_query.data
    context.user_data['answer_3'] = user_answer

    # بررسی جواب سوال تستی دوم
    question_info = questions[context.user_data['question_3']]
    if user_answer == question_info["گزینه صحیح"]:
        context.user_data['امتیاز'] += question_info["امتیاز"]

    # انتقال به مرحله پرسش سوال تستی سوم
    question, keyboard = get_random_question_and_keyboard()
    context.user_data['question_4'] = question

    update.callback_query.edit_message_text(question, reply_markup=keyboard)
    return STAGE_QUESTION_4

def question_4(update: Update, context: CallbackContext) -> int:
    user_answer = update.callback_query.data
    context.user_data['answer_4'] = user_answer

    # بررسی جواب سوال تستی دوم
    question_info = questions[context.user_data['question_4']]
    if user_answer == question_info["گزینه صحیح"]:
        context.user_data['امتیاز'] += question_info["امتیاز"]

    # انتقال به مرحله پرسش سوال تستی سوم
    question, keyboard = get_random_question_and_keyboard()
    context.user_data['question_5'] = question

    update.callback_query.edit_message_text(question, reply_markup=keyboard)
    return STAGE_QUESTION_5


def question_5(update: Update, context: CallbackContext) -> int:
    user_answer = update.callback_query.data
    context.user_data['answer_5'] = user_answer

    # بررسی جواب سوال تستی سوم
    question_info = questions[context.user_data['question_5']]
    if user_answer == question_info["گزینه صحیح"]:
        context.user_data['امتیاز'] += question_info["امتیاز"]

    # ذخیره اطلاعات در فایل اکسل
    data = {
        'نام': [context.user_data.get('name')],
        'ایمیل': [context.user_data.get('email')],
        'تلفن': [context.user_data.get('phone')],
        'پرسش 1': [context.user_data.get('question_1')],
        'پاسخ 1': [context.user_data.get('answer_1')],
        'پرسش 2': [context.user_data.get('question_2')],
        'پاسخ 2': [context.user_data.get('answer_2')],
        'پرسش 3': [context.user_data.get('question_3')],
        'پاسخ 3': [context.user_data.get('answer_3')],
        'پرسش 4': [context.user_data.get('question_4')],
        'پاسخ 4': [context.user_data.get('answer_4')],
        'پرسش 5': [context.user_data.get('question_5')],
        'پاسخ 5': [context.user_data.get('answer_5')],
        
        'امتیاز': [context.user_data.get('امتیاز')],
    }

    save_data_to_excel(data)

    update.callback_query.message.reply_text(f"تمامی اطلاعات با موفقیت ذخیره شدند. امتیاز شما: {context.user_data.get('امتیاز')} از {NUM_QUESTIONS}", reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


if __name__ == '__main__':
    updater = Updater('6364346876:AAENMM1pX8iIRV8TGQbwGRnT6w4slXktNZ8')
    updater.start_polling(timeout=60)
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            STAGE_NAME: [MessageHandler(Filters.text & ~Filters.command, get_user_info)],
            STAGE_EMAIL: [MessageHandler(Filters.text & ~Filters.command, get_email)],
            STAGE_PHONE: [MessageHandler(Filters.text & ~Filters.command, get_phone)],
            STAGE_QUESTION_1: [CallbackQueryHandler(question_1)],
            STAGE_QUESTION_2: [CallbackQueryHandler(question_2)],
            STAGE_QUESTION_3: [CallbackQueryHandler(question_3)],
            STAGE_QUESTION_4: [CallbackQueryHandler(question_4)],
            STAGE_QUESTION_5: [CallbackQueryHandler(question_5)],
            #STAGE_FINISH: [CallbackQueryHandler(finish)],
        },
        fallbacks=[],
    )

    updater.dispatcher.add_handler(conversation_handler)

    updater.idle()
