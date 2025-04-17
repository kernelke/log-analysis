import mmap
import re
import sqlite3
import bisect
import os
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


class LogIndexer:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.conn = None
        self._init_db()

        # 预编译正则表达式
        self.timestamp_pattern = re.compile(
            rb'^(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}\.\d{3})',
            re.MULTILINE
        )
        self.keyword_pattern = re.compile(rb'\b[A-Z][a-zA-Z0-9_:]+\b')

    def _init_db(self):
        """初始化数据库结构"""
        with self.db_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS keywords (
                    id INTEGER PRIMARY KEY,
                    keyword TEXT UNIQUE
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY,
                    keyword_id INTEGER,
                    timestamp REAL,
                    position INTEGER,
                    FOREIGN KEY(keyword_id) REFERENCES keywords(id)
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)")

    @contextmanager
    def db_connection(self):
        """数据库连接上下文管理器"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.execute("PRAGMA journal_mode=WAL")  # 启用WAL模式提升性能
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

    @contextmanager
    def _mmap_file(self, file_path: Path):
        """内存映射文件上下文"""
        try:
            with file_path.open('rb') as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mmap_obj:
                    yield mmap_obj
        except (IOError, ValueError) as e:
            logger.error(f"File mapping error: {str(e)}")
            raise

    def index_file(self, file_path: str):
        """索引日志文件"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with self._mmap_file(path) as mmap_obj:
                for match in self.timestamp_pattern.finditer(mmap_obj):
                    self._process_match(match, mmap_obj, path)
        except Exception as e:
            logger.error(f"Indexing failed for {file_path}: {str(e)}")
            raise

    def _process_match(self, match, mmap_obj, file_path):
        """处理单个日志条目"""
        ts_str = match.group(1).decode('utf-8')
        pos = match.start()

        try:
            # 时间戳转换（适配格式 DD.MM.YYYY HH:MM:SS.mmm）
            ts = datetime.strptime(ts_str, "%d.%m.%Y %H:%M:%S.%f").timestamp()
        except ValueError:
            logger.warning(f"Invalid timestamp format at position {pos}: {ts_str}")
            return

        # 提取关键词（优化性能的字节处理）
        line_bytes = mmap_obj[pos:pos + 500]
        keywords = {kw.decode('utf-8')
                    for kw in self.keyword_pattern.findall(line_bytes)
                    if len(kw) < 50}  # 防止过长异常值

        # 批量插入优化
        with self.db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("BEGIN TRANSACTION")

            # 插入关键词
            keyword_ids = {}
            for kw in keywords:
                cursor.execute(
                    "INSERT OR IGNORE INTO keywords (keyword) VALUES (?)",
                    (kw,)
                )
                cursor.execute(
                    "SELECT id FROM keywords WHERE keyword = ?",
                    (kw,)
                )
                keyword_ids[kw] = cursor.fetchone()[0]

            # 插入事件
            for kw, kw_id in keyword_ids.items():
                cursor.execute(
                    "INSERT INTO events (keyword_id, timestamp, position) "
                    "VALUES (?, ?, ?)",
                    (kw_id, ts, pos)
                )

            conn.commit()

    def get_sequence(self, keywords: list) -> list:
        """获取关键词序列"""
        result = []
        prev_time = None

        with self.db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            for kw in keywords:
                cursor.execute("""
                    SELECT e.timestamp, e.position 
                    FROM events e
                    JOIN keywords k ON e.keyword_id = k.id
                    WHERE k.keyword = ?
                    ORDER BY e.timestamp
                """, (kw,))

                events = [dict(row) for row in cursor.fetchall()]

                if not events:
                    result.append({'keyword': kw, 'status': 'missing'})
                    continue

                if prev_time is None:
                    selected = events[0]
                else:
                    # 使用bisect优化时间查找
                    timestamps = [e['timestamp'] for e in events]
                    idx = bisect.bisect_right(timestamps, prev_time)
                    if idx >= len(events):
                        result.append({'keyword': kw, 'status': 'missing'})
                        continue
                    selected = events[idx]

                result.append({
                    'keyword': kw,
                    'timestamp': selected['timestamp'],
                    'position': selected['position'],
                    'delta': selected['timestamp'] - prev_time if prev_time else 0
                })
                prev_time = selected['timestamp']

        return result


# 测试用例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # 初始化索引器
    indexer = LogIndexer("test_index.db")

    # 索引测试文件
    test_log = "sample.log"
    Path(test_log).write_text("""
23.04.2024 12:34:56.789 [INFO] Process START initiated
23.04.2024 12:35:00.123 [DEBUG] ComponentA: Initialization complete
23.04.2024 12:35:02.456 [ERROR] ModuleB: Failed to connect
""")

    indexer.index_file(test_log)

    # 查询测试
    sequence = indexer.get_sequence(["START", "ComponentA", "ModuleB"])
    print("Test sequence:", sequence)