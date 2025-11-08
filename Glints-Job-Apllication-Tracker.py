import time
import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains

class GlintsApplicationScraper:
    def __init__(self):
        chrome_options = Options()
        # chrome_options.add_argument('--headless')  
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--start-maximized')  # Maximize window
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 15)
        self.applications = []
        self.processed_items = set()  # Track untuk avoid duplicate
    
    def login(self, email, password):
        """Login ke Glints"""
        print("🔐 Membuka halaman login...")
        self.driver.get("https://glints.com/id/login")
        
        try:
            email_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            email_input.send_keys(email)
            
            password_input = self.driver.find_element(By.NAME, "password")
            password_input.send_keys(password)
            
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            print("✅ Login berhasil, menunggu redirect...")
            time.sleep(6)
            
        except Exception as e:
            print(f"❌ Error saat login: {e}")
            return False
        
        return True
    
    def get_current_page_number(self):
        """Ambil nomor halaman saat ini dari URL atau pagination"""
        try:
            # Cari tombol pagination yang aktif
            active_page = self.driver.find_elements(By.XPATH, 
                "//button[contains(@class, 'active') or contains(@class, 'selected')]")
            if active_page:
                return active_page[0].text
            
            # Atau dari URL
            current_url = self.driver.current_url
            if "page=" in current_url:
                page = current_url.split("page=")[1].split("&")[0]
                return page
            
            return "Unknown"
        except:
            return "Unknown"
    
    def scrape_current_page(self, page_number):
        """Scrape data dari halaman saat ini dengan multiple strategies"""
        print(f"\n{'='*60}")
        print(f"📄 HALAMAN {page_number}")
        print(f"{'='*60}")
        
        # Tunggu halaman load dengan lebih lama
        time.sleep(4)
        
        # Scroll perlahan untuk trigger lazy loading
        print("   📜 Scrolling untuk load data...")
        for i in range(3):
            self.driver.execute_script(f"window.scrollTo(0, {(i+1) * 500});")
            time.sleep(0.5)
        
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        try:
            # STRATEGI UTAMA: Cari berdasarkan tanggal submit
            date_keywords = ["Dikirim pada", "Submitted on", "dikirim pada", "submitted on"]
            submitted_elements = []
            
            for keyword in date_keywords:
                elements = self.driver.find_elements(By.XPATH, 
                    f"//*[contains(text(), '{keyword}')]")
                if elements:
                    submitted_elements.extend(elements)
            
            # Remove duplicates
            submitted_elements = list(set(submitted_elements))
            
            print(f"   🔍 Ditemukan {len(submitted_elements)} aplikasi")
            
            if not submitted_elements:
                print("   ⚠️  Tidak ada elemen tanggal ditemukan!")
                # Debug: print page source
                print("   📋 Mencoba strategi alternatif...")
                
            page_items_count = 0
            
            for idx, elem in enumerate(submitted_elements):
                try:
                    # Cari parent container dengan berbagai level
                    parent = None
                    card_text = ""
                    
                    for level in [2, 3, 4, 5, 6]:
                        try:
                            test_parent = elem.find_element(By.XPATH, f"./ancestor::div[{level}]")
                            test_text = test_parent.text
                            
                            # Validasi: parent harus berisi info lengkap
                            if (len(test_text) > 50 and 
                                any(kw in test_text for kw in date_keywords) and
                                len(test_text.split('\n')) >= 3):
                                parent = test_parent
                                card_text = test_text
                                break
                        except:
                            continue
                    
                    if not parent or not card_text:
                        continue
                    
                    lines = [line.strip() for line in card_text.split('\n') if line.strip()]
                    
                    # Parse data
                    position = "Unknown"
                    company = "Unknown"
                    submitted_date = "Unknown"
                    status = "Unknown"
                    
                    # Filter out navigation items
                    filtered_lines = [line for line in lines if line not in 
                                    ["LOWONGAN KERJA", "PERUSAHAAN", "BLOG", "UNDUH APP GLINTS"]]
                    
                    for i, line in enumerate(filtered_lines):
                        # Posisi (biasanya baris pertama)
                        if (position == "Unknown" and 
                            not any(kw in line for kw in ["PT", "Dikirim", "Submitted", "Dilamar", "Rejected", "Ditolak"]) and
                            len(line) > 5 and len(line) < 150):
                            position = line
                        
                         # Company
                        elif any(kw in line for kw in ["PT", "Pt.", "Inc", "Ltd", "Corporation", "Company", "CV", "PT.", "Group", "INC", "LTD", "CORPORATION", "Corp", "Toko", "Company", "Outlet", "Consulting",  "Indonesia", "Semarang", "COMPANY", "Cv", "Pt.", "GROUP"]):
                            company = line
                        
                        # Tanggal
                        elif any(kw in line for kw in date_keywords):
                            submitted_date = line
                            for kw in date_keywords:
                                submitted_date = submitted_date.replace(kw, "").strip()
                        
                        # Status
                        elif line in ["Rejected", "Applied", "Under Review", "Interviewing", 
                                    "Offer Received", "Hired", "Dilamar", "Ditolak", 
                                    "Dalam Peninjauan", "Wawancara", "Diterima", "Tidak Lagi Menerima Lamaran"]:
                            status = line
                    
                    # Buat unique identifier untuk avoid duplicate
                    unique_id = f"{position}|{company}|{submitted_date}"
                    
                    # Simpan jika valid dan belum ada
                    if (position != "Unknown" or company != "Unknown") and unique_id not in self.processed_items:
                        application_data = {
                            'position': position,
                            'company': company,
                            'submitted_date': submitted_date,
                            'status': status
                        }
                        
                        self.applications.append(application_data)
                        self.processed_items.add(unique_id)
                        page_items_count += 1
                        
                        print(f"   ✅ {len(self.applications)}. {position[:50]} | {company[:30]}")
                    
                except Exception as e:
                    continue
            
            print(f"\n   📊 Total baru di halaman ini: {page_items_count}")
            print(f"   📊 Total keseluruhan: {len(self.applications)}")
            
            return page_items_count
            
        except Exception as e:
            print(f"   ❌ Error scraping: {e}")
            import traceback
            traceback.print_exc()
            return 0
    
    def click_next_page_advanced(self):
        """Klik next page dengan multiple strategies dan retry"""
        print(f"\n{'─'*60}")
        print("🔄 Mencoba pindah ke halaman berikutnya...")
        
        try:
            # Scroll ke bawah untuk tampilkan pagination
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # STRATEGI 1: Klik tombol dengan text "PERGI"
            try:
                print("   🎯 Strategi 1: Mencari tombol 'PERGI'...")
                pergi_buttons = self.driver.find_elements(By.XPATH, 
                    "//button[contains(text(), 'PERGI') or contains(text(), 'Pergi')]")
                
                for btn in pergi_buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        # Scroll ke tombol
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                        time.sleep(1)
                        
                        # Coba klik dengan JavaScript
                        try:
                            self.driver.execute_script("arguments[0].click();", btn)
                            print("   ✅ Berhasil klik tombol PERGI dengan JavaScript")
                            time.sleep(5)  # Tunggu load halaman baru
                            return True
                        except:
                            # Coba regular click
                            try:
                                btn.click()
                                print("   ✅ Berhasil klik tombol PERGI")
                                time.sleep(5)
                                return True
                            except:
                                pass
            except Exception as e:
                print(f"   ⚠️  Strategi 1 gagal: {e}")
            
            # STRATEGI 2: Klik nomor halaman berikutnya
            try:
                print("   🎯 Strategi 2: Mencari nomor halaman berikutnya...")
                
                # Ambil halaman aktif saat ini
                active_pages = self.driver.find_elements(By.XPATH, 
                    "//button[contains(@class, 'bg-blue') or @aria-current='page']")
                
                if active_pages:
                    current_page_text = active_pages[0].text
                    if current_page_text.isdigit():
                        next_page = int(current_page_text) + 1
                        
                        # Cari button dengan nomor next page
                        next_button = self.driver.find_elements(By.XPATH, 
                            f"//button[text()='{next_page}']")
                        
                        if next_button:
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button[0])
                            time.sleep(1)
                            self.driver.execute_script("arguments[0].click();", next_button[0])
                            print(f"   ✅ Berhasil klik halaman {next_page}")
                            time.sleep(5)
                            return True
            except Exception as e:
                print(f"   ⚠️  Strategi 2 gagal: {e}")
            
            # STRATEGI 3: Klik icon arrow/chevron
            try:
                print("   🎯 Strategi 3: Mencari tombol arrow...")
                arrow_selectors = [
                    "//button[@aria-label='next page']",
                    "//button[@aria-label='Next']",
                    "//*[contains(@class, 'pagination')]//button[last()]",
                    "//button[contains(@class, 'next')]",
                    "//*[name()='svg' and contains(@class, 'chevron')]/..",
                ]
                
                for selector in arrow_selectors:
                    try:
                        buttons = self.driver.find_elements(By.XPATH, selector)
                        for btn in buttons:
                            if btn.is_displayed() and btn.is_enabled():
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                                time.sleep(1)
                                self.driver.execute_script("arguments[0].click();", btn)
                                print("   ✅ Berhasil klik tombol arrow")
                                time.sleep(5)
                                return True
                    except:
                        continue
            except Exception as e:
                print(f"   ⚠️  Strategi 3 gagal: {e}")
            
            # STRATEGI 4: Input nomor halaman manual ke textbox
            try:
                print("   🎯 Strategi 4: Input halaman manual...")
                page_input = self.driver.find_elements(By.XPATH, 
                    "//input[@type='text' or @type='number']")
                
                for inp in page_input:
                    if inp.is_displayed():
                        current_val = inp.get_attribute('value')
                        if current_val and current_val.isdigit():
                            next_page_num = str(int(current_val) + 1)
                            inp.clear()
                            inp.send_keys(next_page_num)
                            
                            # Cari dan klik tombol PERGI
                            pergi = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'PERGI')]")
                            if pergi:
                                self.driver.execute_script("arguments[0].click();", pergi[0])
                                print(f"   ✅ Input manual ke halaman {next_page_num}")
                                time.sleep(5)
                                return True
            except Exception as e:
                print(f"   ⚠️  Strategi 4 gagal: {e}")
            
            print("   ❌ Semua strategi gagal - kemungkinan sudah halaman terakhir")
            return False
            
        except Exception as e:
            print(f"   ❌ Error fatal: {e}")
            return False
    
    def scrape_all_pages(self):
        """Scrape SEMUA halaman dengan robust error handling"""
        print("\n" + "="*60)
        print("🚀 MEMULAI WEB SCRAPING - SEMUA HALAMAN")
        print("="*60)
        
        print("\n📂 Membuka halaman aplikasi...")
        self.driver.get("https://glints.com/id/user/applications?status=All&sortBy=Most+Recent")
        time.sleep(6)
        
        page_number = 1
        max_pages = 500  # Increased limit
        consecutive_empty = 0  # Track halaman kosong berturut-turut
        max_consecutive_empty = 3  # Stop jika 3 halaman kosong berturut-turut
        
        while page_number <= max_pages:
            # Scrape halaman saat ini
            items_found = self.scrape_current_page(page_number)
            
            # Track empty pages
            if items_found == 0:
                consecutive_empty += 1
                print(f"   ⚠️  Halaman kosong ({consecutive_empty}/{max_consecutive_empty})")
                
                if consecutive_empty >= max_consecutive_empty:
                    print(f"\n🛑 Berhenti: {max_consecutive_empty} halaman kosong berturut-turut")
                    break
            else:
                consecutive_empty = 0  # Reset counter
            
            # Auto-save setiap 10 halaman
            if page_number % 10 == 0:
                print(f"\n💾 Auto-save backup...")
                self.save_to_csv(f'glints_backup_page_{page_number}.csv')
            
            # Coba ke halaman berikutnya
            if not self.click_next_page_advanced():
                print("\n🏁 Tidak bisa ke halaman berikutnya - SELESAI!")
                break
            
            page_number += 1
            
            # Progress setiap 5 halaman
            if page_number % 5 == 0:
                print(f"\n{'='*60}")
                print(f"📈 PROGRESS UPDATE")
                print(f"   Halaman diproses: {page_number}")
                print(f"   Total aplikasi: {len(self.applications)}")
                print(f"   Rata-rata per halaman: {len(self.applications)/page_number:.1f}")
                print(f"{'='*60}")
        
        print("\n" + "="*60)
        print("✅ SCRAPING SELESAI!")
        print(f"   📄 Total Halaman: {page_number}")
        print(f"   📊 Total Aplikasi: {len(self.applications)}")
        print("="*60)
    
    def save_to_csv(self, filename='glints_applications_full.csv'):
        """Save data ke CSV"""
        if not self.applications:
            print("\n❌ Tidak ada data untuk disimpan")
            return
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if not script_dir:  # Jika run dari command line langsung
            script_dir = os.getcwd()
        
        filepath = os.path.join(script_dir, filename)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ['no', 'position', 'company', 'submitted_date', 'status']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                
                for idx, app in enumerate(self.applications, 1):
                    writer.writerow({
                        'no': idx,
                        'position': app['position'],
                        'company': app['company'],
                        'submitted_date': app['submitted_date'],
                        'status': app['status']
                    })
            
            print(f"\n✅ DATA TERSIMPAN!")
            print(f"   📁 {filepath}")
            print(f"   📊 {len(self.applications)} aplikasi")
            
        except Exception as e:
            print(f"\n❌ Error save: {e}")
    
    def close(self):
        """Tutup browser"""
        print("\n🔒 Menutup browser...")
        self.driver.quit()


