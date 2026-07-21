import os
import sys
import time
import requests
import json
import threading
import concurrent.futures
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

ASCII_ART = """\
\033[38;5;205m⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠞
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⠞⠁
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⡶⠛⠉
⠀⠀⠀⠀⠀⠀⠀⣴⠟⠁
⠀⠀⠀⠀⠀⢀⣾⠃
⠀⠀⠀⠀⠀⡸⡇
⠀⠀⠀⠀⠀⡇⡇
⠀⠀⠀⠀⠀⢹⣳⡀
⠀⠀⠀⠀⠀⠀⠑⠯⣗⣒⡶⠶⠒⠒⠲⢶⣄⡀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡤⡞⡟⠃⠀⠘⣷⡀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡏⣼⢁⡷⣄⠀⠀⢸⡇⠀⠀⠀⠀⢀⡤⠖⣒⠖⣒⡭⣿⣷⣶⣄
⠀⠀⠀⠀⠀⠀⠀⠀⠀⡾⡇⠀⢟⠀⠈⠙⢦⡈⡇⠀⠀⢀⡴⠉⣠⠞⢥⡾⣫⣿⠿⠋⠉⢻⡄
⠀⠀⠀⠀⠀⠀⠀⠀⢸⣇⢷⠀⠘⡄⠀⠀⠀⠙⢿⡀⠀⣾⠂⡰⢁⡾⡷⢁⢿⡃
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣟⡄⢣⡀⠹⡄⠀⠀⠀⠀⠙⣴⡇⢰⠃⣾⠳⠁⡸⠀⡇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⡄⠀⠱⡄⠘⡄⢰⣦⡀⠀⠘⡇⢸⢰⡏⠃⢠⠃⠀⡇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣄⢰⣾⣦⠈⢆⢻⣡⢸⣆⢹⢸⢸⡇⠀⡌⠀⣰⠁⢀⣠⠤⠤⠠⢤⣄
⠀⠀⠀⢀⡤⠖⠒⠒⠋⠉⠑⠚⠷⣍⠻⣷⣶⡧⣧⠉⣏⠈⡏⢺⣧⣠⡃⢠⣣⡶⡫⢖⣨⣤⣤⣤⣼⣷⡤⡀
⠀⢀⡴⣋⠤⠀⠀⠀⠀⠂⠤⠜⣿⠷⢽⣮⣿⣽⣝⢧⡸⡄⢳⢸⣿⣸⢁⣿⣿⣿⠾⢋⠭⣲⣶⣶⣟⣽⣿⣿⡆
⠀⣾⣾⣷⠾⠿⠶⠶⠶⠆⣴⣤⢰⣿⣤⣌⡛⠿⣿⣿⣷⣳⣾⣆⡿⡏⣼⣿⡿⢡⡞⣡⠞⠁⠀⠀⠀⠀⠈⣿
⢀⣿⠋⠀⠀⠀⠀⠀⠀⠐⠂⠤⠭⢅⣛⡙⡛⢷⣺⣿⣾⣿⣽⣿⣹⣿⡋⠈⠙⢷⠚⠁⠀⠀⠀⠀⠀⢠⣴⠿
⢸⡾⠋⠙⠲⢦⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠠⠠⣿⣿⣿⣿⣿⣿⢗⡢⣍⠂⡈⢇
⠀⠀⠀⠀⠀⠀⠉⠙⠒⠲⢤⣤⣤⢤⣤⣴⡶⣾⣿⣿⠿⢻⠟⣿⡄⠀⠙⢮⢣⡘⡜⡆
⠀⠀⠀⠀⠀⡤⠖⠚⣩⠟⣩⣔⠟⣋⢝⡲⠝⠛⢩⣿⡀⠈⢆⠑⠙⣦⡀⠀⠳⣳⢰⡇
⠀⠀⠀⠀⠀⠀⠀⡼⢋⢾⢟⡥⡪⠖⠁⣀⣀⣬⡴⣟⡙⠒⠂⠥⢤⣈⣑⡠⡈⢿⣾⡇⠀⠀⠀⠀⠀⣤⡀
⠀⠀⠀⠀⠀⠀⠀⣧⡳⢡⣮⠎⢠⠖⠋⠉⠉⠁⠀⠀⠈⠓⢤⠀⠀⠙⣿⣯⡿⣯⣷⡇⠀⠀⠀⣀⠴⢽⣷⡄
⠀⠀⠀⠀⠀⠀⠀⡟⡇⢷⢃⢆⡏⠀⠀⠀⢀⣤⣤⣤⣶⣶⡶⢦⣄⠀⠈⠹⣇⠘⡿⠀⢀⡴⠚⢁⠀⣸⢹⢱
⠀⠀⠀⠀⠀⠀⠀⢻⣧⣽⢸⡏⠀⠀⠀⠀⠀⠀⠉⢻⠻⡛⢮⣓⢄⠙⠒⢤⡹⣼⡇⢠⠏⠀⠀⡎⢠⡟⡘⢸
⠀⠀⠀⠀⠀⠀⠀⠀⠙⠿⣏⢿⣄⣀⣀⣀⡄⠀⠀⢸⢸⡘⢆⠙⠧⡀⠀⠀⠈⢮⡃⡞⢀⡀⢸⢀⡞⠁⠃⡸
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠓⠿⠿⠟⠋⠀⠀⠀⠘⣇⠃⠀⠱⡌⠹⡔⡄⠀⢰⣳⡇⣾⡇⢣⣿⠇⠆⠀⠃\033[0m
"""

