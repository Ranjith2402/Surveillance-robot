import socket
import time

connection_time_out = 15  # change it to 30
socket.setdefaulttimeout(connection_time_out)


class Client:
    def __init__(self, error_function: callable, new_message_interrupt: callable = None, port=99):
        self.IP = None
        self.PORT = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.error_handler = error_function
        self.run = True
        self.is_connected = False
        self.is_connection_failed = False
        self.is_new_data = False
        self.is_server_tested = False
        self.new_data = ''
        self.new_message_interrupt = new_message_interrupt

        self._receiving_message = False

    def connect(self, ip: str = None, interrupt: callable = None):
        if ip is not None:
            self.IP = ip
        if self.IP is None:
            self.error_handler('IP not set')
            return
        is_error = False
        try:
            self.client.connect((self.IP, self.PORT))
            self.is_connected = True
            self.is_connection_failed = False
        except TimeoutError:
            self.error_handler('TimeOutError')
            is_error = True
        except ConnectionRefusedError:
            self.error_handler('ConnectionFailed')
            # print('Refused')
            is_error = True
        except OSError as err:
            self.error_handler('ConnectionFailed')
            # print('OSError')
            is_error = True
            self.disconnect()
            if err:
                pass
        if is_error:
            self.is_connection_failed = True
            if ip is not None:
                self.IP = None
        if interrupt is not None:
            interrupt(self.IP)

    def test_server(self) -> bool:
        if not self.is_connected:
            return False
        if self.send('HANDSHAKE'):
            self.error_handler('Server failed to receive message')
            return False
        recv = False
        _recv_flag = False
        for _ in range(5):
            recv = self.receive(call_error=False)
            if recv == 'UnicodeError':
                self.send('RESEND')
                continue
            break
        else:
            _recv_flag = True
        if _recv_flag:
            self.error_handler("Unicode error, try checking connection")
            return False
        if not recv:
            self.error_handler('Server failed to respond handshake')
            return False
        else:
            if self.new_data == 'HELLO':
                self.is_server_tested = True
                return True
            else:
                self.error_handler('Server failed to respond properly')
                self.disconnect()
                return False

    def send(self, message: str):
        try:
            self.client.send(message.encode('utf-8'))
        except socket.timeout:
            if message == 'HANDSHAKE':
                return True
            else:
                self.error_handler('TimeOutError')
        except ConnectionAbortedError:
            if message == 'HANDSHAKE':
                return True
            else:
                self.error_handler('Connection aborted by system')
        except BrokenPipeError:
            self.disconnect()
            self.connect()
            self.test_server()

    def receive_thread(self):
        if not self.is_server_tested:
            self.test_server()
            return
        self.run = True
        while self.run:
            self.receive(raise_error=False)
            time.sleep(3)

    def receive(self, interrupt: callable = None, call_error=True, raise_error=True):
        is_error = False
        self._receiving_message = True
        try:
            data = self.client.recv(1024)
            self.new_data = data.decode().replace('\r\n', '\n').strip()
            print(self.new_data, '.')
            self.is_new_data = True
            if self.new_message_interrupt is not None:
                self.new_message_interrupt(self.new_data)
        except socket.timeout:
            if call_error and raise_error:
                self.error_handler('TimeOutError')
            is_error = True
            # if self.is_server_tested is False:
            #     self.client.close()
            #     self.client = socket.socket()
            #     self.connect()
        except ConnectionAbortedError:
            if call_error:
                self.error_handler('Connection aborted by system')
            is_error = True
        except ConnectionResetError:
            if call_error:
                self.error_handler('Connection reset')
            is_error = True
        except UnicodeDecodeError:
            self.send('RESEND')
            return 'UnicodeError'
        except OSError:
            if raise_error:
                self.error_handler('OS error')
            else:
                pass
        if interrupt is not None:
            interrupt(not is_error)
        self._receiving_message = False
        return not is_error

    def disconnect(self):
        self.run = False
        self.client.close()
        self.is_connected = False
        # self.IP = None
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def __error(*args):
    print(*args)


if __name__ == '__main__':
    client = Client(__error)
    _ip = input('Enter ip')
    client.connect(_ip)
    client.test_server()
    client.send('Hello world')
