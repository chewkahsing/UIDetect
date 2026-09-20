<img height="600" alt="UIDetect image" src="https://github.com/user-attachments/assets/5c61c8d1-1721-49e0-9121-ace3803982d1" />

# UIDetect User Manual

UIDetect is an intelligent Chrome browser extension designed to help users understand the security condition of websites before interacting with them.

UIDetect combines multiple security checks, reputation services, and AI-powered recommendations to provide an easy-to-understand website security assessment.

## Quick Links

- **User Manual:** GitHub Pages
- **Latest Installer:** GitHub Releases
- **Source Code:** This GitHub repository

> Replace the GitHub Pages and GitHub Releases placeholders above with the actual repository URLs after the repository is published.

---

# 1. Download UIDetect

Download the latest UIDetect ZIP package from the project repository or the project's GitHub Releases page.

The downloaded file should look similar to:

```text
UIDetect.zip
```

Save the ZIP file to your computer.

---

# 2. Extract the UIDetect ZIP File

After downloading the ZIP file:

1. Locate the downloaded `UIDetect.zip` file.
2. Right-click the ZIP file.
3. Select **Extract All...**.
4. Choose a suitable location.
5. Click **Extract**.

After extraction, you should have a UIDetect project folder.

For example:

```text
UIDetect/
├── backend/
├── popup/
├── scripts/
├── icons/
├── content/
├── manifest.json
├── Install_UIDetect.bat
├── Start_UIDetect.bat
└── installer/
```

> **Important:** Do not run UIDetect directly from inside the ZIP file. Extract the complete ZIP package first.

The online User Manual is maintained separately through GitHub Pages.

---

# 3. Open the UIDetect User Manual

For the complete installation, usage, security assessment, troubleshooting, and feature documentation, open the **UIDetect User Manual** through the project's GitHub Pages site.

The manual is maintained as:

```text
docs/
└── index.html
```

The GitHub Pages version is the recommended version for users who want the latest documentation.

---

# 4. Prerequisites

Before running UIDetect, make sure the following software is available:

* **Windows 10 or later**
* **Google Chrome**
* **Python 3.13.14**
* **Ollama**
* **qwen2.5:3b**
* **Internet connection**

Visual Studio Code is **not required** to run UIDetect. It may be used for development and source-code editing.

---

# 5. Install Python 3.13.14

UIDetect uses Python to run the local backend.

Download Python 3.13.14 from the official Python website:

```text
https://www.python.org/
```

During installation:

1. Run the Python installer.
2. Enable **Add Python to PATH** if the option is shown.
3. Continue with the installation.
4. Complete the installation.

Verify the installation by opening Command Prompt or PowerShell:

```bash
python --version
```

Confirm that Python 3.13.14 is displayed.

---

# 6. Install Ollama

UIDetect uses Ollama to provide the local AI service for AI-powered security recommendations.

Download Ollama from:

```text
https://ollama.com/
```

After installing Ollama, open Command Prompt or PowerShell and run:

```bash
ollama --version
```

If Ollama is installed correctly, its version will be displayed.

---

# 7. Install the UIDetect AI Model

UIDetect uses the following local AI model through Ollama:

```text
qwen2.5:3b
```

Install the model using:

```bash
ollama pull qwen2.5:3b
```

After installation, verify that the model is available:

```bash
ollama list
```

Make sure:

```text
qwen2.5:3b
```

appears in the model list.

---

# 8. Start UIDetect

The recommended way to start UIDetect is to use the UIDetect installer.

Open the `installer` folder and run:

```text
UIDetect_Setup.exe
```

The installer performs the required UIDetect setup and starts the UIDetect backend.

The installer runs:

```text
Install_UIDetect.bat
```

for the required setup process and:

```text
Start_UIDetect.bat
```

to start the UIDetect backend.

> **Important:** Normal users do not need to run the batch files manually. They should normally start UIDetect using `UIDetect_Setup.exe`.

The compiled installer should be distributed through the project's **GitHub Releases** page.

---

# 9. Keep the UIDetect Backend Running

After UIDetect has been started, a Command Prompt window may appear while the backend is running.

Keep the UIDetect backend running while using the Chrome extension.

> **Important:** Do not close the UIDetect backend process while performing website security scans.

If the backend is not running, run:

```text
installer\UIDetect_Setup.exe
```

again.

---

