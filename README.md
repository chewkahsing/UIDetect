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

For normal users, download the latest **UIDetect installer** from the project's GitHub Releases page.

The installer should be:

```text
UIDetect_Setup.exe
```

The installer is the recommended way to set up UIDetect because it automatically checks and prepares the required software components.

> **Important:** The ZIP/source-code package is mainly useful for development, testing, or users who need access to the project files. Normal users should use `UIDetect_Setup.exe`.

---

# 2. UIDetect Package Structure

If you download the UIDetect source-code ZIP package, extract it before using the project files.

After extraction, the project may contain:

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

> **Important:** Do not run UIDetect directly from inside the ZIP file. Extract the complete package first.

The compiled installer is located in the `installer` directory when the installer executable is included in the distribution package.

---

# 3. Open the UIDetect User Manual

The complete UIDetect User Manual is available through the project's GitHub Pages site.

The manual is maintained as:

```text
docs/
└── index.html
```

The GitHub Pages version provides detailed information about:

- UIDetect installation
- System requirements
- Starting UIDetect
- Chrome extension setup
- Dashboard Scan
- Right-Click Website Scan
- Security-Sensitive Interaction Detection
- Security Score
- Final Security Posture
- Core Security Checks
- Security Headers
- Domain Information
- VirusTotal
- OpenPhish
- AI Recommendation
- Troubleshooting
- User safety practices

The GitHub Pages User Manual is recommended when detailed instructions or explanations are required.

---

# 4. System Requirements

The UIDetect installer automatically checks and prepares the required software components.

| Requirement | Purpose | Installation |
|---|---|---|
| Windows Computer | Runs the UIDetect application, backend and Chrome extension | User provides |
| Google Chrome | Runs the UIDetect browser extension | User provides |
| Python 3.13.14 | Runs the UIDetect backend and security assessment modules | Automatically checked and installed when required |
| Ollama | Provides the local AI service | Automatically checked and installed when required |
| `qwen2.5:3b` | Local AI model used by UIDetect | Automatically checked and downloaded when required |
| Internet Connection | Required for website analysis, external services and downloading missing components | User provides |

Visual Studio Code is **not required** to run UIDetect. It may be used for development and source-code editing.

---

# 5. Install UIDetect

The recommended way to install UIDetect is to run:

```text
UIDetect_Setup.exe
```

The installer automatically checks the required UIDetect environment.

Depending on the computer's current configuration, the installer may:

1. Check for Python 3.13.14.
2. Install Python 3.13.14 if required.
3. Check for Ollama.
4. Install Ollama if required.
5. Check for the `qwen2.5:3b` AI model.
6. Download the `qwen2.5:3b` model if required.
7. Test communication with the AI model.
8. Install the required UIDetect Python dependencies.
9. Verify the UIDetect Python environment.
10. Verify the UIDetect connection to Ollama.
11. Complete the UIDetect installation.

The installer displays the installation progress while these steps are performed.

> **Important:** Do not close the installer while installation, dependency setup, AI model downloading or verification is in progress.

---

# 6. Python 3.13.14

UIDetect uses **Python 3.13.14** to run its local backend and security assessment modules.

The UIDetect installer checks specifically for Python 3.13.14.

If Python 3.13.14 is already available, the installer verifies the existing installation.

If it is missing, the installer downloads and installs the required version.

A different Python version does not replace the required Python 3.13.14 environment.

For example, having Python 3.14.x installed does not mean that Python 3.13.14 is available for UIDetect.

### Advanced Verification

For troubleshooting, Python can be checked using:

```bash
python --version
```

The required version is:

```text
Python 3.13.14
```

---

# 7. Ollama and the UIDetect AI Model

UIDetect uses **Ollama** to provide the local AI service used for AI-powered security recommendations.

The UIDetect AI model is:

```text
qwen2.5:3b
```

The installer automatically checks whether Ollama is available.

If Ollama is missing, the installer installs it.

The installer also checks whether:

```text
qwen2.5:3b
```

is available.

If the model is missing, the installer downloads it automatically.

