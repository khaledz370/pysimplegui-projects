import PySimpleGUI as psg
from threading import Timer
from praytimes import PrayTimes
from datetime import datetime, timedelta
from psgtray import SystemTray
from playsound import playsound
import os
import json
from tendo import singleton

# allow only one instance
me = singleton.SingleInstance()

# constants
prayersList = ["fajr", "dhuhr", "asr", "maghrib", "isha"]
methods = ["MWL", "ISNA", "Egypt", "Makkah", "Karachi", "Tehran", "Jafari"]
asrMethods = ["Standard", "Hanafi"]
timezones = list(range(-12, 12))
menu = ['', ["settings", 'Exit']]
menuMain = ['', ["hide", "settings", 'Exit']]
tooltip = 'prayer times'
secondsInDay = 86400
fontsize = 15
font = ("Arial", fontsize)
appSize = (340, 320)
defaultSettings = {'lat': '29.9', 'long': '31.2', 'timeZone': 2, 'method': 'EGYPT', 'fajr': '19.5', 'dhuhr': '0',
                   'asr': 'Standard', 'maghrib': '1', 'isha': '17.5', 'minimized': 1}
appdataFolder = f"{os.getenv('APPDATA')}\prayerTimes"
appdataFile = f"{appdataFolder}\config.json"

# settings
try:
    if not os.path.exists(appdataFolder):
        os.mkdir(appdataFolder)
    if not os.path.exists(appdataFile):
        open(appdataFile, "x")
    file = open(appdataFile, "r")
except:
    file = open(appdataFile, "r")

try:
    settings = json.load(file)
    # print('load settings from config')
except:
    settings = defaultSettings
    with open(appdataFile, 'w') as file:
        json.dump(defaultSettings, file)
    # print("Load default settings")    

def main():
    now = datetime.now()
    pTimes = getPrayerTimes()
    fajr = formatPrayerDate(pTimes["fajr"])
    dhuhr = formatPrayerDate(pTimes["dhuhr"])
    asr = formatPrayerDate(pTimes["asr"])
    maghrib = formatPrayerDate(pTimes["maghrib"])
    isha = formatPrayerDate(pTimes["isha"])
    time = str((now.strftime("%d-%m-%Y, %I:%M:%S %p")))
    settings["thread"] = 0
    
    l_title = [psg.Text("Prayer Times", justification="c", expand_x=True)]
    l_fajr = [psg.Text("fajr: "),psg.Text(fajr, key="fajr",justification="r", expand_x=True)]
    l_dhuhr = [psg.Text("dhuhr: "),psg.Text(dhuhr, key="dhuhr",justification="r", expand_x=True)]
    l_asr= [psg.Text("asr: "),psg.Text(asr, key="asr",justification="r", expand_x=True)]
    l_maghrib = [psg.Text("maghrib: "),psg.Text(maghrib, key="maghrib",justification="r", expand_x=True)]
    l_isha = [psg.Text("isha: "),psg.Text(isha, key="isha",justification="r", expand_x=True)]
    l_date = [psg.Text(time, key="Time", justification="c",enable_events=True, expand_x=True)]
    l_nextPrayer = [psg.Text("next prayer is"),psg.Text("", key="nextPrayer",text_color="red", font=font)]
    l_timeLeft = [psg.Text("", key="timeLeft",justification="c",expand_x=True)]   
    layout = [l_title,l_fajr,l_dhuhr,l_asr,l_maghrib,l_isha,l_date,l_nextPrayer,l_timeLeft]
        
    # print(layout)

    window = psg.Window("Prayer Times", layout, size=isShown(), keep_on_top=True, grab_anywhere=True, font=font,
                        icon='resources/img/prayertimes.ico', alpha_channel=.7, element_justification="c" ,no_titlebar=True, element_padding=4,
                        right_click_menu=menuMain,finalize=True)
    tray = SystemTray(menu, window=window,tooltip=tooltip, icon='resources/img/prayertimes.ico')

    playsound('resources/audio/Bismillah.wav')

    def calcPrayerTimes():
        now = datetime.now()
        nexPrayerIndex = nextPrayer()
        pTimes = getPrayerTimes(nexPrayerIndex)
        fajr = formatPrayerDate(pTimes["fajr"])
        dhuhr = formatPrayerDate(pTimes["dhuhr"])
        asr = formatPrayerDate(pTimes["asr"])
        maghrib = formatPrayerDate(pTimes["maghrib"])
        isha = formatPrayerDate(pTimes["isha"])
        nextprayer = prayersList[nexPrayerIndex]
        window["fajr"].Update(fajr, text_color=("red" if nextprayer == "fajr" else "white"))
        window["dhuhr"].Update(dhuhr, text_color=("red" if nextprayer == "dhuhr" else "white"))
        window["asr"].Update(asr, text_color=("red" if nextprayer == "asr" else "white"))
        window["maghrib"].Update(maghrib, text_color=("red" if nextprayer == "maghrib" else "white"))
        window["isha"].Update(isha, text_color=("red" if nextprayer == "isha" else "white"))
        window["Time"].Update(str((now.strftime("%d-%m-%Y, %I:%M:%S %p"))))
        leftTilNextPrayer = (calcNextPrayer(pTimes[prayersList[nexPrayerIndex]],nexPrayerIndex))
        window["nextPrayer"].Update(f"{nextprayer}")
        window["timeLeft"].Update(f"after {leftTilNextPrayer}")
        l1 = f"fajr:  {fajr}"
        l2 = f"duhr:  {dhuhr}"
        l3 = f"asr:  {asr}"
        l4 = f"maghrib  {maghrib}"
        l5 = f"isha:  {isha}"
        l6 = f"{nextprayer} is after {leftTilNextPrayer}"
        tooltip = f"{l1}\n{l2}\n{l3}\n{l4}\n{l5}\n\n{l6}"
        tray.set_tooltip(tooltip)
        counterId = Timer(1.0, calcPrayerTimes)
        settings["thread"] = counterId
        counterId.start()
        counterId = ""
    Timer(1.0, calcPrayerTimes).start()

    while True:
        event, values = window.read()
        # IMPORTANT step. It's not required, but convenient. Set event to value from tray
        # if it's a tray event, change the event variable to be whatever the tray sent
        if event == tray.key:
            # use the System Tray's event as if was from the window
            event = values[event]
        if event == "__DOUBLE_CLICKED__":
            if settings["minimized"] == 0:
                window.size = (0, 0)
                settings["minimized"] = 1
            else:
                window.size = appSize
                settings["minimized"] = 0
                move_center(window)
        if event == "hide":
            window.size = (0, 0)
            settings["minimized"] = 0
        if event == "settings":
            open_settings()
        if event == "Exit":
            settings["thread"].cancel()
            del settings["thread"]
            window.close()
        if event in (psg.WIN_CLOSED, "Exit"):
            break


