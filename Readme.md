# Iconiq Shot

<p align="center">
<img src="https://img.shields.io/badge/platform-Windows-blue">
<img src="https://img.shields.io/badge/python-3.9+-green">
<img src="https://img.shields.io/badge/license-MIT-orange">
<img src="https://img.shields.io/badge/status-Active-success">
</p>

<p align="center">
<b>Iconiq Shot — Capture. Extract. Copy. Instantly.</b>
</p>

---

## Overview

**Iconiq Shot** is a modern lightweight **screen capture and OCR text extraction tool for Windows**.  
It allows users to quickly select any area of the screen, extract readable text instantly using OCR, copy it to the clipboard, or save the captured image.

This tool is designed for **speed, productivity, and simplicity**, making it useful for developers, researchers, students, and professionals who frequently need to copy text from screenshots.

Iconiq Shot provides a **Lightshot-style screen selection experience** combined with powerful **text extraction capabilities**.

---

## Key Features

- Custom **drag-to-select screen capture**
- **Instant OCR text extraction**
- **Copy extracted text to clipboard**
- **Save captured screenshot**
- **Floating quick action toolbar**
- **Lightweight and fast**
- **User-friendly interface**
- **Windows compatible**
- **Multiple captures without restarting**
- **Automatic save location management**

---

## Screenshots

<img src="screenshots/main.png" width="700">

<img src="screenshots/capture.png" width="700">

---

## Installation

### Method 1 — Download Prebuilt Executable (Recommended)

Download the latest version from the releases page.

⬇ **Download Latest Version**

[![Download Iconiq Shot](https://img.shields.io/badge/Download-Latest%20Release-blue?style=for-the-badge)](../../releases)

---

### Method 2 — Clone and Run From Source

Clone the repository

```bash
git clone https://github.com/astrogeeksagar/iconiqshot
cd iconiq-shot

## To Build Application

```bash
python -m PyInstaller --onefile --windowed --icon=favicon.ico --name=IconiqShot main.py