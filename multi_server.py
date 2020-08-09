import socket
import select
import msvcrt
import datetime

server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 23))
server_socket.listen(5)

open_client_sockets = []
administrator_sockets = []
muted_users = []
waiting_sockets = []
username_dictionary = {}
messages_to_send = []
command = ""

username_length_length = 1
message_length_length = 3
max_server_message_length = 3

def make_number_length_string(num, length):
    string_num=str(num)
    while(len(string_num)<length):
        string_num = "0" + string_num
    return string_num

def chat_message(client_username_length, client_username, data, client_socket, wlist):
    #client_message_length = data[client_username_length + 2:client_username_length + 5]
    client_message = data[username_length_length + int(client_username_length) + 1 + message_length_length:]
    current_time = datetime.datetime.now().strftime('%H:%M')
    if client_message == "\\quit":
        open_client_sockets.remove(client_socket)
        username_dictionary.pop(client_username)
        if client_socket in administrator_sockets:
            administrator_sockets.remove(client_socket)
        client_socket.close()
        server_message = f"{current_time} {client_username} has left the chat!"
        server_message_length = len(server_message)
        server_message_length_string = make_number_length_string(server_message_length, max_server_message_length)
        for client_reciver in open_client_sockets:
            if (client_reciver in wlist):
                client_reciver.send(f"{server_message_length_string}{server_message}".encode())

    elif client_message == "\\view-managers":
        inverted_username_dictionary={v: k for k, v in username_dictionary.items()}
        server_message = ""
        for i in administrator_sockets:
            server_message += inverted_username_dictionary[i]+', '
        server_message = '['+server_message[:-2]+']'
        server_message_length = len(server_message)
        server_message_length_string = make_number_length_string(server_message_length, max_server_message_length)
        client_socket.send(f"{server_message_length_string}{server_message}".encode())

    else:
        if not client_username in muted_users:
            if username_dictionary[client_username] in administrator_sockets:
                server_message = f"{current_time} @{client_username}: {client_message}"
            else:
                server_message = f"{current_time} {client_username}: {client_message}"
            server_message_length = len(server_message)
            server_message_length_string = make_number_length_string(server_message_length, max_server_message_length)
            for client_reciver in open_client_sockets:
                if ((client_reciver in wlist) and (not (client_reciver is client_socket))):
                    client_reciver.send(f"{server_message_length_string}{server_message}".encode())
        else:
            server_message = f"You cannot speak here."
            server_message_length = len(server_message)
            server_message_length_string = make_number_length_string(server_message_length, max_server_message_length)
            username_dictionary[client_username].send(f"{server_message_length_string}{server_message}".encode())

def administrator_appointment(client_username_length, client_username, data):
    if username_dictionary[client_username] in administrator_sockets:
        appointed_username = data[username_length_length + int(client_username_length) + 1 + username_length_length:]
        appointed_socket = username_dictionary[appointed_username]
        if appointed_username in username_dictionary and not appointed_socket in administrator_sockets:
            administrator_sockets.append(appointed_socket)
    else:
        server_message = f"only administrators can appoint users."
        server_message_length = len(server_message)
        server_message_length_string = make_number_length_string(server_message_length, max_server_message_length)
        username_dictionary[client_username].send(f"{server_message_length_string}{server_message}".encode())

def kick_from_chat(client_username_length, client_username, data, wlist):
    if username_dictionary[client_username] in administrator_sockets:
        kick_username = data[username_length_length + int(client_username_length) + 1 + username_length_length:]
        current_time = datetime.datetime.now().strftime('%H:%M')
        server_message = f"{current_time} {kick_username} has been kicked from the chat!"
        server_message_length = len(server_message)
        server_message_length_string = make_number_length_string(server_message_length, max_server_message_length)
        if kick_username in username_dictionary:
            kick_socket = username_dictionary[kick_username]
            open_client_sockets.remove(kick_socket)
            username_dictionary[kick_username].close()
            username_dictionary.pop(kick_username)
        for client_reciver in open_client_sockets:
            if client_reciver in wlist:
                client_reciver.send(f"{server_message_length_string}{server_message}".encode())
    else:
        server_message = f"only administrators can kick users from the chat."
        server_message_length = len(server_message)
        server_message_length_string = make_number_length_string(server_message_length, max_server_message_length)
        username_dictionary[client_username].send(f"{server_message_length_string}{server_message}".encode())

def mute_user(client_username_length, client_username, data):
    if username_dictionary[client_username] in administrator_sockets:
        muted_users.append(data[username_length_length + int(client_username_length) + 1 + username_length_length:])
    else:
        server_message = f"only administrators can mute users."
        server_message_length = len(server_message)
        server_message_length_string = make_number_length_string(server_message_length, max_server_message_length)
        username_dictionary[client_username].send(f"{server_message_length_string}{server_message}".encode())