The installer then tests communication with the AI model.

> **Important:** Downloading `qwen2.5:3b` may take some time. Do not close the installer while the model is being downloaded or verified.

### Advanced Verification

Installed Ollama models can be checked using:

```bash
ollama list
```

The UIDetect AI model should appear as:

```text
qwen2.5:3b
```

Other AI models installed in Ollama are not used by UIDetect.

---

# 8. Start UIDetect

After the installation is completed successfully, launch UIDetect.

The UIDetect Launcher starts the local UIDetect backend and provides the necessary startup status.

The backend is responsible for receiving requests from the Chrome extension and performing the website security assessment.

The normal workflow is:

```text
UIDetect_Setup.exe
        ↓
UIDetect installation
        ↓
UIDetect Launcher
        ↓
Local UIDetect Backend
        ↓
Google Chrome
        ↓
UIDetect Extension
```

> **Important:** Normal users do not need to manually run `Install_UIDetect.bat` or `Start_UIDetect.bat`.

These batch files are used by the UIDetect installation and startup process.

---

# 9. Keep the UIDetect Launcher Running

Keep the **UIDetect Launcher** running while using the UIDetect Chrome extension.

The Launcher provides the local backend required by the extension.

If the Launcher or backend is closed, the extension may not be able to perform website security scans.

If UIDetect is no longer running, start it again using:

```text
UIDetect_Setup.exe
```

> **Important:** Do not close the UIDetect Launcher while performing website security scans.

---

# 10. Load UIDetect into Google Chrome

UIDetect is currently loaded into Google Chrome as an **unpacked extension** for development and testing.

The extension is not installed through the Chrome Web Store.

In Google Chrome, open:

```text
chrome://extensions/
```

Then:

1. Enable **Developer mode**.
2. Click **Load unpacked**.
3. Select the UIDetect extension folder.
4. Confirm that the selected folder contains:
   ```text
   manifest.json
   ```
5. Click **Select Folder**.
6. Confirm that UIDetect appears in the Chrome extension list.
7. Make sure the extension is enabled.
8. Pin UIDetect to the Chrome toolbar if desired.

> **Important:** Select the extracted UIDetect folder containing `manifest.json`. Do not select the ZIP file.

---

# 11. Start Using UIDetect

Before scanning a website, make sure:

- UIDetect installation has completed successfully.
- The UIDetect Launcher is running.
- The UIDetect backend is running.
- The UIDetect Chrome extension is loaded and enabled.
- Your computer has an active Internet connection.

Then:

1. Open Google Chrome.
2. Navigate to the website you want to assess.
3. Click the UIDetect extension icon.
4. Click **Scan Website**.
5. Wait for the security assessment to complete.
6. If necessary, click **Cancel Scan** to stop the running assessment.
7. Review the Security Score.
8. Review the Core Protection results.
9. Review Website Security and Security Headers.
10. Review Domain Information.
11. Review VirusTotal results.
12. Review OpenPhish results.
13. Review the Final Security Posture.
14. Read the AI Recommendation.

The assessment may take some time because UIDetect performs multiple security checks and may communicate with external security services.

---

# 12. UIDetect Detection Methods

UIDetect provides three main detection methods:

1. **Dashboard Scan**
2. **Right-Click Scan**
3. **Security-Sensitive Interaction Detection**

Each detection method determines what should be assessed before the relevant security checks are performed by the UIDetect backend.

---

## 12.1 Dashboard Scan

The Dashboard Scan assesses the website currently open in the active Chrome tab.

To perform a Dashboard Scan:

1. Open the website in Google Chrome.
2. Click the UIDetect extension icon.
3. Click **Scan Website**.
4. Wait for the assessment to complete.
5. Review the assessment results.

The Dashboard Scan provides the main UIDetect security assessment.

---

## 12.2 Right-Click Website Scan

The Right-Click Website Scan allows users to assess a website link before opening it.

To perform a Right-Click Scan:

1. Find a website link.
2. Right-click the link.
3. Select the UIDetect scan option from the Chrome context menu.
4. Wait for the security assessment.
5. Review the security result.
6. Decide whether to continue to the website.

