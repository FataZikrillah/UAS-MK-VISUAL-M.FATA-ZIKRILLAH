
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import json
from datetime import datetime

class KRSAppFataZikrillah:
    def __init__(self, root):
        # Inisialisasi jendela utama aplikasi KRS
        self.root = root
        self.root.title("🎓 KRS Digital - Fata Zikrillah's Edition")
        self.root.geometry("1000x750")
        # Menggunakan warna putih lembut sebagai background utama
        self.root.configure(bg='#f8fafc')  

        # Setup tema dan style untuk aplikasi
        self.setup_styles()

        # Setup database SQLite untuk menyimpan data
        self.setup_database()

        # Load data mata kuliah dari array ke database
        self.load_mata_kuliah_data()

        # Membuat semua widget GUI
        self.create_widgets()

        # Load data awal ke dalam tabel
        self.refresh_mahasiswa_list()
        self.refresh_mata_kuliah_list()

    def setup_styles(self):
        """Setup tema warna putih lembut yang elegan dan modern"""
        style = ttk.Style()
        style.theme_use('clam')

        # Style untuk Notebook (tab container) - putih dengan aksen abu-abu lembut
        style.configure('Custom.TNotebook', background='#ffffff')
        style.configure('Custom.TNotebook.Tab', 
                       background='#e2e8f0', foreground='#334155',
                       padding=[20, 10], font=('Arial', 10, 'bold'))
        # Efek hover dan selected pada tab
        style.map('Custom.TNotebook.Tab',
                  background=[('selected', '#ffffff')],
                  foreground=[('selected', '#1e293b')])

        # Style untuk LabelFrame - frame dengan border dan label
        style.configure('White.TLabelframe', 
                       background='#ffffff', foreground='#475569',
                       borderwidth=2, relief='solid')
        style.configure('White.TLabelframe.Label', 
                       background='#ffffff', foreground='#475569',
                       font=('Arial', 11, 'bold'))

        # Style untuk Button - tombol dengan warna putih dan border
        style.configure('White.TButton',
                       background='#ffffff', foreground='#475569',
                       font=('Arial', 9, 'bold'), padding=10,
                       borderwidth=1, relief='solid')
        # Efek hover pada button
        style.map('White.TButton',
                  background=[('active', '#f1f5f9')])

    def setup_database(self):
        """Setup database SQLite dan membuat tabel-tabel yang diperlukan"""
        # Membuat koneksi ke database SQLite
        self.conn = sqlite3.connect('krs_database.db')
        self.cursor = self.conn.cursor()

        # Membuat tabel mahasiswa untuk menyimpan data mahasiswa
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS mahasiswa (
                nim TEXT PRIMARY KEY,
                nama TEXT NOT NULL,
                jurusan TEXT NOT NULL,
                semester INTEGER NOT NULL,
                max_sks INTEGER DEFAULT 24
            )
        """)

        # Membuat tabel mata_kuliah untuk menyimpan daftar mata kuliah
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

        # Membuat tabel krs untuk menyimpan data pengambilan mata kuliah mahasiswa
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

        # Menyimpan perubahan ke database
        self.conn.commit()

    def load_mata_kuliah_data(self):
        """Load data mata kuliah dari array dan insert ke database jika belum ada"""
        # Data mata kuliah dalam bentuk array
        mata_kuliah_data = [
            {"kode_mk": "TI101", "nama_mk": "Algoritma dan Pemrograman", "sks": 3, "dosen": "Dr. Ahmad", "jadwal": "Senin 08:00-10:00", "ruang": "Lab A", "kapasitas": 40},
            {"kode_mk": "TI102", "nama_mk": "Struktur Data", "sks": 3, "dosen": "Prof. Budi", "jadwal": "Selasa 10:00-12:00", "ruang": "Lab B", "kapasitas": 35},
            {"kode_mk": "TI103", "nama_mk": "Basis Data", "sks": 3, "dosen": "Dr. Citra", "jadwal": "Rabu 13:00-15:00", "ruang": "Lab C", "kapasitas": 30},
            {"kode_mk": "TI104", "nama_mk": "Jaringan Komputer", "sks": 3, "dosen": "Prof. Dedi", "jadwal": "Kamis 08:00-10:00", "ruang": "Lab D", "kapasitas": 25},
            {"kode_mk": "TI105", "nama_mk": "Sistem Operasi", "sks": 3, "dosen": "Dr. Eka", "jadwal": "Jumat 10:00-12:00", "ruang": "Lab E", "kapasitas": 30},
            {"kode_mk": "TI106", "nama_mk": "Pemrograman Web", "sks": 2, "dosen": "Prof. Fata Zikrillah", "jadwal": "Senin 13:00-15:00", "ruang": "Lab F", "kapasitas": 40},
            {"kode_mk": "TI107", "nama_mk": "Kecerdasan Buatan", "sks": 3, "dosen": "Dr. Gita", "jadwal": "Selasa 15:00-17:00", "ruang": "Lab G", "kapasitas": 20},
            {"kode_mk": "TI108", "nama_mk": "Grafika Komputer", "sks": 2, "dosen": "Prof. Hadi", "jadwal": "Rabu 08:00-10:00", "ruang": "Lab H", "kapasitas": 25}
        ]

        # Loop untuk memasukkan data mata kuliah ke database
        for mk in mata_kuliah_data:
            # Cek apakah data sudah ada
            self.cursor.execute("SELECT COUNT(*) FROM mata_kuliah WHERE kode_mk = ?", (mk["kode_mk"],))
            if self.cursor.fetchone()[0] == 0:
                # Insert data jika belum ada
                self.cursor.execute("""
                    INSERT INTO mata_kuliah (kode_mk, nama_mk, sks, dosen, jadwal, ruang, kapasitas)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (mk["kode_mk"], mk["nama_mk"], mk["sks"], mk["dosen"], mk["jadwal"], mk["ruang"], mk["kapasitas"]))

        # Simpan perubahan ke database
        self.conn.commit()

    def create_widgets(self):
        """Membuat tampilan GUI dengan tema putih lembut yang elegan"""
        # Frame header dengan background putih dan shadow effect
        header_frame = tk.Frame(self.root, bg='#ffffff', height=80, relief='solid', borderwidth=1)
        header_frame.pack(fill='x', padx=10, pady=10)
        header_frame.pack_propagate(False)

        # Label judul aplikasi dengan font yang elegan
        title_label = tk.Label(header_frame, text="🚀 SISTEM KRS DIGITAL - FATA ZIKRILLAH EDITION", 
                              font=('Arial', 20, 'bold'), 
                              bg='#ffffff', fg='#1e293b')
        title_label.pack(expand=True)

        # Notebook utama untuk tab dengan style custom putih
        self.notebook = ttk.Notebook(self.root, style='Custom.TNotebook')
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)

        # Membuat tab untuk data mahasiswa
        self.create_mahasiswa_tab()

        # Membuat tab untuk data mata kuliah
        self.create_mata_kuliah_tab()

        # Membuat tab untuk management KRS
        self.create_krs_tab()

    def create_mahasiswa_tab(self):
        """Tab untuk mengelola data mahasiswa dengan tema putih lembut"""
        # Frame utama tab mahasiswa
        mhs_frame = tk.Frame(self.notebook, bg='#ffffff')
        self.notebook.add(mhs_frame, text="👨‍🎓 DATA MAHASISWA")

        # Frame input dengan border dan background putih
        input_frame = ttk.LabelFrame(mhs_frame, text="💫 Input Data Mahasiswa Baru", style='White.TLabelframe')
        input_frame.pack(fill='x', padx=15, pady=10)

        # Input field untuk NIM mahasiswa
        tk.Label(input_frame, text="NIM:", font=('Arial', 10, 'bold'), 
                bg='#ffffff', fg='#475569').grid(row=0, column=0, padx=10, pady=8, sticky='w')
        self.nim_entry = tk.Entry(input_frame, font=('Arial', 10), bg='#f8fafc', fg='#1e293b', width=15)
        self.nim_entry.grid(row=0, column=1, padx=5, pady=8, sticky='ew')

        # Input field untuk nama mahasiswa
        tk.Label(input_frame, text="Nama Lengkap:", font=('Arial', 10, 'bold'), 
                bg='#ffffff', fg='#475569').grid(row=0, column=2, padx=10, pady=8, sticky='w')
        self.nama_entry = tk.Entry(input_frame, font=('Arial', 10), bg='#f8fafc', fg='#1e293b', width=25)
        self.nama_entry.grid(row=0, column=3, padx=5, pady=8, sticky='ew')

        # Dropdown untuk memilih jurusan
        tk.Label(input_frame, text="Program Studi:", font=('Arial', 10, 'bold'), 
                bg='#ffffff', fg='#475569').grid(row=1, column=0, padx=10, pady=8, sticky='w')
        self.jurusan_var = tk.StringVar()
        jurusan_combo = ttk.Combobox(input_frame, textvariable=self.jurusan_var, 
                                   values=["Teknik Informatika", "Sistem Informasi", "Teknik Komputer"],
                                   font=('Arial', 10), width=18)
        jurusan_combo.grid(row=1, column=1, padx=5, pady=8, sticky='ew')

        # Dropdown untuk memilih semester
        tk.Label(input_frame, text="Semester:", font=('Arial', 10, 'bold'), 
                bg='#ffffff', fg='#475569').grid(row=1, column=2, padx=10, pady=8, sticky='w')
        self.semester_var = tk.StringVar()
        semester_combo = ttk.Combobox(input_frame, textvariable=self.semester_var,
                                    values=["1", "2", "3", "4", "5", "6", "7", "8"],
                                    font=('Arial', 10), width=8)
        semester_combo.grid(row=1, column=3, padx=5, pady=8, sticky='w')

        # Konfigurasi grid untuk responsive layout
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=2)

        # Frame untuk tombol-tombol aksi
        btn_frame = tk.Frame(mhs_frame, bg='#ffffff')
        btn_frame.pack(fill='x', padx=15, pady=10)

        # Tombol untuk menambah data mahasiswa
        ttk.Button(btn_frame, text="🚀 Tambah Data", command=self.tambah_mahasiswa, style='White.TButton').pack(side='left', padx=5)
        # Tombol untuk mengupdate data mahasiswa
        ttk.Button(btn_frame, text="✨ Update Data", command=self.update_mahasiswa, style='White.TButton').pack(side='left', padx=5)
        # Tombol untuk menghapus data mahasiswa
        ttk.Button(btn_frame, text="🗑️ Hapus Data", command=self.hapus_mahasiswa, style='White.TButton').pack(side='left', padx=5)
        # Tombol untuk reset form input
        ttk.Button(btn_frame, text="🧹 Reset Form", command=self.clear_mahasiswa_form, style='White.TButton').pack(side='left', padx=5)

        # Frame untuk tabel data mahasiswa
        tree_frame = tk.Frame(mhs_frame, bg='#ffffff')
        tree_frame.pack(fill='both', expand=True, padx=15, pady=10)

        # Definisi kolom untuk tabel mahasiswa
        columns = ('NIM', 'Nama Mahasiswa', 'Program Studi', 'Semester', 'Batas SKS')
        self.mahasiswa_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=12)

        # Setup header dan lebar kolom
        for col in columns:
            self.mahasiswa_tree.heading(col, text=col)
            self.mahasiswa_tree.column(col, width=120)

        # Scrollbar untuk tabel mahasiswa
        scrollbar_mhs = ttk.Scrollbar(tree_frame, orient='vertical', command=self.mahasiswa_tree.yview)
        self.mahasiswa_tree.configure(yscrollcommand=scrollbar_mhs.set)

        # Pack tabel dan scrollbar
        self.mahasiswa_tree.pack(side='left', fill='both', expand=True)
        scrollbar_mhs.pack(side='right', fill='y')

        # Event handler ketika item di tabel diklik
        self.mahasiswa_tree.bind('<<TreeviewSelect>>', self.select_mahasiswa)

    def create_mata_kuliah_tab(self):
        """Tab untuk mengelola data mata kuliah dengan tema putih lembut"""
        # Frame utama tab mata kuliah
        mk_frame = tk.Frame(self.notebook, bg='#ffffff')
        self.notebook.add(mk_frame, text="📚 DAFTAR MATA KULIAH")

        # Header info dengan background putih dan border
        info_frame = tk.Frame(mk_frame, bg='#f8fafc', height=60, relief='solid', borderwidth=1)
        info_frame.pack(fill='x', padx=15, pady=10)
        info_frame.pack_propagate(False)

        # Label judul untuk katalog mata kuliah
        info_label = tk.Label(info_frame, text="📖 KATALOG MATA KULIAH SEMESTER INI", 
                             font=('Arial', 16, 'bold'), bg='#f8fafc', fg='#1e293b')
        info_label.pack(expand=True)

        # Frame untuk tabel mata kuliah
        tree_frame = tk.Frame(mk_frame, bg='#ffffff')
        tree_frame.pack(fill='both', expand=True, padx=15, pady=10)

        # Definisi kolom untuk tabel mata kuliah
        columns = ('Kode MK', 'Nama Mata Kuliah', 'SKS', 'Dosen Pengampu', 'Jadwal', 'Ruang', 'Kapasitas', 'Terisi')
        self.mk_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)

        # Setup header dan lebar kolom mata kuliah
        for col in columns:
            self.mk_tree.heading(col, text=col)
            if col in ['Kode MK', 'SKS', 'Kapasitas', 'Terisi']:
                self.mk_tree.column(col, width=80)
            else:
                self.mk_tree.column(col, width=140)

        # Scrollbar untuk tabel mata kuliah
        scrollbar_mk = ttk.Scrollbar(tree_frame, orient='vertical', command=self.mk_tree.yview)
        self.mk_tree.configure(yscrollcommand=scrollbar_mk.set)

        # Pack tabel dan scrollbar
        self.mk_tree.pack(side='left', fill='both', expand=True)
        scrollbar_mk.pack(side='right', fill='y')

    def create_krs_tab(self):
        """Tab untuk mengelola KRS dengan tema putih lembut"""
        # Frame utama tab KRS
        krs_frame = tk.Frame(self.notebook, bg='#ffffff')
        self.notebook.add(krs_frame, text="📝 PENGISIAN KRS")

        # Frame untuk memilih mahasiswa
        select_frame = ttk.LabelFrame(krs_frame, text="🎯 Pilih Mahasiswa untuk KRS", style='White.TLabelframe')
        select_frame.pack(fill='x', padx=15, pady=10)

        # Label dan dropdown untuk pilih mahasiswa
        tk.Label(select_frame, text="Mahasiswa:", font=('Arial', 11, 'bold'), 
                bg='#ffffff', fg='#475569').grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.mahasiswa_krs_var = tk.StringVar()
        self.mahasiswa_combo = ttk.Combobox(select_frame, textvariable=self.mahasiswa_krs_var, 
                                          width=60, font=('Arial', 10))
        self.mahasiswa_combo.grid(row=0, column=1, padx=10, pady=10, sticky='ew')
        # Event handler ketika mahasiswa dipilih
        self.mahasiswa_combo.bind('<<ComboboxSelected>>', self.on_mahasiswa_selected)

        # Konfigurasi grid untuk responsive
        select_frame.columnconfigure(1, weight=1)

        # Frame info KRS dengan background putih lembut
        self.info_frame = tk.Frame(krs_frame, bg='#f1f5f9', height=80, relief='solid', borderwidth=1)
        self.info_frame.pack(fill='x', padx=15, pady=5)
        self.info_frame.pack_propagate(False)

        # Label untuk menampilkan info mahasiswa dan SKS
        self.info_label = tk.Label(self.info_frame, text="💡 Silakan pilih mahasiswa terlebih dahulu untuk melihat info KRS!", 
                                  font=('Arial', 12, 'bold'), bg='#f1f5f9', fg='#475569', wraplength=800)
        self.info_label.pack(expand=True, padx=10)

        # Frame untuk mata kuliah yang tersedia
        available_frame = ttk.LabelFrame(krs_frame, text="🎓 Mata Kuliah yang Tersedia", style='White.TLabelframe')
        available_frame.pack(fill='both', expand=True, padx=15, pady=5)

        # Frame tabel mata kuliah tersedia
        av_tree_frame = tk.Frame(available_frame, bg='#ffffff')
        av_tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Definisi kolom untuk tabel mata kuliah tersedia
        av_columns = ('Kode MK', 'Nama Mata Kuliah', 'SKS', 'Dosen', 'Jadwal', 'Ruang', 'Slot Tersisa')
        self.available_tree = ttk.Treeview(av_tree_frame, columns=av_columns, show='headings', height=8)

        # Setup kolom mata kuliah tersedia
        for col in av_columns:
            self.available_tree.heading(col, text=col)
            if col in ['Kode MK', 'SKS', 'Slot Tersisa']:
                self.available_tree.column(col, width=80)
            else:
                self.available_tree.column(col, width=130)

        # Scrollbar untuk tabel mata kuliah tersedia
        scrollbar_av = ttk.Scrollbar(av_tree_frame, orient='vertical', command=self.available_tree.yview)
        self.available_tree.configure(yscrollcommand=scrollbar_av.set)

        # Pack tabel dan scrollbar
        self.available_tree.pack(side='left', fill='both', expand=True)
        scrollbar_av.pack(side='right', fill='y')

        # Frame tombol untuk aksi KRS
        krs_btn_frame = tk.Frame(available_frame, bg='#ffffff')
        krs_btn_frame.pack(fill='x', padx=10, pady=8)

        # Tombol untuk mengambil mata kuliah
        ttk.Button(krs_btn_frame, text="✅ Ambil Matkul", command=self.ambil_mata_kuliah, style='White.TButton').pack(side='left', padx=5)
        # Tombol untuk membatalkan mata kuliah
        ttk.Button(krs_btn_frame, text="❌ Batalkan", command=self.batal_ambil_mata_kuliah, style='White.TButton').pack(side='left', padx=5)
        # Tombol untuk refresh data
        ttk.Button(krs_btn_frame, text="🔄 Refresh Data", command=self.refresh_available_courses, style='White.TButton').pack(side='left', padx=5)

        # Frame untuk KRS yang sudah diambil
        current_frame = ttk.LabelFrame(krs_frame, text="📋 KRS yang Sudah Diambil", style='White.TLabelframe')
        current_frame.pack(fill='both', expand=True, padx=15, pady=5)

        # Frame tabel KRS yang sudah diambil
        curr_tree_frame = tk.Frame(current_frame, bg='#ffffff')
        curr_tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Definisi kolom untuk KRS yang sudah diambil
        curr_columns = ('Kode MK', 'Nama Mata Kuliah', 'SKS', 'Dosen', 'Jadwal', 'Status')
        self.current_krs_tree = ttk.Treeview(curr_tree_frame, columns=curr_columns, show='headings', height=6)

        # Setup kolom KRS yang sudah diambil
        for col in curr_columns:
            self.current_krs_tree.heading(col, text=col)
            if col in ['Kode MK', 'SKS']:
                self.current_krs_tree.column(col, width=80)
            else:
                self.current_krs_tree.column(col, width=130)

        # Scrollbar untuk tabel KRS
        scrollbar_curr = ttk.Scrollbar(curr_tree_frame, orient='vertical', command=self.current_krs_tree.yview)
        self.current_krs_tree.configure(yscrollcommand=scrollbar_curr.set)

        # Pack tabel dan scrollbar
        self.current_krs_tree.pack(side='left', fill='both', expand=True)
        scrollbar_curr.pack(side='right', fill='y')

    def tambah_mahasiswa(self):
        """Fungsi untuk menambah data mahasiswa baru ke database"""
        # Ambil data dari form input
        nim = self.nim_entry.get().strip()
        nama = self.nama_entry.get().strip()
        jurusan = self.jurusan_var.get()
        semester = self.semester_var.get()

        # Validasi: pastikan semua field diisi
        if not all([nim, nama, jurusan, semester]):
            messagebox.showwarning("Oops! 😅", "Mohon isi semua data dulu ya!")
            return

        try:
            # Insert data mahasiswa ke database
            self.cursor.execute("""
                INSERT INTO mahasiswa (nim, nama, jurusan, semester)
                VALUES (?, ?, ?, ?)
            """, (nim, nama, jurusan, int(semester)))
            self.conn.commit()
            messagebox.showinfo("Berhasil! 🚀", "Data mahasiswa berhasil ditambahkan!")
            # Reset form dan refresh list
            self.clear_mahasiswa_form()
            self.refresh_mahasiswa_list()
        except sqlite3.IntegrityError:
            # Error jika NIM sudah ada (karena NIM adalah primary key)
            messagebox.showerror("Duplikasi Data! 😔", "NIM ini sudah terdaftar di sistem!")
        except Exception as e:
            # Error lainnya
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")

    def update_mahasiswa(self):
        """Fungsi untuk mengupdate data mahasiswa yang sudah ada"""
        # Cek apakah ada mahasiswa yang dipilih
        selected = self.mahasiswa_tree.selection()
        if not selected:
            messagebox.showwarning("Pilih Data! 😊", "Silakan pilih mahasiswa yang ingin diupdate!")
            return

        # Ambil data dari form
        nim = self.nim_entry.get().strip()
        nama = self.nama_entry.get().strip()
        jurusan = self.jurusan_var.get()
        semester = self.semester_var.get()

        # Validasi input
        if not all([nim, nama, jurusan, semester]):
            messagebox.showwarning("Data Tidak Lengkap! 😅", "Mohon isi semua data yang diperlukan!")
            return

        try:
            # Update data di database
            self.cursor.execute("""
                UPDATE mahasiswa SET nama=?, jurusan=?, semester=?
                WHERE nim=?
            """, (nama, jurusan, int(semester), nim))
            self.conn.commit()
            messagebox.showinfo("Update Berhasil! 🎉", "Data mahasiswa berhasil diperbarui!")
            # Reset form dan refresh list
            self.clear_mahasiswa_form()
            self.refresh_mahasiswa_list()
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")

    def hapus_mahasiswa(self):
        """Fungsi untuk menghapus data mahasiswa dari database"""
        # Cek apakah ada mahasiswa yang dipilih
        selected = self.mahasiswa_tree.selection()
        if not selected:
            messagebox.showwarning("Pilih Data! 😊", "Silakan pilih mahasiswa yang ingin dihapus!")
            return

        # Ambil NIM dari item yang dipilih
        item = self.mahasiswa_tree.item(selected)
        nim = item['values'][0]

        # Konfirmasi penghapusan
        if messagebox.askyesno("Konfirmasi Hapus 🤔", f"Apakah Anda yakin ingin menghapus mahasiswa dengan NIM {nim}?\nData akan hilang permanen!"):
            try:
                # Hapus data KRS terlebih dahulu (foreign key constraint)
                self.cursor.execute("DELETE FROM krs WHERE nim=?", (nim,))
                # Kemudian hapus data mahasiswa
                self.cursor.execute("DELETE FROM mahasiswa WHERE nim=?", (nim,))
                self.conn.commit()
                messagebox.showinfo("Berhasil Dihapus! 🎉", "Data mahasiswa telah dihapus!")
                # Reset form dan refresh list
                self.clear_mahasiswa_form()
                self.refresh_mahasiswa_list()
            except Exception as e:
                messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")

    def clear_mahasiswa_form(self):
        """Fungsi untuk membersihkan form input mahasiswa"""
        self.nim_entry.delete(0, tk.END)
        self.nama_entry.delete(0, tk.END)
        self.jurusan_var.set('')
        self.semester_var.set('')

    def select_mahasiswa(self, event):
        """Event handler ketika mahasiswa diklik di tabel"""
        selected = self.mahasiswa_tree.selection()
        if selected:
            # Ambil data dari item yang dipilih
            item = self.mahasiswa_tree.item(selected)
            values = item['values']

            # Isi form dengan data yang dipilih
            self.nim_entry.delete(0, tk.END)
            self.nim_entry.insert(0, values[0])
            self.nama_entry.delete(0, tk.END)
            self.nama_entry.insert(0, values[1])
            self.jurusan_var.set(values[2])
            self.semester_var.set(values[3])

    def refresh_mahasiswa_list(self):
        """Fungsi untuk me-refresh daftar mahasiswa di tabel"""
        # Hapus semua item di tabel
        for item in self.mahasiswa_tree.get_children():
            self.mahasiswa_tree.delete(item)

        # Load data mahasiswa dari database
        self.cursor.execute("SELECT nim, nama, jurusan, semester, max_sks FROM mahasiswa ORDER BY nim")
        for row in self.cursor.fetchall():
            self.mahasiswa_tree.insert('', 'end', values=row)

        # Update dropdown mahasiswa untuk KRS
        self.cursor.execute("SELECT nim, nama FROM mahasiswa ORDER BY nim")
        mahasiswa_list = [f"{row[0]} - {row[1]}" for row in self.cursor.fetchall()]
        self.mahasiswa_combo['values'] = mahasiswa_list

    def refresh_mata_kuliah_list(self):
        """Fungsi untuk me-refresh daftar mata kuliah di tabel"""
        # Hapus semua item di tabel mata kuliah
        for item in self.mk_tree.get_children():
            self.mk_tree.delete(item)

        # Load data mata kuliah dengan join untuk menghitung jumlah yang sudah terisi
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

    def on_mahasiswa_selected(self, event):
        """Event handler ketika mahasiswa dipilih di dropdown KRS"""
        selected = self.mahasiswa_krs_var.get()
        if selected:
            # Extract NIM dari pilihan
            nim = selected.split(' - ')[0]
            self.current_nim = nim
            # Update info dan refresh data
            self.update_krs_info()
            self.refresh_available_courses()
            self.refresh_current_krs()

    def update_krs_info(self):
        """Fungsi untuk mengupdate informasi KRS mahasiswa"""
        if hasattr(self, 'current_nim'):
            # Ambil info mahasiswa
            self.cursor.execute("""
                SELECT nama, jurusan, semester, max_sks FROM mahasiswa WHERE nim=?
            """, (self.current_nim,))
            mhs_info = self.cursor.fetchone()

            # Hitung total SKS yang sudah diambil
            self.cursor.execute("""
                SELECT SUM(mk.sks) FROM krs k
                JOIN mata_kuliah mk ON k.kode_mk = mk.kode_mk
                WHERE k.nim=? AND k.status='Aktif'
            """, (self.current_nim,))
            current_sks = self.cursor.fetchone()[0] or 0

            # Update label info
            if mhs_info:
                info_text = f"🎓 {mhs_info[0]} | {mhs_info[1]} | Semester {mhs_info[2]} | "
                info_text += f"SKS Diambil: {current_sks}/{mhs_info[3]} | Sisa: {mhs_info[3] - current_sks} SKS"
                self.info_label.config(text=info_text)

    def refresh_available_courses(self):
        """Fungsi untuk me-refresh mata kuliah yang tersedia untuk diambil"""
        # Hapus semua item di tabel
        for item in self.available_tree.get_children():
            self.available_tree.delete(item)

        if hasattr(self, 'current_nim'):
            # Query mata kuliah yang belum diambil dan masih ada slot
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

            # Insert data ke tabel
            for row in self.cursor.fetchall():
                self.available_tree.insert('', 'end', values=row)

    def refresh_current_krs(self):
        """Fungsi untuk me-refresh KRS yang sudah diambil mahasiswa"""
        # Hapus semua item di tabel
        for item in self.current_krs_tree.get_children():
            self.current_krs_tree.delete(item)

        if hasattr(self, 'current_nim'):
            # Query KRS yang sudah diambil
            self.cursor.execute("""
                SELECT mk.kode_mk, mk.nama_mk, mk.sks, mk.dosen, mk.jadwal, k.status
                FROM krs k
                JOIN mata_kuliah mk ON k.kode_mk = mk.kode_mk
                WHERE k.nim=?
                ORDER BY mk.kode_mk
            """, (self.current_nim,))

            # Insert data ke tabel
            for row in self.cursor.fetchall():
                self.current_krs_tree.insert('', 'end', values=row)

    def ambil_mata_kuliah(self):
        """Fungsi untuk mengambil mata kuliah ke dalam KRS"""
        # Validasi: pastikan mahasiswa sudah dipilih
        if not hasattr(self, 'current_nim'):
            messagebox.showwarning("Pilih Mahasiswa! 😊", "Silakan pilih mahasiswa terlebih dahulu!")
            return

        # Validasi: pastikan mata kuliah sudah dipilih
        selected = self.available_tree.selection()
        if not selected:
            messagebox.showwarning("Pilih Mata Kuliah! 😊", "Silakan pilih mata kuliah yang ingin diambil!")
            return

        # Ambil data mata kuliah yang dipilih
        item = self.available_tree.item(selected)
        kode_mk = item['values'][0]
        sks_mk = item['values'][2]

        # Hitung total SKS yang sudah diambil
        self.cursor.execute("""
            SELECT SUM(mk.sks) FROM krs k
            JOIN mata_kuliah mk ON k.kode_mk = mk.kode_mk
            WHERE k.nim=? AND k.status='Aktif'
        """, (self.current_nim,))
        current_sks = self.cursor.fetchone()[0] or 0

        # Ambil batas maksimal SKS mahasiswa
        self.cursor.execute("SELECT max_sks FROM mahasiswa WHERE nim=?", (self.current_nim,))
        max_sks = self.cursor.fetchone()[0]

        # Validasi: cek apakah SKS melebihi batas
        if current_sks + sks_mk > max_sks:
            messagebox.showwarning("Melebihi Batas SKS! 😅", 
                                 f"Jika mengambil mata kuliah ini, total SKS akan melebihi batas maksimal ({max_sks} SKS)!")
            return

        try:
            # Insert data ke tabel KRS
            tanggal_ambil = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute("""
                INSERT INTO krs (nim, kode_mk, tanggal_ambil, status)
                VALUES (?, ?, ?, 'Aktif')
            """, (self.current_nim, kode_mk, tanggal_ambil))

            self.conn.commit()
            messagebox.showinfo("Berhasil! 🚀", f"Mata kuliah {kode_mk} berhasil diambil! Semangat belajar! 💪")

            # Refresh semua data
            self.update_krs_info()
            self.refresh_available_courses()
            self.refresh_current_krs()
            self.refresh_mata_kuliah_list()

        except sqlite3.IntegrityError:
            # Error jika mata kuliah sudah diambil
            messagebox.showerror("Sudah Diambil! 😅", "Mata kuliah ini sudah Anda ambil sebelumnya!")
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")

    def batal_ambil_mata_kuliah(self):
        """Fungsi untuk membatalkan pengambilan mata kuliah"""
        # Validasi: pastikan mahasiswa sudah dipilih
        if not hasattr(self, 'current_nim'):
            messagebox.showwarning("Pilih Mahasiswa! 😊", "Silakan pilih mahasiswa terlebih dahulu!")
            return

        # Validasi: pastikan mata kuliah sudah dipilih
        selected = self.current_krs_tree.selection()
        if not selected:
            messagebox.showwarning("Pilih Mata Kuliah! 😊", "Silakan pilih mata kuliah yang ingin dibatalkan!")
            return

        # Ambil kode mata kuliah yang dipilih
        item = self.current_krs_tree.item(selected)
        kode_mk = item['values'][0]

        # Konfirmasi pembatalan
        if messagebox.askyesno("Konfirmasi Pembatalan 🤔", 
                              f"Apakah Anda yakin ingin membatalkan mata kuliah {kode_mk}?\nAnda harus mendaftar ulang jika ingin mengambil lagi!"):
            try:
                # Hapus data dari tabel KRS
                self.cursor.execute("""
                    DELETE FROM krs WHERE nim=? AND kode_mk=?
                """, (self.current_nim, kode_mk))

                self.conn.commit()
                messagebox.showinfo("Berhasil! 🎉", f"Mata kuliah {kode_mk} berhasil dibatalkan!")

                # Refresh semua data
                self.update_krs_info()
                self.refresh_available_courses()
                self.refresh_current_krs()
                self.refresh_mata_kuliah_list()

            except Exception as e:
                messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")

    def __del__(self):
        """Destructor untuk menutup koneksi database"""
        if hasattr(self, 'conn'):
            self.conn.close()

# Main program - entry point aplikasi
if __name__ == "__main__":
    # Membuat instance root window
    root = tk.Tk()
    # Membuat instance aplikasi KRS
    app = KRSAppFataZikrillah(root)
    # Menjalankan event loop GUI
    root.mainloop()