def main():
    print("="*60)
    print("     GLINTS SCRAPER - FULL VERSION v2.0")
    print("="*60)
    
    scraper = GlintsApplicationScraper()
    
    try:
        # LOGIN - GANTI INI!
        EMAIL = "email_anda@example.com"  # ⚠️⚠️⚠️ GANTI dengan email Glints Anda!
        PASSWORD = "password_anda"         # ⚠️⚠️⚠️ GANTI dengan password Glints Anda!
        
        if scraper.login(EMAIL, PASSWORD):
            scraper.scrape_all_pages()
            scraper.save_to_csv('my_glints_applications_complete.csv')
            
            print("\n" + "="*60)
            print("📊 FINAL SUMMARY")
            print(f"   Total: {len(scraper.applications)} aplikasi")
            if scraper.applications:
                print(f"   Pertama: {scraper.applications[0]['position']}")
                print(f"   Terakhir: {scraper.applications[-1]['position']}")
            print("="*60)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  DIHENTIKAN USER")
        print(f"   Data terkumpul: {len(scraper.applications)}")
        if scraper.applications:
            scraper.save_to_csv('glints_interrupted.csv')
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        if scraper.applications:
            scraper.save_to_csv('glints_error_recovery.csv')
    
    finally:
        scraper.close()
        print("\n✅ SELESAI!")


