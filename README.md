# Group System Testing — F1–F12

Selenium browser tests for the OpenCart demo at https://opencart.abstracta.us/.
This repository contains test automation, not the OpenCart server. No local web server or database deployment is required.

## Prerequisites

- Python 3.10 or newer and Google Chrome installed.
- Internet access to the demo site and the browser driver download service. Selenium Manager locates/downloads ChromeDriver automatically.
- A desktop session: F1–F9 open Chrome windows. F10–F12 run headless by default.
- A registered disposable test account on the demo site for F1–F3 login/logout scenarios. Do not use a personal password. F10–F12 create a temporary account automatically when credentials are absent.

## Install (Windows PowerShell)

```powershell
git clone https://github.com/kosuzu123/System-Testing-Group.git
cd System-Testing-Group
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:TEST_EMAIL = 'your-registered-demo-account@example.com'
$env:TEST_PASSWORD = 'your-demo-account-password'
.\.venv\Scripts\python.exe run_tests.py
```

Register the account through **My Account → Register** on the demo website before running. Environment variables apply to the current terminal and are not written to this repository.

## Install (macOS / Linux desktop)

```bash
git clone https://github.com/kosuzu123/System-Testing-Group.git
cd System-Testing-Group
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
export TEST_EMAIL='your-registered-demo-account@example.com'
export TEST_PASSWORD='your-demo-account-password'
.venv/bin/python run_tests.py
```

## Assessment commands

Run all four suites with the command above, or select one:

```powershell
.\.venv\Scripts\python.exe run_tests.py --suite f10_f12
.\.venv\Scripts\python.exe run_tests.py --collect-only
```

Collection checks discover tests without executing browser scenarios; they do not prove that the scenarios pass. Each suite runs in its own process and working directory to preserve member fixtures and reporting. All suites are attempted even if an earlier suite fails. Execution is serial.

| Folder / selector | Scope | Contributor |
|---|---|---|
| `suites/f01_f03` | Registration, login, logout | Shengxuan Sun |
| `suites/f04_f06` | Search, filter, sort | Chuyu |
| `suites/f07_f09` | Add to cart, update quantity, remove item | Hanlin Yu |
| `suites/f10_f12` | Wishlist, product comparison, checkout | Kunyu Wang |

## Results

- `artifacts/summary.json`: per-suite pytest exit codes (0 means success; nonzero requires inspection).
- `artifacts/f01_f03.xml` through `f10_f12.xml`: JUnit reports for assessment.
- `suites/f01_f03/evidence/` and `suites/f04_f06/evidence/`: screenshots produced by those suites.
- `suites/f07_f09/artifacts/`: timestamped cart execution evidence.
- `suites/f10_f12/artifacts/latest/`: scenario results, environment metadata and screenshots.

Outputs are generated locally and excluded from Git. A nonzero runner exit code means at least one suite did not finish successfully; consult the terminal and reports to distinguish assertions from setup/network errors. Public-demo availability, shared inventory and account state can affect results. Existing source expectations are preserved; no successful result is assumed or fabricated.

If Chrome cannot start, update Chrome and check internet access for Selenium Manager. If login/logout fails, verify both account environment variables and test the credentials in the demo site. Test-account setup and live demo availability are required for a complete execution.

## Source provenance

Member source files were copied from the locally prepared assignment sources. Integration adds the runner, dependency list and this guide; the suites remain separated to avoid conflicting fixtures. F10–F12 are also submitted in [Kunyu Wang's individual repository](https://github.com/kosuzu123/System-Testing-Kunyu-Wang).

- F1–F3: https://github.com/Shawn-Sun-AU/System-Testing-py-code
- F4–F6: https://github.com/Charlie625/UTS-System-Testing
- F7–F9: https://github.com/JustinWalkerJW/assignment3_opencart
