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


Before running the app, set the following environment variables using .env file in build/prod. Examples of variables are in `build/prod/.example.env`.


---

To start:

```bash
make runlet.prod.build.start
```

---

## 🚀 Quickstart

Once containers are up, the API will be ready to accept requests.  
Swagger documentation is available at:

🔗 [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📦 Usage

Current service provides full API coverage for current functional requirements:

- Authenticate endpoints
- Common endpoints for all users of platform
- Endpoints for students
- Endpoints for course teacher/administrator

>Refer to Swagger UI for requests and responses details.
---
## 📌 Additional

One of the main features of platform is the running students code with specified input data. Code of code runner and gateway you can in  [Runlet_runners_py](https://github.com/TheAppleKingy/Runlet_runners_py).

---

## 🧰 Stack

- **FastAPI** – web framework  
- **PostgreSQL** – database  
- **SQLAlchemy** – ORM  
- **Alembic** – DB migrations  
- **Docker** – containerization
- **RabbitMQ**, **[ploomby](https://pypi.org/project/ploomby/)** - messaging
- **[mailgeno](https://hub.docker.com/repository/docker/theapplekingy/mailgeno/tags)** - mail service
---
## 🧪 Testing
To run tests execute:
```bash
make runlet.tests.full
```

Linting:
```bash
make runlet.lint
```