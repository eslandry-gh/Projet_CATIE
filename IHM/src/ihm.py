import threading
import time
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import serial
import serial.tools.list_ports


class MeshMonitorApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Moniteur Réseau Mesh")
    self.root.geometry("1600x900")

    self.serial_conn = None
    self.is_connected = False

    # Configuration des styles
    self.style = ttk.Style()
    self.style.theme_use("clam")

    self.create_widgets()
    self.refresh_ports()

  def create_widgets(self):
    # --- Cadre supérieur : connexion série ---
    control_frame = ttk.LabelFrame(
        self.root, text=" Configuration du Port Série ", padding=10
    )
    control_frame.pack(fill="x", padx=10, pady=10)

    ttk.Label(control_frame, text="Port:").grid(
        row=0, column=0, sticky="w", padx=5
    )
    self.port_combo = ttk.Combobox(control_frame, width=25, state="readonly")
    self.port_combo.grid(row=0, column=1, padx=5)

    refresh_btn = ttk.Button(
        control_frame, text="Actualiser", command=self.refresh_ports
    )
    refresh_btn.grid(row=0, column=2, padx=5)

    ttk.Label(control_frame, text="Baudrate:").grid(
        row=0, column=3, sticky="w", padx=5
    )
    self.baud_combo = ttk.Combobox(
        control_frame, width=10, values=["9600", "19200", "57600", "115200"]
    )
    self.baud_combo.grid(row=0, column=4, padx=5)
    self.baud_combo.set("115200")

    self.connect_btn = ttk.Button(
        control_frame, text="Connexion", command=self.toggle_connection
    )
    self.connect_btn.grid(row=0, column=5, padx=10)
    # --- Fin cadre supérieur ---

    # --- Cadre central : actions et alertes ---
    action_frame = ttk.LabelFrame(
        self.root, text=" Actions & Réseau Mesh ", padding=10
    )
    action_frame.pack(fill="x", padx=10, pady=5)

    self.scan_btn = ttk.Button(
        action_frame,
        text="Scanner le Réseau Mesh",
        command=self.scan_mesh_network,
        state="disabled",
    )
    self.scan_btn.pack(side="left", padx=5)

    self.stop_scan_btn = ttk.Button(
            action_frame,
            text="Arreter le scan",
            command=self.stop_network_scan,
            state="disabled",
        )
    self.stop_scan_btn.pack(side="left", padx=6)
    
    self.record_btn = ttk.Button(
        action_frame,
        text="Sauvegarder l'historique",
        command=self.save_terminal_history,
        state="disabled",
    )
    self.record_btn.pack(side="left", padx=5)

    clear_btn = ttk.Button(
        action_frame, text="Effacer l'affichage", command=self.clear_terminal
    )
    clear_btn.pack(side="right", padx=5)
    # --- Fin cadre central ---

    # Indicateur d'alerte visuelle
    self.alert_banner = tk.Label(
        self.root,
        text="STATUT: Aucun problème détecté",
        bg="green",
        fg="white",
        font=("Arial", 11, "bold"),
    )
    self.alert_banner.pack(fill="x", padx=10, pady=5)

    # --- Cadre inférieur : trames reçues ---
    terminal_frame = ttk.LabelFrame(
        self.root, text=" Trames reçues ", padding=10
    )
    terminal_frame.pack(fill="both", expand=True, padx=10, pady=10)

    self.terminal_text = tk.Text(
        terminal_frame, bg="black", fg="#00FF00", font=("Consolas", 10)
    )
    self.terminal_text.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(
        terminal_frame,
        orient="vertical",
        command=self.terminal_text.yview,
    )
    scrollbar.pack(side="right", fill="y")
    self.terminal_text.configure(yscrollcommand=scrollbar.set)
    # --- Fin cadre inféreur ---

  def refresh_ports(self):
    ports = [port.device for port in serial.tools.list_ports.comports()]
    self.port_combo["values"] = ports
    if ports:
      self.port_combo.current(0)

  def toggle_connection(self):
    if not self.is_connected:
      port = self.port_combo.get()
      baudrate = self.baud_combo.get()
      if not port:
        messagebox.showerror("Erreur", "Veuillez sélectionner un port série.")
        return
      try:
        self.serial_conn = serial.Serial(port, int(baudrate), timeout=0.1)
        self.is_connected = True
        self.connect_btn.config(text="Déconnexion")
        self.scan_btn.config(state="normal")
        self.record_btn.config(state="normal")
        self.port_combo.config(state="disabled")
        self.baud_combo.config(state="disabled")

        # Lancer le thread d'écoute série
        self.listener_thread = threading.Thread(
            target=self.read_serial, daemon=True
        )
        self.listener_thread.start()
        self.log_terminal(f"Connecté à {port} à {baudrate} bauds.\n")
      except Exception as e:
        messagebox.showerror(
            "Erreur de connexion", f"Impossible d'ouvrir le port:\n{e}"
        )
    else:
      self.disconnect_serial()

  def disconnect_serial(self):
    self.is_connected = False
    if self.serial_conn and self.serial_conn.is_open:
      self.serial_conn.close()
    self.connect_btn.config(text="Connexion")
    self.scan_btn.config(state="disabled")
    self.record_btn.config(state="disabled")
    self.port_combo.config(state="readonly")
    self.baud_combo.config(state="normal")
    self.log_terminal("Déconnecté du port série.\n")

  def read_serial(self):
    while self.is_connected:
      try:
        if self.serial_conn and self.serial_conn.in_waiting > 0:
          line = self.serial_conn.readline().decode("utf-8", errors="ignore")
          if line:
            timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
            full_msg = timestamp + line

            # Affichage terminal
            self.log_terminal(full_msg)

            # Analyse du message (Alerte & Mesh)
            self.parse_mesh_message(line.strip())
      except Exception:
        break
      time.sleep(0.01)

  def parse_mesh_message(self, message):
    # Exemple de format d'alerte : "ALERTE:NODE_03:Batterie faible"
    # Exemple de format de réponse de scan : "MESH_NODE:ID=02,STATUS=OK"
    if message.startswith("ALERTE:"):
      parts = message.split(":")
      node_id = parts[1] if len(parts) > 1 else "Inconnu"
      reason = parts[2] if len(parts) > 2 else "Non spécifiée"
      self.trigger_alert(node_id, reason)

  def trigger_alert(self, node_id, reason):
    # Mise à jour graphique de l'alerte (depuis un thread, Tkinter gère bien le changement de bg/text)
    self.alert_banner.config(
        text=f"ALERTE ACTIVE ! Déclenchée par le nœud : {node_id} ({reason})",
        bg="red",
    )

  def scan_mesh_network(self):
    if self.serial_conn and self.serial_conn.is_open:
      # Envoi d'une commande AT ou d'une trame spécifique demandant le scan au réseau mesh
      command = "AT+SCAN_MESH\n"
      self.serial_conn.write(command.encode("utf-8"))
      self.log_terminal(
          "[COMMANDE] Envoi de la demande de scan du réseau mesh...\n"
      )
      # Réinitialisation temporaire de l'alerte ou affichage d'un statut
      self.alert_banner.config(
          text="STATUT: Scan du réseau mesh en cours...", bg="orange"
      )

  def stop_network_scan(self):
        if self.serial_conn and self.serial_conn.is_open:
          self.log_terminal(
              "[COMMANDE] Arrêt du scan...\n"
          )
          self.alert_banner.config(
              text="STATUT: Aucun problème détecté", bg="green"
          )

  def save_terminal_history(self):
    # Récupère tout le texte actuellement affiché dans le terminal
    content = self.terminal_text.get("1.0", tk.END)

    if not content.strip():
      messagebox.showwarning(
          "Attention", "Le terminal est vide, aucun historique à sauvegarder."
      )
      return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")],
        title="Sauvegarder l'historique des trames sous...",
    )
    if file_path:
      try:
        with open(file_path, "w", encoding="utf-8") as f:
          f.write(content)
        self.log_terminal(
            f"[SYSTÈME] Historique complet sauvegardé dans : {file_path}\n"
        )
      except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'enregistrer le fichier :\n{e}")

  def log_terminal(self, text):
    self.terminal_text.insert(tk.END, text)
    self.terminal_text.see(tk.END)

  def clear_terminal(self):
    self.terminal_text.delete("1.0", tk.END)


if __name__ == "__main__":
  root = tk.Tk()
  app = MeshMonitorApp(root)
  root.mainloop()