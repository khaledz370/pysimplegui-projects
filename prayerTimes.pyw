import PySimpleGUI as psg
from threading import Timer
from praytimes import PrayTimes
from datetime import datetime, timedelta
from psgtray import SystemTray
from playsound import playsound
import json
import pyautogui
from tendo import singleton
import os

me = singleton.SingleInstance()

defaultSettings = {'lat': '0', 'long': '0', 'timeZone': 0, 'method': 'MWL', 'fajr': '19.0', 'dhuhr': '1',
                   'asr': 'Standard', 'maghrib': '1', 'isha': '17.5', 'showWindow': 0, 'windowLocationX': 82, 'windowLocationY': 18}
appdataFolder = f"{os.getenv('APPDATA')}\prayerTimes"
appdataFile = f"{appdataFolder}\config.json"
try:
    if not os.path.exists(appdataFolder):
        os.mkdir(appdataFolder) 
    if not os.path.exists(appdataFile):
        open(appdataFile, "x")
except:
    file = open(appdataFile, "r")
    

screenWidth, screenHeight = pyautogui.size()

#  constants
prayersList = ["fajr", "dhuhr", "asr", "maghrib", "isha"]
methods = ["MWL", "ISNA", "Egypt", "Makkah", "Karachi", "Tehran", "Jafari"]
asrMethods = ["Standard", "Hanafi"]
timezones = list(range(-12, 12))
menu = ['', ["settings", 'Exit']]
menuMain = ['', ["hide", "settings", 'Exit']]
tooltip = 'prayer times'

# settings

try:
    settings = json.load(file)
except:
    settings = defaultSettings
    with open(appdataFile, 'w') as file:
        json.dump(defaultSettings, file)
    
fontsize = 15
font = ("Arial", fontsize)
appSize = (22*fontsize, 20*fontsize)

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
    layout = [
        [psg.Text("Prayer Times", justification="c", expand_x=True)],
        [psg.Text("fajr: "), psg.Text(fajr, key="fajr",
                                      justification="r", expand_x=True,)],
        [psg.Text("dhuhr: "), psg.Text(dhuhr, key="dhuhr",
                                       justification="r", expand_x=True,)],
        [psg.Text("asr: "), psg.Text(asr, key="asr",
                                     justification="r", expand_x=True,)],
        [psg.Text("maghrib: "), psg.Text(maghrib, key="maghrib",
                                         justification="r", expand_x=True,)],
        [psg.Text("isha: "), psg.Text(isha, key="isha",
                                      justification="r", expand_x=True,)],
        [psg.Text(time, key="Time", justification="c",
                  enable_events=True, expand_x=True)],
        [psg.Text("next prayer is"), psg.Text("", key="nextPrayer",
                                              text_color="red", font=font), psg.Text("", key="timeLeft",)],
    ]

    window = psg.Window("Prayer Times", layout, size=isShown(), keep_on_top=True, grab_anywhere=True, font=font,
                        icon='resources/img/prayertimes.ico', alpha_channel=.7, no_titlebar=True, element_padding=4, right_click_menu=menuMain,
                        location=((settings["windowLocationX"]*screenWidth/100), (settings["windowLocationY"]*screenHeight/100)))
    tray = SystemTray(menu, window=window,
                      tooltip=tooltip, icon='resources/img/prayertimes.ico')

    playsound('resources/audio/Bismillah.wav')

    def calcPrayerTimes():
        now = datetime.now()
        pTimes = getPrayerTimes()
        fajr = formatPrayerDate(pTimes["fajr"])
        dhuhr = formatPrayerDate(pTimes["dhuhr"])
        asr = formatPrayerDate(pTimes["asr"])
        maghrib = formatPrayerDate(pTimes["maghrib"])
        isha = formatPrayerDate(pTimes["isha"])
        nextprayer = prayersList[nextPrayer()]
        window["fajr"].Update(fajr, text_color=(
            "red" if nextprayer == "fajr" else "white"))
        window["dhuhr"].Update(dhuhr, text_color=(
            "red" if nextprayer == "dhuhr" else "white"))
        window["asr"].Update(asr, text_color=(
            "red" if nextprayer == "asr" else "white"))
        window["maghrib"].Update(maghrib, text_color=(
            "red" if nextprayer == "maghrib" else "white"))
        window["isha"].Update(isha, text_color=(
            "red" if nextprayer == "isha" else "white"))
        window["Time"].Update(str((now.strftime("%d-%m-%Y, %I:%M:%S %p"))))
        leftTilNextPrayer = (calcNextPrayer(pTimes[prayersList[nextPrayer()]])).replace(
            "-1", "").replace("day,", "")
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
            if settings["showWindow"] == 1:
                window.size = (0, 0)
                settings["showWindow"] = 0
            else:
                window.size = appSize
                settings["showWindow"] = 1
        if event == "hide":
            window.size = (0, 0)
            settings["showWindow"] = 0
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
    if prayerIndex > 4:
        prayerIndex = 0
    # print(prayerIndex)
    return prayerIndex


