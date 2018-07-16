#!/usr/bin/env python
# -*- coding: utf-8 -*-
# CheckLendingBooks_Sumida.py
import sys, os, datetime

from robobrowser import RoboBrowser
import time

# 認証の情報は環境変数から取得する
SUMIDA_LIB_ID = os.environ['SUMIDA_LIB_ID']
SUMIDA_LIB_PW = os.environ['SUMIDA_LIB_PW']

def fix_unSJIS(tarStr):
    return tarStr.encode("SJIS","ignore").decode('SJIS')

outDir = os.environ['GOOGLE_DRIVE_PATH'].replace("\\","/") + '/memo/BookRecord/'
description_tmp = "Subject,Start Date,Start Time,End Date,End Time,All Day Event,Description,Location,Private\n"
line_all = ""
line_tmp = ""
modDate = datetime.date.today().strftime("%Y/%m/%d")

# RoboBrowserオブジェクトを作成する
browser = RoboBrowser(
    parser='html.parser',
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3346.8 Safari/537.36')

# ログインページを開く
browser.open('https://www.library.sumida.tokyo.jp/login?2')
assert 'ログイン － 墨田区立図書館' in browser.parsed.title.string

# サインインフォームを埋める
form = browser.get_form(attrs={'id': 'inputForm49'})
form['textUserId'] = SUMIDA_LIB_ID
form['textPassword'] = SUMIDA_LIB_PW
submit_field = form['buttonLogin']
submit_field.value = "入力終了"

# フォームを送信
browser.submit_form(form, headers={'Referer': browser.url,'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3'},submit = submit_field)
assert SUMIDA_LIB_ID + 'さんのマイライブラリ | 墨田区立図書館' in browser.parsed.title.string

browser.follow_link(browser.get_link('貸出状況照会へ'))
assert SUMIDA_LIB_ID + 'さんの貸出状況 | 墨田区立図書館' in browser.parsed.title.string

print("\nタイトル\t返却期限")
for line_item in browser.select('div.infotable'):
    title = line_item.select('h3.space')[0].select('a')[0].get_text()
    lend  = line_item.select('table')[1].select('tr')[1].select('td')[0].get_text()
    reply = line_item.select('table')[1].select('tr')[2].select('td')[0].get_text()
    print(reply + "\t" + title)
    mod_title = fix_unSJIS(title)

    # 総合的なファイル用の貸し出しリスト
    line_all += lend + "," + reply + "," + mod_title + "\n"

    # 暫定的なファイル用の貸し出しリスト
    line_tmp += mod_title + "\n"

with open(outDir + "LendingBookList.csv", 'a', encoding = "SJIS") as f_all:
    f_all.write(line_all)

with open(outDir + datetime.date.today().strftime("%Y%m%d")+"_calendar.csv", 'w', encoding = "SJIS") as f_tmp:
    f_tmp.write(description_tmp + '借りてる書籍,' + modDate + ',,' + modDate + ',,TRUE,\"'+ line_tmp +'\",,TRUE') #"

print("\n\n\n10秒ほどポーズ\n")
time.sleep(10)
