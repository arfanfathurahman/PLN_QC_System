import sqlite3
import pandas as pd
import json

DB_NAME = "qc_database.db"


# ==========================================================
# KONEKSI DATABASE
# ==========================================================
def get_connection():
    """Membuat koneksi ke database SQLite"""
    return sqlite3.connect(DB_NAME)


# ==========================================================
# MEMBUAT DATABASE & TABEL
# ==========================================================
def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    # TABEL BARU UNTUK DRAFT/AUTOSAVE & FOTO PHB TR
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS phbtr_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        no_sn TEXT UNIQUE,
        teknisi TEXT,
        status_selesai TEXT,
        data_json TEXT,
        foto_path TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # TABEL ONEPOST
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS onepost (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tanggal DATETIME DEFAULT CURRENT_TIMESTAMP,
        no_sn TEXT NOT NULL,
        teknisi TEXT,
        mode TEXT,
        durasi_jam REAL,
        kap_aktual REAL,
        soh REAL,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # TABEL PHB TR
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS phbtr (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tanggal DATETIME DEFAULT CURRENT_TIMESTAMP,
        no_sn TEXT NOT NULL,
        teknisi TEXT NOT NULL,
        tipe TEXT,
        p_dielektrik TEXT,
        p_diameter TEXT,
        p_isolasi TEXT,
        p_mekanis TEXT,
        status TEXT
    )
    """)

    # TABEL PMCB
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pmcb (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tanggal DATETIME DEFAULT CURRENT_TIMESTAMP,
        no_sn TEXT NOT NULL,
        teknisi TEXT NOT NULL,
        tipe TEXT,
        p_dielektrik TEXT,
        p_diameter TEXT,
        p_isolasi TEXT,
        p_mekanis TEXT,
        p_cat TEXT,
        status TEXT
    )
    """)

    # TABEL LOG SHEET ONEPOST
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS onepost_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        no_sn TEXT NOT NULL,
        teknisi TEXT NOT NULL,
        mode TEXT NOT NULL,
        keterangan TEXT,
        tanggal_uji TEXT,
        waktu TEXT,
        v_bms REAL,
        i_bms REAL,
        soc REAL,
        suhu TEXT,
        v_avg REAL,
        i_avg REAL,
        p_tot REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # TABEL HISTORY MULTI-UNIT (digunakan oleh unit_manager.py)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS onepost_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        no_sn TEXT NOT NULL,
        form_key TEXT NOT NULL,
        tab_name TEXT,
        field_name TEXT,
        old_value TEXT,
        new_value TEXT,
        changed_by TEXT DEFAULT 'inspector',
        changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        snapshot_json TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS phbtr_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        no_sn TEXT NOT NULL,
        form_key TEXT NOT NULL,
        tab_name TEXT,
        field_name TEXT,
        old_value TEXT,
        new_value TEXT,
        changed_by TEXT DEFAULT 'inspector',
        changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        snapshot_json TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pmcb_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        no_sn TEXT NOT NULL,
        form_key TEXT NOT NULL,
        tab_name TEXT,
        field_name TEXT,
        old_value TEXT,
        new_value TEXT,
        changed_by TEXT DEFAULT 'inspector',
        changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        snapshot_json TEXT
    )
    """)

    conn.commit()
    conn.close()


# ==========================================================
# CRUD ONEPOST
# ==========================================================
def simpan_onepost(no_sn, teknisi, mode, durasi_jam, kap_aktual, soh, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO onepost (no_sn, teknisi, mode, durasi_jam, kap_aktual, soh, status)
    VALUES (?,?,?,?,?,?,?)
    """, (no_sn, teknisi, mode, durasi_jam, kap_aktual, soh, status))
    conn.commit()
    conn.close()


def simpan_onepost_log(no_sn, teknisi, mode, keterangan, tanggal_uji, waktu, v_bms, i_bms, soc, suhu, v_avg, i_avg, p_tot):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO onepost_log (
        no_sn, teknisi, mode, keterangan, tanggal_uji, waktu,
        v_bms, i_bms, soc, suhu, v_avg, i_avg, p_tot
    )
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (no_sn, teknisi, mode, keterangan, tanggal_uji, waktu, v_bms, i_bms, soc, suhu, v_avg, i_avg, p_tot))
    conn.commit()
    conn.close()


def ambil_onepost():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM onepost ORDER BY id DESC", conn)
    conn.close()
    return df


def ambil_semua_onepost():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM onepost_log ORDER BY id DESC", conn)
    conn.close()
    return df


def ambil_onepost_by_sn(no_sn):
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM onepost_log WHERE no_sn=? ORDER BY created_at ASC",
        conn,
        params=(no_sn,)
    )
    conn.close()
    return df


def ambil_onepost_by_mode(mode, no_sn=None):
    """Mendukung pencarian berdasarkan mode saja atau mode + Serial Number"""
    conn = get_connection()
    if no_sn:
        query = "SELECT * FROM onepost_log WHERE mode=? AND no_sn=? ORDER BY created_at ASC"
        df = pd.read_sql_query(query, conn, params=(mode, no_sn))
    else:
        query = "SELECT * FROM onepost_log WHERE mode=? ORDER BY created_at ASC"
        df = pd.read_sql_query(query, conn, params=(mode,))
    conn.close()
    return df


