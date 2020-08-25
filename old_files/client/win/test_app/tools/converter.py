# convert video to webm and mp4 with 2000K v.bitrate and 144K a.bitrate
# input file placed in folder
# like "5316382", "5316395" etc. script req ffmpeg and ffprobe which should
# be included in path system variable.
import os
import ctypes
import subprocess
from tkinter import *
from tkinter.filedialog import askdirectory
from tkinter.ttk import *
from threading import Thread
from tkinter.messagebox import askokcancel


slash = '\\'
ctypes.windll.kernel32.SetConsoleTitleW('Converting script')

def choose_directory():
    global root_directory
    root_directory = askdirectory()
    root_label.configure(text=root_directory)
    if root_directory:
        convert_button_web.config(state=NORMAL)
        convert_button_plasma.config(state=NORMAL)

def create_message_window():
    global message_text
    frame.delete('intro')
    message_window = Frame(frame, style='WF.TFrame')
    message_scrollbar = Scrollbar(message_window)
    message_text = Text(message_window, state="disabled", highlightthickness=0, bd=0, yscrollcommand=message_scrollbar.set)
    frame.create_window(0, 0, anchor=NW, window=message_window, width=400, height=200)
    message_scrollbar.pack(side=RIGHT, fill=Y)
    message_text.pack(side=LEFT, fill=BOTH)
    message_scrollbar.config(command=message_text.yview)

def put_message(text):
        
    message_text.configure(state='normal')
    text +='\n'
    message_text.insert(END, text)
    message_text.configure(state='disabled')
    message_text.see(END)
    root.update()

def call_converter(opt):
    create_message_window()
    if opt == 'web':
        Thread(target=convert_files_for_web).start()
    elif opt == 'plasma':
        Thread(target=convert_files_for_plasma).start()

def on_closing():
    if askokcancel('Quit', 'Do you want to quit program?'):
        try:
            p.kill()
        except:
            pass
        root.destroy()


