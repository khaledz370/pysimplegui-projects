import os
import shutil
import sys
import subprocess
import PySimpleGUI as psg


def main():
    # global values
    psg.theme('LightBlue3')
    settings = psg.UserSettings()
    settings['mkvDir'] = "C:\Program Files\MKVToolNix"
    mkvMerge = f"{settings['mkvDir']}\\mkvmerge.exe"
    mkvpropedit = f"{settings['mkvDir']}\\mkvpropedit.exe"
    selectedDir = ""
    selectedFilesList = []
    cTop = 0
    cBottom = 0
    cLeft = 0
    cRight = 0
    fileTypes = (('mp4, mkv, flv, ts, avi', '*.mp4 *.mkv *.flv *.ts *.avi'),)
    fileTypesList = ['.mp4', '.mkv', '.flv', '.ts', '.avi']
    # end of global values

    # tomkv tab layout
    tomkvLayout = [
        [psg.Text("convert video to mkv", s=(
            600, 0), justification="center")],

        [psg.Text("Select a folder", key="tomkvSelectText",
                  expand_x=True, justification="center")],
        # browser
        [psg.Listbox([], s=(20, 10), enable_events=True, expand_x=True, expand_y=True, key="tomkvList", select_mode="multiple"),
         psg.Column([
             [psg.Listbox(fileTypesList, enable_events=True,
                          select_mode="multiple", s=(24, 14), key='tomkvFileTypes')],
             [
                psg.Input(visible=False, enable_events=True, key="tomkvMyFiles"),
                psg.Button("Files",target=(psg.ThisRow,-1), file_types=fileTypes, button_type=21,expand_x=True,enable_events=True, key="tomkvFilesBrowser"),
                psg.Input(visible=False, enable_events=True,key="tomkvMyFolders", expand_x=True),
                psg.Button("Folder",target=(psg.ThisRow,-1), button_type=1, expand_x=True,  key="tomkvFolderBrowser", visible=True)],
             [psg.Button("delete", key="tomkvDelBtn", disabled=True,enable_events=True, expand_x=True)]
         ], justification="c")],
        [psg.Button("Convert to mkv", key="convertToMkv", s=(15, 0))],
    ]
    # end of tomkv tab layout

    # toaudio tab layout
    toaudioLayout = [
        [psg.Text("convert video to audio", s=(
            600, 0), justification="center")],
        [psg.Text("Select a folder", key="toaudioSelectText",
                  expand_x=True, justification="center")],
        # browser
        [psg.Listbox([], s=(20, 10), enable_events=True, expand_x=True, expand_y=True, key="toaudioList", select_mode="multiple"),
         psg.Column([
             [psg.Listbox(fileTypesList, enable_events=True,
                          select_mode="multiple", s=(24, 14), key='toaudioFileTypes')],
             [psg.Input(visible=False, enable_events=True, key="toaudioMyFiles", expand_x=True),
              psg.Button("Files",target=(psg.ThisRow,-1), file_types=fileTypes, button_type=21,
                         expand_x=True, key="toaudioFilesBrowser"),
              psg.Input(visible=False, enable_events=True,
                        key="toaudioMyFolders", expand_x=True),
              psg.Button("Folder",target=(psg.ThisRow,-1), button_type=1, expand_x=True,  key="toaudioFolderBrowser", visible=True)],
             [psg.Button("delete", key="toaudioDelBtn", disabled=True,
                         enable_events=True, expand_x=True)]
         ])],
        [psg.Button("Convert to audio", key="convertToaudio", s=(15, 0))],
    ]
    # end of toaudio tab layout

    # corp tab layout
    corpLayout = [
        [psg.Text("corp video", s=(
            600, 0), justification="center")],
        [psg.Text("Select a folder", key="corpSelectText",
                  expand_x=True, justification="center")],
        # browser
        [psg.Listbox([], s=(20, 10), enable_events=True, expand_x=True, expand_y=True, key="corpList", select_mode="multiple"),
         psg.Column([
             [psg.Listbox(fileTypesList, enable_events=True,
                          select_mode="multiple", s=(24, 12), key='corpFileTypes')],
             [psg.Input(visible=False, enable_events=True, key="corpMyFiles", expand_x=True), psg.Button("Files",target=(psg.ThisRow,-1), file_types=fileTypes, button_type=21, expand_x=True, key="corpFilesBrowser"),
                 psg.Input(visible=False, enable_events=True, key="corpMyFolders", expand_x=True), psg.Button("Folder",target=(psg.ThisRow,-1), button_type=1, expand_x=True, key="corpFolderBrowser")],
             [psg.Button("delete", key="corpDelBtn", disabled=True,
                         enable_events=True, expand_x=True)]
         ])],
        [psg.Text("Top"), psg.Input("0", key="corpTop", s=(11, 1), enable_events=True),
         psg.Text("Right"), psg.Input(
             "0", key="corpRight", s=(11, 1), enable_events=True),
         psg.Text("Bottom"), psg.Input(
             "0", key="corpBottom", s=(11, 1), enable_events=True),
         psg.Text("Left  "), psg.Input("0", key="corpLeft", s=(11, 1), enable_events=True)],
        [psg.Button("Corp", key="convertCorp", s=(15, 0))],
    ]
    # end of corp tab layout

    settingsLayout = [
        [psg.Text("settings", justification='c')],
        [psg.Text("mkvtoolnix Location "), psg.Input(str(settings['mkvDir']), visible=True,
                                                     enable_events=True, key="mkvtoolnixFolder"), psg.FolderBrowse(s=(10, 0))]
    ]

    # tab group
    tomkvTab = [psg.Tab('to Mkv', tomkvLayout, key="tomkv", title_color="red"),
                psg.Tab("to Audio", toaudioLayout,
                        key="toaudio", title_color="green"),
                psg.Tab("corp", corpLayout, key="corp", title_color="yellow"),
                psg.Tab("settings", settingsLayout, key="settings", title_color="yellow"),]
    # end of tab group

    # layout
    layout = [
        [psg.TabGroup([tomkvTab], change_submits=True, key="myTabs")],
        [psg.Text("Progress",key="currentFile",s=(20)),psg.ProgressBar(100, orientation='h', expand_x=True,
                         s=(20, 30),  key='PBar')],
    ]
    # end of layout

    window = psg.Window("my first app", layout, resizable=False, size=(
        600, 470), element_justification='c', finalize=True)
    # psg.user_settings_filename(path='.')
    # mkvDir = psg.user_settings_get_entry('mkvDir')
    while True:
        event, values = window.read()
        activeTab = window['myTabs'].Get()
        print("event => ", event)
        # print("active tab => ", activeTab)
        if event in (psg.WIN_CLOSED, "Exit"):
            break

        if event == "mkvtoolnixFolder":
            settings["mkvDir"] = values["mkvtoolnixFolder"]

        # browse for files
        if event == f"{activeTab}MyFiles":
            # print(event)
            window[f"{activeTab}List"].Update(
                values[f"{activeTab}MyFiles"].split(";"))
            selectedFilesList = str(values[f"{activeTab}MyFiles"]).split(";")
            if len(selectedFilesList):
                # print(selectedFilesList)
                selectedDir = fixPath(
                    str(splitPath(selectedFilesList[0])["path"]))
        # end of browse for files

        # browse for folder
        if event == f"{activeTab}MyFolders":
            ftypesArray = values[f"{activeTab}FileTypes"]
            selectedDir = fixPath(str(values[f"{activeTab}MyFolders"]))
            if not len(ftypesArray):
                ftypesArray = fileTypesList
            newArray = []
            for x in os.listdir(selectedDir):
                if x.endswith(tuple(ftypesArray)):
                    newArray.append((f"{selectedDir}\\{x}"))
            selectedFilesList = newArray
            # print(selectedFilesList)
            window[f"{activeTab}List"].Update(selectedFilesList)
        # end of browse for folder

        # on select file types
        if event == f"{activeTab}FileTypes":
            if len(values[f"{activeTab}MyFolders"]):
                ftypesArray = values[f"{activeTab}FileTypes"]
                if not len(ftypesArray):
                    ftypesArray = fileTypesList
                newArray = []
                for x in os.listdir(selectedDir):
                    if x.endswith(tuple(ftypesArray)):
                        newArray.append((f"{selectedDir}\\{x}"))
                selectedFilesList = newArray
                window[f"{activeTab}List"].Update(selectedFilesList)
        # end of on select file types

        # enable and disable delete button
        if event == f"{activeTab}List":
            selectedItemsInList = values[f"{activeTab}List"]
            # print(selectedItemsInList)
            if len(selectedItemsInList):
                window[f"{activeTab}DelBtn"].Update(disabled=False)
            else:
                window[f"{activeTab}DelBtn"].Update(disabled=True)
        # end of enable and disable delete button

        # on delete item
        if event == f"{activeTab}DelBtn":
            # print("this is the selected file list=>",selectedFilesList)
            if len(values[f"{activeTab}MyFolders"]) or len(values[f"{activeTab}MyFiles"]):
                ftypesArray = values[f"{activeTab}FileTypes"]
                selectedFiles = values[f"{activeTab}List"]
                # print("this is the  list=>",selectedFiles)
                print("selected deleted files => ", selectedFiles)
                newArray = selectedFilesList
                for x in selectedFiles:
                    newArray.remove(str(x))
                selectedFilesList = newArray
                window[f"{activeTab}List"].Update(selectedFilesList)
                window[f"{activeTab}DelBtn"].Update(disabled=True)
        # end of on delete item

        # on changing corp values
        if event == "corpTop" or "corpBottom" or "corpLeft" or "corpRight":
            cTop = values["corpTop"]
            cBottom = values["corpBottom"]
            cLeft = values["corpLeft"]
            cRight = values["corpRight"]
        # end on changing corp values

        # convert to mkv
        if event == "convertToMkv":
            arraySize = len(selectedFilesList)
            if arraySize:
                # create mkvmerge_old if not exist
                if not os.path.exists((f"{selectedDir}\\mkvmerge_old")):
                    os.makedirs((f"{selectedDir}\\mkvmerge_old"))
                    # print(mkdirCommand)
                for index, file in enumerate(selectedFilesList):
                    window["currentFile"].Update(str(file))
                    fName = splitPath(file)["file"]
                    fNameNoExt = splitPath(file)["noExt"]
                    mkvmerge_old = (f"{selectedDir}\mkvmerge_old\{fName}")
                    shutil.move(fixPath(file), mkvmerge_old)
                    mkvCommand = f"\"{mkvMerge}\" --output \"{selectedDir}\\{fNameNoExt}.mkv\" \"{selectedDir}\\mkvmerge_old\\{fName}\""
                    # print(mkvCommand)
                    presentage = (100*(index+1)/arraySize)
                    window["PBar"].Update(current_count=presentage)
                    runCommand(mkvCommand)
            selectedFilesList = []
            window["tomkvList"].Update([])
            window["PBar"].Update(current_count=0)
            window["currentFile"].Update("")
        # end of convert to mkv

        # convert to audio
        if event == "convertToaudio":
            arraySize = len(selectedFilesList)
            if arraySize:
                # create mkvmerge_audio if not exist
                if not os.path.exists((f"{selectedDir}\\mkvmerge_audio")):
                    os.makedirs((f"{selectedDir}\\mkvmerge_audio"))
                    # print(mkdirCommand)
                for index, file in enumerate(selectedFilesList):
                    window["currentFile"].Update(str(file))
                    fName = splitPath(file)["file"]
                    fNameNoExt = splitPath(file)["noExt"]
                    mkvCommand = f"\"{mkvMerge}\" --output \"{selectedDir}\\mkvmerge_audio\\{fNameNoExt}.mka\" --no-video --language 1:und  \"{selectedDir}\\{fName}\""
                    # print(mkvCommand)
                    presentage = (100*(index+1)/arraySize)
                    window["PBar"].Update(current_count=presentage)
                    runCommand(mkvCommand)
            selectedFilesList = []
            window["toaudioList"].Update([])
            window["PBar"].Update(current_count=0)
            window["currentFile"].Update("")
        # end of convert to audio

        # corp videos
        if event == "convertCorp":
            arraySize = len(selectedFilesList)
            if arraySize:
                # print("the selected dir =>"+selectedDir)
                for index, file in enumerate(selectedFilesList):
                    window["currentFile"].Update(str(file))
                    fName = splitPath(file)["file"]
                    fNameNoExt = splitPath(file)["noExt"]
                    # convert if file type is not mkv
                    if not str(file).lower().endswith(".mkv"):
                        if not os.path.exists((f"{selectedDir}\\mkvmerge_old")):
                            os.makedirs((f"{selectedDir}\\mkvmerge_old"))
                        mkvmerge_old = (f"{selectedDir}\mkvmerge_old\{fName}")
                        shutil.move(file, mkvmerge_old)
                        mkvCommand = f"\"{mkvMerge}\" --output \"{selectedDir}\\{fNameNoExt}.mkv\" \"{selectedDir}\\mkvmerge_old\\{fName}\""
                        runCommand(mkvCommand)
                    # end of convert if file type is not mkv
                    mkvCorpCommand = f"\"{mkvpropedit}\" \"{selectedDir}\\{fNameNoExt}.mkv\" --edit track:v1 --set pixel-crop-top={cTop} --set pixel-crop-left={cLeft}  --set pixel-crop-right={cRight} --set pixel-crop-bottom={cBottom}"
                    # print(mkvCommand)
                    presentage = (100*(index+1)/arraySize)
                    window["PBar"].Update(current_count=presentage)
                    runCommand(mkvCorpCommand)
            selectedFilesList = []
            window["tomkvList"].Update([])
            window["PBar"].Update(current_count=0)
            window["currentFile"].Update("")
        # end of corp videos
    window.close()


# run cmd commands
def runCommand(cmd, timeout=None, window=None):
    cmd = fixPath(cmd)
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    output = ""
    for line in p.stdout:
        line = line.decode(
            errors="replace" if (sys.version_info) < (
                3, 5) else "backslashreplace"
        ).rstrip()
        output += line
        print(line)
        window.Refresh() if window else None  # yes, a 1-line if, so shoot me
    retval = p.wait(timeout)
    return (retval, output)
# end of run cmd commands

# getting file dir and name


def splitPath(fullPath):
    head, tail = os.path.split(fullPath)
    fileNameSplit = tail.split('.')
    fullname = {"path": head, "file": tail,
                "noExt": fileNameSplit[0], "ext": fileNameSplit[1]}
    return fullname
# end of getting file dir and name

# fix file paht


def fixPath(path):
    return path.replace("/", "\\")
# end of fix file paht

# encode


def toUft8(list):
    return [x.encode('utf-8') for x in list]


if __name__ == "__main__":
    main()
