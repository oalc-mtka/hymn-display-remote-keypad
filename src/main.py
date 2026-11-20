import machine
import network
import time
import uasyncio as asyncio

import protocol

# W6100 Default Hardware Pins on EVB Pico2
SPI_NUM = 0
PIN_MISO = 16
PIN_CS = 17
PIN_SCK = 18
PIN_MOSI = 19
PIN_RST = 20

def init_ethernet():
    # Setup SPI and Network
    spi = machine.SPI(
        SPI_NUM,
        baudrate=20000000,
        polarity=0,
        phase=0,
        sck=machine.Pin(PIN_SCK),
        mosi=machine.Pin(PIN_MOSI),
        miso=machine.Pin(PIN_MISO)
    )

    # Initialize LAN (Wiznet W6100) interface driver
    nic = network.WIZNET6K(spi, machine.Pin(PIN_CS), machine.Pin(PIN_RST))  # type: ignore

    # Tell the network driver and your router that this device is named 'hymn'
    try:
        network.hostname("hymn")
        nic.config(hostname="hymn")
    except:
        pass

    nic.active(True)
    nic.ifconfig('dhcp')

    print("Connecting to network...")
    while not nic.isconnected():
        if nic.ifconfig()[0] != '0.0.0.0':
            break
        time.sleep(1)

    print("Connected! IP Address:", nic.ifconfig()[0])
    return nic

# ========================================================
# HYMN DISPLAY WEB APP (ported from main_wifi.py)
# ========================================================

# --- UART Configuration ---
# UART0 for receiving from an external source (e.g., a physical keypad)
# RX=GPIO1 (Pin 2). Inverting RX to match the physical controller's inverted TX.
uart0 = machine.UART(0, baudrate=9600, rx=machine.Pin(1), invert=machine.UART.INV_RX)

# The C code specifies inverted UART logic.
# UART1: TX=GPIO4 (Pin 6), RX=GPIO5 (Pin 7)
# We will only use the TX pin.
uart1 = machine.UART(1, baudrate=9600, tx=machine.Pin(4), rx=machine.Pin(5), invert=machine.UART.INV_TX | machine.UART.INV_RX)

def send_keypad(codes):
    """Sends keypad codes over UART1 one byte at a time, 50 ms apart."""
    for code in codes:
        uart1.write(bytes([code]))
        time.sleep_ms(50) # Synchronous sleep is fine for this specific action

def clear_top():
    print("Sending clearTop() sequence...")
    uart1.write(protocol.CLEAR_TOP)


# --- Global State ---
try:
    with open("index.html", "r") as f:
        HTML_CONTENT = f.read()
except OSError as e:
    print(f"Fatal Error: Cannot open index.html. {e}")
    HTML_CONTENT = "<html><body><h1>Error</h1><p>Could not load index.html</p></body></html>"

SEVEN_MINUTES_MS = 7 * 60 * 1000
timer_active = False
timer_task = None

async def manage_seven_minute_timer():
    """An asyncio task that waits 7 minutes and then clears the display."""
    global timer_active
    await asyncio.sleep_ms(SEVEN_MINUTES_MS)
    print("7-minute timer expired. Clearing top display.")
    clear_top()
    timer_active = False

async def uart_relayer():
    """A non-blocking task to relay data from UART0 to UART1."""
    print("UART relayer started.")
    sreader = asyncio.StreamReader(uart0)
    while True:
        # Wait for any data to arrive on UART0
        data = await sreader.read(1) # Read one byte at a time
        if data:
            print(f"Relaying byte from UART0 to UART1: {data}")
            uart1.write(data)
            # The 50ms delay is not needed here as it was for debouncing web inputs.
            # The physical keypad is already debounced by its own firmware.

async def handle_web_request(reader, writer):
    """Handles a single incoming web request."""
    global timer_active, timer_task

    try:
        request_line = await reader.readline()
        # Read and discard headers
        while await reader.readline() != b"\r\n":
            pass

        request_str = request_line.decode('utf-8')
        addr = writer.get_extra_info('peername')
        print(f"Client connected from {addr}, request: {request_str.strip()}")

        writer.write('HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n')

        if "GET / " in request_str:
            await writer.awrite(HTML_CONTENT)

        elif "GET /on?code=" in request_str:
            try:
                song_number = protocol.parse_song_number(request_str.split('code=')[1].split(' ')[0])
            except ValueError:
                await writer.awrite("Error: Song Number must be 1 to 999.")
            else:
                if timer_active and timer_task:
                    print("New code entered while timer was active. Clearing top display first.")
                    timer_task.cancel()
                    clear_top()

                print(f"Sending '{song_number}' to both displays...")
                send_keypad(protocol.keypad_bytes(song_number))
                uart1.write(protocol.top_frame(song_number))

                print("Starting 7-minute timer.")
                timer_active = True
                timer_task = asyncio.create_task(manage_seven_minute_timer())

                await writer.awrite(f"OK: Sent code {song_number} to display.")

        elif "GET /off" in request_str:
            print("Received OFF command. Stopping timer and clearing display.")
            if timer_active and timer_task:
                timer_task.cancel()
                clear_top()

            timer_active = False
            send_keypad(protocol.KEYPAD_CLEAR)
            await writer.awrite("OK: Sent CLEAR command.")

        else:
            writer.write('HTTP/1.0 404 Not Found\r\n\r\n')
            await writer.awrite("Not Found")

    except Exception as e:
        print(f"Error handling web request: {e}")
    finally:
        await writer.aclose()

async def main():
    """Main asynchronous function to set up and run all tasks."""
    # CRITICAL DELAY: Gives power rails, router ports, and hardware time to stabilize on dead standalone boots
    print("Standalone engine booting... Stabilizing rails...")
    time.sleep(3)

    # Execute network deployment
    nic_interface = init_ethernet()
    if not nic_interface:
        print("Failed to start Ethernet. Halting.")
        return

    print("Starting web server...")
    # Start the UART relayer task
    asyncio.create_task(uart_relayer())
    # Start the web server
    await asyncio.start_server(handle_web_request, '0.0.0.0', 80)

    print("\n🚀 Web Server Active!")
    print("👉 Control Dashboard URL: http://hymn/")

    # Keep the main task running forever
    while True:
        await asyncio.sleep(10)

# ========================================================
# RUN APPLICATION LAUNCH ENGINE
# ========================================================
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Program stopped.")
