from machine import UART, Pin

uart = UART(0, 115200, tx=Pin(0), rx=Pin(1))

last_message = ''


def resend_last_message():
    send(last_message)


def send(message: str) -> str or None:
    global last_message
    uart.write(message.encode('utf-8'))
    last_message = message


def read():
    if uart.any():
        data = uart.read()
        try:
            text = data.decode().replace('\r\n', '\n')
        except UnicodeError:
            return None
        return text
    return None
    