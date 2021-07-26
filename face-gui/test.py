import cv2
from tkinter import *
from PIL import Image, ImageTk
from firebase import Firebase
import os
import schedule
from datetime import datetime

def initialize():
    global config, firebase, db, storage, now, root, width, height, rfid_frame, pin_frame, face_scan_frame, cap, face_cascade, recognizer
    config = {
    }

    firebase = Firebase(config)
    db = firebase.database()
    storage = firebase.storage()
    now = datetime.now()

    root = Tk()
    width = 480
    height = 200
    root.geometry(f"{width}x{height}")
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    rfid_frame = Frame(root)
    pin_frame = Frame(root)
    face_scan_frame = Frame(root)

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    recognizer = cv2.face.LBPHFaceRecognizer_create()

def rfid_frame_setup():
    rfid_frame.grid_rowconfigure(0, weight=1)
    rfid_frame.grid_rowconfigure(1, weight=1)
    rfid_frame.grid_rowconfigure(2, weight=1)
    rfid_frame.grid_rowconfigure(3, weight=1)

    rfid_frame.grid_columnconfigure(0, weight=1)
    rfid_frame.grid_columnconfigure(1, weight=1)
    
    rfid_frame.grid(sticky="EWNS")

def pin_phase_setup():

    pin_frame.grid_rowconfigure(0, weight=1)
    pin_frame.grid_rowconfigure(1, weight=1)
    pin_frame.grid_rowconfigure(2, weight=1)
    pin_frame.grid_rowconfigure(3, weight=1)
    pin_frame.grid_rowconfigure(4, weight=1)

    pin_frame.grid_columnconfigure(0, weight=1)
    pin_frame.grid_columnconfigure(1, weight=1)
    pin_frame.grid_columnconfigure(2, weight=1)

    pin_frame.grid(sticky="EWNS")


def face_scan_setup():
    global camera, face_dict, ids_prediction
    face_scan_frame.grid(sticky="EWNS")
    face_scan_frame.grid_rowconfigure(0, weight=1)
    face_scan_frame.grid_columnconfigure(0, weight=1)
    camera = Label(face_scan_frame)
    camera.grid()

    face_dict = {}
    ids_prediction = None

    recognizer.read('models/model.yml')



def check_rfid(rfid):
    all_user = db.child('Users').get()
    for user in all_user.each():
        if int(rfid) == user.val()['rfid']:
            return True
    return False

def button_verify_rfid():
    global input_rfid
    input_rfid = rfid.get()
    if check_rfid(input_rfid) == True:
        rfid.delete(-1, END)
        rfid_frame.destroy()
        pin_phase()
    else:
        text_result = "Wrong rfid!\nPlease enter again!"
        welcomeLabel.config(text=text_result)
        rfid.delete(-1, END)

def rfid_phase():
    global welcomeLabel, rfid, randomLabel, enter_button, clear_button, \
            count
    count = 0

    rfid_frame_setup()

    welcomeLabel = Label(rfid_frame, text=f"Please Present\nYour Card")
    welcomeLabel.config(font='size, 20')
    welcomeLabel.grid(pady=0, column=0, row=0, columnspan=2)

    rfid = Entry(rfid_frame, show="*")
    rfid.grid(column=0, row=1, columnspan=2)

    enter_button = Button(rfid_frame, text="Enter", command=lambda: button_verify_rfid(), font='size, 14')
    enter_button.grid(column=1, row=2, pady=0)

    clear_button = Button(rfid_frame, text="Clear", command=lambda: rfid.delete(0, END), font='size, 14')
    clear_button.grid(column=0, row=2, pady=0)


    
    schedule.every(30).seconds.do(download_model)
    schedule.run_pending()

def check_pin(pin):
    all_user = db.child('Users').get()
    for user in all_user.each():
        if pin == user.val()['pin']:
            return True
    return False

def click_button(value):
    current_input = str(input_code.get())
    if value == 'Clear':
        input_code.delete(-1, END)
    elif value == 'Enter':
        if check_pin(current_input) == True:
            input_code.delete(-1, END)
            pin_frame.destroy()
            face_scan_setup()
            face_scan_phase()

        else:
            pinlabel.config(text="Wrong pin! Please enter again")
            input_code.delete(0, END)

    else:
        input_code.delete(0, END)
        input_code.insert(-1, current_input + value) 


def create_button():
    global bt_0, bt_1, bt_2, bt_3, bt_4, bt_5, bt_6, bt_7, bt_8, bt_9, bt_clear, bt_enter
    
    bt_0 = add_button(0)
    bt_1 = add_button(1)
    bt_2 = add_button(2)
    bt_3 = add_button(3)
    bt_4 = add_button(4)
    bt_5 = add_button(5)
    bt_6 = add_button(6)
    bt_7 = add_button(7)
    bt_8 = add_button(8)
    bt_9 = add_button(9)
    bt_clear = add_button('Clear')
    bt_enter = add_button('Enter')
    
    row_2 = [bt_7, bt_8, bt_9]
    row_3 = [bt_4, bt_5, bt_6]
    row_4 = [bt_1, bt_2, bt_3]
    row_5 = [bt_clear, bt_0, bt_enter]

    r = 2
    for row in [row_2, row_3, row_4, row_5]:
        c = 0
        for button in row:
            button.grid(row=r, column=c, columnspan=1)
            c += 1
        r += 1