def formatPrayerDate(prayer):
    nowDate = datetime.now()
    prayerTxt = str(prayer).split(":")
    hour = int(prayerTxt[0])
    minute = int(prayerTxt[1])
    formatedDate = nowDate.replace(
        hour=hour, minute=minute).strftime("%I:%M %p")
    return formatedDate


def nextPrayer():
    now = datetime.now()
    pTimes = getPrayerTimes()
    prayers = [pTimes["fajr"], pTimes["dhuhr"],
               pTimes["asr"], pTimes["maghrib"], pTimes["isha"]]
    nowHrMn = now.strftime("%H:%M")
    # print(prayers)
    prayers.append(str(nowHrMn))
    sortedTimes = sorted(prayers)
    prayerIndex = sortedTimes.index(str(nowHrMn))
    # print(prayerIndex)
    if prayerIndex > 4:
        prayerIndex = 0
    return prayerIndex


def getPrayerTimes(index=1):
    now = datetime.now()
    hour = now.strftime("%H")
    year = int(now.strftime("%Y"))
    month = int(now.strftime("%m"))
    day = int(now.strftime("%d"))
    pT = PrayTimes("Egypt")
    s_dhuhr = settings["dhuhr"]
    pT.adjust({"fajr": settings["fajr"], "dhuhr": f"{s_dhuhr} min",
              "asr": settings["asr"], "maghrib": settings["maghrib"], "isha": settings["isha"]})
    if not index and int(hour) > 12:
        try:
            datetime(year,month,day+1)
            prayerTimesList = pT.getTimes([year, month, day+1], [float(settings["lat"]), float(settings["long"])], settings["timeZone"])
        except:
            try:
                datetime(year,month+1,1)
                prayerTimesList = pT.getTimes([year, month+1, 1], [float(settings["lat"]), float(settings["long"])], settings["timeZone"])
            except:
                prayerTimesList = pT.getTimes([year+1, 1, 1], [float(settings["lat"]), float(settings["long"])], settings["timeZone"])
    else:
        prayerTimesList = pT.getTimes([year, month, day], [float(settings["lat"]), float(settings["long"])], settings["timeZone"])
    return prayerTimesList


def calcNextPrayer(prayer,index):
    # print(prayer)
    d1 = datetime.now()
    d1h = d1.strftime("%H")
    d1m = d1.strftime("%M")
    d1s = d1.strftime("%S")
    totalSec1 = int(d1h)*60*60+int(d1m)*60+int(d1s)
    prayerTxt = str(prayer).split(":")
    d2h = int(prayerTxt[0])
    d2m = int(prayerTxt[1])
    d2s = 0
    totalSec2 = int(d2h)*60*60+int(d2m)*60+int(d2s)
    if not index and int(d1h) > 12:
        difSec = secondsInDay-abs(totalSec1-totalSec2)
    else:
        difSec = abs(totalSec1-totalSec2)
    timeLeft = str(timedelta(seconds=(difSec)))
    return timeLeft


