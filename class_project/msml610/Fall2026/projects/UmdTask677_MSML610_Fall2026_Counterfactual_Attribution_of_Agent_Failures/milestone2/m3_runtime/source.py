"""Read recorded inputs without creating tables, WALs, or new branches."""
from pathlib import Path
import gzip
import hashlib
import json
import sqlite3

from .policies import canonical


class RecordedStore:
    def __init__(self, root):
        self.root = Path(root)
        path = self.root / "manifest.sqlite"
        wal = path.with_name(path.name + "-wal")
        if wal.exists() and wal.stat().st_size:
            raise RuntimeError("Checkpoint the source WAL before an immutable read")
        self.db = sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro&immutable=1", uri=True)
        self.db.row_factory = sqlite3.Row

    def close(self):
        self.db.close()

    def query(self, sql, args=()):
        return [dict(r) for r in self.db.execute(sql, args).fetchall()]

    def snapshot(self, sid):
        return self.query("select * from snapshots where id=?", (sid,))[0]

    def snapshots(self, bid):
        return self.query("select * from snapshots where branch_id=? order by seq", (bid,))

    def branch(self, bid):
        return self.query("select * from branches where branch_id=?", (bid,))[0]

    def get_blob(self, kind, key):
        path = self.root / "blobs" / kind / f"{key}.json"
        data = path.read_bytes() if path.exists() else gzip.decompress(path.with_suffix(".json.gz").read_bytes())
        if hashlib.sha256(data).hexdigest() != key:
            raise RuntimeError("Recorded blob identity mismatch")
        return data

    def read_tape(self, bid):
        rows = [json.loads(s) for s in (self.root/"tapes"/f"{bid}.jsonl").read_text().splitlines()]
        prev = None
        for i, e in enumerate(rows):
            body = {k:v for k,v in e.items() if k != "hash"}
            if e["prev"] != prev or e["seq"] != i or hashlib.sha256(canonical(body)).hexdigest() != e["hash"]:
                raise RuntimeError("Recorded tape chain mismatch")
            prev = e["hash"]
        return rows
