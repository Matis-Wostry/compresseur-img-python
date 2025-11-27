import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

def compress_images():
    source_folder = source_entry.get()
    dest_folder = dest_entry.get()
    
    # Vérification des champs
    if not source_folder or not dest_folder:
        messagebox.showerror("Erreur", "Veuillez sélectionner les dossiers source et destination.")
        return

    try:
        quality_val = int(quality_entry.get())
    except ValueError:
        messagebox.showerror("Erreur", "La qualité doit être un nombre entre 1 et 100.")
        return

    # Extensions d'images supportées
    supported_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')
    
    files_processed = 0
    
    # Création du dossier destination s'il n'existe pas
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    lbl_status.config(text="Traitement en cours...", fg="blue")
    root.update() # Force la mise à jour de l'interface

    try:
        for filename in os.listdir(source_folder):
            if filename.lower().endswith(supported_extensions):
                # Chemin complet
                file_path = os.path.join(source_folder, filename)
                
                # Ouverture et conversion
                with Image.open(file_path) as img:
                    # On change l'extension en .webp pour le fichier de sortie
                    file_name_no_ext = os.path.splitext(filename)[0]
                    output_path = os.path.join(dest_folder, file_name_no_ext + ".webp")
                    
                    # Sauvegarde en WebP
                    img.save(output_path, 'webp', quality=quality_val)
                    files_processed += 1
        
        lbl_status.config(text=f"Terminé ! {files_processed} images converties.", fg="green")
        messagebox.showinfo("Succès", f"Opération terminée.\n{files_processed} images ont été compressées en WebP.")

    except Exception as e:
        lbl_status.config(text="Erreur survenue", fg="red")
        messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")

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

# --- Configuration de l'interface graphique (GUI) ---
root = tk.Tk()
root.title("Convertisseur WebP de Masse")
root.geometry("500x350")

# Dossier Source
tk.Label(root, text="Dossier Source (Images):").pack(pady=5)
source_frame = tk.Frame(root)
source_frame.pack(pady=5)
source_entry = tk.Entry(source_frame, width=40)
source_entry.pack(side=tk.LEFT, padx=5)
tk.Button(source_frame, text="Parcourir", command=select_source).pack(side=tk.LEFT)

# Dossier Destination
tk.Label(root, text="Dossier Destination (Sortie):").pack(pady=5)
dest_frame = tk.Frame(root)
dest_frame.pack(pady=5)
dest_entry = tk.Entry(dest_frame, width=40)
dest_entry.pack(side=tk.LEFT, padx=5)
tk.Button(dest_frame, text="Parcourir", command=select_dest).pack(side=tk.LEFT)

# Qualité
tk.Label(root, text="Qualité (1-100, recommandé : 80):").pack(pady=5)
quality_entry = tk.Entry(root, width=10)
quality_entry.insert(0, "80") # Valeur par défaut
quality_entry.pack(pady=5)

# Bouton Action
tk.Button(root, text="Lancer la conversion", command=compress_images, bg="#4CAF50", fg="white", font=("Arial", 12, "bold")).pack(pady=20)

# Status
lbl_status = tk.Label(root, text="Prêt")
lbl_status.pack(pady=10)

root.mainloop()