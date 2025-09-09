<p align="center">
  <a href="https://github.com/Jo0X01/TempMail-Generator">
    <img src="https://raw.githubusercontent.com/Jo0X01/TempMail-Generator/refs/heads/main/TempMailGenerator.ico" alt="Temp Mail Generator" width="300" height="250">
  </a>
</p>
<p align="center">
  <a href="https://pypi.org/project/TempMail-Generator/">
    <img src="https://img.shields.io/badge/-PyPi-blue.svg?logo=pypi&labelColor=555555&style=for-the-badge" alt="PyPi">
  </a>
  <a href="https://github.com/Jo0X01/TempMail-Generator">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg?style=for-the-badge" alt="License: MIT">
  </a>
</p>


# Temp Mail Generator

A lightweight **temporary email generator** built with Flask (Python) and a modern frontend. It allows you to quickly generate disposable email addresses, view incoming messages, and refresh your inbox automatically.

---

## Demo

You can try the live demo here:  
**[View Demo on GitHub](https://htmlpreview.github.io/?https://github.com/Jo0X01/TempMail-Generator/blob/main/TempMail_Generator/templates/index.html)**

---

## Features

- **Generate temporary emails** with one click
- **Read incoming messages** in a modern inbox interface
- Automatic inbox refresh every 10 seconds
- Copy email to clipboard
- Frontend with animated gradient UI
- Multiple API key fallback for reliability
- CLI support with `temp-mail` command after installation

---

## Prerequisites

- Python 3.0+
- pip (Python package manager)
- A [RapidAPI](https://rapidapi.com/) account with access to [Temp Mail 44 API](https://rapidapi.com/calvinloveland335703-0p6BxLYIH8f/api/temp-mail44)

---

## Installation

### From PyPI
```bash
pip install TempMail-Generator
```

or

```bash
pip3 install TempMail-Generator
```

### From Source
```bash
git clone https://github.com/Jo0X01/TempMail-Generator.git
cd TempMail-Generator
pip install -r requirements.txt
```

---

## Configuration

To edit your API keys and endpoints:
```bash
temp-mail --config
```
*(or `python main.py --config` if running from source)*
### Note
* by defualt if u add api keys via python code or via cli
*  it will store them in temp_user_path/config.json

---

## Usage

### Start the server (recommended way)

```bash
python -m TempMail_Generator
```

### OR

```bash
temp-mail
```

### With custom options
```bash
temp-mail --host 0.0.0.0 --port 8080 --no-browser
```

### From source code
```bash
python main.py
```

## Python Code

```bash

from TempMail_Generator import TempMailGenerator
mail = TempMailGenerator()

# to configure the api
api_list = ["api_key_1","api_key_2"]
mail.add_api(api_list) 

# just create temp mail
temp_mail = mail.generate()
# read inbox of created temp mail
json_inbox = temp_mail.read_inbox()

# start server
mail.start_server(True,"127.0.0.1",5555)
```

---

## License

This project is licensed under the **MIT License**.