def total_onepost_log():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM onepost_log")
    total = cursor.fetchone()[0]
    conn.close()
    return total


def hapus_onepost(id_data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM onepost WHERE id=?", (id_data,))
    conn.commit()
    conn.close()


def update_onepost(id_data, no_sn, teknisi, mode, durasi_jam, kap_aktual, soh, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE onepost
    SET no_sn=?, teknisi=?, mode=?, durasi_jam=?, kap_aktual=?, soh=?, status=?
    WHERE id=?
    """, (no_sn, teknisi, mode, durasi_jam, kap_aktual, soh, status, id_data))
    conn.commit()
    conn.close()


# ==========================================================
# CRUD PHB TR
# ==========================================================
def simpan_phbtr(no_sn, teknisi, tipe, p_dielektrik, p_diameter, p_isolasi, p_mekanis, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO phbtr (no_sn, teknisi, tipe, p_dielektrik, p_diameter, p_isolasi, p_mekanis, status)
    VALUES (?,?,?,?,?,?,?,?)
    """, (no_sn, teknisi, tipe, p_dielektrik, p_diameter, p_isolasi, p_mekanis, status))
    conn.commit()
    conn.close()


def ambil_phbtr():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM phbtr ORDER BY id DESC", conn)
    conn.close()
    return df


def hapus_phbtr(id_data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM phbtr WHERE id=?", (id_data,))
    conn.commit()
    conn.close()


def update_phbtr(id_data, no_sn, teknisi, tipe, p_dielektrik, p_diameter, p_isolasi, p_mekanis, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE phbtr
    SET no_sn=?, teknisi=?, tipe=?, p_dielektrik=?, p_diameter=?, p_isolasi=?, p_mekanis=?, status=?
    WHERE id=?
    """, (no_sn, teknisi, tipe, p_dielektrik, p_diameter, p_isolasi, p_mekanis, status, id_data))
    conn.commit()
    conn.close()


# ==========================================================
# CRUD PMCB
# ==========================================================
def simpan_pmcb(no_sn, teknisi, tipe, p_dielektrik, p_diameter, p_isolasi, p_mekanis, p_cat, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO pmcb (no_sn, teknisi, tipe, p_dielektrik, p_diameter, p_isolasi, p_mekanis, p_cat, status)
    VALUES (?,?,?,?,?,?,?,?,?)
    """, (no_sn, teknisi, tipe, p_dielektrik, p_diameter, p_isolasi, p_mekanis, p_cat, status))
    conn.commit()
    conn.close()


def ambil_pmcb():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM pmcb ORDER BY id DESC", conn)
    conn.close()
    return df


def hapus_pmcb(id_data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pmcb WHERE id=?", (id_data,))
    conn.commit()
    conn.close()


def update_pmcb(id_data, no_sn, teknisi, tipe, p_dielektrik, p_diameter, p_isolasi, p_mekanis, p_cat, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE pmcb
    SET no_sn=?, teknisi=?, tipe=?, p_dielektrik=?, p_diameter=?, p_isolasi=?, p_mekanis=?, p_cat=?, status=?
    WHERE id=?
    """, (no_sn, teknisi, tipe, p_dielektrik, p_diameter, p_isolasi, p_mekanis, p_cat, status, id_data))
    conn.commit()
    conn.close()


# ==========================================================
# DRAFT PHB TR
# ==========================================================
def simpan_phbtr_draft(no_sn, teknisi, status_selesai, data_dict, foto_filename=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO phbtr_data (no_sn, teknisi, status_selesai, data_json, foto_path)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(no_sn) DO UPDATE SET
        teknisi=excluded.teknisi,
        status_selesai=excluded.status_selesai,
        data_json=excluded.data_json,
        foto_path=COALESCE(NULLIF(excluded.foto_path, ''), phbtr_data.foto_path),
        updated_at=CURRENT_TIMESTAMP
    """, (no_sn, teknisi, status_selesai, json.dumps(data_dict), foto_filename))
    conn.commit()
    conn.close()


def ambil_semua_phbtr_draft():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM phbtr_data ORDER BY updated_at DESC", conn)
    conn.close()
    return df


# ==========================================================
# DASHBOARD SUMMARY
# ==========================================================
def total_onepost():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM onepost_log")
    total = cursor.fetchone()[0]
    conn.close()
    return total


def total_phbtr():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM phbtr")
    total = cursor.fetchone()[0]
    conn.close()
    return total


def total_pmcb():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM pmcb")
    total = cursor.fetchone()[0]
    conn.close()
    return total


# ==========================================================
# TEST DATABASE
# ==========================================================
if __name__ == "__main__":
    init_db()
    print("✅ Database berhasil dibuat & diinisialisasi.")
    print("DATABASE LOADED")
