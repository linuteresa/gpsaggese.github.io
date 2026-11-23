"""Shared model-aware request reservations; this class grants no run authorization."""
from contextlib import contextmanager
from pathlib import Path
import re
import sqlite3
import time
import uuid

from .policies import AccountingError, NANO, canonical, normalize_usage, policy_for, price_usage, registry_document


class BudgetBusy(RuntimeError):
    pass


class BudgetExhausted(RuntimeError):
    pass


class Budget:
    def __init__(self, path: Path, cap_nano: int):
        if not isinstance(cap_nano, int) or isinstance(cap_nano, bool) or cap_nano < 0:
            raise ValueError("Cap must be a nonnegative integer number of nanodollars")
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        registry = canonical(registry_document()).decode()
        with self.connection() as db:
            tables = {r[0] for r in db.execute("select name from sqlite_master where type='table'")}
            if tables - {"budget_settings", "requests"}:
                raise AccountingError("Refusing to mix an M3 ledger with another database")
            db.executescript("""
                create table if not exists budget_settings (id integer primary key, cap integer not null, registry text not null);
                create table if not exists requests (
                  id text primary key, job_id text not null, model text not null,
                  request_hash text not null, created real not null, maximum integer not null,
                  liability integer not null, status text not null, response_model text,
                  response_id text, usage_json text, error_type text, settled real);
            """)
            db.execute("begin immediate")
            db.execute("insert or ignore into budget_settings values (1,?,?)", (cap_nano, registry))
            row = db.execute("select cap,registry from budget_settings where id=1").fetchone()
            if tuple(row) != (cap_nano, registry):
                db.rollback()
                raise AccountingError("An existing cap or model-price registry cannot change")
            db.commit()

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=120, isolation_level=None)
        db.row_factory = sqlite3.Row
        try:
            yield db
        finally:
            db.close()

    def reserve(self, job_id, model, request_hash):
        p = policy_for(model)
        if not job_id or not re.fullmatch(r"[0-9a-f]{64}", request_hash):
            raise AccountingError("A job ID and canonical request SHA-256 are required")
        with self.connection() as db:
            db.execute("begin immediate")
            cap = db.execute("select cap from budget_settings").fetchone()[0]
            total, active = db.execute("select coalesce(sum(liability),0),coalesce(sum(status='reserved'),0) from requests").fetchone()
            if total + p.maximum > cap:
                db.rollback()
                if active:
                    raise BudgetBusy("Other reservations must settle first")
                raise BudgetExhausted("The cap cannot cover another maximum-cost request")
            token = uuid.uuid4().hex
            db.execute("insert into requests (id,job_id,model,request_hash,created,maximum,liability,status) values (?,?,?,?,?,?,?,'reserved')",
                       (token, job_id, model, request_hash, time.time(), p.maximum, p.maximum))
            db.commit()
            return token

    def settle(self, token, *, usage=None, response_model=None, response_id=None,
               rejection_status=None, error_type=None):
        error = None
        with self.connection() as db:
            db.execute("begin immediate")
            row = db.execute("select * from requests where id=?", (token,)).fetchone()
            if not row or row["status"] != "reserved":
                db.rollback()
                raise AccountingError("Unknown or already-settled reservation")
            cost, status, normalized = row["maximum"], "uncertain_maximum_retained", None
            try:
                if rejection_status is not None:
                    if rejection_status not in {400, 401, 403, 404, 413, 422, 429}:
                        raise AccountingError("Rejection is not known to precede inference")
                    if usage is not None or response_model is not None:
                        raise AccountingError("A billed reply cannot be released as a free rejection")
                    cost, status = 0, "rejected_before_inference"
                elif usage is not None:
                    p = policy_for(row["model"])
                    if response_model not in p.response_models:
                        raise AccountingError("Actual response model differs from the pinned request model")
                    normalized = normalize_usage(usage, p)
                    cost = price_usage(row["model"], usage)
                    if cost > row["maximum"]:
                        raise AccountingError("Actual usage exceeds its reservation")
                    status = "settled"
                elif error_type is None:
                    raise AccountingError("A successful reply requires usage and actual model identity")
            except (AccountingError, TypeError, AttributeError) as exc:
                cost, status, error = row["maximum"], "uncertain_maximum_retained", AccountingError(str(exc))
            kind = type(error).__name__ if error else error_type
            if kind and not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.]{0,80}", kind):
                kind = "UnclassifiedFailure"
            db.execute("update requests set liability=?,status=?,response_model=?,response_id=?,usage_json=?,error_type=?,settled=? where id=?",
                       (cost, status, response_model, response_id, canonical(normalized).decode() if normalized else None, kind, time.time(), token))
            db.commit()
        if error:
            raise error
        return cost

    def summary(self):
        with self.connection() as db:
            cap = db.execute("select cap from budget_settings").fetchone()[0]
            rows = [dict(r) for r in db.execute("select status,count(*) requests,sum(liability) nanodollars from requests group by status")]
        total = sum(r["nanodollars"] for r in rows)
        return {"cap_usd": cap/NANO, "accounted_plus_reserved_usd": total/NANO,
                "within_cap": total <= cap, "requests": sum(r["requests"] for r in rows), "by_status": rows}
