
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import json
from datetime import datetime

class KRSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistem KRS Mahasiswa - Universitas")
        self.root.geometry("900x700")
        
        # Setup database
        self.setup_database()
        
        # Load mata kuliah data
        self.load_mata_kuliah_data()
        
        # Create GUI
        self.create_widgets()
        
        # Load initial data
        self.refresh_mahasiswa_list()
        self.refresh_mata_kuliah_list()

    def setup_database(self):
        """Setup SQLite database dan tabel-tabel yang diperlukan"""
        self.conn = sqlite3.connect('krs_database.db')
        self.cursor = self.conn.cursor()
        
        # Tabel mahasiswa
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS mahasiswa (
                nim TEXT PRIMARY KEY,
                nama TEXT NOT NULL,
                jurusan TEXT NOT NULL,
                semester INTEGER NOT NULL,
                max_sks INTEGER DEFAULT 24
            )
        """)
        
        # Tabel mata kuliah
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS mata_kuliah (
                kode_mk TEXT PRIMARY KEY,
                nama_mk TEXT NOT NULL,
                sks INTEGER NOT NULL,
                dosen TEXT NOT NULL,
                jadwal TEXT NOT NULL,
                ruang TEXT NOT NULL,
                kapasitas INTEGER NOT NULL,
                terisi INTEGER DEFAULT 0
            )
        """)
        
        # Tabel KRS
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS krs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nim TEXT NOT NULL,
                kode_mk TEXT NOT NULL,
                tanggal_ambil TEXT NOT NULL,
                status TEXT DEFAULT 'Aktif',
                FOREIGN KEY (nim) REFERENCES mahasiswa (nim),
                FOREIGN KEY (kode_mk) REFERENCES mata_kuliah (kode_mk),
                UNIQUE(nim, kode_mk)
            )
        """)
        
        self.conn.commit()

    def load_mata_kuliah_data(self):
        """Load data mata kuliah dari JSON dan insert ke database"""
        mata_kuliah_data = [
            {"kode_mk": "TI101", "nama_mk": "Algoritma dan Pemrograman", "sks": 3, "dosen": "Dr. Ahmad", "jadwal": "Senin 08:00-10:00", "ruang": "Lab A", "kapasitas": 40},
            {"kode_mk": "TI102", "nama_mk": "Struktur Data", "sks": 3, "dosen": "Prof. Budi", "jadwal": "Selasa 10:00-12:00", "ruang": "Lab B", "kapasitas": 35},
            {"kode_mk": "TI103", "nama_mk": "Basis Data", "sks": 3, "dosen": "Dr. Citra", "jadwal": "Rabu 13:00-15:00", "ruang": "Lab C", "kapasitas": 30},
            {"kode_mk": "TI104", "nama_mk": "Jaringan Komputer", "sks": 3, "dosen": "Prof. Dedi", "jadwal": "Kamis 08:00-10:00", "ruang": "Lab D", "kapasitas": 25},
            {"kode_mk": "TI105", "nama_mk": "Sistem Operasi", "sks": 3, "dosen": "Dr. Eka", "jadwal": "Jumat 10:00-12:00", "ruang": "Lab E", "kapasitas": 30},
            {"kode_mk": "TI106", "nama_mk": "Pemrograman Web", "sks": 2, "dosen": "Prof. Fajar", "jadwal": "Senin 13:00-15:00", "ruang": "Lab F", "kapasitas": 40},
            {"kode_mk": "TI107", "nama_mk": "Kecerdasan Buatan", "sks": 3, "dosen": "Dr. Gita", "jadwal": "Selasa 15:00-17:00", "ruang": "Lab G", "kapasitas": 20},
            {"kode_mk": "TI108", "nama_mk": "Grafika Komputer", "sks": 2, "dosen": "Prof. Hadi", "jadwal": "Rabu 08:00-10:00", "ruang": "Lab H", "kapasitas": 25}
        ]
        
        # Insert data jika belum ada
        for mk in mata_kuliah_data:
            self.cursor.execute("SELECT COUNT(*) FROM mata_kuliah WHERE kode_mk = ?", (mk["kode_mk"],))
            if self.cursor.fetchone()[0] == 0:
                self.cursor.execute("""
                    INSERT INTO mata_kuliah (kode_mk, nama_mk, sks, dosen, jadwal, ruang, kapasitas)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (mk["kode_mk"], mk["nama_mk"], mk["sks"], mk["dosen"], mk["jadwal"], mk["ruang"], mk["kapasitas"]))
        
        self.conn.commit()

    def create_widgets(self):
        """Membuat tampilan GUI"""
        # Main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Data Mahasiswa
        self.create_mahasiswa_tab()
        
        # Tab 2: Data Mata Kuliah
        self.create_mata_kuliah_tab()
        
        # Tab 3: KRS Management
        self.create_krs_tab()

    def create_mahasiswa_tab(self):
        """Tab untuk mengelola data mahasiswa"""
        mhs_frame = ttk.Frame(self.notebook)
        self.notebook.add(mhs_frame, text="📚 Data Mahasiswa")
        
        # Input frame
        input_frame = ttk.LabelFrame(mhs_frame, text="✏️ Isi Data Mahasiswa")
        input_frame.pack(fill='x', padx=10, pady=5)
        
        # NIM
        ttk.Label(input_frame, text="NIM:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.nim_entry = ttk.Entry(input_frame)
        self.nim_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        # Nama
        ttk.Label(input_frame, text="Nama:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.nama_entry = ttk.Entry(input_frame)
        self.nama_entry.grid(row=0, column=3, padx=5, pady=5, sticky='ew')
        
        # Jurusan
        ttk.Label(input_frame, text="Jurusan:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.jurusan_var = tk.StringVar()
        jurusan_combo = ttk.Combobox(input_frame, textvariable=self.jurusan_var, 
                                   values=["Teknik Informatika", "Sistem Informasi", "Teknik Komputer"])
        jurusan_combo.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        # Semester
        ttk.Label(input_frame, text="Semester:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.semester_var = tk.StringVar()
        semester_combo = ttk.Combobox(input_frame, textvariable=self.semester_var,
                                    values=["1", "2", "3", "4", "5", "6", "7", "8"])
        semester_combo.grid(row=1, column=3, padx=5, pady=5, sticky='ew')
        
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)
        
        # Buttons
        btn_frame = ttk.Frame(mhs_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(btn_frame, text="➕ Tambah", command=self.tambah_mahasiswa).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="✏️ Update", command=self.update_mahasiswa).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🗑️ Hapus", command=self.hapus_mahasiswa).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🧹 Bersihkan", command=self.clear_mahasiswa_form).pack(side='left', padx=5)
        
        # Treeview for displaying data
        tree_frame = ttk.Frame(mhs_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('NIM', 'Nama', 'Jurusan', 'Semester', 'Max SKS')
        self.mahasiswa_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        for col in columns:
            self.mahasiswa_tree.heading(col, text=col)
            self.mahasiswa_tree.column(col, width=100)
        
        scrollbar_mhs = ttk.Scrollbar(tree_frame, orient='vertical', command=self.mahasiswa_tree.yview)
        self.mahasiswa_tree.configure(yscrollcommand=scrollbar_mhs.set)
        
        self.mahasiswa_tree.pack(side='left', fill='both', expand=True)
        scrollbar_mhs.pack(side='right', fill='y')
        
        self.mahasiswa_tree.bind('<<TreeviewSelect>>', self.select_mahasiswa)

    def create_mata_kuliah_tab(self):
        """Tab untuk mengelola data mata kuliah"""
        mk_frame = ttk.Frame(self.notebook)
        self.notebook.add(mk_frame, text="📖 Daftar Mata Kuliah")
        
        # Treeview for displaying mata kuliah
        tree_frame = ttk.Frame(mk_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ('Kode MK', 'Nama Mata Kuliah', 'SKS', 'Dosen Pengampu', 'Jadwal', 'Ruang', 'Kapasitas', 'Terisi')
        self.mk_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        for col in columns:
            self.mk_tree.heading(col, text=col)
            if col in ['Kode MK', 'SKS', 'Kapasitas', 'Terisi']:
                self.mk_tree.column(col, width=80)
            else:
                self.mk_tree.column(col, width=120)
        
        scrollbar_mk = ttk.Scrollbar(tree_frame, orient='vertical', command=self.mk_tree.yview)
        self.mk_tree.configure(yscrollcommand=scrollbar_mk.set)
        
        self.mk_tree.pack(side='left', fill='both', expand=True)
        scrollbar_mk.pack(side='right', fill='y')

    def create_krs_tab(self):
        """Tab untuk mengelola KRS"""
        krs_frame = ttk.Frame(self.notebook)
        self.notebook.add(krs_frame, text="📝 Pengisian KRS")
        
        # Selection frame
        select_frame = ttk.LabelFrame(krs_frame, text="👤 Pilih Mahasiswa")
        select_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(select_frame, text="Mahasiswa:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.mahasiswa_krs_var = tk.StringVar()
        self.mahasiswa_combo = ttk.Combobox(select_frame, textvariable=self.mahasiswa_krs_var, width=50)
        self.mahasiswa_combo.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.mahasiswa_combo.bind('<<ComboboxSelected>>', self.on_mahasiswa_selected)
        
        select_frame.columnconfigure(1, weight=1)
        
        # Info frame
        self.info_frame = ttk.LabelFrame(krs_frame, text="📊 Info KRS")
        self.info_frame.pack(fill='x', padx=10, pady=5)
        
        self.info_label = ttk.Label(self.info_frame, text="Silakan pilih mahasiswa dulu ya untuk melihat info KRS 😊")
        self.info_label.pack(padx=10, pady=10)
        
        # Available courses frame
        available_frame = ttk.LabelFrame(krs_frame, text="📚 Mata Kuliah yang Bisa Diambil")
        available_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Available courses treeview
        av_tree_frame = ttk.Frame(available_frame)
        av_tree_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        av_columns = ('Kode MK', 'Nama Mata Kuliah', 'SKS', 'Dosen', 'Jadwal', 'Ruang', 'Slot Tersisa')
        self.available_tree = ttk.Treeview(av_tree_frame, columns=av_columns, show='headings', height=8)
        
        for col in av_columns:
            self.available_tree.heading(col, text=col)
            if col in ['Kode MK', 'SKS', 'Slot Tersisa']:
                self.available_tree.column(col, width=80)
            else:
                self.available_tree.column(col, width=120)
        
        scrollbar_av = ttk.Scrollbar(av_tree_frame, orient='vertical', command=self.available_tree.yview)
        self.available_tree.configure(yscrollcommand=scrollbar_av.set)
        
        self.available_tree.pack(side='left', fill='both', expand=True)
        scrollbar_av.pack(side='right', fill='y')
        
        # Buttons for KRS actions
        krs_btn_frame = ttk.Frame(available_frame)
        krs_btn_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(krs_btn_frame, text="✅ Ambil Mata Kuliah", command=self.ambil_mata_kuliah).pack(side='left', padx=5)
        ttk.Button(krs_btn_frame, text="❌ Batal Ambil", command=self.batal_ambil_mata_kuliah).pack(side='left', padx=5)
        ttk.Button(krs_btn_frame, text="🔄 Refresh", command=self.refresh_available_courses).pack(side='left', padx=5)
        
        # Current KRS frame
        current_frame = ttk.LabelFrame(krs_frame, text="📋 KRS yang Sudah Diambil")
        current_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        curr_tree_frame = ttk.Frame(current_frame)
        curr_tree_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        curr_columns = ('Kode MK', 'Nama Mata Kuliah', 'SKS', 'Dosen', 'Jadwal', 'Status')
        self.current_krs_tree = ttk.Treeview(curr_tree_frame, columns=curr_columns, show='headings', height=6)
        
        for col in curr_columns:
            self.current_krs_tree.heading(col, text=col)
            if col in ['Kode MK', 'SKS']:
                self.current_krs_tree.column(col, width=80)
            else:
                self.current_krs_tree.column(col, width=120)
        
        scrollbar_curr = ttk.Scrollbar(curr_tree_frame, orient='vertical', command=self.current_krs_tree.yview)
        self.current_krs_tree.configure(yscrollcommand=scrollbar_curr.set)
        
        self.current_krs_tree.pack(side='left', fill='both', expand=True)
        scrollbar_curr.pack(side='right', fill='y')

    # Mahasiswa management functions
    def tambah_mahasiswa(self):
        nim = self.nim_entry.get().strip()
        nama = self.nama_entry.get().strip()
        jurusan = self.jurusan_var.get()
        semester = self.semester_var.get()
        
        if not all([nim, nama, jurusan, semester]):
            messagebox.showwarning("Oops!", "Mohon isi semua data dulu ya 😅")
            return
        
        try:
            self.cursor.execute("""
                INSERT INTO mahasiswa (nim, nama, jurusan, semester)
                VALUES (?, ?, ?, ?)
            """, (nim, nama, jurusan, int(semester)))
            self.conn.commit()
            messagebox.showinfo("Berhasil! 🎉", "Data mahasiswa sudah ditambahkan nih!")
            self.clear_mahasiswa_form()
            self.refresh_mahasiswa_list()
        except sqlite3.IntegrityError:
            messagebox.showerror("Ups!", "NIM ini sudah ada di sistem 😔")
        except Exception as e:
            messagebox.showerror("Error", f"Aduh ada masalah nih: {str(e)}")

    def update_mahasiswa(self):
        selected = self.mahasiswa_tree.selection()
        if not selected:
            messagebox.showwarning("Pilih dulu ya", "Klik mahasiswa yang mau diupdate dulu 😊")
            return
        
        nim = self.nim_entry.get().strip()
        nama = self.nama_entry.get().strip()
        jurusan = self.jurusan_var.get()
        semester = self.semester_var.get()
        
        if not all([nim, nama, jurusan, semester]):
            messagebox.showwarning("Oops!", "Mohon isi semua data dulu ya 😅")
            return
        
        try:
            self.cursor.execute("""
                UPDATE mahasiswa SET nama=?, jurusan=?, semester=?
                WHERE nim=?
            """, (nama, jurusan, int(semester), nim))
            self.conn.commit()
            messagebox.showinfo("Berhasil! 🎉", "Data mahasiswa sudah diupdate!")
            self.clear_mahasiswa_form()
            self.refresh_mahasiswa_list()
        except Exception as e:
            messagebox.showerror("Error", f"Aduh ada masalah nih: {str(e)}")

    def hapus_mahasiswa(self):
        selected = self.mahasiswa_tree.selection()
        if not selected:
            messagebox.showwarning("Pilih dulu ya", "Klik mahasiswa yang mau dihapus dulu 😊")
            return
        
        item = self.mahasiswa_tree.item(selected)
        nim = item['values'][0]
        
        if messagebox.askyesno("Yakin nih?", f"Mau hapus mahasiswa dengan NIM {nim}? Datanya akan hilang lho 😰"):
            try:
                # Hapus KRS terlebih dahulu
                self.cursor.execute("DELETE FROM krs WHERE nim=?", (nim,))
                # Hapus mahasiswa
                self.cursor.execute("DELETE FROM mahasiswa WHERE nim=?", (nim,))
                self.conn.commit()
                messagebox.showinfo("Berhasil! 🎉", "Data mahasiswa sudah dihapus!")
                self.clear_mahasiswa_form()
                self.refresh_mahasiswa_list()
            except Exception as e:
                messagebox.showerror("Error", f"Aduh ada masalah nih: {str(e)}")

    def clear_mahasiswa_form(self):
        self.nim_entry.delete(0, tk.END)
        self.nama_entry.delete(0, tk.END)
        self.jurusan_var.set('')
        self.semester_var.set('')

    def select_mahasiswa(self, event):
        selected = self.mahasiswa_tree.selection()
        if selected:
            item = self.mahasiswa_tree.item(selected)
            values = item['values']
            
            self.nim_entry.delete(0, tk.END)
            self.nim_entry.insert(0, values[0])
            self.nama_entry.delete(0, tk.END)
            self.nama_entry.insert(0, values[1])
            self.jurusan_var.set(values[2])
            self.semester_var.set(values[3])

    def refresh_mahasiswa_list(self):
        # Clear treeview
        for item in self.mahasiswa_tree.get_children():
            self.mahasiswa_tree.delete(item)
        
        # Load data
        self.cursor.execute("SELECT nim, nama, jurusan, semester, max_sks FROM mahasiswa ORDER BY nim")
        for row in self.cursor.fetchall():
            self.mahasiswa_tree.insert('', 'end', values=row)
        
        # Update combo box for KRS
        self.cursor.execute("SELECT nim, nama FROM mahasiswa ORDER BY nim")
        mahasiswa_list = [f"{row[0]} - {row[1]}" for row in self.cursor.fetchall()]
        self.mahasiswa_combo['values'] = mahasiswa_list

    def refresh_mata_kuliah_list(self):
        # Clear treeview
        for item in self.mk_tree.get_children():
            self.mk_tree.delete(item)
        
        # Load data with current enrollment count
        self.cursor.execute("""
            SELECT mk.kode_mk, mk.nama_mk, mk.sks, mk.dosen, mk.jadwal, mk.ruang, 
                   mk.kapasitas, COUNT(krs.kode_mk) as terisi
            FROM mata_kuliah mk
            LEFT JOIN krs ON mk.kode_mk = krs.kode_mk AND krs.status = 'Aktif'
            GROUP BY mk.kode_mk
            ORDER BY mk.kode_mk
        """)
        for row in self.cursor.fetchall():
            self.mk_tree.insert('', 'end', values=row)

    # KRS management functions
    def on_mahasiswa_selected(self, event):
        selected = self.mahasiswa_krs_var.get()
        if selected:
            nim = selected.split(' - ')[0]
            self.current_nim = nim
            self.update_krs_info()
            self.refresh_available_courses()
            self.refresh_current_krs()

    def update_krs_info(self):
        if hasattr(self, 'current_nim'):
            # Get mahasiswa info
            self.cursor.execute("""
                SELECT nama, jurusan, semester, max_sks FROM mahasiswa WHERE nim=?
            """, (self.current_nim,))
            mhs_info = self.cursor.fetchone()
            
            # Get current SKS
            self.cursor.execute("""
                SELECT SUM(mk.sks) FROM krs k
                JOIN mata_kuliah mk ON k.kode_mk = mk.kode_mk
                WHERE k.nim=? AND k.status='Aktif'
            """, (self.current_nim,))
            current_sks = self.cursor.fetchone()[0] or 0
            
            if mhs_info:
                info_text = f"Nama: {mhs_info[0]} | Jurusan: {mhs_info[1]} | Semester: {mhs_info[2]}\n"
                info_text += f"SKS yang sudah diambil: {current_sks} | Batas maksimal: {mhs_info[3]} SKS | Sisa yang bisa diambil: {mhs_info[3] - current_sks} SKS"
                self.info_label.config(text=info_text)

    def refresh_available_courses(self):
        # Clear treeview
        for item in self.available_tree.get_children():
            self.available_tree.delete(item)
        
        if hasattr(self, 'current_nim'):
            # Get available courses (not already taken by student)
            self.cursor.execute("""
                SELECT mk.kode_mk, mk.nama_mk, mk.sks, mk.dosen, mk.jadwal, mk.ruang,
                       (mk.kapasitas - COUNT(krs.kode_mk)) as sisa_kapasitas
                FROM mata_kuliah mk
                LEFT JOIN krs ON mk.kode_mk = krs.kode_mk AND krs.status = 'Aktif'
                WHERE mk.kode_mk NOT IN (
                    SELECT kode_mk FROM krs WHERE nim=? AND status='Aktif'
                )
                GROUP BY mk.kode_mk
                HAVING sisa_kapasitas > 0
                ORDER BY mk.kode_mk
            """, (self.current_nim,))
            
            for row in self.cursor.fetchall():
                self.available_tree.insert('', 'end', values=row)

    def refresh_current_krs(self):
        # Clear treeview
        for item in self.current_krs_tree.get_children():
            self.current_krs_tree.delete(item)
        
        if hasattr(self, 'current_nim'):
            self.cursor.execute("""
                SELECT mk.kode_mk, mk.nama_mk, mk.sks, mk.dosen, mk.jadwal, k.status
                FROM krs k
                JOIN mata_kuliah mk ON k.kode_mk = mk.kode_mk
                WHERE k.nim=?
                ORDER BY mk.kode_mk
            """, (self.current_nim,))
            
            for row in self.cursor.fetchall():
                self.current_krs_tree.insert('', 'end', values=row)

    def ambil_mata_kuliah(self):
        if not hasattr(self, 'current_nim'):
            messagebox.showwarning("Pilih dulu ya", "Pilih mahasiswa dulu sebelum ambil mata kuliah 😊")
            return
        
        selected = self.available_tree.selection()
        if not selected:
            messagebox.showwarning("Pilih dulu ya", "Klik mata kuliah yang mau diambil dulu 😊")
            return
        
        item = self.available_tree.item(selected)
        kode_mk = item['values'][0]
        sks_mk = item['values'][2]
        
        # Check current SKS
        self.cursor.execute("""
            SELECT SUM(mk.sks) FROM krs k
            JOIN mata_kuliah mk ON k.kode_mk = mk.kode_mk
            WHERE k.nim=? AND k.status='Aktif'
        """, (self.current_nim,))
        current_sks = self.cursor.fetchone()[0] or 0
        
        # Get max SKS
        self.cursor.execute("SELECT max_sks FROM mahasiswa WHERE nim=?", (self.current_nim,))
        max_sks = self.cursor.fetchone()[0]
        
        if current_sks + sks_mk > max_sks:
            messagebox.showwarning("Waduh!", f"Kalau ambil mata kuliah ini SKS kamu akan melebihi batas maksimal ({max_sks} SKS) lho! 😅")
            return
        
        try:
            # Add to KRS
            tanggal_ambil = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute("""
                INSERT INTO krs (nim, kode_mk, tanggal_ambil, status)
                VALUES (?, ?, ?, 'Aktif')
            """, (self.current_nim, kode_mk, tanggal_ambil))
            
            self.conn.commit()
            messagebox.showinfo("Berhasil! 🎉", f"Mata kuliah {kode_mk} berhasil diambil! Semangat belajarnya ya! 💪")
            
            # Refresh views
            self.update_krs_info()
            self.refresh_available_courses()
            self.refresh_current_krs()
            self.refresh_mata_kuliah_list()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Ups!", "Mata kuliah ini sudah kamu ambil sebelumnya 😅")
        except Exception as e:
            messagebox.showerror("Error", f"Aduh ada masalah nih: {str(e)}")

    def batal_ambil_mata_kuliah(self):
        if not hasattr(self, 'current_nim'):
            messagebox.showwarning("Pilih dulu ya", "Pilih mahasiswa dulu sebelum batal ambil mata kuliah 😊")
            return
        
        selected = self.current_krs_tree.selection()
        if not selected:
            messagebox.showwarning("Pilih dulu ya", "Klik mata kuliah yang mau dibatalkan dulu 😊")
            return
        
        item = self.current_krs_tree.item(selected)
        kode_mk = item['values'][0]
        
        if messagebox.askyesno("Yakin nih?", f"Mau batalkan mata kuliah {kode_mk}? Nanti harus daftar ulang lho kalau berubah pikiran 😔"):
            try:
                self.cursor.execute("""
                    DELETE FROM krs WHERE nim=? AND kode_mk=?
                """, (self.current_nim, kode_mk))
                
                self.conn.commit()
                messagebox.showinfo("Berhasil! 🎉", f"Mata kuliah {kode_mk} berhasil dibatalkan!")
                
                # Refresh views
                self.update_krs_info()
                self.refresh_available_courses()
                self.refresh_current_krs()
                self.refresh_mata_kuliah_list()
                
            except Exception as e:
                messagebox.showerror("Error", f"Aduh ada masalah nih: {str(e)}")

    def __del__(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = KRSApp(root)
    root.mainloop()