def add_button(value):
    return Button(pin_frame, text=value, width=int(width/3), height=1, font='size, 12', command=lambda: click_button(str(value)))


def pin_phase():
    global input_code, pinlabel
    pin_phase_setup()


    pinlabel=Label(pin_frame, text=f"Enter your pin")
    pinlabel.config(font='size, 20')
    pinlabel.grid(row=0, column=0, columnspan=3, padx=0, pady=0, sticky=N)

    input_code = Entry(pin_frame, width=36, borderwidth=5, show="*")
    input_code.grid(row=1, column=0, columnspan=3, padx=0, pady=0, sticky=N)
    create_button()

def get_username_by_rfid(rfid):
    all_users = db.child('Users').get()
    for user in all_users.each():
        if int(rfid) == user.val()['rfid']:
            name = user.val()['name']
            return name



def face_scan_phase():
    global count, rfid_frame, pin_frame, face_scan_frame, recognizer
    access_date = now.strftime('%d/%m/%Y')
    access_time = now.strftime('%H:%M:%S')

    font = cv2.FONT_HERSHEY_SIMPLEX
    _, frame = cap.read()
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    gray = cv2.cvtColor(cv2image, cv2.COLOR_RGBA2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if count <= 50:
        for (x, y, w, h) in faces:
            count += 1
            cv2.rectangle(cv2image, (x, y), (x + w, y + h),
                        (0, 255, 0), 2)
            roi_gray = gray[y:y+h, x:x+w]
            ids, confidence = recognizer.predict(roi_gray)
            # print(f'ids-1: {ids} - confidence: {confidence}')
            cv2.putText(cv2image, str(ids), (x + 5, y - 5),
                        font, 1, (255, 255, 255), 2)
            cv2.putText(cv2image, str(confidence), (x + 5, y + h - 5),
                        font, 1, (255, 255, 0), 1)
            # print(f"Count = {count}, ids = {ids}, confidence = {confidence}")
        
            if confidence >= 70:
                if ids not in face_dict:
                    face_dict[ids] = 1
                else:
                    face_dict[ids] += 1
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)    
        camera.imgtk = imgtk
        camera.configure(image=imgtk)
        camera.after(10, face_scan_phase)

    else:
        face_scan_frame.destroy()
        ids_count_list = []
        for ids in face_dict:
            ids_count_list.append(face_dict[ids])
        if len(ids_count_list) > 1:
            ids_count_list.sort(reverse=True)
            if ids_count_list[0] == ids_count_list[1]:
                print(f"Equality in ids[0]: {ids_count_list[0]} and ids[1]: {ids_count_list[1]}")
            else:
                for ids in face_dict:
                    if face_dict[ids] == ids_count_list[0]:
                        ids_prediction = ids
                        break
        else:
            for ids in face_dict:
                if face_dict[ids] == ids_count_list[0]:
                    ids_prediction = ids
                    break
        
        if ids_prediction == int(input_rfid):
            name = get_username_by_rfid(input_rfid)
            print('name: ', name)
            print("Success!")
            data = {
                'name': name,
                'rfid': str(ids),
                'access_by_date': access_date,
                'access_by_time': access_time,
            }
            db.child('Access').push(data)
            result("Success! Access Granted")
            print(f'id: {ids_prediction} - input_rfid: {input_rfid}')
        else:
            result("Fail! Access Denied")
            print('Face id != user rfid')
            # print(f'id: {ids_prediction} - input_rfid: {input_rfid}')


def result(result):
    scan_result_label = Label(root, text=result)
    scan_result_label.config(font='size, 20')
    scan_result_label.grid(column=0, row=0)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    scan_result_label.after(5000, scan_result_label.destroy)
    root.after(5000, restart)

def restart():
    global rfid_frame, pin_frame,face_scan_frame

    rfid_frame = Frame(root)
    pin_frame = Frame(root)
    face_scan_frame = Frame(root)
    rfid_phase()


def download_model():
    try:
        time_updated = None
        files = storage.list_files()
        for file in files:
            if file.name == 'model.yml':
                time_updated = str(file.updated)

        time_file = open('models/time.txt', "r")
        local_datetime = time_file.readline()

        if local_datetime != time_updated:
            print('STATUS: Updating the new model')
            os.remove('models/model.yml')
            storage.child('model.yml').download('models/model.yml')
            new_datetime = open('models/time.txt', "w")
            new_datetime.write(time_updated)
            new_datetime.close()
            print('STATUS: Updated the new model')
            root.destroy()

        else:
            print('STATUS: There is no update on the model')

    except Exception as e:
        print(e)

initialize()
rfid_phase()

if __name__ == '__main__':
    while True:
        print('starting')
        root.mainloop()
        initialize()
        rfid_phase()
