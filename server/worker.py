from playwright.sync_api import sync_playwright
import time
import os

# GLOBAL
playwright = None
browser = None
context = None
page = None
current_channel = None

# INIT WHATSAPP (LOGIN SEKALI)
def init_whatsapp():
    global playwright, browser, context, page

    playwright = sync_playwright().start()

    context = playwright.chromium.launch_persistent_context(
        user_data_dir="wa_data",  # folder session
        headless=False,
        args=["--no-sandbox", "--disable-dev-shm-usage"]
    )

    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://web.whatsapp.com")

    print("Tunggu login (scan QR jika perlu)...")

    # tunggu sampai chat muncul
    time.sleep(15)  # tunggu 15 detik untuk load awal
    print("WhatsApp siap!")

# BUKA CHANNEL
def open_channel(channel_name):
    global page, current_channel

    if current_channel == channel_name:
        return True

    try:
        # klik icon Channels
        page.locator('button[data-navbar-item-index="2"]').click()
        time.sleep(3)

        # pilih channel
        page.locator(f'span[title="{channel_name}"]').click()
        time.sleep(3)

        current_channel = channel_name
        print(f"Masuk ke channel: {channel_name}")
        return True

    except Exception as e:
        print("Gagal buka channel:", e)
        return False


# SEND VIDEO
def send_whatsapp_video(video_path, channel_name):
    global page

    if page is None:
        init_whatsapp()

    if not open_channel(channel_name):
        return False

    try:
        # klik attach
        attach_button = page.locator(':is(button[aria-label="Lampirkan"], button[aria-label="Attach"])')
        attach_button.click()
        time.sleep(2)

         # Ini akan memicu pembukaan file picker secara internal di browser
        with page.expect_file_chooser() as fc_info:
            page.locator('span:has-text("Foto & Video"), span:has-text("Photos & Videos")').click()
        
        file_chooser = fc_info.value
        file_chooser.set_files(os.path.abspath(video_path))
        
        print("Menunggu preview media...")

        time.sleep(5)

        # klik send
        page.wait_for_selector('div[role="button"][aria-label="Kirim"]', timeout=10000)
        page.locator(':is(div[role="button"][aria-label="Kirim"], div[role="button"][aria-label="Send"])').first.click()

        print(f"Video terkirim ke {channel_name}")

        # delay anti spam
        time.sleep(60)

        return True

    except Exception as e:
        print("Gagal kirim:", e)
        return False

# WORKER LOOP
if __name__ == "__main__":
    init_whatsapp()

    print("Worker siap menerima trigger...")

    while True:
        # Debug: untuk testing manual
        # cmd = input("Ketik perintah: ")
        # if cmd == "kirim":
        #     send_whatsapp_video("test.mp4", "ESPCAM Deteksi RT 07")
        # elif cmd == "keluar":
        #     send_whatsapp_video("pasphoto.PNG", "ESPCAM Deteksi RT 07")
        # elif cmd == "buka":
        #     send_whatsapp_video("001_detected.jpg", "ESPCAM Deteksi RT 07")
            
        time.sleep(10)