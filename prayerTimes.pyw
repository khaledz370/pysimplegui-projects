import PySimpleGUI as psg
from threading import Timer
from praytimes import PrayTimes
from datetime import datetime,timedelta

coords = [29.7667,31.3]
prayersList = ["fajr", "dhuhr", "asr", "maghrib", "isha"]

def main():
    now = datetime.now()
    pTimes = getPrayerTimes()
    print(pTimes)
    fajr = formatPrayerDate(pTimes["fajr"])
    dhuhr = formatPrayerDate(pTimes["dhuhr"])
    asr = formatPrayerDate(pTimes["asr"])
    maghrib = formatPrayerDate(pTimes["maghrib"])
    isha = formatPrayerDate(pTimes["isha"])
    time = str((now.strftime("%d-%m-%Y, %I:%M:%S %p")))

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
        [psg.Text("",key="timeLeft",expand_x=True,justification="c"),psg.Text("",key="nextPrayer",expand_x=True,justification="c")],

    ]

    window = psg.Window("Prayer Times", layout, size=(200, 220))

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
        leftTilNextPrayer = calcNextPrayer(pTimes[prayersList[nextPrayer()]])
        window["timeLeft"].Update(leftTilNextPrayer)
        window["nextPrayer"].Update(f" til {nextprayer}")
        Timer(1.0, calcPrayerTimes).start()
    Timer(1.0, calcPrayerTimes).start()

    while True:
        event, values = window.read()
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
    pT.adjust({"fajr": 19.5, "dhuhr": '0 min', "asr": 'Standard',"maghrib":1, "isha": 17.5})
    return pT.getTimes([year, month, day], coords, 2)

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
    difSec = totalSec2- totalSec1
    timeLeft = str(timedelta(seconds=difSec))
    return timeLeft  


if __name__ == "__main__":
    main()
