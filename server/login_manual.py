from playwright.sync_api import sync_playwright
import time
import os

def run():
    with sync_playwright() as p:
        # Gunakan user_data_dir agar session tersimpan di Linux
        context = p.chromium.launch_persistent_context(
            user_data_dir="wa_data",
            headless=False # Harus False agar WA Web tidak memblokir
        )
        page = context.new_page()
        page.goto("https://web.whatsapp.com")
        
        print("Menunggu QR Code muncul...")
        time.sleep(20) # Beri waktu loading
        
        # Ambil screenshot QR Code
        page.screenshot(path="qr_scan.png")
        print("QR Code tersimpan di file: qr_scan.png")
        print("Buka file tersebut di laptop kamu dan scan secepatnya!")

        # Tunggu sampai login berhasil (ditandai dengan munculnya search bar)
        try:
            page.wait_for_selector('div[contenteditable="true"]', timeout=60000)
            print("Login Berhasil! Session tersimpan di wa_data.")
        except:
            print("Waktu habis atau login gagal. Coba lagi.")
        
        context.close()

if __name__ == "__main__":
    run()