def peivate_message(client_username_length, client_username, data):
    before_taarget_username_length = username_length_length + int(client_username_length) + 1
    target_username_length = int(data[before_taarget_username_length:before_taarget_username_length + username_length_length])
    before_taarget_username = before_taarget_username_length + username_length_length
    target_username = data[before_taarget_username:before_taarget_username + target_username_length]
    current_time = datetime.datetime.now().strftime('%H:%M')
    client_message = data[data.find(target_username) + target_username_length + message_length_length:]
    if not client_username in muted_users:
        if username_dictionary[target_username] in open_client_sockets:
            if username_dictionary[client_username] in administrator_sockets:
                server_message = f"{current_time} !@{client_username}: {client_message}"
            else:
                server_message = f"{current_time} !{client_username}: {client_message}"
            server_message_length_string = make_number_length_string(len(server_message), max_server_message_length)
            username_dictionary[target_username].send(f"{server_message_length_string}{server_message}".encode())
    else:
        server_message = f"You cannot speak here."
        server_message_length = len(server_message)
        server_message_length_string = make_number_length_string(server_message_length, max_server_message_length)
        username_dictionary[client_username].send(f"{server_message_length_string}{server_message}".encode())

def send_waiting_messages(wlist):
    for message in messages_to_send:
        (client_socket, data) = message
        data=data.decode()
        client_username_length = int(data[0])
        client_username = data[1:client_username_length + 1]
        client_command = int(data[client_username_length + 1])
        if client_command == 1:
            chat_message(client_username_length, client_username, data, client_socket, wlist)
        elif client_command == 2:
            administrator_appointment(client_username_length, client_username, data)
        elif client_command == 3:
            kick_from_chat(client_username_length, client_username, data, wlist)
        elif client_command == 4:
            mute_user(client_username_length, client_username, data)
        elif client_command == 5:
            peivate_message(client_username_length, client_username, data)
        messages_to_send.remove(message)

while (not (command == "stop")) :
    if msvcrt.kbhit():
        command = input()
    rlist, wlist, xlist = select.select([server_socket]+open_client_sockets+waiting_sockets, open_client_sockets, open_client_sockets)
    for x in xlist:
        if x in rlist:
            rlist.remove(x)
        if x in wlist:
            wlist.remove(x)
        if x in open_client_sockets:
            x.remove(x)
    if administrator_sockets == [] and open_client_sockets != []:
        administrator_sockets.append(open_client_sockets[0])
    for current_socket in rlist:
        if current_socket is server_socket:
            (new_socket, address) = server_socket.accept()
            data = new_socket.recv(1024).decode()
            username_length = int(data[0:username_length_length])
            new_username = data[username_length_length:username_length+1]
            if not new_username in username_dictionary:
                username_dictionary[new_username] = new_socket
                server_message = f"username approved"
                server_message_length_string = make_number_length_string(len(server_message), max_server_message_length)
                new_socket.send(f"{server_message_length_string}{server_message}".encode())
                open_client_sockets.append(new_socket)
                for wsocket in wlist:
                    server_message = f"{new_username} had joined the chat."
                    server_message_length_string = make_number_length_string(len(server_message),
                                                                             max_server_message_length)
                    wsocket.send(f"{server_message_length_string}{server_message}".encode())
            else:
                server_message = f"username not approved"
                server_message_length_string = make_number_length_string(len(server_message), max_server_message_length)
                new_socket.send(f"{server_message_length_string}{server_message}".encode())
                waiting_sockets.append(new_socket)
        elif current_socket in waiting_sockets:
            data = current_socket.recv(1024).decode()
            username_length = int(data[0:username_length_length])
            new_username = data[username_length_length:username_length + 1]
            if not new_username in username_dictionary:
                username_dictionary[new_username] = current_socket
                server_message = f"username approved"
                server_message_length_string = make_number_length_string(len(server_message), max_server_message_length)
                current_socket.send(f"{server_message_length_string}{server_message}".encode())
                open_client_sockets.append(current_socket)
                waiting_sockets.remove(current_socket)
                for wsocket in wlist:
                    server_message = f"{new_username} had joined the chat."
                    server_message_length_string = make_number_length_string(len(server_message),
                                                                             max_server_message_length)
                    wsocket.send(f"{server_message_length_string}{server_message}".encode())
            else:
                server_message = f"username not approved"
                server_message_length_string = make_number_length_string(len(server_message), max_server_message_length)
                new_socket.send(f"{server_message_length_string}{server_message}".encode())

        else:
            try:
                data = current_socket.recv(1024).decode()
            except(Exception, ConnectionResetError):
                data = ""
            if data == "":
                open_client_sockets.remove(current_socket)
                username_dictionary = {v: k for k, v in username_dictionary.items()}
                username_dictionary.pop(current_socket)
                username_dictionary = {v: k for k, v in username_dictionary.items()}
            else:
                messages_to_send.append((current_socket, (data).encode()))

    send_waiting_messages(wlist)