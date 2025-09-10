
---

# fastapi-tenants

*A multi-tenancy solution for FastAPI with support for database-per-tenant, schema-per-tenant, and row-level tenancy strategies.*

---

## ✨ Features

* **Flexible strategies** → database-per-tenant, schema-per-tenant, row-level.
* **Tenant-aware middleware** → resolve tenant from headers, subdomains, or tokens.
* **DB session management** → per-tenant scoped sessions.
* **Pluggable design** → extend strategies or authentication as needed.
* **FastAPI-first** → built for dependency injection and async support.

---

## 📦 Installation

```bash
pip install fastapi-tenants
```

Optional extras:

```bash
pip install "fastapi-tenants[postgres]"
pip install "fastapi-tenants[mysql]"
```

---

## 🚀 Quick Start

```python
from fastapi import FastAPI, Depends
from fastapi_tenants import TenancyMiddleware, get_tenant_session

app = FastAPI()

# Enable tenancy
app.add_middleware(
    TenancyMiddleware,
    strategy="schema",   # or "database", "row"
    header="X-Tenant-ID"
)

@app.get("/users")
def list_users(session = Depends(get_tenant_session)):
    return session.query(User).all()
```

---

## 📚 Roadmap

* [ ] Schema-based tenancy ✅
* [ ] Database-per-tenant support
* [ ] Row-level tenancy
* [ ] Multi-backend support (Postgres, MySQL, SQLite)
* [ ] Example apps & docs

---

## 🤝 Contributing

Contributions are welcome!
Check out [CONTRIBUTING.md](CONTRIBUTING.md) (coming soon).

---

## 📜 License

MIT License © 2025 [Kapil Dagur](https://github.com/KapilDagur)

---
