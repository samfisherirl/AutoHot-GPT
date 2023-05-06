#Requires Autohotkey v2.0
#SingleInstance Force
#Include chatgpt_ahk_generator\convert\ConvertFuncs.ahk
#Include chatgpt_ahk_generator\convert\_menu_handler_mod.ahk
;AutoGUI 2.5.8
;Auto-GUI-v2 credit to autohotkey.com/boards/viewtopic.php?f=64&t=89901
;AHKv2converter credit to github.com/mmikeww/AHK-v2-script-converter
exe := "`"" A_ScriptDir "\chatgpt_ahk_generator\AutoHotKey Exe\AutoHotkeyV1.exe`" " 
exe2 := "`"" A_ScriptDir "\chatgpt_ahk_generator\AutoHotKey Exe\AutoHotkeyV2.exe`" "     ; specify the path to the AutoHotkey V1 executable
autogui := "`"" A_ScriptDir "\chatgpt_ahk_generator\AutoGUI.ahk`""   ; specify the path to the AutoGUI script
logs := A_ScriptDir "\chatgpt_ahk_generator\log.txt"    ; set the path to the log file
app := A_ScriptDir "\chatgpt_ahk_generator\AutoHot-ChatGPT.exe"    ; set the path to the log file

empty := A_ScriptDir "\chatgpt_ahk_generator\empty.txt"    ; set the path to an empty file
temps := A_ScriptDir "\chatgpt_ahk_generator\temp.txt"    ; set the path to a temporary file
ret := A_ScriptDir "\chatgpt_ahk_generator\return.txt"    ; set the path to the return status file
sets := A_ScriptDir "\chatgpt_ahk_generator\AutoGUI.ini"
runscript := A_ScriptDir "\chatgpt_ahk_generator\runscript.ahk"

if FileExist(logs) {
    FileDelete(logs)
}
if FileExist(temps) {
    FileDelete(temps)
}
if FileExist(ret) {
    FileDelete(ret)
}

Run(app, A_ScriptDir "\chatgpt_ahk_generator", , &PID)     ; run the concatenated command, which launches AutoGUI
Sleep(1000)    ; wait for 1 second
findProcess(PID)

While ProcessExist(PID)    ; while the AutoGUI process exists
    ; wait for %logs% to exist, that means AutoGui is trying to generate code.
    ; this loop will convert to v2 and notify AutoGUI via %retstat%
    ; wait for %logs% to exist, that means AutoGui is trying to generate code.
    ; this loop will convert to v2 and notify AutoGUI via %retstat%
{
    if FileExist(logs)    ; check if the log file exists
    {
        inscript := tryRead(logs)    ; read the contents of the log file into a variable
        if (inscript != "")    ; if the variable is not empty       
            {
                FileMove(logs, "temps.txt", 1)    ; move the log file to the temporary file
                    Converter(inscript)
                    sleep(10)
                } }
    else {
        Sleep(10)
        continue
    }
}
ExitApp


Converter(inscript) {
    global ret
    script := Convert(inscript)    ; convert the script from AHK v1 to AHK v2
    ; final_code := add_menuhandler(script)    ; add menu handlers to the script
    outfile := FileOpen(temps, "w", "utf-8")    ; open the file for writing
    outfile.Write(script)    ; write the final code to the file
    outfile.Close()    ; close the file
    FileCopy(temps, ret, 1)    ; append the return status to the return status file
    FileCopy(temps, A_ScriptDir "\code.ahk", 1)    ; append the return status to the return status file
    A_Clipboard := ""
    A_Clipboard := script
}

setDesignMode(ini) {
    replaceSettings := ""
    x := 0
    Loop Parse, ini, "`n", "`r" {
        if (x == 0) && InStr(A_LoopField, "DesignMode") {
            replaceSettings .= "DesignMode=1`n"
        }
        else {
            replaceSettings .= A_LoopField "`n"
        }
    }
    f := FileOpen(sets, "w", "utf-8")
    f.Write(replaceSettings)
    f.Close()
}

findProcess(PID) {
    Loop 10 {     ; loop up to 10 times
        if ProcessExist(PID) {     ; check if the AutoGUI process exists
            break     ; if it does, break out of the loop
        }
        else {
            Sleep(10)     ; if it doesn't, wait for 1 second and check again
        }
    }
}
;try {out := FileRead(path)}
tryRead(path) {
    try {
        out := FileRead(path)
        return out
    }
    catch {
        Sleep(10)
        return ""
    }
}