if __name__ == "__main__":
    main()

## 🎯 Fitur Baru:

# ### 1. **Multi-Page Scraping** 
# - ✅ Otomatis scrape SEMUA halaman (ratusan halaman)
# - ✅ Klik tombol "PERGI" otomatis untuk pindah halaman
# - ✅ Stop otomatis saat mencapai halaman terakhir

# ### 2. **Progress Tracking**
# - ✅ Menampilkan progress setiap halaman
# - ✅ Update total data setiap 10 halaman
# - ✅ Informasi real-time

# ### 3. **Error Handling & Recovery**
# - ✅ Jika di-interrupt (Ctrl+C), data yang sudah terkumpul tetap disimpan
# - ✅ Jika error, simpan data partial
# - ✅ Anti-duplicate: tidak menyimpan data yang sama 2x

# ### 4. **CSV Output**
# - ✅ Disimpan di folder yang sama dengan script Python
# - ✅ Encoding UTF-8-BOM agar Excel bisa baca karakter Indonesia
# - ✅ Ada kolom nomor urut

# ### 5. **Safety Features**
# - ✅ Max 200 halaman (safety limit, bisa diubah)
# - ✅ Delay antar halaman untuk hindari rate limiting
# - ✅ Multiple selector untuk tombol Next

# ## 📊 Output:

# # File CSV akan berisi:
# # ```
# # no, position, company, submitted_date, status
# # 1, DATA ANALYST, Pt. Bhinneka Sangkuriang Transport, Agustus 10 2025 7:10 malam, Dilamar
# # 2, ...