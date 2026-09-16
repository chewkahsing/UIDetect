<img width="1917" height="676" alt="image" src="https://github.com/user-attachments/assets/b04c7cf1-08af-47e8-8feb-2a501b9aa505" /># UIDetect

**Intelligent Website Security Assessment**

UIDetect is an intelligent Chrome browser extension designed to help users understand the security condition of websites before interacting with them.

UIDetect combines multiple security checks, reputation services and local AI-powered recommendations to provide an easy-to-understand website security assessment.

---

## Features

UIDetect provides three main detection methods:

- **Dashboard Scan** — Assess the website currently open in Chrome.
- **Right-Click Scan** — Assess a link before opening it.
- **Security-Sensitive Interaction Detection** — Detect interactions such as Login, Registration, Upload, Download, Payment and Logout.

The assessment includes:

- Security Score
- Final Security Posture
- HTTPS / SSL / TLS checks
- Google Safe Browsing
- Security Headers
- Domain Information
- VirusTotal
- OpenPhish
- AI Recommendation

---

## Quick Start

### 1. Download UIDetect

Download the latest:

```text
UIDetect_Setup.exe
```

from the **GitHub Releases** page. https://github.com/chewkahsing/UIDetect/releases/tag/UIDetect 

### 2. Run the Installer

Run:

```text
UIDetect_Setup.exe
```

The installer automatically checks and prepares the required UIDetect components, including:

- Python 3.13.14
- Ollama
- `qwen2.5:3b`
- UIDetect Python dependencies

> Normal users do not need to manually install these components.

### 3. Start UIDetect

After installation is completed, launch UIDetect.

Keep the **UIDetect Launcher** running while using the Chrome extension.

### 4. Load the Chrome Extension

Open:

```text
chrome://extensions/
```
<img width="400" alt="How to find Extensions" src="https://github.com/user-attachments/assets/48696d90-3871-47f6-b945-d0a011606d29" />

<img width="700" alt="Chrome Extensions page" src="https://github.com/user-attachments/assets/a8a6d1c8-6382-4936-adf6-1b8dd574d691" />

Then:

1. Enable **Developer mode**.
<img width="850" alt="Enable Developer mode" src="https://github.com/user-attachments/assets/25dcde0e-1cdd-4af5-9b0c-944e63406cf0" />


2. Click **Load unpacked**.
<img width="850" alt="Load unpacked button" src="https://github.com/user-attachments/assets/6b776fc6-9cb0-4a43-91ff-598612f3b670" />


3. Select the UIDetect extension folder containing `manifest.json`.
<img width="700" alt="Select UIDetect extension folder" src="https://github.com/user-attachments/assets/a1c77477-4cfe-4710-a616-4b257a1db1f2" />


4. Make sure UIDetect is enabled.
5. Pin the extension to the Chrome toolbar if desired.
<img width="850" alt="UIDetect extension enabled and pinned" src="https://github.com/user-attachments/assets/2113b5d9-e9b8-4996-8218-e1d691a9c2b7" />



> UIDetect is currently loaded as an unpacked Chrome extension for development and testing.

### 5. Scan a Website

1. Open a website in Google Chrome.
2. Click the UIDetect extension.
3. Click **Scan Website**.
4. Wait for the assessment to complete.
5. Review the security results and AI recommendation.

---

## System Requirements

- Windows 10 or later
- Google Chrome
- Internet connection

The UIDetect installer automatically checks and prepares the required Python, Ollama, AI model and Python dependencies.

---

## User Manual

For complete instructions and explanations, open the:

**UIDetect User Manual**

The manual covers:

- Installation
- Chrome Extension Setup
- Dashboard Scan
- Right-Click Scan
- Interaction Detection
- Security Score
- Final Security Posture
- Security Checks
- VirusTotal
- OpenPhish
- AI Recommendation
- Troubleshooting
- User Safety

**User Manual:** GitHub Pages

**Latest Installer:** GitHub Releases

---

## Project Structure

```text
UIDetect/
├── backend/
├── content/
├── popup/
├── scripts/
├── icons/
├── installer/
├── docs/
│   └── index.html
└── manifest.json
```

### Important Files

```text
installer/UIDetect_Setup.iss
```

Inno Setup project used to build the UIDetect installer.

```text
docs/index.html
```

UIDetect's complete online User Manual.

---

## Security Notice

UIDetect is a website security assessment tool.

Its results are intended to provide security indicators and warnings. They do **not** guarantee that a website is completely safe or malicious.

Users should consider multiple security indicators before entering passwords, providing personal information, uploading files, downloading files or making payments.

HTTPS alone does not prove that a website is legitimate.

---

**UIDetect — Intelligent Website Security Assessment**