def open_settings():
    l_title = [psg.Text("Settings", justification="c", expand_x=True)]
    l_latLongTimeZone = [psg.Text("lat:", s=(10, 1)),
                         psg.Input(str(settings["lat"]), k="s_lat", s=(20, 1)),
                         psg.Text("long:"), psg.Input(str(settings["long"]), k="s_long", s=(20, 1)),
                         psg.Text("timezone"),psg.Combo(timezones, k="s_timeZone", s=(5, 1), expand_x=True, default_value=settings["timeZone"])]
    l_method = [psg.Text("method:", s=(10, 1)),psg.Combo(methods, s=(10, 1), expand_x=True, k="s_method", default_value=settings["method"])]
    l_fajr_duhr_asr = [psg.Text("fajr :", s=(10, 1)),psg.Input(str(settings["fajr"]), expand_x=True, justification="r",  s=(5, 1), k="s_fajr"),
                        psg.Text("deg", s=(5, 1)),psg.Text("dhuhr:"),
                        psg.Input(str(settings["dhuhr"]), expand_x=True, justification="r", s=(5, 1), k="s_dhuhr"),psg.Text("min", s=(6, 1)),
                        psg.Text("asr:"),psg.Combo(asrMethods, s=(6, 1), k="s_asr", expand_x=True, default_value=settings["asr"])]
    l_maghrib_isha = [psg.Text("maghrib:", s=(10, 1)),psg.Input(str(settings["maghrib"]), justification="r", expand_x=True, k="s_maghrib"),
                        psg.Text("degrees"),psg.Text("isha:"),psg.Input(str(settings["isha"]), justification="r", expand_x=True, k="s_isha"),
                        psg.Text("degrees", s=(6, 1))]
    l_minimized = [psg.Checkbox("start minimized", default=settings["minimized"],k="s_minimized", enable_events=True)]
    l_buttons = [psg.Button("Default", enable_events=True, key="default", expand_x=True),psg.Button("Save", enable_events=True, expand_x=True),
                        psg.Button("Exit", enable_events=True, expand_x=True)]
    settingLayout = [l_title,l_latLongTimeZone,l_method,l_fajr_duhr_asr,l_maghrib_isha,l_minimized,l_buttons]
    settingsWindow = psg.Window("Settings", settingLayout, modal=True,
                                icon="resources/img/prayertimesSettings.ico", grab_anywhere=True, element_justification="c",finalize=True)
    while True:
        event, values = settingsWindow.read()
        # print(event)
        if event == "Exit" or event == psg.WIN_CLOSED:
            break
        if event == "Save":
            settings["lat"] = values["s_lat"]
            settings["long"] = values["s_long"]
            settings["timeZone"] = values["s_timeZone"]
            settings["method"] = values["s_method"]
            settings["fajr"] = values["s_fajr"]
            settings["dhuhr"] = values["s_dhuhr"]
            settings["asr"] = values["s_asr"]
            settings["maghrib"] = values["s_maghrib"]
            settings["isha"] = values["s_isha"]
            if values["s_minimized"]:
                settings["minimized"] = 1
            else:
                settings["minimized"] = 0
            del settings["thread"]
            with open(appdataFile, 'w') as file:
                json.dump(settings, file)
        if event == "default":
            settings["lat"] = defaultSettings["lat"]
            settings["long"] = defaultSettings["long"]
            settings["timeZone"] = defaultSettings["timeZone"]
            settings["method"] = defaultSettings["method"]
            settings["fajr"] = defaultSettings["fajr"]
            settings["dhuhr"] = defaultSettings["dhuhr"]
            settings["asr"] = defaultSettings["asr"]
            settings["maghrib"] = defaultSettings["maghrib"]
            settings["isha"] = defaultSettings["isha"]
            settings["minimized"] = defaultSettings["minimized"]
            settingsWindow["s_lat"].Update(defaultSettings["lat"])
            settingsWindow["s_long"].Update(defaultSettings["long"])
            settingsWindow["s_timeZone"].Update(defaultSettings["timeZone"])
            settingsWindow["s_method"].Update(defaultSettings["method"])
            settingsWindow["s_fajr"].Update(defaultSettings["fajr"])
            settingsWindow["s_dhuhr"].Update(defaultSettings["dhuhr"])
            settingsWindow["s_asr"].Update(defaultSettings["asr"])
            settingsWindow["s_maghrib"].Update(defaultSettings["maghrib"])
            settingsWindow["s_isha"].Update(defaultSettings["isha"])
            settingsWindow["s_minimized"].Update(defaultSettings["minimized"])
    settingsWindow.close()


def isShown():
    if settings["minimized"]:
        return (0, 0)
    else:
        return appSize

def move_center(window):
    screen_width, screen_height = window.get_screen_dimensions()
    win_width, win_height = window.size
    x, y = (screen_width - win_width)//2, (screen_height - win_height)//2
    window.move(x, y)

if __name__ == "__main__":
    main()
