import socket
import select
import msvcrt
from tkinter import *

def make_number_length_string(num, length):
    string_num=str(num)
    while(len(string_num)<length):
        string_num = "0" + string_num
    return string_num

username_length_length = 1
message_length_length = 3
max_server_message_length = 3
max_username_length = 9
max_message_length = 120

print("""if you are not muted, send: \'\\quit\' to quit.
if you are not muted, send: \'\\view-managers\' to view a list of the managers
if you are a manager and not muted, send: \'\\appoint {username}\' to make {username} a manager
if you are a manager and not muted, send: \'\\kick {username}\' to kick {username} a manager
if you are a manager and not muted, send: \'\\mute {username}\' to mute {username} a manager
if you are a manager and not muted, send: \'\\appoint {username}\' to make {username} a manager
if you are not muted, send: \'\\whisper to {username}, your {message}\' to send a private message to {username} containing {message}'""")
username = input("please enter your username: ")
while (len(username)<=0 or len(username)>max_username_length) or username[0] == "@":
    username = input(f"please enter a different username again, it can't be more than {max_username_length} characters long, can't start with \'@\', and can't contain the string \', \': ")

client_socket = socket.socket()
client_socket.connect(('127.0.0.1', 23))

username_length = make_number_length_string(len(username), username_length_length)
message_length = make_number_length_string(0, message_length_length)
client_socket.send(f"{username_length}{username}1{message_length} ".encode())
while client_socket.recv(1024).decode()[max_server_message_length:] == "username not approved":
    username = input("username already used, please enter another one: ")
    while (len(username) <= 0 or len(username) > max_username_length) or username[0] == "@":
        username = input(
            f"please enter a different username, it can't be more than {max_username_length} characters long, can't start with \'@\', and can't contain the string \', \': ")
    client_socket.send(f"{username_length}{username}1{message_length} ".encode())

message_length = make_number_length_string(0, message_length_length)
username_length = make_number_length_string(len(username), username_length_length)

message=""
key_pressed=""
data="start"

while data!="":
    rlist, wlist, xlist = select.select([client_socket], [client_socket], [])
    if client_socket in wlist:
        if msvcrt.kbhit():
            try:
                key_pressed = msvcrt.getch().decode()
            except (UnicodeDecodeError, AttributeError):
                pass
            if key_pressed != '\r':
                if len(message) <= max_message_length:
                    print(key_pressed, end="", flush=True)
                    message += key_pressed
                else:
                    print(f"\r\nmesseges can't be more than {max_message_length} characters long.")
                    message = ""
            else:
                username_length = make_number_length_string(len(username), username_length_length)
                message_length = make_number_length_string(len(message), message_length_length)
                if len(message) > 0 and message[0] == "\\" and message[1] != "\\":
                    if message[:len("\\quit")] == "\\quit":
                        client_socket.send(f"{username_length}{username}1{message_length}{message}".encode())

                    elif message[:len("\\view-managers")] == "\\view-managers":
                        client_socket.send(f"{username_length}{username}1{message_length}{message}".encode())

                    elif message[:len("\\appoint ")] == "\\appoint ":
                        appointed_username = message[len("\\appoint "):]
                        appointed_username_length = make_number_length_string(len(appointed_username), username_length_length)
                        client_socket.send(f"{username_length}{username}2{appointed_username_length}{appointed_username}".encode())

                    elif message[:len("\\kick ")] == "\\kick ":
                        kick_username = message[len("\\kick "):]
                        kick_username_length = make_number_length_string(len(kick_username), username_length_length)
                        client_socket.send(f"{username_length}{username}3{kick_username_length}{kick_username}".encode())

                    elif message[:len("\\mute ")] == "\\mute ":
                        mute_username = message[len("\\mute "):]
                        mute_username_length = make_number_length_string(len(mute_username), username_length_length)
                        client_socket.send(f"{username_length}{username}4{mute_username_length}{mute_username}".encode())

                    elif message[:len("\\whisper to ")] == "\\whisper to " and message.find(", ") != -1:
                        target_username = message[len("\\whisper to "):message.find(", ")]
                        target_username_length = make_number_length_string(len(target_username), username_length_length)
                        actual_message = message[message.find(", ")+2:]
                        actual_message_length = make_number_length_string(len(actual_message), message_length_length)
                        client_socket.send(f"{username_length}{username}5{target_username_length}{target_username}{actual_message_length}{actual_message}".encode())

                else:
                    if message[0] == "\\":
                        message = message[1:]
                    client_socket.send(f"{username_length}{username}1{message_length}{message}".encode())
                print("")
                message = ""
    if client_socket in rlist:
        data = client_socket.recv(1024).decode()
        print(data[max_server_message_length:])