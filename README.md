# biometric-cryptography
It's not what you type, it's how you type it. A biometric encryption tool that turns your typing rhythm into an AES-256 key

# GhostCRYP (v1.0.0-beta)

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

> **"It's not what you type, it's how you type it."**

GhostRhythm is a Proof-of-Concept (PoC) security tool that implements **Biometric Keystroke Dynamics** to generate high-entropy encryption keys. Instead of relying solely on a static password, it analyzes the millisecond-accurate timing between your keystrokes to create a unique physiological signature

---

## The Concept: Beyond Passwords

Traditional passwords can be stolen via keyloggers or shoulder surfing. However, your **typing rhythm** is a behavioral biometric that is nearly impossible to replicate

GhostRhythm captures the "musiq" of your typing and transforms it into a **SHA-512** hashed **AES-256** key. Even if an attacker knows your password, they cannot decrypt your files unless they can mimic your exact typing speed and cadence.

## Key Features

- **Biometric Matrix Generation:** Captures inter-key latencies with microsecond precision.
- **Zero-Trust Architecture:** Access is denied if the biometric similarity score falls below 90%.
- **AES-256-CBC Encryption:** Industry-standard encryption powered by your unique rhythm.
- **Linux Native Integration:** Utilizes low-level `termios` and `tty` for raw input handling on Kali Linux.
- **Stealth Protection:** Designed to be resilient against traditional software-based keylogging.

## 📦 Installation & Setup

1. **Clone the research repository:**
   ```bash
   git clone [https://github.com/nazhickorkmaz/GhostRhythm.git](https://github.com/nazhickorkmaz/GhostCryp.git)
   cd GhostCryp
