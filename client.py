import cv2
from tkinter import *
from PIL import Image, ImageTk
from tkinter import messagebox
import threading,socket
import pickle
import os,struct
import sounddevice as sd
import numpy as np
import tkinter as tk


c_video=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c_text=socket.socket()
c_file=socket.socket()
c_audio=socket.socket()

#gut
def main_interface():
    root = Tk()
    root.geometry('1200x800')
    root.title("Client")
    root.configure(bg='black')  # Set the background color

    frame = Frame(root, background='black')
    frame.grid(row=0, column=0, padx=10)

    # Replace 'no_im.webp' with your image file path
    img = Image.open('no_im.webp')
    img = img.resize((400, 300))
    img = ImageTk.PhotoImage(img)

    # Label for 'YOU'
    label = Label(frame, image=img, text='(YOU)', compound="top", fg="white", bg="black", font=("Arial", 16, "bold"))
    label.config(padx=40, pady=10)
    label.grid(row=0, column=0)

    # Label for 'client2'
    label1= Label(frame, image=img, text='CLIENT2', compound="top", fg="white", bg="black", font=("Arial", 16, "bold"))
    label1.config(padx=10, pady=10)
    label1.grid(row=0, column=1)

    frame1 = Frame(root, bg='black')
    frame1.grid(pady=40, sticky="ew")

    entry = Entry(frame1, width=60, fg='grey', highlightthickness=1, highlightbackground="blue")
    entry.insert(0, 'Enter message you want to send')
    entry.grid(row=0, column=0, padx=50)

    entry1 = Entry(frame1, width=60, fg='grey', highlightthickness=1, highlightbackground="green")
    entry1.insert(0, 'Enter file you want to send')
    entry1.grid(row=0, column=1, padx=10)

    f2 = Frame(root, bg='black')
    f2.grid(sticky='w')

    b= Button(f2, text='Send Message')
    b.grid(row=0, column=0, padx=160)

    b2= Button(f2, text='Send File')
    b2.grid(row=0, column=1, padx=(200, 100))

    f3 = Frame(root, bg='black')
    f3.grid(sticky='w')

    d = Button(f3, text='Disconnect')
    d.grid(row=0, column=0, padx=400, pady=30)

    m= Frame(root, bg='black')
    m.grid(sticky='nw')

    label4 = Label(f3, text='Notifications:', font=("Arial", 16), fg='white', bg='black')
    label4.grid(row=0, column=0, padx=70, pady=20)

    label5 = Label(f3, font=("Arial", 16), fg='white', bg='black')
    label5.grid(row=1, column=0, padx=50)

    label6 = Label(f3, font=("Arial", 16), fg='white', bg='black')
    label6.grid(row=2, column=0, padx=50)

    label7 = Label(f3, font=("Arial", 16), fg='white', bg='black')
    label7.grid(row=3, column=0, padx=50)

    label8 = Label(f3, font=("Arial", 16), fg='white', bg='black')
    label8.grid(row=4, column=0, padx=50)

    cap=cv2.VideoCapture(0)
    def update_image():
        ret, frame = cap.read()
        if ret:
            _, frame_data = cv2.imencode(".jpg", frame)
            # Convert the OpenCV BGR image to a Pillow (PIL) image
            frame = cv2.resize(frame, (400, 300))
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            imgtk = ImageTk.PhotoImage(image=image)
            label.imgtk = imgtk
            label.config(image=imgtk)
        label.after(10, update_image)
    update_image()



    def send_video():
        while True:
            ret,frame=cap.read()
            a= pickle.dumps(frame)
            message = struct.pack("Q",len(a))+a
            if c_video:
                c_video.sendall(message)


    def send_audio():
        fs=44100
        stream = sd.InputStream(channels=1, samplerate=fs, dtype=np.int16)
        with stream:
            while True:
                audio_data, overflowed = stream.read(fs)
                c_audio.sendall(audio_data.tobytes())


    def recv_audio():
        fs = 44100 
        stream = sd.OutputStream(channels=1, samplerate=fs, dtype=np.int16)

        with stream:
            while True:
                audio_data = c_audio.recv(4096) 
                stream.write(np.frombuffer(audio_data, dtype=np.int16))


    def send_msg():
        msg=entry.get()
        c_text.send(msg.encode())
        print(f'message sent : {msg}')

    def send_file():
        fil=entry1.get()
        len=str(os.path.getsize(fil))
        msg=fil+':'+len
        c_file.send(msg.encode())
        file=open(fil,'rb')
        data=file.read()
        c_file.sendall(data)
        file.close()

    def recv_file():
        while True:
            msg=c_file.recv(1024).decode()
            fil,len=msg.split(':')
            file=open(fil,'wb')
            len=int(len)
            data=c_file.recv(len)
            file.write(data)
            file.close()
            label8.config(text='you recieved a file : '+fil)

    def recv_msg():
        c=1
        while True:
            msg=c_text.recv(1024).decode()
            print('message recieved')
            if c==1:
                label5.config(text='Msg Recieved : '+msg)
                c=2
            elif c==2:
                label6.config(text='Msg Recieved : '+msg)
                c=3
            else:
                label7.config(text='Msg Recieved : '+msg)
                c=1
    def recv_vid(client):
        data = b""
        payload_size = struct.calcsize("Q")
        while True:
            while len(data) < payload_size:
                packet = client.recv(4*1024) 
                if not packet: break
                data+=packet
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]    
            
            while len(data) < msg_size:
                data += client.recv(4*1024)
            frame_data = data[:msg_size]
            data = data[msg_size:]
            frame = pickle.loads(frame_data)
            # cv2.imshow("frnd", frame)
            # key = cv2.waitKey(1) & 0xFF
            # if key == ord('q'):     #using the letter q to quit 
            #     break
            _, frame_data = cv2.imencode(".jpg", frame)
            if True:
                # Convert the OpenCV BGR image to a Pillow (PIL) image
                frame = cv2.resize(frame, (400, 300))
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                imgtk = ImageTk.PhotoImage(image=image)
                label1.imgtk = imgtk
                label1.config(image=imgtk)
                print('image updated')

    tvd=threading.Thread(target=send_video,args=())
    tvd.start()
    t_audio=threading.Thread(target=send_audio,args=())
    t_audio.start()
    tv_audio=threading.Thread(target=recv_audio,args=())
    tv_audio.start()
    t_vid=threading.Thread(target=recv_vid,args=(c_video,))
    t_vid.start()
    t_text=threading.Thread(target=recv_msg,args=())
    t_text.start()
    t_file=threading.Thread(target=recv_file,args=())
    t_file.start()
    b.config(command=send_msg)
    b2.config(command=send_file)
    root.mainloop()

