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
docker pull
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
