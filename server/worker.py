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
    page.wait_for_load_state("networkidle")

    print("Tunggu login (scan QR jika perlu)...")

    # tunggu sampai chat muncul
    time.sleep(15)  # tunggu 15 detik untuk load awal
    print("WhatsApp siap!")

# Tambahkan fungsi ini untuk mengecek apakah WA masih sehat
def check_whatsapp_health():
    global page
    try:
        # 1. Cek apakah ada tombol "Gunakan di Sini" (jika WA terbuka di tempat lain)
        use_here_btn = page.locator('div[role="button"]:has-text("Gunakan di Sini"), div[role="button"]:has-text("Use Here")')
        if use_here_btn.is_visible():
            print("WhatsApp terbuka di perangkat lain. Mengalihkan kembali ke sini...", flush=True)
            use_here_btn.click()
            time.sleep(5)

        # 2. Cek apakah halaman error/crash (tidak ada input chat)
        chat_input = page.locator('div[contenteditable="true"]')
        if not chat_input.first.is_visible():
            print("WhatsApp Web tampak macet/idle. Melakukan Reload...", flush=True)
            page.reload()
            time.sleep(15) # Tunggu loading setelah reload
            return False
        
        return True
    except Exception as e:
        print(f"Health Check Error: {e}", flush=True)
        return False


# BUKA CHANNEL
def open_channel(channel_name):
    global page, current_channel

    # Cek kesehatan sesi sebelum pindah channel
    if not check_whatsapp_health():
        current_channel = None # Reset agar dipaksa buka ulang setelah reload

    if current_channel == channel_name:
        return True

    try:
        # klik icon Channels
        page.locator('button[data-navbar-item-index="2"]').click()
        time.sleep(3)

        target = page.locator(f'span[title="{channel_name}"]').first
        if not target.is_visible():
            # Jika tidak ketemu, coba cari di kolom search atau scroll
            print(f"Saluran {channel_name} tidak terlihat, mencoba refresh...", flush=True)
            page.reload()
            time.sleep(10)
            # Coba lagi setelah reload
            page.locator('button[data-navbar-item-index="2"]').click()
            time.sleep(3)
            target = page.locator(f'span[title="{channel_name}"]').first
            
        target.click()
        time.sleep(3)

        current_channel = channel_name
        print(f"Masuk ke channel: {channel_name}")
        return True

    except Exception as e:
        print("Gagal buka channel:", e)
        return False


# SEND VIDEO
def send_whatsapp_video(video_path, channel_name, caption=""):
    global page

    if page is None:
        print("Error: Browser belum siap. Pastikan init_whatsapp dipanggil di main.")
        return False

    if not open_channel(channel_name):
        return False

    try:
        # Gunakan selector data-tab="10" yang sangat spesifik untuk caption media
        caption_selector = 'div[contenteditable="true"][data-tab]'
        page.wait_for_selector(caption_selector, state="visible", timeout=20000)
        
        # masukan teks sekaligus(Mencegah Bubble Terpisah)
        target_input = page.locator(caption_selector).last
        target_input.click(force=True)
        
        target_input.fill(caption)
        # Beri jeda agar sistem WhatsApp mensinkronkan teks ke file video
        time.sleep(3)

        print("Caption terisi lengkap. Atur file video...")

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

        # klik tombol send
        send_btn_editor = 'span[data-icon="send"], div[aria-label="Kirim"], div[aria-label="Send"]'
        
        # Tunggu tombol benar-benar siap diklik
        page.wait_for_selector(send_btn_editor, state="visible", timeout=15000)
        
        # Klik tombol kirim yang ada di editor (biasanya elemen terakhir yang muncul)
        page.locator(send_btn_editor).last.click(force=True)
        
        print(f"Video terkirim ke {channel_name}")

        # delay anti spam
        time.sleep(60)
        print("Bot Ready untuk deteksi batch berikutnya...")
        return True

    except Exception as e:
        print("Gagal kirim:", e)
        page.keyboard.press("Escape")  # coba tutup layar editor jika error
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
