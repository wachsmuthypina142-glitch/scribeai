import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), '..', 'scribeai.db')
db_path = os.path.abspath(db_path)
print('Database path:', db_path)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 获取现有列
cursor.execute('PRAGMA table_info(contents)')
content_cols = [row[1] for row in cursor.fetchall()]
print('Content columns:', content_cols)

# 添加缺失的列到 contents 表
new_cols = {
    'category_id': 'TEXT',
    'file_path': 'TEXT',
    'file_type': 'TEXT',
    'entities': 'TEXT'
}

for col, col_type in new_cols.items():
    if col not in content_cols:
        cursor.execute(f'ALTER TABLE contents ADD COLUMN {col} {col_type}')
        print(f'Added column: {col}')

# 创建 categories 表
cursor.execute('''
CREATE TABLE IF NOT EXISTS categories (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    parent_id TEXT,
    color TEXT DEFAULT '#6366f1',
    user_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id)
)
''')
print('Created/verified categories table')

# 创建 relations 表
cursor.execute('''
CREATE TABLE IF NOT EXISTS relations (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    relation_type TEXT DEFAULT 'related',
    note TEXT,
    user_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES contents(id),
    FOREIGN KEY (target_id) REFERENCES contents(id)
)
''')
print('Created/verified relations table')

conn.commit()
conn.close()
print('Migration completed!')

# 创建 uploads 目录
upload_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
upload_dir = os.path.abspath(upload_dir)
os.makedirs(upload_dir, exist_ok=True)
print(f'Uploads directory: {upload_dir}')
