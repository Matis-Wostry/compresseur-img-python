import os  # Pour interagir avec Windows (lire les dossiers, fichiers, tailles)
import tkinter as tk  # La base pour créer la fenêtre
from tkinter import filedialog, messagebox  # Pour les popups (alertes) et choisir les dossiers
from tkinter import ttk  # Pour les widgets modernes (notamment la barre de progression)
from PIL import Image  # "Pillow" : La bibliothèque qui manipule réellement les images

# =============================================================================
# FONCTION 1 : Le Convertisseur Mathématique
# =============================================================================
def format_bytes(size):
    """
    Transforme un nombre brut (ex: 5242880 octets) en format lisible (ex: 5.00 Mo).
    C'est purement esthétique pour l'humain.
    """
    # 1024 octets = 1 Ko, 1024 Ko = 1 Mo, etc.
    power = 2**10  # 1024
    n = 0
    power_labels = {0 : '', 1: 'Ko', 2: 'Mo', 3: 'Go', 4: 'To'}
    
    # Tant que le nombre est plus grand que 1024, on le divise
    while size > power:
        size /= power
        n += 1
    # On retourne une chaîne de caractères formatée (2 chiffres après la virgule)
    return f"{size:.2f} {power_labels[n]}"

# =============================================================================
# FONCTION 2 : Le Moteur du Programme (Logique)
# =============================================================================
def compress_images():
    # --- ÉTAPE A : Récupérer ce que l'utilisateur a écrit ---
    source_folder = source_entry.get() # Prend le texte du champ "Source"
    dest_folder = dest_entry.get()     # Prend le texte du champ "Destination"
    
    # Vérification de sécurité : les champs sont-ils vides ?
    if not source_folder or not dest_folder:
        messagebox.showerror("Erreur", "Veuillez sélectionner les dossiers.")
        return # On arrête tout ici si c'est vide

    # On essaie de convertir la qualité en nombre entier
    try:
        quality_val = int(quality_entry.get())
    except ValueError:
        messagebox.showerror("Erreur", "La qualité doit être un chiffre (ex: 80).")
        return

    # Liste des formats que notre programme accepte de traiter
    supported_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')
    
    # --- ÉTAPE B : Analyse préliminaire (Le Scan) ---
    # On change le texte en bas pour dire qu'on travaille
    lbl_status.config(text="Analyse des fichiers en cours...", fg="blue")
    root.update() # Force l'interface à afficher ce texte tout de suite

    # On liste tous les fichiers du dossier
    all_files = os.listdir(source_folder)
    # On filtre : on ne garde que les images (fichiers qui finissent par .jpg, .png...)
    images_to_process = [f for f in all_files if f.lower().endswith(supported_extensions)]
    total_images = len(images_to_process)

    # Si aucune image trouvée, on prévient et on arrête
    if total_images == 0:
        messagebox.showinfo("Info", "Aucune image compatible trouvée dans ce dossier.")
        return

    # --- ÉTAPE C : Calcul du poids AVANT compression ---
    total_src_size = 0
    for img_name in images_to_process:
        # On reconstitue le chemin complet (ex: C:/Dossier/photo.jpg)
        full_path = os.path.join(source_folder, img_name)
        # os.path.getsize nous donne la taille en octets
        total_src_size += os.path.getsize(full_path)

    # Mise à jour des stats à l'écran
    lbl_total_files.config(text=f"Images à traiter : {total_images}")
    lbl_initial_size.config(text=f"Poids total source : {format_bytes(total_src_size)}")
    
    # Préparation de la barre de progression (0 sur Total)
    progress_bar['maximum'] = total_images
    progress_bar['value'] = 0
    
    # Création du dossier de destination s'il n'existe pas déjà
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    # Initialisation des compteurs pour la boucle
    files_processed = 0
    total_dest_size = 0 

    # --- ÉTAPE D : La Boucle de Traitement (Le cœur du travail) ---
    for filename in images_to_process:
        try:
            # 1. On ouvre l'image originale
            file_path = os.path.join(source_folder, filename)
            
            with Image.open(file_path) as img:
                # 2. On prépare le nouveau nom (on remplace .jpg par .webp)
                # splitext sépare le nom de l'extension
                file_name_no_ext = os.path.splitext(filename)[0]
                output_path = os.path.join(dest_folder, file_name_no_ext + ".webp")
                
                # 3. La conversion magique
                # 'optimize=True' demande à la lib de chercher la meilleure compression possible
                img.save(output_path, 'webp', quality=quality_val, optimize=True)
                
                # 4. On pèse le nouveau fichier créé pour les stats
                dest_size = os.path.getsize(output_path)
                total_dest_size += dest_size
                
                # 5. On met à jour l'interface graphique
                files_processed += 1
                progress_bar['value'] = files_processed
                
                # Calcul du pourcentage pour l'affichage texte
                percent = int((files_processed / total_images) * 100)
                lbl_status.config(text=f"Traitement : {percent}% ({files_processed}/{total_images})")
                
                # Mise à jour du poids final en temps réel (effet compteur)
                lbl_final_size.config(text=f"Poids total obtenu : {format_bytes(total_dest_size)}")
                
                # CRUCIAL : root.update_idletasks() permet à la fenêtre de ne pas "geler".
                # Sans ça, Windows croirait que le logiciel a planté pendant la boucle.
                root.update_idletasks()

        except Exception as e:
            print(f"Erreur sur le fichier {filename} : {e}")

    # --- ÉTAPE E : Le Bilan Final ---
    # Calcul mathématique de l'espace gagné
    saved_size = total_src_size - total_dest_size
    # Évite une division par zéro si le dossier était vide (peu probable ici mais bonne pratique)
    saved_percent = (saved_size / total_src_size) * 100 if total_src_size > 0 else 0

    lbl_status.config(text="Terminé avec succès !", fg="green")
    
    # Création du texte pour la fenêtre pop-up de fin
    result_text = (f"Opération terminée !\n\n"
                   f"Images traitées : {files_processed}\n"
                   f"Taille Avant : {format_bytes(total_src_size)}\n"
                   f"Taille Après : {format_bytes(total_dest_size)}\n"
                   f"Gain : {format_bytes(saved_size)} (-{saved_percent:.1f}%)")
    
    messagebox.showinfo("Bilan de compression", result_text)
    progress_bar['value'] = 0 # On remet la barre à zéro pour la prochaine fois

