# Phase 2: Database Setup

This folder contains the MySQL structure for the Intelligent Data Privacy Management System.

## What the tables store

| Table | Purpose |
| --- | --- |
| `users` | User accounts, roles, and password hashes. |
| `documents` | Uploaded-file metadata, classification, and scan/encryption status. |
| `pii_findings` | Detected PII using only redacted values. |
| `privacy_risk_scores` | The latest risk score for each document. |
| `recommendations` | Suggested privacy improvements for a document. |
| `document_access` | Permissions granted to users for a document. |
| `audit_logs` | Security-relevant activity records. |

## Important privacy rule

Do not store a detected full Aadhaar number, password, card number, or other raw sensitive value in `pii_findings`. Store only a redacted value, such as `XXXX-XXXX-1234`.

## Create the database

After MySQL Server and MySQL Workbench are installed and running:

1. Open MySQL Workbench and connect to your local MySQL server.
2. Open `schema.sql` from this folder in a new SQL tab.
3. Click the lightning-bolt **Execute** button.
4. Refresh the **Schemas** panel. You should see `idpms_db` and its seven tables.

This phase deliberately does not connect Flask to MySQL. That will happen in the next phase.