This feature is useful when receiving an unfamiliar link and wanting to assess its available security indicators before visiting the website.

> **Important:** A Right-Click Scan does not guarantee that a website is completely safe.

---

## 12.3 Security-Sensitive Interaction Detection

UIDetect can detect security-sensitive interactions on a website and provide additional security warnings.

Supported interaction types include:

- Login
- Registration
- Upload
- Download
- Payment
- Logout

These interactions may involve accounts, files, personal information or financial information.

When a potentially sensitive interaction is detected, UIDetect can provide an additional security warning based on the available website assessment.

---

# 13. Security Score

UIDetect calculates an overall Security Score using multiple security indicators.

| Security Level | Score | Meaning |
|---|---:|---|
| Excellent | 90–100 | Strong security indicators were detected. |
| Good | 70–89 | The website generally shows good security protection. |
| Moderate | 50–69 | Some security weaknesses were detected. |
| Poor | 0–49 | Significant security weaknesses may exist. |

The Security Score provides an overall indication of the available security assessment results.

> **Important:** A high Security Score does not guarantee that a website is completely safe.

Users should consider the other security indicators before entering sensitive information or performing sensitive actions.

---

# 14. Final Security Posture

UIDetect combines the available security assessment results to determine a **Final Security Posture**.

The Final Security Posture includes:

| Field | Meaning |
|---|---|
| Overall Status | Overall security condition determined from the available assessment results |
| Risk | Overall level of risk identified from confirmed findings |
| Highest Severity | Most serious confirmed security finding |
| Confidence | Indicates how complete the assessment is based on the availability of the security checks |
| Primary Finding | Main confirmed security finding used to guide the user-facing warning and recommendation |

The Final Security Posture is based on the available assessment evidence.

An unavailable external security service does not automatically mean that a website is unsafe.

If there is insufficient evidence, some posture information may be shown as unavailable or unknown.

---

# 15. Core Security Checks

UIDetect performs several core security checks.

## HTTPS

HTTPS is the secure version of HTTP.

It helps protect information sent between the browser and website by encrypting the connection.

However, HTTPS alone does not prove that a website is legitimate.

---

## SSL Certificate

The SSL certificate helps establish the secure connection between the browser and website.

UIDetect checks the website's certificate as part of its security assessment.

---

## TLS

TLS is the technology used to protect information while it travels between the browser and website.

UIDetect identifies the negotiated TLS protocol information during its security assessment.

Newer TLS versions generally provide stronger protection than older versions.

---

## Google Safe Browsing

Google Safe Browsing provides an additional website reputation check.

It checks whether a website is known to be associated with phishing, malware or other harmful activities.

---

# 16. Website Security and Security Headers

UIDetect checks several HTTP security headers.

The headers include:

- HSTS
- Content Security Policy
- X-Frame-Options
- X-Content-Type-Options
- Referrer Policy

| Header | Simple Explanation |
|---|---|
| HSTS | Helps ensure that browsers use secure HTTPS connections |
| Content Security Policy | Helps control which scripts and other resources a website can load |
| X-Frame-Options | Helps protect against clickjacking |
| X-Content-Type-Options | Helps prevent incorrect interpretation of file types |
| Referrer Policy | Controls how much referrer information is shared with another website |

Missing security headers do not automatically mean that a website is malicious.

They should be considered together with the other UIDetect security indicators.

---

# 17. Domain Information

UIDetect retrieves available domain information such as:

- Domain name
- Registrar
- Registration date
- Expiration date
- Domain age
- Domain status

## Domain Age

Domain age provides additional context when evaluating unfamiliar websites.

A very new domain may require additional caution.

However, a newly registered domain is not automatically malicious.

## Registrar

The registrar is the company responsible for registering and managing the domain name.

> **Important:** Domain age and registrar information should not be used by themselves to determine whether a website is safe.

---

# 18. VirusTotal Assessment

UIDetect uses VirusTotal as an additional website reputation assessment source.

VirusTotal may provide results such as:

