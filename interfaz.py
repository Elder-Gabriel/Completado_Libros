import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os, sys
from PIL import Image, ImageTk
from main import generar_libro

class GeneradorLibrosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Libros TEI")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
        self.root.configure(bg="#f5f5f5")
        self.ruta_pdf = None

        # Icono (solo si existe)
        try:
            icono = self._ruta_recurso("assets/book_icon.ico")
            self.root.iconbitmap(icono)
        except:
            pass

        self._crear_ui()

    def _ruta_recurso(self, rel):
        if getattr(sys, "frozen", False):
            base = sys._MEIPASS
        else:
            base = os.path.dirname(__file__)
        return os.path.join(base, rel)

    def _crear_ui(self):
        # Banner
        frame_banner = ttk.Frame(self.root)
        frame_banner.pack(pady=20)
        try:
            logo = Image.open(self._ruta_recurso("assets/logo_tei.png"))
            logo = logo.resize((60,60), Image.LANCZOS)
            img = ImageTk.PhotoImage(logo)
            lbl = tk.Label(frame_banner, image=img, bg="#f5f5f5")
            lbl.image = img
            lbl.pack(side=tk.LEFT, padx=10)
        except:
            pass
        tk.Label(frame_banner, text="Generador TEI",
                 font=("Segoe UI", 18, "bold"), bg="#f5f5f5").pack(side=tk.LEFT)

        # Formulario
        form = ttk.LabelFrame(self.root, text="Detalles del libro", padding=15)
        form.pack(fill=tk.X, padx=20, pady=10)

        lbl_cfg = {'font':("Segoe UI",10)}
        ttk.Label(form, text="Título:", **lbl_cfg).grid(row=0,column=0,sticky=tk.W,pady=5)
        self.entry_titulo = ttk.Entry(form, width=40); self.entry_titulo.grid(row=0,column=1,padx=5)

        ttk.Label(form, text="Público:", **lbl_cfg).grid(row=1,column=0,sticky=tk.W,pady=5)
        self.publico = tk.StringVar(value="Niños")
        self.cb_publico = ttk.Combobox(form, textvariable=self.publico,
                                       values=["Niños","Jóvenes","Adultos"], state="readonly")
        self.cb_publico.grid(row=1,column=1,padx=5)

        ttk.Label(form, text="Edad sugerida:", **lbl_cfg).grid(row=2,column=0,sticky=tk.W,pady=5)
        self.entry_edad = ttk.Entry(form, width=40); self.entry_edad.grid(row=2,column=1,padx=5)

        # Guardado personalizado
        opts = ttk.LabelFrame(self.root, text="Opciones", padding=15)
        opts.pack(fill=tk.X, padx=20, pady=(0,10))
        self.var_guardar = tk.BooleanVar()
        ttk.Checkbutton(opts, text="Guardar en ruta personalizada",
                        variable=self.var_guardar, command=self._toggle_ruta).grid(row=0,column=0,sticky=tk.W)
        self.frame_ruta = ttk.Frame(opts); self.frame_ruta.grid(row=1,column=0,sticky=tk.EW,pady=5)
        self.frame_ruta.grid_remove()
        self.entry_ruta = ttk.Entry(self.frame_ruta); self.entry_ruta.pack(side=tk.LEFT,expand=True,fill=tk.X)
        ttk.Button(self.frame_ruta, text="Examinar…", command=self._sel_ruta).pack(side=tk.RIGHT)

        # Estado y botones
        self.lbl_estado = ttk.Label(self.root, text="", font=("Segoe UI",9,"italic"), background="#f5f5f5")
        self.lbl_estado.pack(pady=(0,10))
        btn_frame = ttk.Frame(self.root); btn_frame.pack(pady=10)
        style = ttk.Style(); style.configure("Accent.TButton", font=("Segoe UI",10,"bold"))
        self.btn_gen = ttk.Button(btn_frame, text="Generar Libro",
                                  style="Accent.TButton", command=self._on_generar)
        self.btn_gen.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5)
        self.btn_open = ttk.Button(btn_frame, text="Abrir PDF", state=tk.DISABLED,
                                   command=self._on_abrir)
        self.btn_open.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5)

    def _toggle_ruta(self):
        if self.var_guardar.get():
            self.frame_ruta.grid()
        else:
            self.frame_ruta.grid_remove(); self.entry_ruta.delete(0,tk.END)

    def _sel_ruta(self):
        nombre = (self.entry_titulo.get() or "libro").lower().replace(" ","_")+".pdf"
        path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                            filetypes=[("PDF","*.pdf")],
                                            initialfile=nombre)
        if path: self.entry_ruta.delete(0,tk.END); self.entry_ruta.insert(0,path)

    def _on_generar(self):
        tit = self.entry_titulo.get().strip(); pub = self.publico.get(); ed = self.entry_edad.get().strip()
        if not tit or not ed:
            messagebox.showerror("Error","Título y edad obligatorios."); return
        ruta = self.entry_ruta.get().strip() if self.var_guardar.get() else None

        self.lbl_estado.config(text="Generando…"); self.btn_gen.config(state=tk.DISABLED); self.root.update()
        try:
            self.ruta_pdf = generar_libro(tit, pub, ed, ruta)
            self.lbl_estado.config(text=f"Generado: {os.path.basename(self.ruta_pdf)}")
            self.btn_open.config(state=tk.NORMAL)
            messagebox.showinfo("Listo","¡Libro generado correctamente!")
        except Exception as e:
            self.lbl_estado.config(text="Error."); messagebox.showerror("Error",str(e))
        finally:
            self.btn_gen.config(state=tk.NORMAL)

    def _on_abrir(self):
        if self.ruta_pdf and os.path.exists(self.ruta_pdf):
            try: os.startfile(self.ruta_pdf)
            except:
                import subprocess
                if sys.platform=="darwin": subprocess.call(["open",self.ruta_pdf])
                else: subprocess.call(["xdg-open",self.ruta_pdf])
        else:
            messagebox.showerror("Error","No se encontró el PDF.")

if __name__ == "__main__":
    root = tk.Tk()
    app = GeneradorLibrosApp(root)
    root.mainloop()