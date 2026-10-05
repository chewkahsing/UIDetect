# Google From UIDetect User Evaluation: Website Security Assessment
https://forms.gle/wVBVF1Uk2CrzvoiKA 

# UIDetect

<img height="400" alt="UIDetect" src="https://github.com/user-attachments/assets/5c61c8d1-1721-49e0-9121-ace3803982d1" />

**UIDetect: Intelligent Browser Extension for Real-time Website Security Assessment**

UIDetect is an intelligent Chrome browser extension designed to help users understand the security condition of websites before interacting with them.

UIDetect combines multiple security checks, reputation services, website security indicators, context-aware interaction detection, and AI-powered recommendations to provide an easy-to-understand website security assessment.

---

## Quick Links

* **User Manual:** This README / GitHub repository
* **Latest Installer:** GitHub Releases
* **Source Code:** This GitHub repository

> The GitHub Pages documentation link can be added when the documentation site is published.

---

# 1. UIDetect Overview

UIDetect performs website security assessment using multiple security indicators rather than relying on a single security service.

The main assessment sources include:

* Google Safe Browsing
* VirusTotal
* OpenPhish
* HTTPS
* SSL/TLS
* Security Headers
* WHOIS / domain information

UIDetect also provides:

* Security Score
* Final Security Posture
* Security Findings
* Confidence information
* AI Recommendation
* Dashboard Scan
* Right-Click Website Scan
* Context-Aware Interaction Detection

---

# 2. System Requirements

Before running UIDetect, make sure the following are available:

| Requirement      | Version / Information                                                                         |
| ---------------- | --------------------------------------------------------------------------------------------- |
| Operating System | Windows 10 or later                                                                           |
| Browser          | Google Chrome                                                                                 |
| Internet         | Required during installation (to download components) and for external security services      |
| Disk Space       | Several GB free (for Python, Ollama and the AI model)                                         |

Python 3.13.14, Ollama and the `qwen2.5:3b` AI model are **installed automatically** by the UIDetect installer if they are not already on your computer. You do not need to install them yourself.

Visual Studio Code is **not required** to run UIDetect. It is only useful for development and source-code editing.

---

# 3. Project Structure

The main UIDetect project contains:

```text
UIDetect/
├── backend/
│   ├── app.py
│   ├── routes.py
│   ├── scanner.py
│   ├── checkers/
│   └── modules/
│
├── content/
│   ├── scanModal.js
│   └── scanModal.css
│
├── popup/
│   ├── popup.html
│   ├── popup.js
│   └── popup.css
│
├── scripts/
│   ├── background.js
│   ├── content.js
│   └── interactionDetector.js
│
├── icons/
│
├── installer/
│   ├── UIDetect_Setup.exe
│   └── UIDetect_Setup.iss
│
├── manifest.json
├── Install_UIDetect.bat
├── UIDetect.exe
├── UIDetect_Launcher.py
├── UIDetect_Launcher.c
└── README.md
```

The compiled installer is intended to be distributed through GitHub Releases.

---

# 4. Download UIDetect

Download the latest UIDetect installer or project package from the project's GitHub repository or GitHub Releases page.

The recommended installer is:

> https://github.com/chewkahsing/UIDetect/releases/tag/Installer  

Download `UIDetect_Setup.exe`. You do not need to download Python, Ollama or the AI model separately, because the installer handles them for you (see Section 5).

If the source-code ZIP package is provided instead, download and extract the complete package before using UIDetect.

> **Important:** Do not run UIDetect directly from inside a ZIP file.

---

# 5. Install UIDetect (Automatic Setup)

Run the installer:

```text
UIDetect_Setup.exe
```

The installer sets up everything UIDetect needs. It checks your computer and automatically downloads and installs any missing component:

| Component             | What the installer does                                         |
| --------------------- | --------------------------------------------------------------- |
| Python 3.13.14        | Downloads and installs it if not found, and adds it to PATH     |
| Python dependencies   | Installs the packages the Flask backend needs                   |
| Ollama                | Downloads and installs it if not found                          |
| AI model `qwen2.5:3b` | Downloads it through Ollama if not already installed            |

Components that are already installed are detected and skipped.

Steps:

1. Make sure you have an internet connection.
2. Run `UIDetect_Setup.exe`.
3. Choose the installation folder.
4. Wait for setup to finish. The AI model download is the longest step and can take several minutes.
5. Do not close the installer while components are downloading.

When setup finishes, UIDetect is installed with `UIDetect.exe` in the selected folder.

The installation process uses:

```text
Install_UIDetect.bat
```

to check and install the required components. The installer runs it automatically.

> **Important:** Normal users should use `UIDetect_Setup.exe` and should not run `Install_UIDetect.bat` manually.

