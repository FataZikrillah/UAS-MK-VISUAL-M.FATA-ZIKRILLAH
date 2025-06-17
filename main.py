import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class KRSApplication:
    def __init__(self, root):
        """
        Konstruktor untuk menginisialisasi aplikasi KRS
        - Mengatur jendela utama
        - Membuat koneksi database
        - Menginisialisasi database dan data default
        - Membuat tampilan GUI
        """
        self.root = root
        self.root.title("Sistem KRS (Kartu Rencana Studi)")
        self.root.geometry("1000x700")  # Ukuran jendela aplikasi
        self.root.configure(bg='#f0f0f0')  # Warna latar belakang jendela

        # Membuat koneksi ke database SQLite
        self.conn = sqlite3.connect('krs_database.db')
        self.cursor = self.conn.cursor()

        # Inisialisasi tabel-tabel database
        self.init_database()

        # Memuat data default jika database kosong
        self.load_default_data()

        # Mengatur gaya tampilan (styling)
        self.configure_styles()

        # Membuat komponen-komponen GUI
        self.create_widgets()

        # Memuat data awal ke dalam tampilan
        self.refresh_all_data()

    def configure_styles(self):
        """
        Mengkonfigurasi gaya visual untuk komponen GUI
        - Mengatur warna, font, dan tampilan komponen
        - Membuat tema yang konsisten dan menarik
        """
        style = ttk.Style()
        style.theme_use('clam')  # Menggunakan tema clam

        # Mengatur gaya untuk label judul
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'), foreground='#2c3e50')
        style.configure('Header.TLabel', font=('Arial', 10, 'bold'), foreground='#34495e')

        # Mengatur gaya untuk tabel (Treeview) dengan border
        style.configure('Custom.Treeview', 
                       background='white',           # Latar belakang putih
                       foreground='black',           # Teks hitam
                       rowheight=25,                # Tinggi baris
                       fieldbackground='white',      # Latar belakang field
                       borderwidth=1,               # Lebar border
                       relief='solid')              # Jenis border solid

        # Mengatur gaya untuk header tabel
        style.configure('Custom.Treeview.Heading',
                       background='#3498db',         # Latar belakang biru
                       foreground='white',           # Teks putih
                       font=('Arial', 9, 'bold'),   # Font tebal
                       borderwidth=1,               # Lebar border
                       relief='solid')              # Jenis border solid

        # Mengatur gaya untuk tombol aksi (biru)
        style.configure('Action.TButton',
                       background='#3498db',         # Latar belakang biru
                       foreground='white',           # Teks putih
                       font=('Arial', 9, 'bold'),   # Font tebal
                       padding=(10, 5))             # Padding dalam tombol
        style.map('Action.TButton',
                 background=[('active', '#2980b9')])  # Warna saat hover

        # Mengatur gaya untuk tombol sukses (hijau)
        style.configure('Success.TButton',
                       background='#27ae60',         # Latar belakang hijau
                       foreground='white',           # Teks putih
                       font=('Arial', 9, 'bold'),   # Font tebal
                       padding=(10, 5))             # Padding dalam tombol
        style.map('Success.TButton',
                 background=[('active', '#229954')])  # Warna saat hover

        # Mengatur gaya untuk tombol bahaya (merah)
        style.configure('Danger.TButton',
                       background='#e74c3c',         # Latar belakang merah
                       foreground='white',           # Teks putih
                       font=('Arial', 9, 'bold'),   # Font tebal
                       padding=(10, 5))             # Padding dalam tombol
        style.map('Danger.TButton',
                 background=[('active', '#c0392b')])  # Warna saat hover

    def init_database(self):
        """
        Menginisialisasi struktur database
        - Membuat tabel-tabel yang diperlukan
        - Menambahkan kolom yang hilang pada tabel existing
        - Memastikan integritas referensial antar tabel
        """

        # Membuat tabel mahasiswa (students)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,    -- ID unik mahasiswa
                nim TEXT UNIQUE NOT NULL,                -- NIM mahasiswa (harus unik)
                nama TEXT NOT NULL,                      -- Nama lengkap mahasiswa
                semester INTEGER NOT NULL,               -- Semester saat ini
                max_credits INTEGER DEFAULT 24,          -- Batas maksimal SKS per semester
                created_at TEXT DEFAULT CURRENT_TIMESTAMP -- Waktu pendaftaran
            )
        """)

        # Mengecek dan menambahkan kolom created_at jika belum ada
        try:
            self.cursor.execute("SELECT created_at FROM students LIMIT 1")
        except sqlite3.OperationalError:
            # Menambahkan kolom tanpa default value, lalu update data existing
            self.cursor.execute("ALTER TABLE students ADD COLUMN created_at TEXT")
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute("UPDATE students SET created_at = ? WHERE created_at IS NULL", (current_time,))

        # Membuat tabel mata kuliah (courses)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,    -- ID unik mata kuliah
                kode_mk TEXT UNIQUE NOT NULL,            -- Kode mata kuliah (harus unik)
                nama_mk TEXT NOT NULL,                   -- Nama mata kuliah
                sks INTEGER NOT NULL,                    -- Jumlah SKS
                semester INTEGER NOT NULL,               -- Semester mata kuliah ditawarkan
                jadwal TEXT NOT NULL,                    -- Jadwal kuliah
                dosen TEXT NOT NULL,                     -- Nama dosen pengampu
                kapasitas INTEGER DEFAULT 40,            -- Kapasitas maksimal mahasiswa
                terisi INTEGER DEFAULT 0,               -- Jumlah mahasiswa terdaftar
                created_at TEXT DEFAULT CURRENT_TIMESTAMP -- Waktu pembuatan data
            )
        """)

        # Mengecek dan menambahkan kolom created_at untuk tabel courses
        try:
            self.cursor.execute("SELECT created_at FROM courses LIMIT 1")
        except sqlite3.OperationalError:
            self.cursor.execute("ALTER TABLE courses ADD COLUMN created_at TEXT")
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute("UPDATE courses SET created_at = ? WHERE created_at IS NULL", (current_time,))

        # Membuat tabel pendaftaran KRS (enrollments)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,    -- ID unik pendaftaran
                student_id INTEGER,                      -- ID mahasiswa (foreign key)
                course_id INTEGER,                       -- ID mata kuliah (foreign key)
                tanggal_daftar TEXT NOT NULL,            -- Tanggal pendaftaran
                status TEXT DEFAULT 'aktif',             -- Status pendaftaran (aktif/nonaktif)
                created_at TEXT DEFAULT CURRENT_TIMESTAMP, -- Waktu pembuatan data
                FOREIGN KEY (student_id) REFERENCES students (id),  -- Relasi ke tabel students
                FOREIGN KEY (course_id) REFERENCES courses (id),    -- Relasi ke tabel courses
                UNIQUE(student_id, course_id)            -- Satu mahasiswa tidak bisa daftar mata kuliah yang sama 2x
            )
        """)

        # Mengecek dan menambahkan kolom created_at untuk tabel enrollments
        try:
            self.cursor.execute("SELECT created_at FROM enrollments LIMIT 1")
        except sqlite3.OperationalError:
            self.cursor.execute("ALTER TABLE enrollments ADD COLUMN created_at TEXT")
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute("UPDATE enrollments SET created_at = ? WHERE created_at IS NULL", (current_time,))

        # Membuat tabel konfigurasi sistem
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,    -- ID unik konfigurasi
                config_key TEXT UNIQUE NOT NULL,         -- Kunci konfigurasi (harus unik)
                config_value TEXT NOT NULL,              -- Nilai konfigurasi
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP -- Waktu update terakhir
            )
        """)

        # Mengecek dan menambahkan kolom updated_at untuk tabel system_config
        try:
            self.cursor.execute("SELECT updated_at FROM system_config LIMIT 1")
        except sqlite3.OperationalError:
            self.cursor.execute("ALTER TABLE system_config ADD COLUMN updated_at TEXT")
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute("UPDATE system_config SET updated_at = ? WHERE created_at IS NULL", (current_time,))

        # Menyimpan perubahan ke database
        self.conn.commit()

    def load_default_data(self):
        """
        Memuat data default ke dalam database jika masih kosong
        - Mengisi konfigurasi sistem default
        - Mengisi mata kuliah default untuk demo
        """

        # Data konfigurasi sistem default
        default_configs = [
            ('max_credits_per_semester', '24'),    # Maksimal SKS per semester
            ('min_credits_per_semester', '12'),    # Minimal SKS per semester
            ('academic_year', '2024/2025'),        # Tahun akademik
            ('current_semester', 'Ganjil')         # Semester saat ini
        ]

        # Memasukkan konfigurasi default (jika belum ada)
        for key, value in default_configs:
            self.cursor.execute("""
                INSERT OR IGNORE INTO system_config (config_key, config_value)
                VALUES (?, ?)
            """, (key, value))

        # Mengecek apakah perlu memuat ulang data mata kuliah
        self.cursor.execute("SELECT COUNT(*) FROM courses")
        current_count = self.cursor.fetchone()[0]
        
        # Jika kurang dari 46 mata kuliah, hapus dan muat ulang semua data
        if current_count < 46:
            print(f"Mendeteksi data mata kuliah tidak lengkap ({current_count}/46). Memuat ulang...")
            
            # Hapus semua data mata kuliah yang ada
            self.cursor.execute("DELETE FROM courses")
            
            # Data mata kuliah lengkap untuk semua semester (1-8)
            default_courses = [
                # SEMESTER 1 (GANJIL)
                ('IF101', 'Pemrograman Dasar', 3, 1, 'Senin 08:00-10:30', 'Dr. Ahmad Fauzi', 40),
                ('MTK101', 'Matematika Diskrit', 3, 1, 'Selasa 10:30-13:00', 'Prof. Siti Aminah', 35),
                ('IF103', 'Algoritma dan Pemrograman', 4, 1, 'Rabu 13:00-16:30', 'Dr. Rudi Hartono', 38),
                ('IF105', 'Logika Informatika', 3, 1, 'Kamis 08:00-10:30', 'Dr. Budi Santoso', 35),
                ('ENG101', 'Bahasa Inggris', 2, 1, 'Jumat 10:00-11:30', 'Ms. Lisa Johnson', 45),
                ('MTK103', 'Kalkulus I', 3, 1, 'Senin 13:00-15:30', 'Prof. Maria Sari', 40),
                ('CHAR101', 'Pancasila', 2, 1, 'Selasa 08:00-09:30', 'Dr. Agus Setiawan', 50),

                # SEMESTER 2 (GENAP)
                ('IF102', 'Pemrograman Berorientasi Objek', 4, 2, 'Senin 08:00-11:30', 'Dr. Ahmad Fauzi', 38),
                ('MTK102', 'Kalkulus II', 3, 2, 'Selasa 13:00-15:30', 'Prof. Maria Sari', 35),
                ('IF104', 'Sistem Digital', 3, 2, 'Rabu 10:00-12:30', 'Dr. Eko Prasetyo', 32),
                ('IF106', 'Arsitektur Komputer', 3, 2, 'Kamis 13:00-15:30', 'Prof. Indra Gunawan', 30),
                ('MTK104', 'Statistika dan Probabilitas', 3, 2, 'Jumat 08:00-10:30', 'Dr. Rina Susanti', 40),
                ('ENG102', 'Bahasa Inggris Teknik', 2, 2, 'Selasa 10:00-11:30', 'Ms. Lisa Johnson', 45),
                ('CHAR102', 'Kewarganegaraan', 2, 2, 'Rabu 08:00-09:30', 'Dr. Sari Dewi', 50),

                # SEMESTER 3 (GANJIL)
                ('IF201', 'Struktur Data', 4, 3, 'Senin 08:00-11:30', 'Dr. Budi Santoso', 35),
                ('IF203', 'Basis Data', 3, 3, 'Selasa 13:00-15:30', 'Dr. Maya Sari', 32),
                ('IF205', 'Pemrograman Web', 3, 3, 'Rabu 10:00-12:30', 'Dr. Lisa Putri', 35),
                ('IF207', 'Sistem Operasi', 3, 3, 'Kamis 08:00-10:30', 'Prof. Rudi Hartanto', 30),
                ('MTK201', 'Matematika Numerik', 3, 3, 'Jumat 13:00-15:30', 'Dr. Wawan Kurniawan', 35),
                ('IF209', 'Jaringan Komputer Dasar', 3, 3, 'Senin 13:00-15:30', 'Dr. Fitri Handayani', 32),

                # SEMESTER 4 (GENAP)
                ('IF202', 'Algoritma dan Kompleksitas', 3, 4, 'Senin 10:00-12:30', 'Dr. Rudi Hartono', 30),
                ('IF204', 'Pemrograman Mobile', 3, 4, 'Selasa 08:00-10:30', 'Dr. Lisa Putri', 35),
                ('IF206', 'Manajemen Basis Data', 3, 4, 'Rabu 13:00-15:30', 'Dr. Maya Sari', 32),
                ('IF208', 'Interaksi Manusia Komputer', 3, 4, 'Kamis 10:00-12:30', 'Dr. Nina Kusuma', 35),
                ('IF210', 'Teori Bahasa dan Otomata', 3, 4, 'Jumat 08:00-10:30', 'Prof. Siti Aminah', 28),
                ('MTK202', 'Riset Operasi', 3, 4, 'Senin 13:00-15:30', 'Dr. Wawan Kurniawan', 30),

                # SEMESTER 5 (GANJIL)
                ('IF301', 'Rekayasa Perangkat Lunak', 4, 5, 'Senin 08:00-11:30', 'Prof. Andi Wijaya', 30),
                ('IF303', 'Jaringan Komputer', 3, 5, 'Selasa 13:00-15:30', 'Dr. Fitri Handayani', 32),
                ('IF305', 'Komputer Grafik', 3, 5, 'Rabu 10:00-12:30', 'Dr. Eko Prasetyo', 28),
                ('IF307', 'Sistem Informasi', 3, 5, 'Kamis 08:00-10:30', 'Dr. Nina Kusuma', 35),
                ('IF309', 'Pemrograman Game', 3, 5, 'Jumat 13:00-15:30', 'Dr. David Chen', 25),
                ('IF311', 'Data Mining', 3, 5, 'Senin 13:00-15:30', 'Dr. Sarah Abdullah', 30),

                # SEMESTER 6 (GENAP)
                ('IF302', 'Manajemen Proyek TI', 3, 6, 'Senin 10:00-12:30', 'Prof. Andi Wijaya', 35),
                ('IF304', 'Keamanan Jaringan', 3, 6, 'Selasa 08:00-10:30', 'Dr. Fitri Handayani', 28),
                ('IF306', 'Pengembangan Aplikasi Web', 3, 6, 'Rabu 13:00-15:30', 'Dr. Lisa Putri', 32),
                ('IF308', 'Business Intelligence', 3, 6, 'Kamis 10:00-12:30', 'Dr. Maya Sari', 30),
                ('IF310', 'Cloud Computing', 3, 6, 'Jumat 08:00-10:30', 'Dr. Indra Gunawan', 28),
                ('IF312', 'Internet of Things', 3, 6, 'Senin 13:00-15:30', 'Dr. Eko Prasetyo', 25),

                # SEMESTER 7 (GANJIL)
                ('IF401', 'Kecerdasan Buatan', 4, 7, 'Senin 08:00-11:30', 'Prof. David Chen', 30),
                ('IF403', 'Keamanan Sistem', 3, 7, 'Selasa 13:00-15:30', 'Dr. Sarah Abdullah', 28),
                ('IF405', 'Pembelajaran Mesin', 3, 7, 'Rabu 10:00-12:30', 'Prof. David Chen', 25),
                ('IF407', 'Sistem Terdistribusi', 3, 7, 'Kamis 08:00-10:30', 'Dr. Indra Gunawan', 30),
                ('IF409', 'Visi Komputer', 3, 7, 'Jumat 13:00-15:30', 'Dr. Eko Prasetyo', 25),
                ('IF411', 'Metodologi Penelitian', 2, 7, 'Senin 13:00-14:30', 'Prof. Andi Wijaya', 40),

                # SEMESTER 8 (GENAP)
                ('IF402', 'Skripsi', 6, 8, 'Konsultasi Individual', 'Tim Dosen Pembimbing', 50),
                ('IF404', 'Kerja Praktek', 2, 8, 'Industri Partner', 'Tim Dosen Supervisor', 50),
                ('IF406', 'Etika Profesi', 2, 8, 'Senin 10:00-11:30', 'Dr. Agus Setiawan', 45),
                ('IF408', 'Technopreneurship', 3, 8, 'Selasa 08:00-10:30', 'Dr. Nina Kusuma', 35),
                ('IF410', 'Seminar Hasil', 1, 8, 'Rabu 13:00-14:00', 'Tim Dosen Penguji', 40),
                ('IF412', 'Proyek Akhir', 3, 8, 'Kamis 08:00-11:30', 'Tim Dosen Pembimbing', 30)
            ]

            # Memasukkan data mata kuliah lengkap ke database
            for course in default_courses:
                self.cursor.execute("""
                    INSERT INTO courses (kode_mk, nama_mk, sks, semester, jadwal, dosen, kapasitas)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, course)

            # Menyimpan perubahan ke database
            self.conn.commit()
            print(f"Data mata kuliah berhasil dimuat: {len(default_courses)} mata kuliah")

        # Verifikasi data mata kuliah setelah load
        self.cursor.execute("SELECT COUNT(*) FROM courses")
        final_count = self.cursor.fetchone()[0]
        print(f"Verifikasi: Total mata kuliah setelah load_default_data: {final_count}")

        # Menyimpan perubahan ke database
        self.conn.commit()

    def get_config_value(self, key, default=''):
        """
        Mengambil nilai konfigurasi dari database
        - key: kunci konfigurasi yang dicari
        - default: nilai default jika kunci tidak ditemukan
        """
        self.cursor.execute("SELECT config_value FROM system_config WHERE config_key = ?", (key,))
        result = self.cursor.fetchone()
        return result[0] if result else default

    def create_widgets(self):
        """
        Membuat komponen-komponen GUI utama
        - Header aplikasi
        - Tab navigasi
        - Memanggil fungsi untuk membuat setiap tab
        """

        # Frame untuk judul aplikasi dengan background berwarna
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill="x", pady=(0, 10))
        title_frame.pack_propagate(False)  # Mempertahankan ukuran frame

        # Label judul aplikasi
        title_label = tk.Label(title_frame, text="SISTEM KARTU RENCANA STUDI (KRS)  - BY M.FATA ZIKRILLAH", 
                              font=('Arial', 16, 'bold'), 
                              fg='white', bg='#2c3e50')
        title_label.pack(expand=True)

        # Membuat notebook (container untuk tab)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=10)

        # Membuat tab-tab aplikasi
        self.create_student_tab()    # Tab data mahasiswa
        self.create_course_tab()     # Tab data mata kuliah
        self.create_krs_tab()        # Tab pengisian KRS
        self.create_report_tab()     # Tab laporan KRS

    def create_student_tab(self):
        """
        Membuat tab untuk manajemen data mahasiswa
        - Form input data mahasiswa
        - Tabel untuk menampilkan daftar mahasiswa
        - Tombol-tombol untuk operasi CRUD
        """

        # Membuat frame untuk tab mahasiswa
        self.student_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.student_frame, text="📚 Data Mahasiswa")

        # Frame untuk form input dengan background berwarna
        input_frame = tk.Frame(self.student_frame, bg='#ecf0f1', relief='raised', bd=2)
        input_frame.pack(fill="x", padx=10, pady=10)

        # Label judul form
        title_label = tk.Label(input_frame, text="Form Input Data Mahasiswa", 
                              font=('Arial', 12, 'bold'), 
                              bg='#ecf0f1', fg='#2c3e50')
        title_label.grid(row=0, column=0, columnspan=4, pady=10)

        # Input field untuk NIM
        tk.Label(input_frame, text="NIM:", font=('Arial', 10, 'bold'), 
                bg='#ecf0f1', fg='#34495e').grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.entry_nim = tk.Entry(input_frame, width=20, font=('Arial', 10), relief='solid', bd=1)
        self.entry_nim.grid(row=1, column=1, padx=10, pady=5)

        # Input field untuk Nama
        tk.Label(input_frame, text="Nama:", font=('Arial', 10, 'bold'), 
                bg='#ecf0f1', fg='#34495e').grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.entry_nama_mhs = tk.Entry(input_frame, width=30, font=('Arial', 10), relief='solid', bd=1)
        self.entry_nama_mhs.grid(row=1, column=3, padx=10, pady=5)

        # Dropdown untuk Semester
        tk.Label(input_frame, text="Semester:", font=('Arial', 10, 'bold'), 
                bg='#ecf0f1', fg='#34495e').grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.entry_semester = ttk.Combobox(input_frame, values=[1,2,3,4,5,6,7,8], width=17, font=('Arial', 10))
        self.entry_semester.grid(row=2, column=1, padx=10, pady=5)

        # Input field untuk Maksimal SKS
        tk.Label(input_frame, text="Max SKS:", font=('Arial', 10, 'bold'), 
                bg='#ecf0f1', fg='#34495e').grid(row=2, column=2, padx=10, pady=5, sticky="w")
        self.entry_max_sks = tk.Entry(input_frame, width=10, font=('Arial', 10), relief='solid', bd=1)
        self.entry_max_sks.insert(0, "24")  # Nilai default
        self.entry_max_sks.grid(row=2, column=3, padx=10, pady=5, sticky="w")

        # Frame untuk tombol-tombol aksi
        button_frame = tk.Frame(input_frame, bg='#ecf0f1')
        button_frame.grid(row=3, column=0, columnspan=4, pady=15)

        # Tombol untuk menambah mahasiswa baru
        ttk.Button(button_frame, text="➕ Tambah", style='Success.TButton', command=self.tambah_mahasiswa).pack(side="left", padx=5)
        # Tombol untuk mengupdate data mahasiswa
        ttk.Button(button_frame, text="✏️ Update", style='Action.TButton', command=self.update_mahasiswa).pack(side="left", padx=5)
        # Tombol untuk menghapus mahasiswa
        ttk.Button(button_frame, text="🗑️ Hapus", style='Danger.TButton', command=self.hapus_mahasiswa).pack(side="left", padx=5)
        # Tombol untuk membersihkan form
        ttk.Button(button_frame, text="🔄 Clear", command=self.clear_student_form).pack(side="left", padx=5)

        # Frame untuk menampilkan data mahasiswa
        data_frame = tk.Frame(self.student_frame, bg='white', relief='solid', bd=2)
        data_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Label judul untuk bagian data
        data_title = tk.Label(data_frame, text="Daftar Mahasiswa Terdaftar", 
                             font=('Arial', 12, 'bold'), 
                             bg='#3498db', fg='white', pady=10)
        data_title.pack(fill="x")

        # Frame untuk tabel mahasiswa
        tree_frame = tk.Frame(data_frame, bg='white')
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Definisi kolom untuk tabel mahasiswa
        columns = ("ID", "NIM", "Nama", "Semester", "Max SKS", "Tanggal Daftar")
        self.student_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", style='Custom.Treeview')

        # Mengatur lebar kolom dan header
        column_widths = {"ID": 60, "NIM": 120, "Nama": 200, "Semester": 80, "Max SKS": 80, "Tanggal Daftar": 150}
        for col in columns:
            self.student_tree.heading(col, text=col)  # Mengatur header kolom
            self.student_tree.column(col, width=column_widths.get(col, 100))  # Mengatur lebar kolom

        # Mengatur warna baris bergantian untuk kemudahan baca
        self.student_tree.tag_configure('oddrow', background='#f8f9fa')   # Baris ganjil
        self.student_tree.tag_configure('evenrow', background='white')     # Baris genap

        # Scrollbar untuk tabel mahasiswa
        scrollbar_student = ttk.Scrollbar(tree_frame, orient="vertical", command=self.student_tree.yview)
        self.student_tree.configure(yscrollcommand=scrollbar_student.set)

        # Menempatkan tabel dan scrollbar
        self.student_tree.pack(side="left", fill="both", expand=True)
        scrollbar_student.pack(side="right", fill="y")

        # Menghubungkan event klik pada tabel dengan fungsi select_student
        self.student_tree.bind("<<TreeviewSelect>>", self.select_student)

    def create_course_tab(self):
        """
        Membuat tab untuk menampilkan katalog mata kuliah
        - Tabel mata kuliah dengan informasi lengkap
        - Filter berdasarkan semester
        - Informasi kapasitas dan ketersediaan
        """

        # Membuat frame untuk tab mata kuliah
        self.course_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.course_frame, text="📖 Data Mata Kuliah")

        # Frame untuk menampilkan data mata kuliah
        data_frame = tk.Frame(self.course_frame, bg='white', relief='solid', bd=2)
        data_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Label judul untuk katalog mata kuliah
        data_title = tk.Label(data_frame, text="Katalog Mata Kuliah", 
                             font=('Arial', 12, 'bold'), 
                             bg='#e67e22', fg='white', pady=10)
        data_title.pack(fill="x")

        # Frame untuk filter semester
        filter_frame = tk.Frame(data_frame, bg='#f8f9fa', pady=10)
        filter_frame.pack(fill="x", padx=10, pady=(10, 0))

        # Label dan dropdown untuk filter semester
        tk.Label(filter_frame, text="Filter Semester:", font=('Arial', 10, 'bold'), 
                bg='#f8f9fa').pack(side="left", padx=5)
        self.filter_semester = ttk.Combobox(filter_frame, values=["Semua", 1,2,3,4,5,6,7,8], width=10, state="readonly")
        self.filter_semester.set("Semua")  # Nilai default
        self.filter_semester.pack(side="left", padx=5)
        # Menghubungkan event perubahan filter dengan fungsi filter_courses
        self.filter_semester.bind("<<ComboboxSelected>>", self.filter_courses)

        # Frame untuk tabel mata kuliah
        tree_frame = tk.Frame(data_frame, bg='white')
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Definisi kolom untuk tabel mata kuliah
        columns = ("Kode MK", "Nama Mata Kuliah", "SKS", "Semester", "Jadwal", "Dosen", "Kapasitas", "Terisi", "Sisa")
        self.course_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", style='Custom.Treeview')

        # Mengatur lebar kolom
        column_widths = {"Kode MK": 80, "Nama Mata Kuliah": 200, "SKS": 50, "Semester": 70, 
                        "Jadwal": 150, "Dosen": 150, "Kapasitas": 70, "Terisi": 60, "Sisa": 50}

        for col in columns:
            self.course_tree.heading(col, text=col)  # Mengatur header kolom
            self.course_tree.column(col, width=column_widths.get(col, 100))  # Mengatur lebar kolom

        # Mengatur warna baris bergantian dan warna khusus untuk mata kuliah penuh
        self.course_tree.tag_configure('oddrow', background='#f8f9fa')                    # Baris ganjil
        self.course_tree.tag_configure('evenrow', background='white')                     # Baris genap
        self.course_tree.tag_configure('full', background='#ffebee', foreground='#c62828') # Mata kuliah penuh (merah)

        # Scrollbar untuk tabel mata kuliah
        scrollbar_course = ttk.Scrollbar(tree_frame, orient="vertical", command=self.course_tree.yview)
        self.course_tree.configure(yscrollcommand=scrollbar_course.set)

        # Menempatkan tabel dan scrollbar
        self.course_tree.pack(side="left", fill="both", expand=True)
        scrollbar_course.pack(side="right", fill="y")

        # Tombol untuk refresh data mata kuliah
        ttk.Button(self.course_frame, text="🔄 Refresh Data", style='Action.TButton', command=self.refresh_courses).pack(pady=10)

    def create_krs_tab(self):
        """
        Membuat tab untuk pengisian KRS
        - Pemilihan mahasiswa
        - Daftar mata kuliah tersedia dan yang sudah diambil
        - Tombol untuk mengambil/membatalkan mata kuliah
        - Informasi total SKS
        """

        # Membuat frame untuk tab KRS
        self.krs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.krs_frame, text="📝 Pengisian KRS")

        # Frame untuk pemilihan mahasiswa
        select_frame = tk.Frame(self.krs_frame, bg='#e8f5e8', relief='raised', bd=2)
        select_frame.pack(fill="x", padx=10, pady=10)

        # Label dan dropdown untuk memilih mahasiswa
        tk.Label(select_frame, text="Pilih Mahasiswa:", font=('Arial', 11, 'bold'), 
                bg='#e8f5e8', fg='#27ae60').grid(row=0, column=0, padx=10, pady=10)
        self.student_combo = ttk.Combobox(select_frame, width=50, state="readonly", font=('Arial', 10))
        self.student_combo.grid(row=0, column=1, padx=10, pady=10)
        # Menghubungkan event pemilihan mahasiswa dengan fungsi on_student_selected
        self.student_combo.bind("<<ComboboxSelected>>", self.on_student_selected)

        # Label untuk menampilkan informasi total SKS
        self.credits_info = tk.Label(select_frame, text="Total SKS: 0 / 24", 
                                   font=('Arial', 11, 'bold'), 
                                   bg='#e8f5e8', fg='#27ae60')
        self.credits_info.grid(row=0, column=2, padx=20, pady=10)

        # Frame utama untuk konten KRS
        main_content_frame = tk.Frame(self.krs_frame)
        main_content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame untuk mata kuliah yang tersedia (kiri)
        available_frame = tk.Frame(main_content_frame, bg='white', relief='solid', bd=2)
        available_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Label judul untuk mata kuliah tersedia
        self.available_title = tk.Label(available_frame, text="📚 Mata Kuliah Tersedia", 
                                      font=('Arial', 11, 'bold'), 
                                      bg='#3498db', fg='white', pady=8)
        self.available_title.pack(fill="x")

        # Frame untuk tabel mata kuliah tersedia
        available_tree_frame = tk.Frame(available_frame, bg='white')
        available_tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Definisi kolom untuk tabel mata kuliah tersedia
        columns = ("Kode", "Nama MK", "SKS", "Jadwal", "Dosen", "Sisa")
        self.available_tree = ttk.Treeview(available_tree_frame, columns=columns, show="headings", 
                                         height=12, style='Custom.Treeview')

        # Mengatur lebar kolom untuk tabel mata kuliah tersedia
        column_widths = {"Kode": 70, "Nama MK": 150, "SKS": 40, "Jadwal": 120, "Dosen": 120, "Sisa": 50}
        for col in columns:
            self.available_tree.heading(col, text=col)
            self.available_tree.column(col, width=column_widths.get(col, 80))

        # Scrollbar untuk tabel mata kuliah tersedia
        scrollbar_available = ttk.Scrollbar(available_tree_frame, orient="vertical", command=self.available_tree.yview)
        self.available_tree.configure(yscrollcommand=scrollbar_available.set)

        self.available_tree.pack(side="left", fill="both", expand=True)
        scrollbar_available.pack(side="right", fill="y")

        # Frame untuk tombol kontrol (tengah)
        button_frame = tk.Frame(main_content_frame, bg='#f8f9fa', width=100)
        button_frame.pack(side="left", fill="y", padx=10)
        button_frame.pack_propagate(False)  # Mempertahankan lebar frame

        # Frame untuk menempatkan tombol di tengah secara vertikal
        center_frame = tk.Frame(button_frame, bg='#f8f9fa')
        center_frame.pack(expand=True)

        # Tombol untuk mengambil mata kuliah
        ttk.Button(center_frame, text="➡️ Ambil", style='Success.TButton', command=self.enroll_course).pack(pady=10)
        # Tombol untuk membatalkan mata kuliah
        ttk.Button(center_frame, text="⬅️ Batal", style='Danger.TButton', command=self.drop_course).pack(pady=10)

        # Frame untuk mata kuliah yang sudah diambil (kanan)
        enrolled_frame = tk.Frame(main_content_frame, bg='white', relief='solid', bd=2)
        enrolled_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # Label judul untuk mata kuliah yang sudah diambil
        enrolled_title = tk.Label(enrolled_frame, text="✅ Mata Kuliah Diambil", 
                                font=('Arial', 11, 'bold'), 
                                bg='#27ae60', fg='white', pady=8)
        enrolled_title.pack(fill="x")

        # Frame untuk tabel mata kuliah yang sudah diambil
        enrolled_tree_frame = tk.Frame(enrolled_frame, bg='white')
        enrolled_tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Tabel untuk mata kuliah yang sudah diambil (menggunakan kolom yang sama)
        self.enrolled_tree = ttk.Treeview(enrolled_tree_frame, columns=columns, show="headings", 
                                        height=12, style='Custom.Treeview')

        for col in columns:
            self.enrolled_tree.heading(col, text=col)
            self.enrolled_tree.column(col, width=column_widths.get(col, 80))

        # Scrollbar untuk tabel mata kuliah yang sudah diambil
        scrollbar_enrolled = ttk.Scrollbar(enrolled_tree_frame, orient="vertical", command=self.enrolled_tree.yview)
        self.enrolled_tree.configure(yscrollcommand=scrollbar_enrolled.set)

        self.enrolled_tree.pack(side="left", fill="both", expand=True)
        scrollbar_enrolled.pack(side="right", fill="y")

    def create_report_tab(self):
        """
        Membuat tab untuk laporan dan cetak KRS
        - Pemilihan mahasiswa untuk laporan
        - Tampilan KRS dalam format yang dapat dicetak
        - Tombol untuk mencetak KRS
        """

        # Membuat frame untuk tab laporan
        self.report_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.report_frame, text="📊 Laporan KRS")

        # Frame untuk pemilihan mahasiswa untuk laporan
        select_frame = tk.Frame(self.report_frame, bg='#f3e5f5', relief='raised', bd=2)
        select_frame.pack(fill="x", padx=10, pady=10)

        # Label dan dropdown untuk memilih mahasiswa
        tk.Label(select_frame, text="Pilih Mahasiswa:", font=('Arial', 11, 'bold'), 
                bg='#f3e5f5', fg='#8e24aa').grid(row=0, column=0, padx=10, pady=10)
        self.report_student_combo = ttk.Combobox(select_frame, width=50, state="readonly", font=('Arial', 10))
        self.report_student_combo.grid(row=0, column=1, padx=10, pady=10)
        # Menghubungkan event pemilihan mahasiswa dengan fungsi generate_report
        self.report_student_combo.bind("<<ComboboxSelected>>", self.generate_report)

        # Frame untuk menampilkan laporan
        report_display_frame = tk.Frame(self.report_frame, bg='white', relief='solid', bd=2)
        report_display_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Label judul untuk laporan KRS
        report_title = tk.Label(report_display_frame, text="📋 Kartu Rencana Studi (KRS)", 
                               font=('Arial', 12, 'bold'), 
                               bg='#9c27b0', fg='white', pady=10)
        report_title.pack(fill="x")

        # Frame untuk widget teks laporan
        text_frame = tk.Frame(report_display_frame, bg='white')
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Widget teks untuk menampilkan laporan KRS
        self.report_text = tk.Text(text_frame, wrap="word", font=("Courier New", 10), 
                                  bg='#fafafa', relief='solid', bd=1)
        # Scrollbar untuk widget teks laporan
        scrollbar_report = ttk.Scrollbar(text_frame, orient="vertical", command=self.report_text.yview)
        self.report_text.configure(yscrollcommand=scrollbar_report.set)

        self.report_text.pack(side="left", fill="both", expand=True)
        scrollbar_report.pack(side="right", fill="y")

        # Tombol untuk mencetak KRS
        ttk.Button(self.report_frame, text="🖨️ Cetak KRS", style='Action.TButton', command=self.print_krs).pack(pady=10)

    # Fungsi-fungsi untuk manajemen mahasiswa
    def tambah_mahasiswa(self):
        """
        Menambahkan mahasiswa baru ke database
        - Mengambil data dari form input
        - Melakukan validasi data
        - Menyimpan ke database
        - Menampilkan pesan sukses/error
        """

        # Mengambil data dari form input
        nim = self.entry_nim.get().strip()           # NIM mahasiswa
        nama = self.entry_nama_mhs.get().strip()     # Nama mahasiswa
        semester = self.entry_semester.get()         # Semester saat ini
        max_sks = self.entry_max_sks.get().strip()   # Maksimal SKS

        # Validasi: semua field harus diisi
        if not all([nim, nama, semester, max_sks]):
            messagebox.showwarning("Input Error", "Semua field harus diisi")
            return

        try:
            # Konversi ke integer untuk validasi
            semester = int(semester)
            max_sks = int(max_sks)

            # Memasukkan data mahasiswa baru ke database
            self.cursor.execute("""
                INSERT INTO students (nim, nama, semester, max_credits) 
                VALUES (?, ?, ?, ?)
            """, (nim, nama, semester, max_sks))
            self.conn.commit()  # Menyimpan perubahan

            # Menampilkan pesan sukses
            messagebox.showinfo("Sukses", "Data mahasiswa berhasil ditambahkan")
            self.clear_student_form()  # Membersihkan form
            self.refresh_students()    # Refresh tampilan data

        except sqlite3.IntegrityError:
            # Error jika NIM sudah ada (constraint UNIQUE)
            messagebox.showerror("Error", "NIM sudah terdaftar")
        except ValueError:
            # Error jika semester atau max_sks bukan angka
            messagebox.showerror("Error", "Semester dan Max SKS harus berupa angka")
        except Exception as e:
            # Error lainnya
            messagebox.showerror("Error", f"Gagal menambah data: {str(e)}")

    def update_mahasiswa(self):
        """
        Mengupdate data mahasiswa yang dipilih
        - Mengecek apakah ada mahasiswa yang dipilih
        - Mengambil data dari form
        - Melakukan update ke database
        """

        # Mengecek apakah ada mahasiswa yang dipilih di tabel
        selected = self.student_tree.selection()
        if not selected:
            messagebox.showwarning("Pilih Data", "Pilih mahasiswa yang akan diupdate")
            return

        # Mengambil ID mahasiswa dari baris yang dipilih
        item = self.student_tree.item(selected[0])
        student_id = item['values'][0]

        # Mengambil data dari form input
        nim = self.entry_nim.get().strip()
        nama = self.entry_nama_mhs.get().strip()
        semester = self.entry_semester.get()
        max_sks = self.entry_max_sks.get().strip()

        # Validasi: semua field harus diisi
        if not all([nim, nama, semester, max_sks]):
            messagebox.showwarning("Input Error", "Semua field harus diisi")
            return

        try:
            # Konversi ke integer
            semester = int(semester)
            max_sks = int(max_sks)

            # Update data mahasiswa di database
            self.cursor.execute("""
                UPDATE students SET nim=?, nama=?, semester=?, max_credits=?
                WHERE id=?
            """, (nim, nama, semester, max_sks, student_id))
            self.conn.commit()

            # Menampilkan pesan sukses
            messagebox.showinfo("Sukses", "Data mahasiswa berhasil diupdate")
            self.clear_student_form()  # Membersihkan form
            self.refresh_students()    # Refresh tampilan data

        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "NIM sudah terdaftar")
        except ValueError:
            messagebox.showerror("Error", "Semester dan Max SKS harus berupa angka")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal update data: {str(e)}")

    def hapus_mahasiswa(self):
        """
        Menghapus mahasiswa yang dipilih dari database
        - Mengecek apakah ada mahasiswa yang dipilih
        - Menampilkan konfirmasi penghapusan
        - Menghapus data enrollment terlebih dahulu (foreign key)
        - Menghapus data mahasiswa
        """

        # Mengecek apakah ada mahasiswa yang dipilih
        selected = self.student_tree.selection()
        if not selected:
            messagebox.showwarning("Pilih Data", "Pilih mahasiswa yang akan dihapus")
            return

        # Mengambil data mahasiswa dari baris yang dipilih
        item = self.student_tree.item(selected[0])
        student_id = item['values'][0]
        nama = item['values'][2]

        # Menampilkan dialog konfirmasi
        result = messagebox.askyesno("Konfirmasi", f"Hapus data mahasiswa {nama}?")
        if result:
            try:
                # Menghapus data enrollment mahasiswa terlebih dahulu (foreign key constraint)
                self.cursor.execute("DELETE FROM enrollments WHERE student_id=?", (student_id,))
                # Menghapus data mahasiswa
                self.cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
                self.conn.commit()

                # Menampilkan pesan sukses
                messagebox.showinfo("Sukses", "Data mahasiswa berhasil dihapus")
                self.clear_student_form()  # Membersihkan form
                self.refresh_students()    # Refresh tampilan data

            except Exception as e:
                messagebox.showerror("Error", f"Gagal hapus data: {str(e)}")

    def select_student(self, event):
        """
        Menangani event pemilihan mahasiswa di tabel
        - Mengisi form input dengan data mahasiswa yang dipilih
        - Memudahkan proses update data
        """

        # Mengecek apakah ada baris yang dipilih
        selected = self.student_tree.selection()
        if selected:
            # Mengambil data dari baris yang dipilih
            item = self.student_tree.item(selected[0])
            values = item['values']

            # Membersihkan form input
            self.entry_nim.delete(0, tk.END)
            self.entry_nama_mhs.delete(0, tk.END)
            self.entry_semester.delete(0, tk.END)
            self.entry_max_sks.delete(0, tk.END)

            # Mengisi form dengan data mahasiswa yang dipilih
            self.entry_nim.insert(0, values[1])        # NIM
            self.entry_nama_mhs.insert(0, values[2])   # Nama
            self.entry_semester.set(values[3])         # Semester
            self.entry_max_sks.insert(0, values[4])    # Max SKS

    def clear_student_form(self):
        """
        Membersihkan form input mahasiswa
        - Menghapus semua isi field
        - Mengembalikan nilai default untuk Max SKS
        """
        self.entry_nim.delete(0, tk.END)
        self.entry_nama_mhs.delete(0, tk.END)
        self.entry_semester.set('')
        self.entry_max_sks.delete(0, tk.END)
        self.entry_max_sks.insert(0, "24")  # Nilai default Max SKS

    def filter_courses(self, event):
        """
        Menangani event perubahan filter semester
        - Memanggil fungsi refresh_courses untuk memfilter data
        """
        self.refresh_courses()

    # Fungsi-fungsi untuk KRS
    def on_student_selected(self, event):
        """
        Menangani event pemilihan mahasiswa di tab KRS
        - Merefresh data mata kuliah tersedia dan yang sudah diambil
        """
        self.refresh_krs_data()

    def enroll_course(self):
        """
        Mendaftarkan mahasiswa ke mata kuliah yang dipilih
        - Validasi pemilihan mahasiswa dan mata kuliah
        - Mengecek kapasitas mata kuliah (warning saja)
        - Mengecek batas SKS mahasiswa
        - Mengecek duplikasi pendaftaran
        - Menyimpan data enrollment ke database
        """

        # Validasi: harus memilih mahasiswa terlebih dahulu
        if not self.student_combo.get():
            messagebox.showwarning("Pilih Mahasiswa", "Pilih mahasiswa terlebih dahulu")
            return

        # Validasi: harus memilih mata kuliah yang akan diambil
        selected = self.available_tree.selection()
        if not selected:
            messagebox.showwarning("Pilih Mata Kuliah", "Pilih mata kuliah yang akan diambil")
            return

        # Mengambil data mahasiswa dari combobox
        student_data = self.student_combo.get().split(" - ")
        student_nim = student_data[0]

        # Mengambil informasi mahasiswa dari database
        self.cursor.execute("SELECT id, max_credits FROM students WHERE nim=?", (student_nim,))
        student_info = self.cursor.fetchone()
        if not student_info:
            messagebox.showerror("Error", "Data mahasiswa tidak ditemukan")
            return

        student_id, max_credits = student_info

        # Mengambil data mata kuliah dari tabel yang dipilih
        item = self.available_tree.item(selected[0])
        course_code = item['values'][0]  # Kode mata kuliah
        course_sks = int(item['values'][2])  # Jumlah SKS

        # Mengambil informasi mata kuliah dari database
        self.cursor.execute("SELECT id, kapasitas, terisi FROM courses WHERE kode_mk=?", (course_code,))
        course_info = self.cursor.fetchone()
        if not course_info:
            messagebox.showerror("Error", "Data mata kuliah tidak ditemukan")
            return

        course_id, kapasitas, terisi = course_info

        # Peringatan jika kapasitas mata kuliah penuh (tapi tetap bisa daftar)
        if terisi >= kapasitas:
            result = messagebox.askyesno("Kapasitas Penuh", 
                f"Mata kuliah {course_code} sudah penuh ({terisi}/{kapasitas}).\nTetap ingin mendaftar?")
            if not result:
                return

        # Mengecek total SKS saat ini
        self.cursor.execute("""
            SELECT SUM(c.sks) FROM enrollments e
            JOIN courses c ON e.course_id = c.id
            WHERE e.student_id = ? AND e.status = 'aktif'
        """, (student_id,))
        current_credits = self.cursor.fetchone()[0] or 0

        # Mengecek apakah total SKS akan melebihi batas maksimal
        if current_credits + course_sks > max_credits:
            messagebox.showwarning("Batas SKS", 
                f"Total SKS akan melebihi batas maksimal ({current_credits + course_sks} > {max_credits})")
            return

        # Mengecek apakah mahasiswa sudah terdaftar di mata kuliah ini
        self.cursor.execute("""
            SELECT id FROM enrollments 
            WHERE student_id=? AND course_id=? AND status='aktif'
        """, (student_id, course_id))
        if self.cursor.fetchone():
            messagebox.showwarning("Sudah Terdaftar", "Mahasiswa sudah terdaftar di mata kuliah ini")
            return

        # Proses pendaftaran mata kuliah
        try:
            # Mendapatkan tanggal dan waktu saat ini
            tanggal_daftar = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Memasukkan data enrollment ke database
            self.cursor.execute("""
                INSERT INTO enrollments (student_id, course_id, tanggal_daftar, status)
                VALUES (?, ?, ?, 'aktif')
            """, (student_id, course_id, tanggal_daftar))

            # Menambah jumlah mahasiswa terisi di mata kuliah
            self.cursor.execute("""
                UPDATE courses SET terisi = terisi + 1 WHERE id = ?
            """, (course_id,))

            self.conn.commit()  # Menyimpan perubahan

            # Menampilkan pesan sukses
            messagebox.showinfo("Sukses", "Berhasil mendaftar mata kuliah")
            self.refresh_krs_data()  # Refresh data KRS
            self.refresh_courses()   # Refresh data mata kuliah

        except Exception as e:
            messagebox.showerror("Error", f"Gagal mendaftar mata kuliah: {str(e)}")

    def drop_course(self):
        """
        Membatalkan pendaftaran mata kuliah yang dipilih
        - Validasi pemilihan mahasiswa dan mata kuliah
        - Menampilkan konfirmasi pembatalan
        - Menghapus data enrollment dari database
        - Mengurangi jumlah mahasiswa terisi di mata kuliah
        """

        # Validasi: harus memilih mahasiswa terlebih dahulu
        if not self.student_combo.get():
            messagebox.showwarning("Pilih Mahasiswa", "Pilih mahasiswa terlebih dahulu")
            return

        # Validasi: harus memilih mata kuliah yang akan dibatalkan
        selected = self.enrolled_tree.selection()
        if not selected:
            messagebox.showwarning("Pilih Mata Kuliah", "Pilih mata kuliah yang akan dibatalkan")
            return

        # Mengambil data mahasiswa
        student_data = self.student_combo.get().split(" - ")
        student_nim = student_data[0]

        # Mengambil ID mahasiswa dari database
        self.cursor.execute("SELECT id FROM students WHERE nim=?", (student_nim,))
        student_info = self.cursor.fetchone()
        if not student_info:
            messagebox.showerror("Error", "Data mahasiswa tidak ditemukan")
            return

        student_id = student_info[0]

        # Mengambil kode mata kuliah dari tabel yang dipilih
        item = self.enrolled_tree.item(selected[0])
        course_code = item['values'][0]

        # Mengambil ID mata kuliah dari database
        self.cursor.execute("SELECT id FROM courses WHERE kode_mk=?", (course_code,))
        course_info = self.cursor.fetchone()
        if not course_info:
            messagebox.showerror("Error", "Data mata kuliah tidak ditemukan")
            return

        course_id = course_info[0]

        # Menampilkan dialog konfirmasi pembatalan
        result = messagebox.askyesno("Konfirmasi", f"Batalkan mata kuliah {course_code}?")
        if result:
            try:
                # Menghapus data enrollment
                self.cursor.execute("""
                    DELETE FROM enrollments 
                    WHERE student_id=? AND course_id=? AND status='aktif'
                """, (student_id, course_id))

                # Mengurangi jumlah mahasiswa terisi di mata kuliah
                self.cursor.execute("""
                    UPDATE courses SET terisi = terisi - 1 WHERE id = ?
                """, (course_id,))

                self.conn.commit()  # Menyimpan perubahan

                # Menampilkan pesan sukses
                messagebox.showinfo("Sukses", "Mata kuliah berhasil dibatalkan")
                self.refresh_krs_data()  # Refresh data KRS
                self.refresh_courses()   # Refresh data mata kuliah

            except Exception as e:
                messagebox.showerror("Error", f"Gagal membatalkan mata kuliah: {str(e)}")

    def generate_report(self, event):
        """
        Menggenerate laporan KRS untuk mahasiswa yang dipilih
        - Mengambil data mahasiswa dan mata kuliah yang diambil
        - Membuat format laporan KRS yang rapi
        - Menampilkan informasi total SKS dan validasi
        """

        # Mengecek apakah ada mahasiswa yang dipilih
        if not self.report_student_combo.get():
            return

        # Mengambil NIM mahasiswa dari combobox
        student_data = self.report_student_combo.get().split(" - ")
        student_nim = student_data[0]

        # Mengambil informasi mahasiswa dari database
        self.cursor.execute("""
            SELECT s.nim, s.nama, s.semester, s.max_credits
            FROM students s WHERE s.nim = ?
        """, (student_nim,))
        student_info = self.cursor.fetchone()

        if not student_info:
            return

        nim, nama, semester, max_credits = student_info

        # Mengambil mata kuliah yang diambil mahasiswa
        self.cursor.execute("""
            SELECT c.kode_mk, c.nama_mk, c.sks, c.jadwal, c.dosen
            FROM enrollments e
            JOIN courses c ON e.course_id = c.id
            JOIN students s ON e.student_id = s.id
            WHERE s.nim = ? AND e.status = 'aktif'
            ORDER BY c.kode_mk
        """, (student_nim,))
        enrolled_courses = self.cursor.fetchall()

        # Mengambil konfigurasi sistem
        academic_year = self.get_config_value('academic_year', '2024/2025')
        current_semester = self.get_config_value('current_semester', 'Ganjil')

        # Membuat format laporan KRS
        report = "=" * 70 + "\n"
        report += "              KARTU RENCANA STUDI (KRS)\n"
        report += "=" * 70 + "\n\n"
        report += f"NIM           : {nim}\n"
        report += f"Nama          : {nama}\n"
        report += f"Semester      : {semester}\n"
        report += f"Tahun Akademik: {academic_year}\n"
        report += f"Semester      : {current_semester}\n\n"

        report += "=" * 70 + "\n"
        report += f"{'No':<3} {'Kode MK':<8} {'Nama Mata Kuliah':<25} {'SKS':<4} {'Jadwal':<20}\n"
        report += "=" * 70 + "\n"

        # Menambahkan daftar mata kuliah ke laporan
        total_sks = 0
        for i, course in enumerate(enrolled_courses, 1):
            kode_mk, nama_mk, sks, jadwal, dosen = course
            total_sks += sks
            # Memotong nama mata kuliah jika terlalu panjang
            nama_mk_truncated = nama_mk[:24] if len(nama_mk) > 24 else nama_mk
            report += f"{i:<3} {kode_mk:<8} {nama_mk_truncated:<25} {sks:<4} {jadwal:<20}\n"

        report += "=" * 70 + "\n"
        report += f"Total SKS yang diambil: {total_sks}\n"
        report += f"Batas Maksimal SKS    : {max_credits}\n"

        # Menambahkan peringatan jika ada masalah dengan total SKS
        if total_sks > max_credits:
            report += "\n⚠️  PERINGATAN: Total SKS melebihi batas maksimal!\n"
        elif total_sks < 12:
            report += "\n⚠️  PERINGATAN: Total SKS kurang dari batas minimal (12 SKS)!\n"

        report += "\n" + "=" * 70 + "\n"
        report += f"Tanggal Cetak: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        report += "=" * 70 + "\n"

        # Menampilkan laporan di widget teks
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(1.0, report)

    def print_krs(self):
        """
        Fungsi untuk mencetak KRS
        - Mengecek apakah ada laporan yang ditampilkan
        - Menampilkan pesan informasi tentang fungsi cetak
        """
        if not self.report_text.get(1.0, tk.END).strip():
            messagebox.showwarning("Tidak Ada Data", "Pilih mahasiswa untuk mencetak KRS")
            return

        # Placeholder untuk fungsi cetak - bisa diintegrasikan dengan printer sistem
        messagebox.showinfo("Cetak KRS", "Fungsi cetak akan diintegrasikan dengan printer sistem")

    # Fungsi-fungsi untuk refresh data
    def refresh_students(self):
        """
        Merefresh data mahasiswa di tabel dan combobox
        - Menghapus data lama dari tabel
        - Mengambil data terbaru dari database
        - Mengisi tabel dengan data terbaru
        - Memperbarui combobox di tab lain
        """

        # Menghapus semua item dari tabel mahasiswa
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)

        # Mengambil data mahasiswa dari database
        self.cursor.execute("""
            SELECT id, nim, nama, semester, max_credits, 
                   COALESCE(created_at, 'N/A') as created_at
            FROM students ORDER BY nim
        """)

        # Mengisi tabel dengan data mahasiswa
        for i, row in enumerate(self.cursor.fetchall()):
            # Menentukan tag untuk warna baris bergantian
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'

            # Memformat tanggal created_at untuk tampilan yang lebih baik
            row_data = list(row)
            if row_data[5] != 'N/A':
                try:
                    date_obj = datetime.fromisoformat(row_data[5].replace('Z', '+00:00'))
                    row_data[5] = date_obj.strftime('%d/%m/%Y')
                except:
                    row_data[5] = 'N/A'

            # Menambahkan baris ke tabel
            self.student_tree.insert("", "end", values=row_data, tags=(tag,))

        # Memperbarui combobox mahasiswa di tab KRS dan laporan
        self.cursor.execute("SELECT nim, nama FROM students ORDER BY nim")
        students = [f"{nim} - {nama}" for nim, nama in self.cursor.fetchall()]

        self.student_combo['values'] = students
        self.report_student_combo['values'] = students

    def refresh_courses(self):
        """
        Merefresh data mata kuliah di tabel
        - Menghapus data lama dari tabel
        - Menerapkan filter semester jika ada
        - Mengambil data mata kuliah dari database
        - Mengisi tabel dengan data terbaru
        - Menandai mata kuliah yang penuh dengan warna berbeda
        """

        # Menghapus semua item dari tabel mata kuliah
        for item in self.course_tree.get_children():
            self.course_tree.delete(item)

        # Membuat query berdasarkan filter semester
        filter_semester = self.filter_semester.get()

        if filter_semester == "Semua" or filter_semester == "":
            # Query untuk menampilkan semua mata kuliah
            query = """
                SELECT kode_mk, nama_mk, sks, semester, jadwal, dosen, kapasitas, terisi,
                       (kapasitas - terisi) as sisa
                FROM courses ORDER BY semester, kode_mk
            """
            params = ()
        else:
            # Query untuk menampilkan mata kuliah berdasarkan semester tertentu
            query = """
                SELECT kode_mk, nama_mk, sks, semester, jadwal, dosen, kapasitas, terisi,
                       (kapasitas - terisi) as sisa
                FROM courses WHERE semester = ? ORDER BY semester, kode_mk
            """
            params = (int(filter_semester),)

        # Mengeksekusi query dan mengisi tabel
        self.cursor.execute(query, params)
        courses = self.cursor.fetchall()

        # Debug: Print jumlah mata kuliah yang ditemukan
        print(f"Filter: {filter_semester}, Mata kuliah ditemukan: {len(courses)}")

        for i, row in enumerate(courses):
            # Menentukan tag untuk warna baris bergantian
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'

            # Mengecek apakah mata kuliah penuh (warna merah)
            if row[7] >= row[6]:  # terisi >= kapasitas
                tag = 'full'

            # Menambahkan baris ke tabel
            self.course_tree.insert("", "end", values=row, tags=(tag,))

    def refresh_krs_data(self):
        """
        Merefresh data KRS untuk mahasiswa yang dipilih
        - Mengambil data mahasiswa yang dipilih
        - Menampilkan mata kuliah tersedia (belum diambil dan tidak penuh)
        - Menampilkan mata kuliah yang sudah diambil
        - Menghitung dan menampilkan total SKS
        """

        # Mengecek apakah ada mahasiswa yang dipilih
        if not self.student_combo.get():
            return

        # Mengambil NIM mahasiswa dari combobox
        student_data = self.student_combo.get().split(" - ")
        student_nim = student_data[0]

        # Mengambil informasi mahasiswa dari database
        self.cursor.execute("SELECT id, max_credits FROM students WHERE nim=?", (student_nim,))
        student_info = self.cursor.fetchone()
        if not student_info:
            return

        student_id, max_credits = student_info

        # Menghapus data lama dari kedua tabel
        for item in self.available_tree.get_children():
            self.available_tree.delete(item)
        for item in self.enrolled_tree.get_children():
            self.enrolled_tree.delete(item)

        # Mengambil ID mata kuliah yang sudah diambil mahasiswa
        self.cursor.execute("""
            SELECT course_id FROM enrollments 
            WHERE student_id=? AND status='aktif'
        """, (student_id,))
        enrolled_course_ids = [row[0] for row in self.cursor.fetchall()]

        # Mengambil semester mahasiswa untuk filter mata kuliah
        self.cursor.execute("SELECT semester FROM students WHERE id=?", (student_id,))
        student_semester = self.cursor.fetchone()[0]

        # Menentukan filter semester berdasarkan ganjil/genap
        if student_semester % 2 == 1:  # Semester ganjil (1, 3, 5, 7)
            # Tampilkan mata kuliah semester ganjil
            semester_condition = "semester IN (1, 3, 5, 7)"
        else:  # Semester genap (2, 4, 6, 8)
            # Tampilkan mata kuliah semester genap
            semester_condition = "semester IN (2, 4, 6, 8)"

        # Mengambil mata kuliah yang tersedia (belum diambil dan sesuai semester)
        # Tampilkan semua mata kuliah yang sesuai dengan semester ganjil/genap
        if enrolled_course_ids:
            # Jika ada mata kuliah yang sudah diambil, exclude dari daftar tersedia
            placeholders = ','.join(['?'] * len(enrolled_course_ids))
            self.cursor.execute(f"""
                SELECT kode_mk, nama_mk, sks, jadwal, dosen, (kapasitas - terisi) as sisa
                FROM courses 
                WHERE id NOT IN ({placeholders}) AND {semester_condition}
                ORDER BY semester, kode_mk
            """, enrolled_course_ids)
        else:
            # Jika belum ada mata kuliah yang diambil, tampilkan semua yang sesuai semester
            self.cursor.execute(f"""
                SELECT kode_mk, nama_mk, sks, jadwal, dosen, (kapasitas - terisi) as sisa
                FROM courses 
                WHERE {semester_condition}
                ORDER BY semester, kode_mk
            """)

        # Mengisi tabel mata kuliah tersedia
        for course in self.cursor.fetchall():
            self.available_tree.insert("", "end", values=course)

        # Memperbarui judul dengan informasi filter semester
        semester_type = "Ganjil" if student_semester % 2 == 1 else "Genap"
        semester_list = "1,3,5,7" if student_semester % 2 == 1 else "2,4,6,8"
        self.available_title.config(text=f"📚 Mata Kuliah Tersedia (Semester {semester_type}: {semester_list})")

        # Mengambil mata kuliah yang sudah diambil mahasiswa
        self.cursor.execute("""
            SELECT c.kode_mk, c.nama_mk, c.sks, c.jadwal, c.dosen, '-' as sisa
            FROM enrollments e
            JOIN courses c ON e.course_id = c.id
            WHERE e.student_id=? AND e.status='aktif'
            ORDER BY c.kode_mk
        """, (student_id,))

        # Mengisi tabel mata kuliah yang sudah diambil dan menghitung total SKS
        total_sks = 0
        for course in self.cursor.fetchall():
            self.enrolled_tree.insert("", "end", values=course)
            total_sks += course[2]  # course[2] adalah jumlah SKS

        # Memperbarui informasi total SKS dengan warna yang sesuai
        color = '#27ae60' if total_sks <= max_credits else '#e74c3c'  # Hijau jika OK, merah jika over
        self.credits_info.config(text=f"Total SKS: {total_sks} / {max_credits}", fg=color)

    def refresh_all_data(self):
        """
        Merefresh semua data di aplikasi
        - Memanggil fungsi refresh untuk mahasiswa
        - Memanggil fungsi refresh untuk mata kuliah
        """
        self.refresh_students()
        # Pastikan filter semester diset ke "Semua" saat refresh pertama kali
        if hasattr(self, 'filter_semester'):
            self.filter_semester.set("Semua")
        self.refresh_courses()

    def __del__(self):
        """
        Destruktor untuk menutup koneksi database
        - Memastikan koneksi database ditutup dengan benar saat aplikasi selesai
        """
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    """
    Fungsi utama untuk menjalankan aplikasi
    - Membuat jendela utama Tkinter
    - Menginisialisasi aplikasi KRS
    - Memulai event loop GUI
    """
    root = tk.Tk()           # Membuat jendela utama
    app = KRSApplication(root)  # Menginisialisasi aplikasi KRS
    root.mainloop()          # Memulai event loop GUI

# Menjalankan aplikasi jika file ini dieksekusi langsung
if __name__ == "__main__":
    main()
