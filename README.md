# SKKUed-IN
Your trusted campus connection for team building

## 1. Summary
![image1](/images/summary-1.png)
![image2](/images/summary-2.png)

## 2. Problem
It is difficult to find reliable teammates for competition participation.

Limitations of Existing Solutions:
- Everytime
    Due to its anonymity, it's difficult to assess a team member's reliability, and there's a risk of"no show".
- iCampus Bulletin Board/Messenger
    Information is scattered across various channels, making it difficult to efficiently find the optimal teammates required at a glance.

## 3. Solution
A verified identity-based team-building
platform exclusively forSKKU students.

Key features:
- Profile System
    Similar to LinkedIn, students can organize their portfolios and share their technical skill sets
- Recommendation System
    Analyzes student profiles and project
    requirements to recommend the most optimal
    teammates
- Centralized Opportunity & Party System
    All internal and external opportunities are shared centrally, allowing forimmediate "party" formation directly within the platform

## 4. Team members
<br/>
<div align="center">
<table>
<th>members</th>
    <th><a href="https://github.com/mariahwy">유혜원</a></th>
    <th><a href="https://github.com/">이명원</a></th>
    <th><a href="https://github.com/">박윤서</a></th>
    <th><a href="https://github.com/">심세윤</a></th>
    <tr>
    <td>  </td>
      <td>
        <img width="160" height="160" alt="유혜원" src="https://github.com/user-attachments/assets/d07c2440-5249-4ada-bb52-0bed83408455" />
      </td>
      <td>
        <img width="160" height="160" alt="이명원" src="" />
      </td>
      <td>
        <img width="160" height="160" alt="박윤서" src="" />
      </td>
      <td>
        <img width="160" height="160" alt="심세윤" src="" />
      </td>
    </tr>
    <tr>
    <td> roles </td>
    <td>
        <p align="center">Team Leader</p>
    </td>
    <td>
        <p align="center">A</p>
    </td>
    <td>
        <p align="center">B</p>
    </td>
    <td>
        <p align="center">C</p>
    </td>
    </tr>
  </table>
</div>

## 5. Cooperation Tools

| Tool | Use |
|------|-----------|
| **Notion** | Document meeting minutes, plans, and daily scrums |
| **GitHub** | Code Management + PR & Review Management |

## 6. Technical skills
<div align="left">
  <!-- Cloud & Infrastructure -->
  <img src="https://img.shields.io/badge/AWS%20EC2-FF9900?style=for-the-badge&logo=amazonec2&logoColor=white"/>
  <img src="https://img.shields.io/badge/AWS%20Lambda-FF9900?style=for-the-badge&logo=awslambda&logoColor=white"/>
  <img src="https://img.shields.io/badge/AWS%20DynamoDB-4053D6?style=for-the-badge&logo=amazondynamodb&logoColor=white"/>
  <img src="https://img.shields.io/badge/AWS%20S3-569A31?style=for-the-badge&logo=amazons3&logoColor=white"/>
  <img src="https://img.shields.io/badge/AWS%20RDS%20(Postgres)-527FFF?style=for-the-badge&logo=amazonrds&logoColor=white"/>
  <img src="https://img.shields.io/badge/AWS%20EventBridge-FF4F8B?style=for-the-badge&logo=amazoneventbridge&logoColor=white"/>
  <!-- Data & Processing -->
  <img src="https://img.shields.io/badge/Apache%20Spark-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white"/>
  <!-- DevOps & Tools -->
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white"/>
  <!-- Application & Frontend -->
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
  <!-- Language -->
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
</div>

---

## Backend Server

This section details the setup and execution of the FastAPI-based backend server.

### Tech Stack

| Category         | Technology                                | Purpose                               |
| ---------------- | ----------------------------------------- | ------------------------------------- |
| Language         | Python 3.11+                              | Core programming language             |
| Web Framework    | FastAPI                                   | High-performance API framework        |
| Database ORM     | SQLAlchemy                                | Database interaction and modeling     |
| Data Validation  | Pydantic                                  | Data validation and settings management |
| Password Hashing | Argon2 (`argon2-cffi`)                    | Secure password storage               |
| JWT Authentication | `python-jose`                             | Token generation and validation       |
| Server           | Uvicorn                                   | ASGI server for running FastAPI       |

### Project Structure

The backend code is organized within the `app/` directory with a modular structure.

```
app/
├── api/          # API endpoint logic
│   ├── deps.py   # Dependency injection (e.g., DB session)
│   └── v1/       # API version 1
│       └── endpoints/
│           └── auth.py # Authentication-related APIs
├── core/         # Core logic (settings, security)
│   ├── config.py
│   └── security.py
├── crud/         # Database CRUD (Create, Read, Update, Delete) operations
│   └── crud_user.py
├── db/           # Database session management and base models
│   ├── base.py
│   └── session.py
├── models/       # SQLAlchemy database models
│   └── user.py
└── schemas/      # Pydantic data schemas for request/response validation
    ├── __init__.py
    ├── token.py
    └── user.py
```

### Local Development Setup

Follow these steps to set up and run the backend server on your local machine.

**1. Create a Virtual Environment**

Create and activate a Python virtual environment. This keeps project dependencies isolated.

```shell
# Create the virtual environment
python -m venv .venv

# Activate on Windows
.venv\Scripts\activate
```

**2. Install Dependencies**

Install all required libraries from the `requirements.txt` file.

```shell
pip install -r requirements.txt
```

**3. Set Up Environment Variables**

Create a `.env` file in the project root by copying the example file.

```shell
# On Windows
copy .env.example .env
```

Open the newly created `.env` file and change `SECRET_KEY` to a new random string. The other default values are suitable for local development.

### Running the API Server

Once the setup is complete, run the Uvicorn server with the following command:

```shell
uvicorn app.main:app --reload
```

The server will be available at `http://127.0.0.1:8000`. The `--reload` flag ensures the server automatically restarts when you make code changes.

### API Documentation

With the server running, you can access the interactive API documentation (Swagger UI) by navigating to the following URL in your browser:

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

From this page, you can view all available API endpoints and test them directly.

## Frontend Server
### Local Development Setup

Follow these steps to set up and run the backend server on your local machine.

**1. Create a Virtual Environment**

Create and activate a Python virtual environment. This keeps project dependencies isolated.

```shell
# Create the virtual environment
python -m venv .venv

# Activate on Windows
.venv\Scripts\activate
```

**2. Install Dependencies**

Install all the required libraries (packages) for the project. This command creates the `node_modules` folder.

```shell
npm install
```

### Running the Development Server

Once the installation is complete, start the Vite development server with the following command:

```shell
npm run dev
```

When the server starts successfully, the terminal will display a local address like `http://localhost:5173/`.

The server run with npm run dev supports HMR (Hot Module Replacement). Similar to a --reload flag, this means that when you edit and save your code, the changes are reflected in the browser instantly without a full server restart.

### Access the Application

While the server is running, you can access the frontend application by navigating to the following URL in your browser:

`http://localhost:5173`
