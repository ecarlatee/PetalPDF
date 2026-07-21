import os
import sys
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# ASCII Art fixed, right border removed, cut in half, and colored in pink!
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

def main():
    clear_screen()
    print(ASCII_ART)
    
    animated_print("\033[1;35m✧ Welcome to PetalPDF / Bienvenue dans PetalPDF ✧\033[0m")
    print("\033[90m-------------------------------------------------\033[0m")
    
    # Language Selection
    lang = ""
    while lang not in ['fr', 'en']:
        lang = input("\033[1;33m[?] Choose your language / Choisissez votre langue (fr/en) : \033[0m").strip().lower()

    if lang == 'fr':
        t_title = "🌸 Assistant de téléchargement PetalPDF 🌸"
        t_url = "Veuillez entrer l'URL de la page"
        t_scope_q = "Que souhaitez-vous explorer ?"
        t_scope_page = "Uniquement cette page"
        t_scope_site = "Tout le site (max 100 pages, peut être long)"
        t_dir = "Dossier de destination"
        t_scanning = "🔍 Analyse de la page en cours..."
        t_scanning_site = "🔍 Exploration du site en cours (recherche de PDFs)..."
        t_err_url = "Impossible d'accéder à l'URL :"
        t_found = "✨ Génial ! J'ai trouvé {} fichier(s) PDF."
        t_not_found = "Aucun PDF trouvé."
        t_downloading = "📥 Téléchargement de {}..."
        t_exists = "⏩ Le fichier {} existe déjà. Ignoré."
        t_success = "✔ Terminé !"
        t_fail = "✖ Échec :"
        t_done = "🎉 Tous les téléchargements sont terminés ! Retrouvez vos fichiers dans :"
        t_again = "Voulez-vous analyser une autre URL ? (o/n)"
        t_bye = "Merci d'avoir utilisé PetalPDF. À bientôt ! 🌸"
        default_dir = "PetalPDF_Fichiers"
    else:
        t_title = "🌸 PetalPDF Download Assistant 🌸"
        t_url = "Please enter the page URL"
        t_scope_q = "What do you want to scan?"
        t_scope_page = "Only this page"
        t_scope_site = "Entire site (max 100 pages, might take a while)"
        t_dir = "Destination folder"
        t_scanning = "🔍 Scanning the page..."
        t_scanning_site = "🔍 Crawling site (looking for PDFs)..."
        t_err_url = "Could not access URL:"
        t_found = "✨ Awesome! I found {} PDF file(s)."
        t_not_found = "No PDFs found."
        t_downloading = "📥 Downloading {}..."
        t_exists = "⏩ File {} already exists. Skipping."
        t_success = "✔ Done!"
        t_fail = "✖ Failed:"
        t_done = "🎉 All downloads complete! Find your files in:"
        t_again = "Do you want to scan another URL? (y/n)"
        t_bye = "Thank you for using PetalPDF. See you soon! 🌸"
        default_dir = "PetalPDF_Files"

    print("\n" + "\033[90m-\033[0m" * 50)
    animated_print(f"\033[1;36m{t_title}\033[0m")
    
    while True:
        url = ""
        print("\n")
        while not url.startswith("http"):
            url = get_input(f"➤ {t_url}")
            if not url.startswith("http"):
                print("\033[91m⚠️ Format d'URL invalide. / Invalid URL format.\033[0m")

        # Scope Selection
        scope = ""
        print(f"\n\033[1;33m[?] {t_scope_q}\033[0m")
        print(f"   \033[36m1)\033[0m {t_scope_page}")
        print(f"   \033[36m2)\033[0m {t_scope_site}")
        while scope not in ['1', '2']:
            scope = input(f"\033[96m➤ Choix (1/2) \033[90m(Entrée pour: 1)\033[0m: ").strip()
            if not scope: scope = "1"

        dest_dir = get_input(f"\n➤ {t_dir}", default=default_dir)

        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        pdf_links = set()

        if scope == '1':
            print(f"\n\033[1;33m{t_scanning}\033[0m")
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                for link in soup.find_all('a'):
                    href = link.get('href')
                    if href:
                        full_url = urljoin(url, href)
                        if full_url.lower().endswith('.pdf') or '.pdf?' in full_url.lower():
                            pdf_links.add(full_url)
            except Exception as e:
                print(f"\033[91m{t_err_url} {e}\033[0m")
                
        else:
            print(f"\n\033[1;33m{t_scanning_site}\033[0m")
            visited = set()
            to_visit = {url}
            base_netloc = urlparse(url).netloc
            max_pages = 100
            
            while to_visit and len(visited) < max_pages:
                current_url = to_visit.pop().split('#')[0]
                
                if current_url in visited:
                    continue
                visited.add(current_url)
                
                print(f"\033[90m  -> {current_url[:80]}...\033[0m")
                
                try:
                    resp = requests.get(current_url, headers=headers, timeout=5)
                    # Skip if not HTML (like images) to avoid slowing down parsing
                    if 'text/html' not in resp.headers.get('Content-Type', ''):
                        continue
                        
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    for link in soup.find_all('a'):
                        href = link.get('href')
                        if not href: continue
                        
                        full_url = urljoin(current_url, href)
                        parsed = urlparse(full_url)
                        
                        if full_url.lower().endswith('.pdf') or '.pdf?' in full_url.lower():
                            pdf_links.add(full_url)
                        elif parsed.netloc == base_netloc and parsed.scheme in ['http', 'https']:
                            clean_url = full_url.split('#')[0]
                            
                            # Scan intelligent : on ignore les extensions qui ne sont clairement pas des pages
                            ignored_exts = {
                                '.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico',
                                '.css', '.js', '.js.map', '.json', '.xml', '.csv',
                                '.zip', '.rar', '.7z', '.tar', '.gz',
                                '.mp3', '.mp4', '.avi', '.mov', '.wav',
                                '.exe', '.dmg', '.iso', '.apk'
                            }
                            ext = os.path.splitext(parsed.path)[1].lower()
                            
                            if ext not in ignored_exts:
                                if clean_url not in visited:
                                    to_visit.add(clean_url)
                except Exception:
                    pass

        pdf_links = list(pdf_links)
        
        if not pdf_links:
            print(f"\033[91m{t_not_found}\033[0m")
        else:
            animated_print(f"\n\033[1;32m{t_found.format(len(pdf_links))}\033[0m")
            print("\033[90m" + "-" * 40 + "\033[0m")
            
            for index, pdf_url in enumerate(pdf_links, 1):
                filename = os.path.basename(urlparse(pdf_url).path)
                if not filename.lower().endswith('.pdf'):
                    filename = f"document_{index}.pdf"
                    
                filepath = os.path.join(dest_dir, filename)
                
                print(f"\033[36m[{index}/{len(pdf_links)}] {t_downloading.format(filename)}\033[0m", end=" ")
                sys.stdout.flush()
                
                if os.path.exists(filepath):
                    print(f"\n   \033[90m{t_exists.format(filename)}\033[0m")
                    continue
                    
                try:
                    pdf_response = requests.get(pdf_url, headers=headers, timeout=10)
                    pdf_response.raise_for_status()
                    with open(filepath, 'wb') as f:
                        f.write(pdf_response.content)
                    print(f"\033[92m{t_success}\033[0m")
                except Exception as e:
                    print(f"\n   \033[91m{t_fail} {e}\033[0m")

            print("\033[90m" + "-" * 40 + "\033[0m")
            print(f"\n\033[1;32m{t_done}\033[0m \033[1;37m{os.path.abspath(dest_dir)}\033[0m\n")

        again = input(f"\033[1;33m[?] {t_again} : \033[0m").strip().lower()
        if again not in ['o', 'y', 'oui', 'yes']:
            break

    print("\n\033[90m" + "=" * 50 + "\033[0m")
    animated_print(f"\033[1;35m{t_bye}\033[0m")
    print("\033[90m" + "=" * 50 + "\033[0m\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n\033[91mInterrompu par l'utilisateur. / Interrupted by user.\033[0m")
        sys.exit(0)