> **Note:** If the installation fails or you are offline, see *Automatic Installation Failed* in the Troubleshooting section (Section 22).

---

# 6. Start UIDetect

After installation, start:

```text
UIDetect.exe
```

The UIDetect launcher starts the local Flask backend and checks the required system components.

The launcher displays the status of:

* Backend
* Ollama
* AI Model

The configured AI model is:

```text
qwen2.5:3b
```

When the backend is ready, UIDetect can be used with the Chrome extension.

> **Important:** Keep UIDetect running while performing security scans.

If the UIDetect backend stops or failed, restart UIDetect.

---

# 7. UIDetect Launcher

The UIDetect launcher provides several functions.

### Open Chrome

Opens Google Chrome.

### Open Installation Folder

Opens the folder where UIDetect is installed.

### User Manual

Opens the UIDetect GitHub repository containing the project documentation.

### Load UIDetect Extension

Provides step-by-step instructions for loading the unpacked Chrome extension.

### Start Using UIDetect

Provides instructions for the main UIDetect assessment features.

---

# 8. Load UIDetect into Google Chrome

UIDetect is loaded into Chrome as an unpacked extension.

Open:

```text
chrome://extensions/
```

Then:

1. Enable **Developer mode**.
2. Click **Load unpacked**.
3. Select the UIDetect project folder (the installation folder, which you can open from the launcher using **Open Installation Folder**).
4. Make sure the selected folder contains:

```text
manifest.json
```

5. Confirm that UIDetect appears in the extension list.
6. Make sure the extension is enabled.
7. Pin UIDetect to the Chrome toolbar if desired.

> **Important:** Select the extracted UIDetect folder, not the ZIP file.

---

# 9. Start Using UIDetect

Before performing a scan, make sure:

* UIDetect is running.
* The backend status is ready.
* Ollama is available.
* `qwen2.5:3b` is installed.
* UIDetect is loaded into Chrome.
* The Chrome extension is enabled.
* An internet connection is available.

Then open a normal website in Google Chrome.

UIDetect provides several ways to assess a website.

---

# 10. Dashboard Scan

The Dashboard Scan is the main website security assessment.

To perform a Dashboard Scan:

1. Open a website in Google Chrome.
2. Click the UIDetect extension.
3. Click **Scan Website**.
4. Wait for the assessment to complete.
5. Review the security results.
6. Review the Final Security Posture.
7. Read the AI Recommendation.

The assessment may include:

* Security Score
* Core Protection
* Security Headers
* Domain Information
* VirusTotal
* OpenPhish
* Final Security Posture
* AI Recommendation

If necessary, use **Cancel Scan** to stop the current scan.

---

# 11. Security Assessment Sources

UIDetect uses several security assessment sources.

## Google Safe Browsing

Google Safe Browsing provides information about known website threats.

A result may indicate whether the website is:

* Safe
* Unsafe
* Unknown / unavailable

A Safe result means no known threat was identified by the service at the time of the assessment.

---

## VirusTotal

VirusTotal provides an additional reputation assessment.

UIDetect may receive:

* Malicious detections
* Suspicious detections
* Safe results
* Undetected results
* Timeout or unavailable results

VirusTotal should be considered together with the other UIDetect assessment sources.

---

## OpenPhish

OpenPhish provides an additional phishing reputation assessment.

Possible UIDetect results include:

* **Not Listed**
* **Listed**
* **Unavailable**

A website not being listed by OpenPhish does not guarantee that it is safe.

---

## HTTPS

UIDetect checks whether the website uses HTTPS.

HTTPS helps protect communication between the browser and website.

However:

> HTTPS does not prove that a website is legitimate or trustworthy.

---

## SSL/TLS

UIDetect checks SSL/TLS certificate information where available.

The result may be:

* Valid
* Invalid
* Unknown / unavailable

An unavailable SSL/TLS result does not automatically mean that the website is malicious.

---

## Security Headers

UIDetect checks five security headers:

* Strict-Transport-Security (HSTS)
* Content-Security-Policy (CSP)
* X-Frame-Options
* X-Content-Type-Options
* Referrer-Policy

Missing security headers may indicate a security configuration weakness.

However:

> A missing security header does not automatically mean that a website is malicious.

---

## WHOIS / Domain Information

UIDetect retrieves available domain information such as:

* Domain name
* Registrar
* Registration date
* Expiration date
* Domain age
* Domain status

Domain age provides additional context when assessing unfamiliar websites.

A newly registered domain is not automatically malicious.

---

# 12. Security Score

UIDetect calculates a security score using multiple security indicators.

The current score classification is:

| Security Level |  Score | Meaning                                                         |
| -------------- | -----: | --------------------------------------------------------------- |
| Excellent      | 80–100 | Strong security indicators were detected.                       |
| Good           |  60–79 | The website generally shows good security protection.           |
| Moderate       |  40–59 | Some security weaknesses or limitations were detected.          |
| Poor           |   0–39 | Significant security weaknesses or security concerns may exist. |

A high score does not guarantee that a website is completely safe.

### Score Components

The current scoring system uses the following maximum contributions:

| Security Check       | Maximum Contribution |
| -------------------- | -------------------: |
| Google Safe Browsing |                   25 |
| VirusTotal           |                   15 |
| HTTPS                |                   15 |
| SSL/TLS              |                   15 |
| Security Headers     |                   10 |
| WHOIS                |                   10 |
| OpenPhish            |                   10 |
| **Total**            |              **100** |

Unavailable checks do not automatically receive positive points.

Certain confirmed threat-intelligence results can also limit the maximum score to prevent a high numerical score from hiding a serious reputation finding.

---

# 13. Final Security Posture

The Final Security Posture is separate from the numerical Security Score.

UIDetect uses the assessment findings together with the score to determine the final security posture.

The Final Security Posture includes:

* **Overall Status**
* **Risk**
* **Highest Severity**
* **Recommendation Action**
* **Recommendation Reason**
* **Confidence**
* **Primary Finding**
* **Severity Counts**
* **Finding Class Counts**
* **Security Findings**
* **Summary**

### Risk Levels

| Risk     | General Meaning                                                            |
| -------- | -------------------------------------------------------------------------- |
| Very Low | No significant confirmed concern was identified from the available checks. |
| Low      | The assessment indicates relatively low risk.                              |
| Medium   | Security concerns were detected and should be reviewed.                    |
| High     | A significant security concern was detected.                               |
| Critical | A critical threat finding was detected.                                    |

An unavailable security service is treated as a verification limitation rather than automatically being classified as a malicious threat.

---

# 14. Confidence

UIDetect also reports an assessment confidence level.

Confidence reflects the availability and completeness of the security checks.

For example, if several external services are unavailable, UIDetect may report lower confidence even when no malicious finding is confirmed.

Therefore:

> Low confidence does not automatically mean that the website is unsafe.

It means that fewer available checks were able to contribute to the assessment.

---

# 15. AI Recommendation

UIDetect uses the local:

```text
qwen2.5:3b
```

model through Ollama.

The AI converts the available UIDetect security assessment results into recommendations that are easier for users to understand.

The AI recommendation is based on the security assessment and final posture generated by UIDetect.

The AI does not independently determine the authoritative numerical security score or final security posture.

AI recommendations are intended as security guidance and should not be treated as an absolute guarantee that a website is safe or unsafe.

---

# 16. Context-Aware Security Assessment

UIDetect can detect potentially security-sensitive interactions on websites.

The main supported interaction categories include:

* Login
* Registration
* Upload
* Download

When a potentially sensitive interaction is detected, UIDetect can interrupt the interaction and display a security assessment before allowing the user to continue.

The assessment can include:

* Detected interaction
* Security findings
* Final Security Posture
* Risk
* AI Recommendation

Users can review the warning before deciding whether to continue.

---

# 17. Login and Registration Detection

UIDetect can identify common login and registration interactions.

Examples include:

* Login buttons
* Username and password forms
* Sign-in controls
* Registration controls
* Account creation forms

When UIDetect detects a relevant interaction, it performs an additional assessment before the action continues.

---

# 18. Upload Detection

UIDetect can detect file upload interactions.

Examples include:

* File input controls
* Upload controls
* File attachment controls
* Supported upload forms

Users should avoid uploading personal or sensitive documents to unfamiliar websites.

---

# 19. Download Detection

UIDetect can detect download-related interactions.

Examples include:

* Download controls
* File download links
* Export controls
* Links to supported downloadable file types

Users should review unfamiliar downloads carefully before opening them.

---

# 20. Right-Click Website Scan

UIDetect can assess a website link before opening it.

To perform a Right-Click Scan:

1. Find a website link.
2. Right-click the link.
3. Select the UIDetect scan option.
4. Wait for the assessment.
5. Review the Security Score and Final Security Posture.
6. Read the AI Recommendation.
7. Decide whether to continue to the website.

This is useful for unfamiliar links because the user can assess the destination before opening it.

---

# 21. Cancellation

UIDetect provides cancellation for scans where the **Cancel Scan** control is available.

If a scan is taking too long:

1. Click **Cancel Scan**.
2. Wait for the cancellation to complete.
3. Start a new scan if required.

Cancellation stops the current UIDetect assessment rather than indicating that the website is safe or unsafe.

---

# 22. Troubleshooting

