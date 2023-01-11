# Defi AI 2022

This package provides a Python interface to scrape, save and load data from a Google Cloud SQL server.

---

# Installation

## Local machine

To install this package for loading/saving data

```bash
git clone https://github.com/vnghia/defi-ai
cd defi-ai && pip install .
```

To install the dependencies to train or inference.

```bash
pip install -r requirements.txt
```

## Docker

Build the image

```
docker build .
```

Or pull directly from Docker Hub

```
docker pull fishies43/defi
```

# Trainning

```
python train.py
```

# Gradio

To download pretrained model (no need if running inside Docker)

```
python model/download.py
```

Start Gradio

```
python app.py
```

## How to use

- Enter an username in `Signup username` or leave it as a random string and press `Signup`.
- New user will automatically appear in `Login username`. Choose one username and press `Login`.
- The `Current user` shows which user is currently logged in.
- Choose `City` and `Hotel brand` and press `Search hotels`.
- Choose one hotel in `Hotel`.
- Choose `Languages`, `Is mobile`, `Date before` and `Stock` (if `Stock < 0` the model will automatically regress the value of `Stock` based on other information).
- Press `Get Price`, the price will be shown in `Price`.
- `History` shows the request and prices histories of current user and will automaticall reload if:
  - The current user makes a new price request (press the `Get Price` button).
  - A new user logged in.