print_lock = threading.Lock()

def safe_print(*args, **kwargs):
    with print_lock:
        print(*args, **kwargs)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def animated_print(text, delay=0.015):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def get_input(prompt_text, default=""):
    if default:
        return input(f"\033[96m{prompt_text}\033[0m \033[90m(Entrée pour: {default})\033[0m: ") or default
    return input(f"\033[96m{prompt_text}\033[0m: ")

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

class PetalPDFApp:
    def __init__(self):
        self.lang = 'fr'
        self.t = {}
        self.cache_file = '.petal_cache.json'
        
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) PetalPDF'})
        
        self.current_url = ""
        self.dest_dir = ""
        self.visited = set()
        self.to_visit = set()
        self.pdf_links = set()
        self.downloaded_pdfs = set()
        self.failed_downloads = []

    def load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_url = data.get('url', '')
                    self.dest_dir = data.get('dest_dir', '')
                    self.visited = set(data.get('visited', []))
                    self.to_visit = set(data.get('to_visit', []))
                    self.pdf_links = set(data.get('pdf_links', []))
                    self.downloaded_pdfs = set(data.get('downloaded_pdfs', []))
                    return True
            except:
                pass
        return False

    def save_cache(self):
        data = {
            'url': self.current_url,
            'dest_dir': self.dest_dir,
            'visited': list(self.visited),
            'to_visit': list(self.to_visit),
            'pdf_links': list(self.pdf_links),
            'downloaded_pdfs': list(self.downloaded_pdfs)
        }
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f)

    def clear_cache(self):
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        self.visited.clear()
        self.to_visit.clear()
        self.pdf_links.clear()
        self.downloaded_pdfs.clear()

    def set_translations(self):
        if self.lang == 'fr':
            self.t = {
                'title': "🌸 Assistant de téléchargement PetalPDF 🌸",
                'resume_q': "Une session inachevée a été trouvée. Voulez-vous la reprendre ? (o/n)",
                'url_q': "Veuillez entrer l'URL de la page",
                'scope_q': "Que souhaitez-vous explorer ?",
                'scope_page': "Uniquement cette page précise",
                'scope_site': "Cette page et les pages liées (par blocs de 100)",
                'scope_adv': "Options avancées Pro 🚀 (Turbo, Filtres, Cookies, Renommage...)",
                'adv_size': "Taille maximale par PDF en Mo (Entrée = sans limite)",
                'adv_keys': "Mots-clés requis dans l'URL du PDF (séparés par virgule, Entrée = tout)",
                'adv_cookies': "Cookies de session (format 'nom=valeur;...', Entrée = aucun)",
                'adv_rename': "Renommer automatiquement les PDF avec leur vrai titre interne ? (o/n)",
                'adv_threads': "Mode Turbo : nombre de téléchargements simultanés ? (1-10)",
                'dir_q': "Dossier de destination",
                'pypdf_warn': "⚠️ Attention : pypdf n'est pas installé. Le renommage auto est désactivé. (pip install pypdf)",
                'scanning': "🔍 Analyse en cours...",
                'more_pages': "Limite de {} pages atteinte. Il reste {} liens trouvés non explorés. Voulez-vous scanner 100 pages supplémentaires ? (o/n)",
                'found': "✨ Génial ! J'ai trouvé {} fichier(s) PDF.",
                'not_found': "Aucun PDF trouvé.",
                'dl_start': "📥 Téléchargement...",
                'dl_skip': "⏩ Le fichier {} existe déjà. Ignoré.",
                'done': "🎉 Tous les téléchargements sont terminés ! Retrouvez vos fichiers dans :",
                'retry_q': "Certains téléchargements ({}) ont échoué. Voulez-vous réessayer ? (o/n)",
                'again_q': "Voulez-vous analyser une autre URL ? (o/n)",
                'bye': "Merci d'avoir utilisé PetalPDF. À bientôt ! 🌸"
            }
        else:
            self.t = {
                'title': "🌸 PetalPDF Download Assistant 🌸",
                'resume_q': "An unfinished session was found. Do you want to resume it? (y/n)",
                'url_q': "Please enter the page URL",
                'scope_q': "What do you want to scan?",
                'scope_page': "Only this specific page",
                'scope_site': "This page and linked pages (100 at a time)",
                'scope_adv': "Advanced Pro Options 🚀 (Turbo, Filters, Cookies, Renaming...)",
                'adv_size': "Max size per PDF in MB (Enter to skip)",
                'adv_keys': "Required keywords in PDF URL (comma-separated, Enter for all)",
                'adv_cookies': "Session cookies (format 'name=value;...', Enter for none)",
                'adv_rename': "Automatically rename PDFs with their true internal title? (y/n)",
                'adv_threads': "Turbo Mode: number of simultaneous downloads? (1-10)",
                'dir_q': "Destination folder",
                'pypdf_warn': "⚠️ Warning: pypdf is not installed. Auto-renaming is disabled. (pip install pypdf)",
                'scanning': "🔍 Scanning in progress...",
                'more_pages': "Limit of {} pages reached. There are {} unvisited links left. Do you want to scan 100 more pages? (y/n)",
                'found': "✨ Awesome! I found {} PDF file(s).",
                'not_found': "No PDFs found.",
                'dl_start': "📥 Downloading...",
                'dl_skip': "⏩ File {} already exists. Skipping.",
                'done': "🎉 All downloads complete! Find your files in:",
                'retry_q': "Some downloads ({}) failed. Do you want to retry? (y/n)",
                'again_q': "Do you want to scan another URL? (y/n)",
                'bye': "Thank you for using PetalPDF. See you soon! 🌸"
            }

    def download_worker(self, pdf_url, dest_dir, max_size_bytes, rename_smart):
        if pdf_url in self.downloaded_pdfs:
            return
            
        filename = os.path.basename(urlparse(pdf_url).path)
        if not filename.lower().endswith('.pdf'):
            filename += ".pdf"
            
        filepath = os.path.join(dest_dir, filename)
        
        if os.path.exists(filepath):
            safe_print(f"\033[90m{self.t['dl_skip'].format(filename)}\033[0m")
            self.downloaded_pdfs.add(pdf_url)
            self.save_cache()
            return

        try:
            response = self.session.get(pdf_url, timeout=15, stream=True)
            response.raise_for_status()
            
            if max_size_bytes and 'Content-Length' in response.headers:
                size_bytes = int(response.headers['Content-Length'])
                if size_bytes > max_size_bytes:
                    safe_print(f"\033[91m✖ Ignoré (Trop volumineux) : {filename}\033[0m")
                    return
            
            downloaded = 0
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        downloaded += len(chunk)
                        if max_size_bytes and downloaded > max_size_bytes:
                            f.close()
                            os.remove(filepath)
                            safe_print(f"\033[91m✖ Ignoré (Dépasse limite en cours) : {filename}\033[0m")
                            return
                        f.write(chunk)

            if rename_smart and HAS_PYPDF:
                try:
                    reader = PdfReader(filepath)
                    if reader.metadata and reader.metadata.title:
                        title = sanitize_filename(reader.metadata.title)
                        if title:
                            new_filepath = os.path.join(dest_dir, f"{title}.pdf")
                            if not os.path.exists(new_filepath):
                                os.rename(filepath, new_filepath)
                                filename = f"{title}.pdf"
                except Exception:
                    pass

            self.downloaded_pdfs.add(pdf_url)
            self.save_cache()
            safe_print(f"\033[92m✔ Succès : {filename}\033[0m")
            
        except Exception as e:
            safe_print(f"\033[91m✖ Échec : {filename} ({str(e)})\033[0m")
            with print_lock:
                self.failed_downloads.append((pdf_url, filename, filepath))

    def run(self):
        clear_screen()
        print(ASCII_ART)
        
        animated_print("\033[1;35m✧ Welcome to PetalPDF / Bienvenue dans PetalPDF ✧\033[0m")
        print("\033[90m-------------------------------------------------\033[0m")
        
        while self.lang not in ['fr', 'en']:
            self.lang = input("\033[1;33m[?] Choose your language / Choisissez votre langue (fr/en) : \033[0m").strip().lower()

        self.set_translations()
        print("\n" + "\033[90m-\033[0m" * 50)
        animated_print(f"\033[1;36m{self.t['title']}\033[0m")

        # Resume Check
        resumed = False
        if self.load_cache():
            ans = input(f"\n\033[1;33m[?] {self.t['resume_q']}\033[0m ").strip().lower()
            if ans in ['o', 'y', 'oui', 'yes']:
                resumed = True
            else:
                self.clear_cache()

        while True:
            if not resumed:
                self.current_url = ""
                print("\n")
                while not self.current_url.startswith("http"):
                    self.current_url = get_input(f"➤ {self.t['url_q']}")

                scope = ""
                print(f"\n\033[1;33m[?] {self.t['scope_q']}\033[0m")
                print(f"   \033[36m1)\033[0m {self.t['scope_page']}")
                print(f"   \033[36m2)\033[0m {self.t['scope_site']}")
                print(f"   \033[35m3)\033[0m {self.t['scope_adv']}")
                
                while scope not in ['1', '2', '3']:
                    scope = input(f"\033[96m➤ Choix (1/2/3) \033[90m(Entrée pour: 1)\033[0m: ").strip()
                    if not scope: scope = "1"

                # Init Advanced vars
                max_size_bytes = None
                keywords = []
                rename_smart = False
                thread_count = 1
                base_scope = scope
                
                if scope == '3':
                    # Taille
                    size_str = get_input(f"➤ {self.t['adv_size']}")
                    try: max_size_bytes = float(size_str.replace(',','.')) * 1024 * 1024
                    except: max_size_bytes = None
                    
                    # Mots clés
                    kw_str = get_input(f"➤ {self.t['adv_keys']}")
                    if kw_str: keywords = [k.strip().lower() for k in kw_str.split(',') if k.strip()]
                    
                    # Cookies
                    cook_str = get_input(f"➤ {self.t['adv_cookies']}")
                    if cook_str:
                        for c in cook_str.split(';'):
                            if '=' in c:
                                k, v = c.split('=', 1)
                                self.session.cookies.set(k.strip(), v.strip())
                    
                    # Rename
                    if not HAS_PYPDF:
                        print(f"\033[93m{self.t['pypdf_warn']}\033[0m")
                    else:
                        ren = get_input(f"➤ {self.t['adv_rename']}", default="n").strip().lower()
                        rename_smart = (ren in ['o', 'y', 'oui', 'yes'])
                    
                    # Threads
                    th_str = get_input(f"➤ {self.t['adv_threads']}", default="5")
                    try: thread_count = max(1, min(10, int(th_str)))
                    except: thread_count = 5

                    # Return to page/site scope choice
                    sub_scope = ""
                    while sub_scope not in ['1', '2']:
                        sub_scope = input(f"\033[96m➤ Page (1) ou Site (2) ? \033[90m(Entrée pour: 1)\033[0m: ").strip()
                        if not sub_scope: sub_scope = "1"
                    base_scope = sub_scope

                self.dest_dir = get_input(f"\n➤ {self.t['dir_q']}", default="PetalPDF_Files" if self.lang=='en' else "PetalPDF_Fichiers")
                if not os.path.exists(self.dest_dir):
                    os.makedirs(self.dest_dir)

                print(f"\n\033[1;33m{self.t['scanning']}\033[0m")
                
                if base_scope == '1':
                    try:
                        response = self.session.get(self.current_url, timeout=10)
                        response.raise_for_status()
                        soup = BeautifulSoup(response.text, 'html.parser')
                        for link in soup.find_all('a'):
                            href = link.get('href')
                            if href:
                                full_url = urljoin(self.current_url, href)
                                if full_url.lower().endswith('.pdf') or '.pdf?' in full_url.lower():
                                    if not keywords or any(kw in full_url.lower() for kw in keywords):
                                        self.pdf_links.add(full_url)
                    except Exception as e:
                        print(f"\033[91m✖ Erreur : {e}\033[0m")
                else:
                    self.to_visit = {self.current_url}
                    base_netloc = urlparse(self.current_url).netloc
                    max_pages = 100
                    
                    while self.to_visit:
                        if len(self.visited) >= max_pages:
                            ans = input(f"\n\033[1;33m[?] {self.t['more_pages'].format(max_pages, len(self.to_visit))} \033[0m").strip().lower()
                            if ans in ['o', 'y', 'oui', 'yes']:
                                max_pages += 100
                            else:
                                break

                        curl = self.to_visit.pop().split('#')[0]
                        if curl in self.visited: continue
                        self.visited.add(curl)
                        
                        print(f"\033[90m  -> {curl[:80]}...\033[0m")
                        
                        try:
                            resp = self.session.get(curl, timeout=5)
                            if 'text/html' not in resp.headers.get('Content-Type', ''): continue
                            
                            soup = BeautifulSoup(resp.text, 'html.parser')
                            for link in soup.find_all('a'):
                                href = link.get('href')
                                if not href: continue
                                
                                full_url = urljoin(curl, href)
                                parsed = urlparse(full_url)
                                
                                if full_url.lower().endswith('.pdf') or '.pdf?' in full_url.lower():
                                    if not keywords or any(kw in full_url.lower() for kw in keywords):
                                        self.pdf_links.add(full_url)
                                elif parsed.netloc == base_netloc and parsed.scheme in ['http', 'https']:
                                    cln = full_url.split('#')[0]
                                    ignored = {'.jpg','.png','.gif','.svg','.css','.js','.json','.xml','.zip','.rar','.mp3','.mp4','.avi','.exe'}
                                    ext = os.path.splitext(parsed.path)[1].lower()
                                    if ext not in ignored and cln not in self.visited:
                                        self.to_visit.add(cln)
                        except Exception:
                            pass
                self.save_cache()

            # End Scan / Resume Phase
            if not self.pdf_links:
                print(f"\033[91m{self.t['not_found']}\033[0m")
            else:
                animated_print(f"\n\033[1;32m{self.t['found'].format(len(self.pdf_links))}\033[0m")
                print("\033[90m" + "-" * 40 + "\033[0m")
                
                # Fetch settings locally if resuming (fallback defaults)
                try: thread_count
                except NameError: thread_count = 5
                try: max_size_bytes
                except NameError: max_size_bytes = None
                try: rename_smart
                except NameError: rename_smart = False
                
                # Filter out already downloaded
                pending = [link for link in self.pdf_links if link not in self.downloaded_pdfs]
                
                print(f"\033[1;36m{self.t['dl_start']} (Mode Turbo: {thread_count} threads)\033[0m")
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
                    futures = [
                        executor.submit(self.download_worker, link, self.dest_dir, max_size_bytes, rename_smart)
                        for link in pending
                    ]
                    concurrent.futures.wait(futures)

                # Retries
                while self.failed_downloads:
                    print("\033[90m" + "-" * 40 + "\033[0m")
                    retry = input(f"\033[1;33m[?] {self.t['retry_q'].format(len(self.failed_downloads))} \033[0m").strip().lower()
                    if retry in ['o', 'y', 'oui', 'yes']:
                        still_failed = []
                        failed_links = [item[0] for item in self.failed_downloads]
                        self.failed_downloads = []
                        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
                            futs = [
                                executor.submit(self.download_worker, link, self.dest_dir, max_size_bytes, rename_smart)
                                for link in failed_links
                            ]
                            concurrent.futures.wait(futs)
                    else:
                        break

                print("\033[90m" + "-" * 40 + "\033[0m")
                print(f"\n\033[1;32m{self.t['done']}\033[0m \033[1;37m{os.path.abspath(self.dest_dir)}\033[0m\n")

            self.clear_cache()
            resumed = False
            
            again = input(f"\033[1;33m[?] {self.t['again_q']} : \033[0m").strip().lower()
            if again not in ['o', 'y', 'oui', 'yes']:
                break

        print("\n\033[90m" + "=" * 50 + "\033[0m")
        animated_print(f"\033[1;35m{self.t['bye']}\033[0m")
        print("\033[90m" + "=" * 50 + "\033[0m\n")

if __name__ == '__main__':
    try:
        PetalPDFApp().run()
    except KeyboardInterrupt:
        print("\n\n\033[91mInterrompu par l'utilisateur. Cache sauvegardé.\033[0m")
        sys.exit(0)
