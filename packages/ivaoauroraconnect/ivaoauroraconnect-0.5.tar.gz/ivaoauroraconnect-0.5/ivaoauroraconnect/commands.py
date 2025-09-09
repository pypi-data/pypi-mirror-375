import socket
from tkinter.messagebox import showerror

HOST = "127.0.0.1"
PORT = 1130


class Error(Exception):
    pass


def command(cmnd: str, points=None, s=None) -> str:
    if s != None:
        cmnd.replace("#", "")
        command = f"#{cmnd}\n"
        s.sendall(command.encode("ascii"))
        response = s.recv(1024)
        response_str = response.decode("ascii")
        response_str = response_str.strip()
        if response_str.startswith(f"#{cmnd};"):
            response_str = response_str[len(f"#{cmnd};") :]
        parts = response_str.split(";")
        values = parts[0:]
        values_list = [value.strip() for value in values]
        if points == None:
            return values_list
        if values_list[points] != "":
            return values_list[points]
        else:
            return ""
    else:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((HOST, PORT))
                cmnd.replace("#", "")
                command = f"#{cmnd}\n"
                s.sendall(command.encode("ascii"))
                response = s.recv(1024)
                response_str = response.decode("ascii")
                response_str = response_str.strip()
                if response_str.startswith(f"#{cmnd};"):
                    response_str = response_str[len(f"#{cmnd};") :]
                parts = response_str.split(";")
                values = parts[0:]
                values_list = [value.strip() for value in values]
                if points == None:
                    return values_list
                if values_list[points] != "":
                    return values_list[points]
                else:
                    return ""
            except ConnectionRefusedError as e:
                raise Error("Aurora not responding")
            except Exception as e:
                raise Error(e)