# 10. Load UIDetect into Google Chrome

UIDetect is loaded into Chrome as an unpacked extension.

Open Google Chrome and enter:

```text
chrome://extensions/
```

Then:

1. Enable **Developer mode**.
2. Click **Load unpacked**.
3. Select the extracted **UIDetect project folder**.
4. Confirm that UIDetect appears in the extension list.
5. Pin UIDetect to the Chrome toolbar for easier access.

The selected folder must contain:

```text
manifest.json
```

> **Important:** Select the extracted UIDetect folder, not the ZIP file.

---

# 11. Start Using UIDetect

Before scanning a website, make sure:

* The UIDetect ZIP file has been extracted.
* Python is installed and available.
* Ollama is installed and available.
* `qwen2.5:3b` is installed.
* UIDetect has been started using `UIDetect_Setup.exe`.
* The UIDetect backend is running.
* The UIDetect Chrome extension is loaded and enabled.
* Your computer has an active internet connection.

Then:

1. Open Google Chrome.
2. Navigate to the website you want to assess.
3. Click the UIDetect extension icon.
4. Click **Scan Website**.
5. Wait for the security assessment to complete.
6. If necessary, use **Cancel Scan** to stop the running assessment.
7. Review the Security Score.
8. Review the Core Protection results.
9. Review Website Security / Security Headers.
10. Review Domain Information.
11. Review VirusTotal results.
12. Review OpenPhish results.
13. Review the Final Security Posture.
14. Read the AI Recommendation.

---

# 12. UIDetect Features

## Security Score

UIDetect calculates an overall security score based on multiple security indicators.

The score helps users understand the general security condition of the website.

| Security Level | Score | Meaning |
|---|---:|---|
| Excellent | 90–100 | Strong security indicators were detected. |
| Good | 70–89 | The website generally shows good security protection. |
| Moderate | 50–69 | Some security weaknesses were detected. |
| Poor | 0–49 | Significant security weaknesses may exist. |

A high score does not guarantee that a website is completely safe.

---

## Final Security Posture

UIDetect combines the available security assessment results to determine a final security posture.

The final posture includes:

* **Overall Status** — Overall security condition determined from the available assessment results.
* **Risk** — Overall level of risk identified from confirmed findings.
* **Highest Severity** — Most serious confirmed security finding.
* **Confidence** — Indicates how complete the assessment is based on the availability of the security checks.
* **Primary Finding** — Main confirmed security finding used to guide the user-facing warning and recommendation.

An unavailable external security service does not automatically mean that a website is unsafe.

---

## Core Protection

UIDetect checks several core security indicators, including:

* HTTPS
* SSL Certificate
* TLS
* Google Safe Browsing

These checks provide information about the website's connection security and known security reputation.

---

## Website Security

UIDetect checks important website security headers, including:

* HSTS
* Content Security Policy
* X-Frame-Options
* X-Content-Type-Options
* Referrer Policy

Security headers provide instructions that help control certain browser security behaviours.

Missing security headers do not automatically mean that a website is malicious.

---

## Domain Information

UIDetect retrieves domain information such as:

* Domain name
* Registrar
* Registration date
* Expiration date
* Domain age
* Domain status

Domain age provides additional context when evaluating unfamiliar websites.

A newly registered domain is not automatically malicious.

---

## VirusTotal Analysis

UIDetect uses VirusTotal as an additional reputation assessment source.

The results may include:

* Malicious detections
* Suspicious detections
* Harmless detections
* Undetected results
* Timeout results

VirusTotal results should be considered together with the other UIDetect security indicators.

---

## OpenPhish Assessment

UIDetect uses OpenPhish as an additional phishing reputation assessment source.

UIDetect checks whether the assessed website is listed in the available OpenPhish phishing feed.

Possible results include:

* **Not Listed** — The website was not found in the available OpenPhish feed.
* **Listed** — The website was found in the available OpenPhish phishing feed.
* **Unavailable** — The OpenPhish check could not provide a result.

A website not being listed by OpenPhish does not guarantee that it is safe.

---

## AI Recommendation

UIDetect uses the local `qwen2.5:3b` model through Ollama to convert technical security assessment results into recommendations that are easier for users to understand.

The AI recommendation is based on the available UIDetect security assessment results.

AI recommendations are intended as security guidance and should not be treated as an absolute guarantee that a website is safe or unsafe.

