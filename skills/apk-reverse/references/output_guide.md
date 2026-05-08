# APK Reverse Engineering - Results Presentation Guide

## Report Structure for the User

Always present results in clear sections using markdown. Adapt the level of detail to what the user requested.

---

## Required Sections (always include)

### 1. Identification

- App name, package, version
- SHA256 hash (for reference/verification)
- File size

### 2. Permissions

- Highlight dangerous permissions in red/bold
- Group them into: dangerous vs. normal
- Explain what each dangerous permission allows

### 3. Security Summary

- Overall assessment: Low / Medium / High / Critical risk
- Top 3-5 most important findings

---

## Optional Sections (include if relevant)

### Android Components

- Main Activities (app flow)
- Background Services
- Broadcast Receivers (especially BOOT_COMPLETED)

### Strings and URLs

- External server URLs
- Strings that look like keys or tokens
- Third-party domains (analytics, ads, CDN)

### Sensitive APIs

- List which sensitive APIs are called
- Provide context: "The app accesses contacts because..."

### Obfuscation

- If detected, mention it clearly
- Implication: more limited analysis, possible intent to hide behavior

---

## Tone and Language

- **Technical user**: use terms like DEX, Smali, API level, manifest
- **Non-technical user**: use simple language: "the app can read your SMS messages", "the app runs in the background"
- Always explain the **practical impact** of each finding
- Do not make definitive claims about maliciousness — use terms like "suspicious", "may indicate", "deserves investigation"

---

## Legal and Ethical Warnings

Include at the beginning or end of the report:

> ⚠️ This analysis is for educational, security, or research purposes only. Make sure you have authorization to analyze the APK in question.

---

## Example Risk Assessment

| Indicator                            | Weight            |
| ------------------------------------ | ----------------- |
| Dangerous permissions (each)         | +1                |
| BIND_DEVICE_ADMIN                    | +3                |
| SMS API + location together          | +2                |
| Obfuscation detected                 | +2                |
| URLs using direct IPs (not domain)   | +2                |
| Suspicious strings (keys, passwords) | +1 per occurrence |
| Native libraries (.so)               | +1                |
| Multiple DEX files                   | +1                |

- 0-2: 🟢 Low risk
- 3-5: 🟡 Moderate risk
- 6-9: 🟠 High risk
- 10+: 🔴 Critical risk
