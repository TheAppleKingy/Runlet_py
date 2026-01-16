# Runlet


**Runlet** is a system for remote code execution.  
It provides an API for solving programming problems by running code on remote services and retrieving execution results.  
 

---

- [Install](#️-install)
- [Quickstart](#-quickstart)
- [Usage](#-usage)
- [Stack](#-stack)

---

## ⚙️ Install


Before running the app, set the following environment variables:

### 🔑 JWT Auth

| Variable                 | Description                        |
|--------------------------|------------------------------------|
| `SECRET`             | Secret key to sign JWT tokens      |
| `TOKEN_EXPIRE_TIME`  | Token expiration time (in seconds) |

### 🗄 PostgreSQL

| Variable            | Description             |
|---------------------|-------------------------|
| `POSTGRES_USER`       | Database name           |
| `POSTGRES_PASSWORD`     | PostgreSQL username     |
| `POSTGRES_DB` | PostgreSQL password     |
| `POSTGRES_HOST`                |          Host using to connect to database           |

### 🏃 Runners

| Variable            | Description                             |
|---------------------|-----------------------------------------|
| `RUNNERS_CONF_PATH` | Path to runners config (runners.yaml)   |


---

To start:

```bash
make runlet.build.start
```

---

## 🚀 Quickstart

Once containers are up, the API will be ready to accept requests.  
Swagger documentation is available at:

🔗 [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📦 Usage

The API provides basic authentication features:

- Registration
- Login / Logout

>Refer to Swagger UI for request details.


---

## 🧰 Stack

- **FastAPI** – web framework  
- **PostgreSQL** – database  
- **SQLAlchemy** – ORM  
- **Alembic** – DB migrations  
- **Docker** – containerization
- **RabbitMQ** - messaging
---

Feel free to contribute or open issues.