---

## Context-Aware Security Assessment

UIDetect can assess security-sensitive website interactions, including:

* Login
* Registration
* Upload
* Download
* Payment

When a potentially sensitive interaction is detected, UIDetect can provide an additional security warning.

### Risk Levels

| Risk Level | Meaning |
|---|---|
| Very Low / Low | The interaction shows relatively low risk based on the assessment. |
| Medium | The user should review the warning before continuing. |
| High / Critical | The interaction may present a significant security concern. |

When UIDetect presents a high or critical warning, carefully consider whether you should continue with the interaction.

---

## Right-Click Website Scan

UIDetect can assess a website link before the user opens it.

To perform a right-click scan:

1. Find a website link.
2. Right-click the link.
3. Select the UIDetect scan option.
4. Wait for the security assessment.
5. Review the result.
6. Decide whether to continue to the website.

This feature is useful when a user receives an unfamiliar link and wants to assess it before visiting the website.

---

# 13. Troubleshooting

## UIDetect Cannot Scan the Page

Some Chrome internal pages and unsupported page types cannot be scanned.

Examples:

```text
chrome://
edge://
file://
```

Try opening a normal website before performing the scan.

---

## Scan Failed

If UIDetect displays **Scan Failed**:

1. Make sure the UIDetect backend is running.
2. Make sure the backend Command Prompt window remains open.
3. Check your internet connection.
4. Reload the website.
5. Try scanning again.

If the backend is not running, start UIDetect again using:

```text
installer\UIDetect_Setup.exe
```

---

## AI Recommendation Is Unavailable

Verify that Ollama is installed and that the UIDetect AI model is available.

Run:

```bash
ollama list
```

Confirm that:

```text
qwen2.5:3b
```

is available.

Also make sure the UIDetect backend is running.

---

## UIDetect Does Not Appear in Chrome

Open:

```text
chrome://extensions/
```

Then:

1. Enable **Developer mode**.
2. Click **Load unpacked**.
3. Select the extracted UIDetect folder.
4. Make sure the folder contains `manifest.json`.

---

## VirusTotal Information Is Unavailable

External security services may occasionally be unavailable or may not return a result.

If VirusTotal is unavailable, review the other UIDetect security indicators instead of relying on a single assessment source.

---

## OpenPhish Information Is Unavailable

The OpenPhish service or available phishing feed may occasionally be unavailable.

If OpenPhish is unavailable, review the other UIDetect security indicators instead of relying on a single assessment source.

---

## Scan Is Taking Too Long

Wait for the security checks and AI assessment to finish.

If you do not want to continue the current scan, use the **Cancel Scan** button when it is available.

After cancellation, a new scan can be started.

---

# 14. Quick Setup

For a quick installation, follow this order:

```text
1. Download UIDetect ZIP
        ↓
2. Extract the ZIP file
        ↓
3. Open UIDetect User Manual through GitHub Pages if detailed instructions are needed
        ↓
4. Install Python 3.13.14
        ↓
5. Install Ollama
        ↓
6. Install qwen2.5:3b
        ↓
7. Run installer\UIDetect_Setup.exe
        ↓
8. Keep the UIDetect backend running
        ↓
9. Open Google Chrome
        ↓
10. Open chrome://extensions/
        ↓
11. Enable Developer mode
        ↓
12. Click Load unpacked
        ↓
13. Select the extracted UIDetect folder
        ↓
14. Open a website
        ↓
15. Click the UIDetect extension
        ↓
16. Click Scan Website
        ↓
17. Review the security assessment
```

---

# 15. GitHub Distribution

The recommended UIDetect GitHub repository structure is:

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
├── manifest.json
├── Install_UIDetect.bat
└── Start_UIDetect.bat
```

The distribution workflow is:

```text
GitHub Repository
       │
       ├── Source Code
       │
       ├── GitHub Pages
       │       └── UIDetect User Manual
       │
       └── GitHub Releases
               └── UIDetect_Setup.exe
```

The installer source file:

```text
installer/UIDetect_Setup.iss
```

should remain in the repository.

The compiled installer:

```text
UIDetect_Setup.exe
```

should be provided as a GitHub Release asset.

---

# 16. Important Security Notice

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

Always consider multiple security indicators before deciding whether to trust a website.

---

**UIDetect — Intelligent Website Security Assessment**
