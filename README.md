# 📈 Streamlit Graftool 

This project is a boilerplate for anyone who'd like to use Streamlit as a supervision tool.

## Why ? 

Because Streamlit is designed to ease data analytics with seamless integration with plotting and data process libs. Furthermore, Streamlit is easy to use and customize for people who know more about platforms than front-end code.
This makes Streamlit a very good candidate for SRE/Devops/Plaform Engineers who want to customize their supervision experience.

## What 

[Online demo](https://graftool.streamlit.app/)

Currently includes: 
 * a structured project
 * some functions to ease prometheus and charts render
 * a sample of prometheus dashboard you can reuse,
 * an example of kubernetes api integration you can adapt,
 * an example of OpenAI ChatGPT integration

This a very young project. Also most of the current functions names/signature may change in future. Do not use for production.

## Config

Can be configured either with environment variables or in `.streamlit/secrets.toml`:

| env var              | secrets.toml         |                           |
|----------------------|----------------------|---------------------------|
| PROM_CREDENTIALS_URL | prom_credentials.url | Set target prometheus url |
| OPENAI_API_KEY       | OPENAI_API_KEY       | Set OpenAI api key        | 

## Deploy

### Docker

Customize source and build Docker image. Then run with a port-forward to 8051 and env vars. Here is demo with pre-built docker image: 

```
docker run -p 8851:8501 -e PROM_CREDENTIALS_URL=https://prometheus.demo.do.prometheus.io -e OPENAI_API_KEY="sk-XXXX"  jseguillon/graftool:main
```

### Kubernetes

Create secret:

```
kubectl create secret generic graftool-secrets \
  --from-literal=OPENAI_API_KEY=XXX-KEY \
  --from-literal=PROM_CREDENTIALS_URL=https://prometheus.demo.do.prometheus.io
```

Apply Deployment and Service

```
kubectl apply -f kubernetes/bundle.yaml
```