## Automatic Installation Failed

If the installer could not download or install a component (for example, because of no internet connection or a blocked download), you can install the components manually and then run `UIDetect_Setup.exe` again.

### Manual Installation (Optional)

1. **Python 3.13.14:** https://www.python.org/ftp/python/3.13.14/python-3.13.14-amd64.exe (enable **Add Python to PATH**). Verify with:

```bash
python --version
```

2. **Ollama:** https://ollama.com/download/OllamaSetup.exe. Verify with:

```bash
ollama --version
```

3. **AI model:** run the following, then check it with `ollama list`:

```bash
ollama pull qwen2.5:3b
```

---

## UIDetect Cannot Scan the Page

Some Chrome internal pages and unsupported page types cannot be scanned.

Examples include:

```text
chrome://
edge://
file://
```

Try opening a normal website before performing the scan.

---

## Scan Failed

If UIDetect displays **Scan Failed**:

1. Make sure UIDetect is running.
2. Check the backend status in the UIDetect launcher.
3. Make sure Ollama is available.
4. Check your internet connection.
5. Reload the website.
6. Try the scan again.

---

## Backend Is Unavailable

If the backend is unavailable:

1. Close UIDetect if necessary.
2. Start `UIDetect.exe` again.
3. Wait for the Backend status to become ready.
4. Try the scan again.

---

## AI Recommendation Is Unavailable

Check that Ollama is installed:

```bash
ollama --version
```

Then check the available models:

```bash
ollama list
```

Make sure:

```text
qwen2.5:3b
```

is available.

Also make sure UIDetect is running.

---

## UIDetect Does Not Appear in Chrome

Open:

```text
chrome://extensions/
```

Then:

1. Enable **Developer mode**.
2. Click **Load unpacked**.
3. Select the UIDetect project folder.
4. Make sure the selected folder contains:

```text
manifest.json
```

5. Make sure UIDetect is enabled.

---

## VirusTotal Information Is Unavailable

VirusTotal may occasionally be unavailable or may not return a usable result.

If VirusTotal is unavailable, review the other UIDetect security indicators.

An unavailable VirusTotal result does not automatically mean that the website is unsafe.

---

## OpenPhish Information Is Unavailable

OpenPhish may occasionally be unavailable or may not provide a result.

If OpenPhish is unavailable, review the other UIDetect security indicators.

---

## Scan Is Taking Too Long

Some external security checks may take longer depending on network conditions and service availability.

If **Cancel Scan** is available:

1. Click **Cancel Scan**.
2. Wait for the current scan to stop.
3. Start a new scan if necessary.

---

# 23. Quick Setup

For a quick setup:

```text
1. Download UIDetect_Setup.exe from GitHub Releases
        ↓
2. Run UIDetect_Setup.exe
   (Python, Ollama and qwen2.5:3b are installed automatically)
        ↓
3. Start UIDetect.exe
        ↓
4. Check Backend / Ollama / AI Model status
        ↓
5. Open Google Chrome
        ↓
6. Open chrome://extensions/
        ↓
7. Enable Developer mode
        ↓
8. Click Load unpacked
        ↓
9. Select the UIDetect folder
        ↓
10. Open a website
        ↓
11. Click UIDetect, then Scan Website
        ↓
12. Review the Security Score, Final Security Posture and AI Recommendation
```

---

# 24. GitHub Distribution

The recommended distribution structure is:

```text
GitHub Repository
│
├── Source Code
│
├── README.md
│
└── GitHub Releases
        │
        └── UIDetect_Setup.exe
```

The installer source is:

```text
installer/UIDetect_Setup.iss
```

The compiled installer should be provided as a GitHub Release asset.

The source repository contains the UIDetect backend, Chrome extension, launcher, installer configuration, and supporting files.

---

# 25. Important Security Notice

UIDetect is designed to assist users in understanding website security.

UIDetect **does not guarantee** that a website is completely safe or malicious.

Users should continue to exercise caution when:

* Entering passwords
* Entering financial information
* Providing personal information
* Uploading files
* Downloading files
* Interacting with unfamiliar websites

HTTPS alone does not prove that a website is legitimate.

A website not being listed by a reputation service does not guarantee that it is safe.

An unavailable security service does not automatically mean that a website is malicious.

Always consider multiple security indicators before deciding whether to trust a website.

---

# 26. Project Information

**Project:** UIDetect

**Description:** Intelligent Browser Extension for Real-time Website Security Assessment

**Platform:** Google Chrome

**Backend:** Python / Flask

**AI Service:** Ollama

**AI Model:** `qwen2.5:3b`

**Extension Standard:** Chrome Manifest V3


---

**UIDetect — Intelligent Website Security Assessment**
