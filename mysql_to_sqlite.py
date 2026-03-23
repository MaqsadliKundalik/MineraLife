"""
MySQL dump faylni SQLite db.sqlite3 ga import qiluvchi script.
Ishlatish: python mysql_to_sqlite.py
"""

import re
import sqlite3
import os
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SQL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "zahira_nusxa (1).sql")
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db.sqlite3")


# ─── Yordamchi: satrlarga bo'lib, statementlarni ajratish ────────────────────

def split_statements(sql: str) -> list[str]:
    """Semicolonni string ichida ham to'g'ri hisoblab, statementlarni ajratadi."""
    statements = []
    current = []
    in_string = False
    string_char = None
    i = 0
    while i < len(sql):
        c = sql[i]
        if in_string:
            current.append(c)
            if c == "\\" :
                # escape
                i += 1
                if i < len(sql):
                    current.append(sql[i])
            elif c == string_char:
                in_string = False
        else:
            if c in ("'", '"'):
                in_string = True
                string_char = c
                current.append(c)
            elif c == ";":
                stmt = "".join(current).strip()
                if stmt:
                    statements.append(stmt)
                current = []
            else:
                current.append(c)
        i += 1
    last = "".join(current).strip()
    if last:
        statements.append(last)
    return statements


# ─── CREATE TABLE konvertatsiyasi ────────────────────────────────────────────

def convert_create_table(stmt: str) -> str:
    # Backtick olib tashlash
    stmt = stmt.replace("`", "")

    # Jadval nomini olish
    m = re.match(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\S+)\s*\(", stmt, re.IGNORECASE)
    if not m:
        return stmt

    # '(' dan ')' gacha bo'lgan kolonlar blokirovkasini ajratish
    paren_start = stmt.index("(")
    # Oxirgi ')' — jadval yopuvchi qavs
    paren_end = stmt.rindex(")")
    header = stmt[:paren_start + 1]
    columns_block = stmt[paren_start + 1:paren_end]
    # Jadval parametrlari (ENGINE, CHARSET, ...) — kerak emas
    # footer = stmt[paren_end:]

    # Har bir kolonnni alohida parse qilish
    # Vergul bo'yicha split — lekin qavs ichidagi vergulga e'tibor bermaslik
    col_defs = []
    depth = 0
    current = []
    for ch in columns_block:
        if ch == "(":
            depth += 1
            current.append(ch)
        elif ch == ")":
            depth -= 1
            current.append(ch)
        elif ch == "," and depth == 0:
            col_defs.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    if "".join(current).strip():
        col_defs.append("".join(current).strip())

    new_cols = []
    for col in col_defs:
        col_stripped = col.strip()

        # Tashlab yuborilishi kerak bo'lgan satrlar
        if re.match(r"KEY\s+", col_stripped, re.IGNORECASE):
            continue
        if re.match(r"CONSTRAINT\s+", col_stripped, re.IGNORECASE):
            continue

        # UNIQUE KEY name (cols) -> UNIQUE (cols)
        m_uq = re.match(r"UNIQUE\s+KEY\s+\w+\s*(\([^)]+\))", col_stripped, re.IGNORECASE)
        if m_uq:
            new_cols.append(f"UNIQUE {m_uq.group(1)}")
            continue

        # AUTO_INCREMENT -> AUTOINCREMENT
        col_stripped = re.sub(r"\bAUTO_INCREMENT\b", "AUTOINCREMENT", col_stripped, flags=re.IGNORECASE)

        # int/bigint NOT NULL AUTOINCREMENT -> INTEGER NOT NULL
        # (SQLite da AUTOINCREMENT faqat `INTEGER PRIMARY KEY AUTOINCREMENT` shaklida)
        col_stripped = re.sub(
            r"\b(int|bigint)\b",
            "INTEGER",
            col_stripped,
            flags=re.IGNORECASE,
        )

        # Ortiqcha MySQL type modifikatorlarini olib tashlash
        col_stripped = re.sub(r"\bUNSIGNED\b", "", col_stripped, flags=re.IGNORECASE)
        col_stripped = re.sub(r"\bZEROFILL\b", "", col_stripped, flags=re.IGNORECASE)
        col_stripped = re.sub(r"\bCHARACTER\s+SET\s+\w+\b", "", col_stripped, flags=re.IGNORECASE)
        col_stripped = re.sub(r"\bCOLLATE\s+\w+\b", "", col_stripped, flags=re.IGNORECASE)
        col_stripped = re.sub(r"\bCOMMENT\s+'[^']*'", "", col_stripped, flags=re.IGNORECASE)
        col_stripped = col_stripped.strip()

        new_cols.append(col_stripped)

    result = header + "\n  " + ",\n  ".join(new_cols) + "\n)"
    return result


# ─── Asosiy konvertatsiya ────────────────────────────────────────────────────

def preprocess(raw: str) -> str:
    # MySQL direktivalarini olib tashlash
    raw = re.sub(r"/\*!.*?\*/", "", raw, flags=re.DOTALL)
    raw = re.sub(r"/\*.*?\*/", "", raw, flags=re.DOTALL)
    # -- izohlar
    raw = re.sub(r"--[^\n]*", "", raw)
    # LOCK / UNLOCK TABLES
    raw = re.sub(r"LOCK\s+TABLES\s+[^;]+;", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"UNLOCK\s+TABLES\s*;", "", raw, flags=re.IGNORECASE)
    # SET statements
    raw = re.sub(r"SET\s+[^;]+;", "", raw, flags=re.IGNORECASE)
    return raw


def convert(raw: str) -> list[str]:
    raw = preprocess(raw)
    stmts = split_statements(raw)

    result = []
    for stmt in stmts:
        stmt = stmt.strip()
        if not stmt:
            continue

        upper = stmt.upper().lstrip()

        if upper.startswith("CREATE TABLE"):
            stmt = convert_create_table(stmt)
        elif upper.startswith("INSERT") or upper.startswith("DROP") or upper.startswith("DELETE"):
            stmt = stmt.replace("`", "")
        else:
            # Boshqa statementlarni o'tkazib yuboramiz
            continue

        result.append(stmt)
    return result


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    if not os.path.exists(SQL_FILE):
        print(f"SQL fayl topilmadi: {SQL_FILE}")
        sys.exit(1)

    print(f"O'qilmoqda: {SQL_FILE}")
    with open(SQL_FILE, "r", encoding="utf-8", errors="replace") as f:
        raw_sql = f.read()

    print("Konvertatsiya qilinmoqda...")
    statements = convert(raw_sql)
    print(f"Jami {len(statements)} ta statement topildi.")

    if os.path.exists(DB_FILE):
        backup = DB_FILE + ".bak"
        import shutil
        shutil.copy2(DB_FILE, backup)
        print(f"Eski baza zahiralandi: {backup}")

    print(f"SQLite bazaga yozilmoqda: {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = OFF;")
    conn.execute("PRAGMA journal_mode = WAL;")

    errors = []
    success = 0
    for stmt in statements:
        try:
            conn.execute(stmt)
            success += 1
        except Exception as e:
            errors.append((stmt[:150], str(e)))

    conn.commit()
    conn.close()

    print(f"\nMuvaffaqiyatli: {success} ta statement")
    if errors:
        print(f"Xatoliklar: {len(errors)} ta")
        for stmt_preview, err in errors[:30]:
            print(f"  [{err}]\n  {stmt_preview!r}\n")
    else:
        print("Hammasi muvaffaqiyatli bajarildi!")


if __name__ == "__main__":
    main()
