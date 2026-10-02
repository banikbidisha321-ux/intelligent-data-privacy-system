# Final Testing Checklist

Use only dummy or non-sensitive files during testing.

| Test | Expected result |
| --- | --- |
| Register with a new email | Account is created and password is never displayed. |
| Log in with the correct password | Dashboard opens. |
| Open Dashboard/Documents/Activity without login | App redirects to the login page. |
| Upload a TXT, PDF, or DOCX under 10 MB | File appears in My Documents with encryption status `encrypted`. |
| Upload an EXE or a file over 10 MB | App rejects the file. |
| Scan a TXT file containing dummy PII | Masked findings, a risk score, and recommendations appear. |
| Scan a PDF or DOCX | App explains that scanning currently supports TXT only. |
| Encrypt a legacy pending document | Status changes to `encrypted`. |
| Share a document with another account | Recipient sees it under Documents shared with me. |
| Download a shared encrypted document | Download works only for `download` or `manage` permission. |
| Review Activity | Safe records appear for login, upload, scan, encryption, and sharing. |
| Log in as the configured admin | Admin page shows metrics and user-management controls. |

## Automated smoke test

From the project folder, run:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```
