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

If running inside Docker, you must start Docker with:

```
docker run -it -p 7860:7860 -e GRADIO_SERVER_NAME=0.0.0.0 --rm fishies43/defi
```

Start Gradio

```
python app.py
```

## How to use

This app aims to give user a close experience to a normal "searching hotel price" experience.

- Enter an username in `Signup username` or leave it as a random string and press `Signup`.
- New user will automatically appear in `Login username`. Choose one username and press `Login`.
- The `Current user` shows which user is currently logged in.
- Choose `Languages`, `Is mobile`, `Date before` and `City`.
- Press `Get price`, the price will be shown in `Price`.
- `Past requests` show the previous requests made by the current user and will automatically reload if:
  - The current user makes a new price request (press the `Get Price` button).
  - A new user logged in.
- Choose one of `Past requests` and press `Get past request` to view the response corresponding to that request.