def convert_files_for_web():
    global p
    os.chdir(root_directory)
    folders = os.listdir(os.getcwd())
    for i in folders:
        if i.isdigit() and int(i) > 5000000:
            put_message('%s' % i)
            files = os.listdir(os.getcwd() +"\\" + i)
            point = 1
            for n in files:
                if len(n) > 20:
                    npr = n[:20]
                else:
                    npr = n
                if (n[-4:] in ['.mp4', '.mov']) and (n[:7] != i):
                    os.chdir(os.getcwd() +"\\" + i)
                    bitrate = subprocess.check_output(['ffprobe', '-loglevel', 'quiet', '-v', 'error',
                                                    '-select_streams', 'v:0','-show_entries', 'stream=bit_rate',
                                                       '-of', 'default=noprint_wrappers=1', n])
                    bitrate = int(bitrate.decode('utf-8')[9:])
                    if bitrate > 2000000:
                        bitrate = 2000000
                    bitrate = str(bitrate // 1000) + 'K'

                    with subprocess.Popen(['ffmpeg', \
                        '-i', n, '-t' ,'10', '-vf', \
                        'cropdetect', '-f', 'null', '-'], \
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, \
                        universal_newlines=True) as crop_proc:
                        for line in crop_proc.stdout:
                            if 'crop' in line: 
                                line = line.split()[-1].split('=')[-1]
                                if int(line.split(':')[1]) > 0:
                                    crop = line
                    crop = 'crop=' + crop
                    print(crop)
                    put_message('\twebm')
                    # make webm
                
                    out = i +"_" + str(point) + ".webm"
                    # Popen() makes new process instead of .run()
                    p = subprocess.Popen(["ffmpeg", '-y', '-loglevel', 'quiet', '-i', n, '-deadline', 'realtime',
                                            '-cpu-used', '5', '-c:v', 'libvpx', '-b:v', bitrate,
                                            '-b:a', '144K', out])
                    p.wait()
                    put_message('\tmp4')
                    # make mp4
                    out = i + "_" + str(point) + ".mp4"
                    p = subprocess.Popen(["ffmpeg", '-y', '-loglevel', 'quiet', '-i', n, '-threads', '4', '-preset', 'superfast',
                                            '-b:v', bitrate, '-b:a', '144K', out])
                    p.wait()
                
                    put_message('\tsshot')
                    # find half of duration, it appears to be a string of bytes so we decode
                    time = subprocess.check_output(['ffprobe', '-loglevel', 'quiet', '-v', 'error',
                                                    '-show_entries', 'format=duration',
                                                    '-of', 'default=noprint_wrappers=1:nokey=1', n])
                    time = str(float(time.decode('utf-8'))/2)
                    # make screenshot at half of duration and check it for size to avoid black screen
                    vol = 1
                    while True:
                        out = i + "_" + str(point) + ".jpg"
                        p = subprocess.Popen(['ffmpeg', '-ss', time, '-i', n,
                                              '-q:v', '2', '-vframes', '1', '-vf', crop, out])
                        p.wait()
                        if os.path.getsize(out) > 50000:
                                break
                        os.remove(out)
                        count = vol*pow(-1, vol)
                        time = str(float(time) +count*1)
                        vol += 1
                    # delete input
                    os.remove(n)
                    put_message('\tDone')
                    os.chdir("..")
                    point += 1
                else: put_message('"%s" in "%s" looks like output of this converting script.' % (npr, i))
            put_message('.........................')
        else: put_message('"%s" does not look like "5316380" etc.' % i)
    put_message('All files were converted')

def convert_files_for_plasma():
    global p
    os.chdir(root_directory)
    folders = os.listdir(os.getcwd())

    folder_raw = root_directory + slash + 'raw'
    if not os.path.exists(folder_raw):
        input('folder "raw" not found, press enter to exit')
        sys.exit()
    os.chdir(folder_raw)
    files = os.listdir(os.getcwd())
    os.chdir("..")
    if not os.path.exists('converted'):
        os.mkdir(os.getcwd()+ slash + "converted")
    for n in files:
            if n[-4:] in [".mp4", ".mov", ".avi"]:
                    put_message(n)
                    #check bitrate of input and make it 2000K or leave it the same
                    name = "raw" + "\\" + n
                    bitrate = subprocess.check_output(['ffprobe', '-loglevel', 'quiet', '-v', 'error',
                                                    '-select_streams', 'v:0','-show_entries', 'stream=bit_rate',
                                                       '-of', 'default=noprint_wrappers=1', name])
                    bitrate = int(bitrate.decode('utf-8')[9:])
                    if bitrate > 2050000:
                            bitrate = 2050000
                    bitrate = str(bitrate // 1000) + 'K'

                    out = "converted" + "\\" + n[:-3] + "mp4"
                    
                    framesize = "scale=1280:720:force_original_aspect_ratio=1,pad=1280:720:(ow-iw)/2:(oh-ih)/2"
                    p = subprocess.Popen(["ffmpeg", '-y', '-loglevel', 'quiet','-i', name, "-vf", framesize, '-threads', '4', '-preset', 'superfast',
                            '-b:v', bitrate, '-b:a', '144K', out])
                    p.wait()
                    put_message("\tDone")
    put_message('All files were converted')

root_directory = ''
root = Tk()
root.title('Converting script')
root.resizable(False, False)

Style().configure("WF.TFrame", background='white', relief=GROOVE)

frame = Canvas(root, highlightthickness=0, width=400, height=200)
frame.pack(fill=BOTH)
choose_button = Button(frame, text='Choose directory', command=choose_directory)
frame.create_window(200, 20, window=choose_button, tag='intro')
root_label = Label(frame, text=root_directory)
frame.create_window(200, 60, window=root_label, tag='intro')
convert_button_web = Button(frame, text='Convert videos for web', command=lambda: call_converter('web'), state=DISABLED)
frame.create_window(200, 120, window=convert_button_web, tag='intro')
convert_button_plasma = Button(frame, text='Convert videos for plasma', command=lambda: call_converter('plasma'), state=DISABLED)
frame.create_window(200, 160, window=convert_button_plasma, tag='intro')

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()