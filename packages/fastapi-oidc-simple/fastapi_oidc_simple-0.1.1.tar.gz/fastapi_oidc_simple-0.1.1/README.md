# fastapi-oidc

A lightweight **OpenID Connect (OIDC)** integration for **FastAPI**, built on top of [Authlib](https://docs.authlib.org/).  
It provides simple routes for OIDC login, callback, and user info, along with dependency helpers to protect endpoints and enforce group-based access.

---

## ✨ Features

- 🔑 Easy OIDC integration with FastAPI  
- 🔗 Built-in routes for `/auth/login`, `/auth/callback`, and `/auth/userinfo`  
- 🛡️ Dependency helpers:
  - `require_oidc` → protect endpoints with authentication  
  - `require_oidc_group("group")` → enforce group-based authorization  
- 🧩 Uses Authlib’s discovery-based OIDC client  
- ⚡ Minimal setup: just plug it into your FastAPI app  

---