- Malicious
- Suspicious
- Harmless
- Undetected
- Timeout

### Understanding Detection Counts

**Malicious**  
Number of security engines that identified potentially malicious activity.

**Suspicious**  
Number of security engines that considered the website suspicious.

**Harmless**  
Number of security engines that did not identify malicious activity.

**Undetected**  
Security engines that did not detect malicious or suspicious activity.

**Timeout**  
Security engines that did not return a result within the available scanning time.

VirusTotal is an additional security indicator and should be considered together with the other UIDetect assessment results.

---

# 19. OpenPhish Assessment

UIDetect uses OpenPhish as an additional phishing reputation assessment source.

UIDetect checks whether the assessed website is listed in the available OpenPhish phishing feed.

Possible results include:

| Result | Meaning |
|---|---|
| **Not Listed** | The website was not found in the available OpenPhish feed |
| **Listed** | The website was found in the available OpenPhish phishing feed |
| **Unavailable** | The OpenPhish check could not provide a result |

A website not being listed by OpenPhish does not guarantee that it is safe.

OpenPhish is one of several indicators used by UIDetect.

---

# 20. AI Recommendation

UIDetect uses the local:

```text
qwen2.5:3b
```

model through Ollama to convert technical security assessment results into recommendations that are easier for users to understand.

The AI recommendation uses the available UIDetect security assessment results.

It provides user-facing information such as:

- About the website
- Security warning
- Recommendation

The AI does not replace the underlying security checks.

> **Important:** AI recommendations should be treated as security guidance and not as an absolute guarantee that a website is safe or unsafe.

---

# 21. Context-Aware Security Assessment

UIDetect can provide additional security warnings when security-sensitive interactions are detected.

Supported interaction types include:

| Interaction | Purpose |
|---|---|
| Login | Assesses potential risk when entering account credentials |
| Registration | Assesses potential risk when creating an account or providing registration information |
| Upload | Assesses potential risk before uploading files or information |
| Download | Helps identify potential risk when downloading files or other content |
| Payment | Assesses potential risk during payment or checkout actions |
| Logout | Detects logout-related security-sensitive interaction |

### Risk Levels

| Risk Level | Meaning |
|---|---|
| Very Low / Low | The interaction shows relatively low risk based on the available assessment |
| Medium | The user should review the warning before continuing |
| High / Critical | The interaction may present a significant security concern |

When a High or Critical warning appears, carefully consider whether to continue.

This is especially important when the interaction involves:

- Passwords
- Personal information
- File uploads
- Downloads
- Payments

---

# 22. Assessment Sources

UIDetect combines information from several assessment sources.

| Source | Type | Purpose |
|---|---|---|
| VirusTotal | Third-party reputation API | Provides aggregated website reputation results from multiple security engines |
| Google Safe Browsing | Third-party reputation API | Checks whether a website is known for phishing, malware or unwanted software |
| OpenPhish | Third-party phishing feed | Checks whether a URL appears in the available phishing feed |
| WHOIS / RDAP | Domain registry information | Provides domain registration and status information |
| HTTPS Check | Direct UIDetect backend check | Checks whether the website uses HTTPS |
| SSL / TLS Check | Direct UIDetect backend check | Checks certificate and TLS information |
| HTTP Security Headers | Direct UIDetect backend check | Checks important website security headers |
| UIDetect AI | Local AI model | Converts available assessment results into user-friendly recommendations |

The AI model is not a reputation source. It does not provide independent security evidence.

Instead, it uses the security assessment results already produced by UIDetect.

> **Important:** Third-party services such as VirusTotal, Google Safe Browsing and OpenPhish are independent services and are not operated by UIDetect.

If an external source is unavailable, UIDetect does not simply assume a result.

The affected source may be displayed as:

```text
Unavailable
```

or another unavailable/unknown state.

Users should review the other available security indicators.

---

# 23. Troubleshooting

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

1. Make sure the UIDetect Launcher is running.
2. Make sure the UIDetect backend is running.
3. Check your Internet connection.
4. Reload the website.
5. Try scanning again.

