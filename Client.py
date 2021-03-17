from tkinter import *
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import simpledialog
from functools import partial
from threading import Thread
from win32api import GetSystemMetrics
from plyer import notification
from tkinter import font
import socket
import webbrowser

def ask_ip_port():
    '''
    The programme asks user to enter the room code and room password which are nothing but ip and port of host
    '''
    host1 = simpledialog.askstring("Room code","Enter the the chat room code") #Actually the host ip
    port1 = simpledialog.askinteger("Password","Enter the room password")#The port
    return host1,port1

class Connection:
    '''
    Constructor
    '''
    def __init__(self):
        
        win = Tk() #For the simpledialog box
        win.withdraw() #Withdrawing the window so the blank window isn't visible to the user

        self.connection_made = False
        host,port =ask_ip_port()
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            self.s.connect((host,port))
            self.connection_made = True
        except:
            messagebox.showerror("Error!","The room code or the password is wrong! Try again.")
            host,port = ask_ip_port()
            '''
            Giving user 2 chances to enter correct ip and port else the programme will close.
            '''
            try:
                self.s.connect((host,port))
                self.connection_made = True
            except:
                messagebox.showerror("Error!","The room code or the password is wrong! Try again.")

        if self.connection_made:
            self.usrnm = simpledialog.askstring("Username","Enter your username : ",parent = win)#Username
            while len(self.usrnm) < 4: #Username should have atleast 4 characters
                messagebox.showerror("Error","Username can't have less than 4 characters")
                self.usrnm = simpledialog.askstring("Username","Enter your username : ",parent = win)
                
            win.destroy()
            self.over = False
            self.shift_press = False
            self.setup= False
            self.letter_index = []
            self.metrics = [GetSystemMetrics(0),GetSystemMetrics(1)]#Getting the monitor resolution
            self.front_thread = Thread(target=self.Frontend) #GUI
            self.recv_thread = Thread(target=self.recv) #Receiving messages from the server

            self.front_thread.start()
            self.recv_thread.start()
        else:
            quit() #Close the programme if the provided ip and port isn't valid
            
    def Frontend(self):#User-interface
        self.root = Tk()
        self.icon = "data/images/chat.ico"
        self.root.geometry("800x600"+f"+{int(self.metrics[0]/2) -400}+{int(self.metrics[1]/2)-300}")#800x600 and positioning the window at center
        self.root.title("PyChat")
        self.root.iconbitmap(self.icon)
        self.root.configure(bg = "gray40")
        '''
        Disabaling the maximize button
        '''
        self.root.resizable(0,0)
        self.btnimg = PhotoImage(file = "data/images/send1.png",master=self.root)
        self.prof = PhotoImage(file = "data/images/prof1.png",master=self.root)
        self.mail = PhotoImage(file = "data/images/mail.png",master=self.root)
        tab = Canvas(self.root,width = 800,height = 60,bg = "cyan")
        tab.place(x=0,y=0)
        prflabel = Label(self.root,image = self.prof)
        prflabel.place(x=4,y=8)
        Label(self.root,text = "Chat Room",font = ("Arial",17),bg = "gray78").place(x=350,y=16)
        cht_font = font.Font(family = "Trebuchet MS",size =17)
        
        self.cht_place = scrolledtext.ScrolledText(self.root,width=97,height = 16) #Chat history here
        self.cht_place.place(x=2,y=67)
        self.cht_place.configure(font = cht_font)
        self.cht_place.config(state = "disabled")
        self.entry_area = Text(self.root,width = 89,height = 4)
        self.entry_area.place(x=5,y=525)
        self.entry_area.focus_force()
        
        sendbtn = Button(self.root,width = 65,height =60,bg="white",image = self.btnimg,command=self.sendmsg)
        sendbtn.place(x=726,y=526)
        feedbackbtn = Button(self.root,width = 40,height = 40,image =self.mail,command = self.feedback)
        feedbackbtn.place(x=740,y=10)
        self.setup = True
        self.root.protocol("WM_DELETE_WINDOW",self.handle_quit) #Handling the exit event
        
        #Binding the keys to some methods
        
        self.root.bind("<Shift_L>",self.checkkeyprs)
        self.root.bind("<KeyRelease>",self.onrel)
        self.root.bind("<Return>",self.sendmsg)
        self.root.mainloop()
    def feedback(self):
        webbrowser.open("https://mail.google.com/mail/u/0/?fs=1&to=shouryasinha001@gmail.com&su=Feedback%20regarding%20PyChat&&tf=cm")
    def recv(self):
        while not self.over:
            try:
                message1 = self.s.recv(1024)
                message1 = message1.decode()
                if message1 == "usr":
                    self.s.send(self.usrnm.encode())
                else:
                    if self.setup:
                        self.cht_place.config(state = 'normal')
                        self.cht_place.insert('end',message1)
                        self.cht_place.yview('end')
                        self.cht_place.config(state = 'disabled')
                        '''
                        If the chat window isn't in focus then a notification pops up with a sound
                        indicating that there's a new message
                        '''
                        if str(self.root.focus_get()) == "None":
                            notification.notify(
                                title = "New message!",
                                message = message1,
                                app_icon = self.icon,
                                timeout = 8
                            )
            except ConnectionAbortedError:
                break
            except:
                self.s.close()
                break

    def handle_quit(self):
        if messagebox.askyesnocancel("Quit","Do you want to quit?"):
            self.over = True
            self.s.close()
            exit(0) #Exit code 0

    def sendmsg(self,*argv): 
        '''
        When the user will press Enter event will be passed as an argument and whenever the user clicks the send button
        then no args will be passed so *argv will be empty.
        '''
        if not self.shift_press:
            entrytxt = self.entry_area.get('1.0','end')
            msg = f"{self.usrnm} : {entrytxt}"
            lenx = len(msg)
            if msg[lenx-1] == "\n" : msg = msg.replace(msg[lenx-1],"")
            if len(msg) < 546: #Limiting the maximum character in a single message to 546 letters
                contents = self.entry_area.get('1.0','end').replace('\n',"")
                contents2 = str(contents).replace(' ',"")
                if len(contents) > 0 and len(contents2) > 0: #Sending the message to server if the length of message(excluding the line break and spaces) is greater than 0
                    try:
                        self.s.send(msg.encode())
                        self.s.send('\n'.encode())
                    except:
                        messagebox.showerror("Error!","You're not connected to the internet!")
                    self.entry_area.delete('1.0','end')
                else:
                    self.entry_area.delete('end','end')
            else:
                messagebox.showerror("Too many characters!","You can't send a message consisting of more than 546 letters! Your message currently has {} characters in it".format(len(msg)))
        
    def checkkeyprs(self,event):self.shift_press = True
      
    def onrel(self,event):
        #Checking if shift is released by the user
        if str(event).startswith("<KeyRelease event state=Shift"):self.shift_press = False
        
con = Connection() #Object