users=['user1','user2','user3']
def authentication():
    def check_credentials():
        username = entry_username.get()
        password = entry_password.get()
        # Simulated check - Replace this with your authentication logic
        if username in users and password == "pass":
            login_interface.destroy()
            main_interface()
        else:
            label_feedback.config(text="Wrong password", fg="red")
    
    login_interface = tk.Tk()
    login_interface.title("Login")
    login_interface.geometry('400x300')
    label_welcome = tk.Label( text="Connect to the Server!", font=("Arial", 16))
    label_welcome.pack()
    label_username = tk.Label(login_interface, text="Username:")
    label_username.pack()
    entry_username = tk.Entry(login_interface)
    entry_username.pack()

    label_password = tk.Label(login_interface, text="Password:")
    label_password.pack()
    entry_password = tk.Entry(login_interface, show="*")
    entry_password.pack()

    btn_login = tk.Button(login_interface, text="Login", command=check_credentials)
    btn_login.pack()

    label_feedback = tk.Label(login_interface, text="")
    label_feedback.pack()
    login_interface.mainloop()

if __name__=='__main__':
    ip =socket.gethostbyname(socket.gethostname())
    port_t = 6000
    port_f = 6001
    port_v = 6002
    port_a = 6003

    addr_v=(ip,port_v)
    addr_t=(ip,port_t)
    addr_f=(ip,port_f)
    addr_a=(ip,port_a)

    c_text.connect(addr_t)
    c_file.connect(addr_f)
    c_video.connect(addr_v)
    c_audio.connect(addr_a)

    authentication()
    