If UIDetect is no longer running, start it again using:

```text
UIDetect_Setup.exe
```

---

## AI Recommendation Is Unavailable

Make sure the UIDetect Launcher and Ollama are running.

For advanced troubleshooting, check the installed Ollama models:

```bash
ollama list
```

Confirm that:

```text
qwen2.5:3b
```

is available.

---

## UIDetect Does Not Appear in Chrome

Open:

```text
chrome://extensions/
```

Then:

1. Enable **Developer mode**.
2. Click **Load unpacked**.
3. Select the extracted UIDetect extension folder.
4. Make sure the folder contains:
   ```text
   manifest.json
   ```
5. Confirm that UIDetect appears in the extension list.
6. Make sure the extension is enabled.

---

## VirusTotal Information Is Unavailable

VirusTotal may occasionally be unavailable or may not return a result.

Possible causes include:

- Internet connection problems
- Missing API configuration
- Service limitations
- Temporary service availability issues

If VirusTotal is unavailable, review the other UIDetect security indicators instead of relying on a single assessment source.

---

## OpenPhish Information Is Unavailable

OpenPhish may occasionally be unavailable or may not provide a result.

If OpenPhish is unavailable, review the other UIDetect security indicators.

---

## Scan Is Taking Too Long

UIDetect performs multiple security checks and may communicate with external services.

Wait for the assessment to complete.

If you do not want to continue the current scan, use the **Cancel Scan** button when it is available.

After cancellation, a new scan can be started.

---

# 24. Quick Setup

For normal users, follow this order:

```text
1. Download UIDetect_Setup.exe
        ↓
2. Run UIDetect_Setup.exe
        ↓
3. Allow the installer to check and prepare required components
        ↓
4. Wait until installation is completed successfully
        ↓
5. Launch UIDetect
        ↓
6. Keep the UIDetect Launcher running
        ↓
7. Click Open Chrome
        ↓
8. Open chrome://extensions/
        ↓
9. Enable Developer mode
        ↓
10. Click Load unpacked
        ↓
11. Select the UIDetect extension folder
        ↓
12. Make sure UIDetect is enabled
        ↓
13. Open a website
        ↓
14. Click the UIDetect extension
        ↓
15. Click Scan Website
        ↓
16. Review the security assessment
        ↓
17. Read the AI Recommendation
```

### Important

Normal users do **not** need to manually install:

```text
Python 3.13.14
Ollama
qwen2.5:3b
```

The UIDetect installer checks and prepares these components when required.

---

# 25. GitHub Distribution

The recommended UIDetect GitHub repository structure is:

```text
UIDetect/
├── backend/
├── content/
├── popup/
├── scripts/
├── icons/
├── installer/
│   └── UIDetect_Setup.iss
├── docs/
│   └── index.html
├── manifest.json
├── Install_UIDetect.bat
└── Start_UIDetect.bat
```

The repository provides three main distribution areas:

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

## Source Code

The GitHub repository contains the UIDetect source code and project files.

The installer source is located at:

```text
installer/UIDetect_Setup.iss
```

## GitHub Pages

The UIDetect User Manual is maintained in:

```text
docs/index.html
```

GitHub Pages can be used to provide the online version of the manual.

## GitHub Releases

The compiled installer should be distributed through GitHub Releases.

The main installer file is:

```text
UIDetect_Setup.exe
```

This allows normal users to download the installer without needing to compile the Inno Setup project themselves.

---

# 26. Important Security Notice

UIDetect is designed to assist users in understanding website security.

UIDetect **does not guarantee** that a website is completely safe or malicious.

Users should continue to exercise caution when:

- Entering passwords
- Entering financial information
- Providing personal information
- Uploading files
- Downloading files
- Interacting with unfamiliar websites

HTTPS alone does not prove that a website is legitimate.

A high Security Score does not guarantee that a website is safe.

A website that is not listed by a reputation service does not automatically mean that it is safe.

Users should consider multiple security indicators before deciding whether to trust or interact with a website.

---

**UIDetect — Intelligent Website Security Assessment**
