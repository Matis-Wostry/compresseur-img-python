import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image

# --- FONCTION UTILITAIRE : Convertir les octets en Ko, Mo, Go ---
def format_bytes(size):
    # 1024 octets = 1 Ko, 1024 Ko = 1 Mo...
    power = 2**10 # 1024
    n = 0
    power_labels = {0 : '', 1: 'Ko', 2: 'Mo', 3: 'Go', 4: 'To'}
    while size > power:
        size /= power
        n += 1
    # Retourne le nombre avec 2 chiffres après la virgule (ex: "12.50 Mo")
    return f"{size:.2f} {power_labels[n]}"

def compress_images():
    source_folder = source_entry.get()
    dest_folder = dest_entry.get()
    
    if not source_folder or not dest_folder:
        messagebox.showerror("Erreur", "Veuillez sélectionner les dossiers.")
        return

    try:
        quality_val = int(quality_entry.get())
    except ValueError:
        messagebox.showerror("Erreur", "La qualité doit être un nombre.")
        return

    supported_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')
    
    # --- PHASE 1 : ANALYSE AVANT TRAITEMENT ---
    lbl_status.config(text="Analyse des fichiers...", fg="blue")
    root.update()

    all_files = os.listdir(source_folder)
    images_to_process = [f for f in all_files if f.lower().endswith(supported_extensions)]
    total_images = len(images_to_process)

    if total_images == 0:
        messagebox.showinfo("Info", "Aucune image trouvée.")
        return

    # Calcul de la taille totale INITIALE
    total_src_size = 0
    for img_name in images_to_process:
        # os.path.getsize donne la taille en octets
        total_src_size += os.path.getsize(os.path.join(source_folder, img_name))

    # On affiche les infos de départ
    lbl_total_files.config(text=f"Images à traiter : {total_images}")
    lbl_initial_size.config(text=f"Poids total source : {format_bytes(total_src_size)}")
    
    # Reset des compteurs pour le traitement
    progress_bar['maximum'] = total_images
    progress_bar['value'] = 0
    
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    files_processed = 0
    total_dest_size = 0 # Compteur pour la taille finale

    # --- PHASE 2 : TRAITEMENT ---
    for filename in images_to_process:
        try:
            file_path = os.path.join(source_folder, filename)
            
            with Image.open(file_path) as img:
                file_name_no_ext = os.path.splitext(filename)[0]
                output_path = os.path.join(dest_folder, file_name_no_ext + ".webp")
                
                img.save(output_path, 'webp', quality=quality_val, optimize=True)
                
                # On récupère la taille du nouveau fichier créé
                dest_size = os.path.getsize(output_path)
                total_dest_size += dest_size
                
                files_processed += 1
                
                # Mise à jour barre et texte
                progress_bar['value'] = files_processed
                percent = int((files_processed / total_images) * 100)
                lbl_status.config(text=f"Conversion : {percent}%")
                
                # Mise à jour dynamique de la taille obtenue
                lbl_final_size.config(text=f"Poids total obtenu : {format_bytes(total_dest_size)}")
                
                root.update_idletasks()

        except Exception as e:
            print(f"Erreur : {e}")

    # --- PHASE 3 : BILAN FINAL ---
    # Calcul du gain
    saved_size = total_src_size - total_dest_size
    saved_percent = (saved_size / total_src_size) * 100 if total_src_size > 0 else 0

    lbl_status.config(text="Terminé avec succès !", fg="green")
    
    # Affichage d'un bilan clair
    result_text = (f"Opération terminée !\n\n"
                   f"Images traitées : {files_processed}\n"
                   f"Taille Avant : {format_bytes(total_src_size)}\n"
                   f"Taille Après : {format_bytes(total_dest_size)}\n"
                   f"Gain : {format_bytes(saved_size)} (-{saved_percent:.1f}%)")
    
    messagebox.showinfo("Bilan de compression", result_text)
    progress_bar['value'] = 0

# --- GUI SETUP ---
def select_source():
    path = filedialog.askdirectory()
    if path:
        source_entry.delete(0, tk.END)
        source_entry.insert(0, path)

def select_dest():
    path = filedialog.askdirectory()
    if path:
        dest_entry.delete(0, tk.END)
        dest_entry.insert(0, path)

root = tk.Tk()
root.title("Compressor WebP - Avec Stats")
root.geometry("600x550")

main_frame = tk.Frame(root, padx=20, pady=20)
main_frame.pack(expand=True, fill="both")

# Source
tk.Label(main_frame, text="Dossier Source :", anchor="w").pack(fill="x")
source_frame = tk.Frame(main_frame)
source_frame.pack(fill="x", pady=(0, 10))
source_entry = tk.Entry(source_frame)
source_entry.pack(side=tk.LEFT, expand=True, fill="x", padx=(0, 10))
tk.Button(source_frame, text="...", command=select_source).pack(side=tk.RIGHT)

# Destination
tk.Label(main_frame, text="Dossier Destination :", anchor="w").pack(fill="x")
dest_frame = tk.Frame(main_frame)
dest_frame.pack(fill="x", pady=(0, 10))
dest_entry = tk.Entry(dest_frame)
dest_entry.pack(side=tk.LEFT, expand=True, fill="x", padx=(0, 10))
tk.Button(dest_frame, text="...", command=select_dest).pack(side=tk.RIGHT)

# Qualité
tk.Label(main_frame, text="Qualité (1-100) :", anchor="w").pack(fill="x")
quality_entry = tk.Entry(main_frame)
quality_entry.insert(0, "80")
quality_entry.pack(anchor="w", pady=(0, 20))

# --- NOUVEAU : CADRE STATISTIQUES ---
stats_frame = tk.LabelFrame(main_frame, text="Statistiques en temps réel", padx=10, pady=10)
stats_frame.pack(fill="x", pady=10)

lbl_total_files = tk.Label(stats_frame, text="Images à traiter : 0", font=("Arial", 10))
lbl_total_files.pack(anchor="w")

lbl_initial_size = tk.Label(stats_frame, text="Poids total source : 0 Ko", font=("Arial", 10, "bold"))
lbl_initial_size.pack(anchor="w")

lbl_final_size = tk.Label(stats_frame, text="Poids total obtenu : 0 Ko", font=("Arial", 10, "bold"), fg="#4CAF50")
lbl_final_size.pack(anchor="w")
# ------------------------------------

# Barre de progression
progress_bar = ttk.Progressbar(main_frame, orient="horizontal", length=100, mode="determinate")
progress_bar.pack(fill="x", pady=10)

lbl_status = tk.Label(main_frame, text="En attente", fg="grey")
lbl_status.pack(pady=5)

# Bouton
tk.Button(main_frame, text="LANCER LA COMPRESSION", command=compress_images, 
          bg="#007bff", fg="white", font=("Arial", 11, "bold"), height=2).pack(fill="x", pady=10)

root.mainloop()