# Galario ETL — Render + PostgreSQL

A one-click ETL web app that extracts Japan & Myanmar store CSVs,
transforms them, and loads the result into a PostgreSQL database on Render.

---

## Project Structure

```
galario_render/
├── app.py              # Flask web app (ETL trigger UI + SSE log streaming)
├── extract.py          # Stage 1 — CSV → staging tables
├── transform.py        # Stage 2 — clean & standardize
├── load.py             # Stage 3 — build BIG TABLE
├── db.py               # PostgreSQL connection (SQLAlchemy)
├── requirements.txt
├── Dockerfile
├── render.yaml         # Render IaC config
└── data/
    └── source/
        ├── japan_store/
        └── myanmar_store/
```

---

## PostgreSQL Table Layout (after ETL runs)

| Layer        | Table Name                             |
|--------------|----------------------------------------|
| Staging      | `staging_japan_store_sales_data`       |
| Staging      | `staging_myanmar_store_sales_data`     |
| Staging      | `staging_japan_store_japan_customers`  |
| Staging      | *(all other CSVs…)*                    |
| Transform    | `transform_japan_sales_clean`          |
| Transform    | `transform_myanmar_sales_clean`        |
| Presentation | **`presentation_big_table`**           |

---

## Deploy on Render (step by step)

### 1. Push this folder to GitHub

```bash
cd galario_render
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

### 2. Create a Web Service on Render

1. Go to https://dashboard.render.com → **New → Web Service**
2. Connect your GitHub repo
3. Set **Runtime** → **Docker**
4. Add environment variable:
   - Key: `DATABASE_URL`
   - Value:
     ```
     postgresql://db_nako_user:3halkU77mrx0Gaw8HxpVqoDGDDNSDCpc@dpg-d7ngs4vlk1mc73d4p9m0-a.singapore-postgres.render.com/db_nako
     ```
5. Click **Create Web Service**

> ⚠️ **Tip:** Use the **Internal Database URL** if your web service and DB are in the same Render region — it's faster and free of egress charges. Find it in your DB dashboard under "Internal Database URL".

### 3. Run the ETL

Once deployed, visit your Render URL and click **▶ Run ETL Pipeline**.
Logs stream in real-time. The final `presentation_big_table` will be in your PostgreSQL DB.

---

## Environment Variables

| Variable       | Description                        |
|----------------|------------------------------------|
| `DATABASE_URL` | Full PostgreSQL connection string  |
| `PORT`         | App port (Render sets this auto)   |
