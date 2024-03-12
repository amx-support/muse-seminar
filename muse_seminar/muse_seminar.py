from mojo import context

# デバイス定義 ------------------------------------------------------------------------------------------

# MU-1300
dvMuse = context.devices.get("idevice")
dvCOM = dvMuse.serial[0]
dvIR = dvMuse.ir[0]

# VARIA-100
dvVaria = context.devices.get("AMX-10001")
dvTP = dvVaria.port[1]

# TIMELINE
tl = context.services.get("timeline")


# 変数定義 --------------------------------------------------------------------------------------------

class Vars:
    level = 0

vars = Vars()


# イベント定義 ------------------------------------------------------------------------------------------

def button_event(ev):
    ch = int(ev.id)
    print("[Button] Ch: " + str(ch) + " - " + ("Push" if ev.value else "Release"))

    # TO[BUTTON.INPUT]
    dvTP.channel[ch] = ev.value

    if ch == 1:
        if ev.value:
            dvIR.onIr(1)
        else:
            dvIR.offIr(1)
    elif ch == 2:
        if ev.value:
            dvIR.onIr(2)
        else:
            dvIR.offIr(2)
    
    elif ch == 3 and ev.value:
        dvTP.send_command("^TXT-1,0,Hello World!")
    elif ch == 4 and ev.value:
        dvTP.send_command("^TXT-1,0,")
    
    elif ch == 5 and ev.value:
        dvCOM.send("VOL:" + str(vars.level))
    
    elif ch == 6 and ev.value:
        dvCOM.send("VOL:0")
    elif ch == 7 and ev.value:
        dvCOM.send("VOL:128")
    elif ch == 8 and ev.value:
        dvCOM.send("VOL:255")
    
    elif ch == 9 and ev.value:
        tl.start([1000,2000,3000],False,-1)
    elif ch == 10 and ev.value:
        tl.stop()
        dvTP.channel[11] = False
        dvTP.channel[12] = False
        dvTP.channel[13] = False

def level_event(ev):
    code = int(ev.id)
    lv = int(ev.value)
    vars.level = lv
    print("[LEVEL] Code: " + str(code) + " - " + str(lv))

def data_event(ev):
    data_text = ev.arguments["data"].decode()
    print("[DATA] " + data_text)

    dvTP.send_command("^TXT-2,0," + data_text)

    if "VOL:" in data_text:
        text = data_text.partition("VOL:")
        dvTP.level[1] = int(text[2])

def timeline_event(ev):
    seq = ev.arguments["sequence"]
    repetition = ev.arguments["repetition"]
    print("[TL] Repetition: " + str(repetition) + " Sequence: " + str(seq))

    if seq == 1:
        dvTP.channel[11] = True
        dvTP.channel[12] = False
        dvTP.channel[13] = False
    if seq == 2:
        dvTP.channel[11] = False
        dvTP.channel[12] = True
        dvTP.channel[13] = False
    if seq == 3:
        dvTP.channel[11] = False
        dvTP.channel[12] = False
        dvTP.channel[13] = True


# イベント登録 ------------------------------------------------------------------------------------------

for ch in range(1,11):
    dvTP.button[ch].watch(button_event)
dvTP.level[1].watch(level_event)
dvCOM.receive.listen(data_event)
tl.expired.listen(timeline_event)

context.run(globals())
