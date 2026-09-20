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

| Requirement      | Version / Information                   |
| ---------------- | --------------------------------------- |
| Operating System | Windows 10 or later                     |
| Browser          | Google Chrome                           |
| Python           | 3.13.14                                 |
| Ollama           | Current supported version               |
| AI Model         | `qwen2.5:3b`                            |
| Internet         | Required for external security services |

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

```text
UIDetect_Setup.exe
```

If the source-code ZIP package is provided, download and extract the complete package before using UIDetect.

> **Important:** Do not run UIDetect directly from inside a ZIP file.

---

# 5. Install Python 3.13.14

UIDetect uses Python for its local backend.

Download Python 3.13.14 from the official Python website:

```text
https://www.python.org/
```

During installation:

1. Run the Python installer.
2. Enable **Add Python to PATH** if the option is available.
3. Continue with the installation.
4. Complete the installation.

Verify the installation:

```bash
python --version
```

The expected version is:

```text
Python 3.13.14
```

The UIDetect installer also checks for Python and can install the required version when necessary.

---

# 6. Install Ollama

UIDetect uses Ollama to provide the local AI service.

Download Ollama from:

```text
https://ollama.com/
```

After installation, verify it:

```bash
ollama --version
```

If Ollama is installed correctly, its version will be displayed.

---

# 7. Install the UIDetect AI Model

UIDetect currently uses:

```text
qwen2.5:3b
```

Install the model using:

```bash
ollama pull qwen2.5:3b
```

Verify the model:

```bash
ollama list
```

The following model should appear:

```text
qwen2.5:3b
```

The UIDetect launcher also checks whether Ollama and the configured AI model are available.

---

# 8. Install UIDetect

The recommended installation method is the UIDetect installer:

```text
UIDetect_Setup.exe
```

The installer performs the required setup and prepares the UIDetect runtime.

The installation process uses:

```text
Install_UIDetect.bat
```

to check and install required components such as Python, Ollama, the AI model, and Python dependencies.

After installation, UIDetect is installed into the selected installation directory.

The installed application includes:

```text
UIDetect.exe
```

which launches the UIDetect interface and backend.

> **Important:** Normal users should use `UIDetect_Setup.exe` instead of manually running the installation batch file.

---

# 9. Start UIDetect

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

If the UIDetect backend stops, restart UIDetect.

---

# 10. UIDetect Launcher

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

# 11. Load UIDetect into Google Chrome

UIDetect is loaded into Chrome as an unpacked extension.

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

5. Confirm that UIDetect appears in the extension list.
6. Make sure the extension is enabled.
7. Pin UIDetect to the Chrome toolbar if desired.

> **Important:** Select the extracted UIDetect folder, not the ZIP file.

---

# 12. Start Using UIDetect

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

# 13. Dashboard Scan

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

# 14. Security Assessment Sources

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

# 15. Security Score

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

# 16. Final Security Posture

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

# 17. Confidence

UIDetect also reports an assessment confidence level.

Confidence reflects the availability and completeness of the security checks.

For example, if several external services are unavailable, UIDetect may report lower confidence even when no malicious finding is confirmed.

Therefore:

> Low confidence does not automatically mean that the website is unsafe.

It means that fewer available checks were able to contribute to the assessment.

---

# 18. AI Recommendation

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

# 19. Context-Aware Security Assessment

UIDetect can detect potentially security-sensitive interactions on websites.

The main supported interaction categories include:

* Login
* Registration
* Upload
* Download
* Payment

When a potentially sensitive interaction is detected, UIDetect can interrupt the interaction and display a security assessment before allowing the user to continue.

The assessment can include:

* Detected interaction
* Security findings
* Final Security Posture
* Risk
* AI Recommendation

Users can review the warning before deciding whether to continue.

---

# 20. Login and Registration Detection

UIDetect can identify common login and registration interactions.

Examples include:

* Login buttons
* Username and password forms
* Sign-in controls
* Registration controls
* Account creation forms

When UIDetect detects a relevant interaction, it performs an additional assessment before the action continues.

---

# 21. Upload Detection

UIDetect can detect file upload interactions.

Examples include:

* File input controls
* Upload controls
* File attachment controls
* Supported upload forms

Users should avoid uploading personal or sensitive documents to unfamiliar websites.

---

# 22. Download Detection

UIDetect can detect download-related interactions.

Examples include:

* Download controls
* File download links
* Export controls
* Links to supported downloadable file types

Users should review unfamiliar downloads carefully before opening them.

---

# 23. Payment Detection

UIDetect can detect payment-related interactions.

Payment-related detection may identify controls or forms containing common payment-related information or actions.

When a payment interaction is detected, UIDetect can provide an additional security warning before the action continues.

Users should carefully verify the website before entering financial information.

---

# 24. Right-Click Website Scan

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

# 25. Cancellation

UIDetect provides cancellation for scans where the **Cancel Scan** control is available.

If a scan is taking too long:

1. Click **Cancel Scan**.
2. Wait for the cancellation to complete.
3. Start a new scan if required.

Cancellation stops the current UIDetect assessment rather than indicating that the website is safe or unsafe.

---

# 26. Troubleshooting

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

# 27. Quick Setup

For a quick setup:

```text
1. Download UIDetect
        ↓
2. Extract the project package if using ZIP
        ↓
3. Install Python 3.13.14
        ↓
4. Install Ollama
        ↓
5. Install qwen2.5:3b
        ↓
6. Run UIDetect_Setup.exe
        ↓
7. Start UIDetect.exe
        ↓
8. Check Backend / Ollama / AI Model status
        ↓
9. Open Google Chrome
        ↓
10. Open chrome://extensions/
        ↓
11. Enable Developer mode
        ↓
12. Click Load unpacked
        ↓
13. Select the UIDetect folder
        ↓
14. Open a website
        ↓
15. Click UIDetect
        ↓
16. Click Scan Website
        ↓
17. Review the Security Score
        ↓
18. Review the Final Security Posture
        ↓
19. Read the AI Recommendation
```

---

# 28. GitHub Distribution

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

# 29. Important Security Notice

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

# 30. Project Information

**Project:** UIDetect
**Description:** Intelligent Browser Extension for Real-time Website Security Assessment
**Platform:** Google Chrome
**Backend:** Python / Flask
**AI Service:** Ollama
**AI Model:** `qwen2.5:3b`
**Extension Standard:** Chrome Manifest V3

---

**UIDetect — Intelligent Website Security Assessment**
