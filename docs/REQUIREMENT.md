# Requirements

## Goal

Uniskope is an open-source, personal-first SaaS control plane.
This document defines what Uniskope **will and will not** do.

---

## In Scope (v0.1)

- Single-user usage
- Local-first data storage
- SaaS configuration CRUD
- API-first design

---

## Explicit Non-Goals (v0.1)

The following items are **explicitly out of scope** and should not be implemented.

### ❌ Authentication & Authorization
- No user accounts
- No login / signup
- No RBAC / permissions

### ❌ Multi-tenancy
- No organization or team concept
- No tenant isolation

### ❌ Hosted / Cloud Features
- No SaaS hosting
- No managed backend
- No background jobs or workers

### ❌ Advanced UI
- No dashboard analytics
- No real-time updates
- No complex UI workflows

### ❌ Enterprise Features
- No audit logs
- No compliance features
- No SSO

---

## Future Considerations (Not for v0.1)

These may be considered in future versions but must not influence v0.1 design.

- Multi-user support
- Hosted SaaS version
- Billing and subscriptions