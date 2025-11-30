# Deployment Guide (Render.com)

This guide explains how to deploy the C2 Framework to **Render.com** for free.

## Prerequisites
- A GitHub account.
- A [Render.com](https://render.com) account.

## Steps

1. **Fork/Clone the Repository**
   Ensure you have your own copy of this repository on GitHub.
   Repo: `https://github.com/c0d3d3m0n/C2`

2. **Create a New Web Service on Render**
   - Log in to your Render dashboard.
   - Click **New +** and select **Web Service**.
   - Connect your GitHub account if you haven't already.
   - Search for your `C2` repository and click **Connect**.

3. **Configure the Service**
   - **Name**: `c2-server` (or any name you prefer)
   - **Region**: Choose the one closest to you.
   - **Branch**: `main`
   - **Runtime**: Select **Docker**.
   - **Instance Type**: Select **Free**.

4. **Deploy**
   - Click **Create Web Service**.
   - Render will start building your Docker image. This might take a few minutes.
   - Once finished, you will see a green "Live" badge and your URL (e.g., `https://c2-server.onrender.com`).

## Important Notes
- **Database**: The current configuration uses SQLite (`c2.db`). On the free tier of Render, the filesystem is **ephemeral**. This means **all data (registered agents, results) will be lost** if the service restarts or redeploys.
    - *Solution for persistence*: Upgrade to a paid plan with a persistent disk or modify the code to use an external database like PostgreSQL (Render offers a managed PostgreSQL service).
- **Client Connection**: Update your client code to point to the new Render URL instead of `http://127.0.0.1:8000`.

## Updating the Client
When running the client, make sure to specify the remote URL:
```bash
python client/cli.py --url https://your-app-name.onrender.com
```