def getPrayerTimes():
    now = datetime.now()
    year = int(now.strftime("%Y"))
    month = int(now.strftime("%m"))
    day = int(now.strftime("%d"))
    pT = PrayTimes("Egypt")
    s_dhuhr = settings["dhuhr"]
    pT.adjust({"fajr": settings["fajr"], "dhuhr": f"{s_dhuhr} min",
              "asr": settings["asr"], "maghrib": settings["maghrib"], "isha": settings["isha"]})
    return pT.getTimes([year, month, day], [float(settings["lat"]), float(settings["long"])], settings["timeZone"])


def calcNextPrayer(prayer):
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
    difSec = totalSec2 - totalSec1
    timeLeft = str(timedelta(seconds=difSec))
    return timeLeft


def open_settings():
    settingLayout = [
        [psg.Text("Settings", justification="c", expand_x=True)],
        [psg.Text("lat:", s=(5, 1)), psg.Input(str(settings["lat"]), k="s_lat", s=(9, 1)),
         psg.Text("long:"), psg.Input(
             str(settings["long"]), k="s_long", s=(9, 1)), psg.Text("timezone:"),
         psg.Combo(timezones, k="s_timeZone", s=(9, 1), expand_x=True, default_value=settings["timeZone"])],
        [psg.Text("method:", s=(10, 1)),
         psg.Combo(methods, s=(10, 1), expand_x=True, k="s_method", default_value=settings["method"])],
        [psg.Text("fajr :", s=(10, 1)),
         psg.Input(str(settings["fajr"]), justification="r", expand_x=True, s=(10, 1), k="s_fajr"), psg.Text("degrees", s=(6, 1))],
        [psg.Text("dhuhr:", s=(10, 1)),
         psg.Input(str(settings["dhuhr"]), justification="r", expand_x=True, s=(10, 1), k="s_dhuhr"), psg.Text("minutes", s=(6, 1))],
        [psg.Text("asr:", s=(10, 1)),
         psg.Combo(asrMethods, s=(10, 1), k="s_asr", expand_x=True, default_value=settings["asr"]), psg.Text(s=(6, 1))],
        [psg.Text("maghrib:", s=(10, 1)),
         psg.Input(str(settings["maghrib"]), justification="r", expand_x=True, s=(10, 1), k="s_maghrib"), psg.Text("degrees", s=(6, 1))],
        [psg.Text("isha:", s=(10, 1)),
         psg.Input(str(settings["isha"]), justification="r", expand_x=True, s=(10, 1), k="s_isha"), psg.Text("degrees", s=(6, 1))],
        [psg.Checkbox("show main window:", default=settings["showWindow"],
                      k="s_showWindow", enable_events=True)],
        [psg.Text("window location X"), psg.Input(
            settings["windowLocationX"], k="s_windowLocationX"), psg.Text("%")],
        [psg.Text("window location Y"), psg.Input(
            settings["windowLocationY"], k="s_windowLocationY"), psg.Text("%")],
        [psg.Button("Default", enable_events=True, key="default", expand_x=True),
         psg.Button("Save", enable_events=True, expand_x=True),
         psg.Button("Exit", enable_events=True, expand_x=True)]
    ]
    settingsWindow = psg.Window(
        "Settings", settingLayout, modal=True, icon="resources/img/prayertimesSettings.ico",grab_anywhere=True)
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
            settings["windowLocationX"] = int(values["s_windowLocationX"])
            settings["windowLocationY"] = int(values["s_windowLocationY"])
            if values["s_showWindow"]:
                settings["showWindow"] = 1
            else:
                settings["showWindow"] = 0
            del settings["thread"]
            with open(appdataFile, 'w') as file:
                json.dump(settings, file)
        if event == "default":
            settings["lat"] = 0
            settings["long"] = 0
            settings["timeZone"] = 0
            settings["method"] = "MWL"
            settings["fajr"] = 19.
            settings["dhuhr"] = 1
            settings["asr"] = "Standard"
            settings["maghrib"] = 1
            settings["isha"] = 17.5
            settings["showWindow"] = 0
            settings["windowLocationX"] = 50
            settings["windowLocationY"] = 50
            settingsWindow["s_lat"].Update(0)
            settingsWindow["s_long"].Update(0)
            settingsWindow["s_timeZone"].Update(0)
            settingsWindow["s_method"].Update("MWL")
            settingsWindow["s_fajr"].Update(19.)
            settingsWindow["s_dhuhr"].Update(1,)
            settingsWindow["s_asr"].Update("Standard")
            settingsWindow["s_maghrib"].Update(1)
            settingsWindow["s_isha"].Update(17.5)
            settingsWindow["s_showWindow"].Update(0)
            settingsWindow["s_windowLocationX"].Update(82)
            settingsWindow["s_windowLocationY"].Update(18)
    settingsWindow.close()


def isShown():
    if settings["showWindow"]:
        return appSize
    else:
        return (0, 0)


if __name__ == "__main__":
    main()