# =============================================================================
# FONCTION 3 : Gestion de l'Interface Graphique (GUI)
# =============================================================================

# Ces fonctions servent juste à ouvrir la fenêtre "Choisir un dossier" de Windows
def select_source():
    path = filedialog.askdirectory()
    if path:
        source_entry.delete(0, tk.END) # On vide le champ texte actuel
        source_entry.insert(0, path)   # On insère le chemin choisi

def select_dest():
    path = filedialog.askdirectory()
    if path:
        dest_entry.delete(0, tk.END)
        dest_entry.insert(0, path)

# --- Initialisation de la fenêtre principale ---
root = tk.Tk()
root.title("Compressor WebP - Avec Stats")
root.geometry("600x550") # Taille de la fenêtre (Largeur x Hauteur)

# Création d'un conteneur principal pour avoir des marges propres (padding)
main_frame = tk.Frame(root, padx=20, pady=20)
main_frame.pack(expand=True, fill="both")

# --- BLOC 1 : Sélection Source ---
tk.Label(main_frame, text="Dossier Source (Vos images originales) :", anchor="w").pack(fill="x")
source_frame = tk.Frame(main_frame)
source_frame.pack(fill="x", pady=(0, 10))

source_entry = tk.Entry(source_frame)
source_entry.pack(side=tk.LEFT, expand=True, fill="x", padx=(0, 10))
# Le bouton appelle la fonction 'select_source' quand on clique dessus
tk.Button(source_frame, text="Parcourir...", command=select_source).pack(side=tk.RIGHT)

# --- BLOC 2 : Sélection Destination ---
tk.Label(main_frame, text="Dossier Destination (Où sauvegarder ?) :", anchor="w").pack(fill="x")
dest_frame = tk.Frame(main_frame)
dest_frame.pack(fill="x", pady=(0, 10))

dest_entry = tk.Entry(dest_frame)
dest_entry.pack(side=tk.LEFT, expand=True, fill="x", padx=(0, 10))
tk.Button(dest_frame, text="Parcourir...", command=select_dest).pack(side=tk.RIGHT)

# --- BLOC 3 : Réglage Qualité ---
tk.Label(main_frame, text="Qualité de compression (1-100, défaut 80) :", anchor="w").pack(fill="x")
quality_entry = tk.Entry(main_frame)
quality_entry.insert(0, "80") # On pré-remplit avec 80
quality_entry.pack(anchor="w", pady=(0, 20))

# --- BLOC 4 : Les Statistiques (LabelFrame = Cadre avec titre) ---
stats_frame = tk.LabelFrame(main_frame, text="Statistiques en temps réel", padx=10, pady=10)
stats_frame.pack(fill="x", pady=10)

# Les labels sont vides ou à 0 au début, ils seront remplis par le code plus tard
lbl_total_files = tk.Label(stats_frame, text="Images à traiter : 0", font=("Arial", 10))
lbl_total_files.pack(anchor="w")

lbl_initial_size = tk.Label(stats_frame, text="Poids total source : 0 Ko", font=("Arial", 10, "bold"))
lbl_initial_size.pack(anchor="w")

lbl_final_size = tk.Label(stats_frame, text="Poids total obtenu : 0 Ko", font=("Arial", 10, "bold"), fg="#4CAF50") # Vert
lbl_final_size.pack(anchor="w")

# --- BLOC 5 : Barre de progression et Bouton ---
# 'determinate' veut dire qu'on sait quand ça finit (contrairement à une barre de chargement infinie)
progress_bar = ttk.Progressbar(main_frame, orient="horizontal", length=100, mode="determinate")
progress_bar.pack(fill="x", pady=10)

lbl_status = tk.Label(main_frame, text="En attente", fg="grey")
lbl_status.pack(pady=5)

# LE GROS BOUTON : C'est lui qui déclenche la fonction 'compress_images' tout en haut
tk.Button(main_frame, text="LANCER LA COMPRESSION", command=compress_images, 
          bg="#007bff", fg="white", font=("Arial", 11, "bold"), height=2).pack(fill="x", pady=10)

# Lancement de la boucle infinie qui maintient la fenêtre ouverte
root.mainloop()