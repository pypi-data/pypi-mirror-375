# SerPy

SerPy is a minimal, modern, and lightning-fast ASGI web framework for Python. It is designed for simplicity, flexibility, and performance, making it ideal for building APIs, microservices, and web applications with minimal overhead.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Example Project](#example-project)
- [Middleware](#middleware)
- [Advanced Routing](#advanced-routing)
- [Contributing](#contributing)
- [Running Locally](#running-locally)
- [License](#license)
- [Contact](#contact)

---

## Features

- **ASGI compatible**: Works seamlessly with ASGI servers like Uvicorn and Hypercorn
- **Simple routing**: Path parameters, method-based routing, and easy route registration
- **Middleware support**: Add custom middleware for logging, authentication, CORS, etc.
- **Request/Response abstraction**: Clean API for handling requests and responses
- **Modular**: Use routers to organize your application
- **Type hints**: Modern Pythonic code with type hints

---

## Installation

Install the latest release from PyPI:

```bash
pip install serpy-rest
```

Or, to use the latest development version, clone this repository:

```bash
git clone https://github.com/ragav2005/SerPy.git
cd SerPy
pip install .
```

---

## Quick Start

Create a file called `main.py`:

```python
from serpy import SerPy, Response

app = SerPy()

@app.route("/hello/{name}", methods=["GET"])
async def hello(request, name):
	return Response({"message": f"Hello, {name}!"})

# Run with: uvicorn main:app
```

Start the server:

```bash
uvicorn main:app --reload
```

---

## Example Project Structure

```
myproject/
├── main.py
├── requirements.txt
└── ...
```

---

## Middleware

Add global middleware to your app:

```python
async def log_middleware(request, call_next):
	print(f"Request: {request.method} {request.path}")
	response = await call_next(request)
	return response

app.add_middleware(log_middleware)
```

---

## Advanced Routing

Use routers to organize endpoints:

```python
from serpy import Router

user_router = Router()

@user_router.route("/users/{user_id}", methods=["GET"])
async def get_user(request, user_id):
	# Fetch user logic here
	return Response({"user_id": user_id})

app.include_router(user_router, prefix="/api")
```

---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Push to your fork and submit a pull request

Please ensure your code follows PEP8 and includes tests where appropriate.

---

## Running Locally (Development)

1. Clone the repository:
   ```bash
   git clone https://github.com/ragav2005/SerPy.git
   cd SerPy
   ```
2. (Optional) Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the example app or your own app with Uvicorn:
   ```bash
   uvicorn main:app --reload
   ```

---

## License

This project is licensed under the MIT License.

---

## Contact

Author: [ragav2005](https://github.com/ragav2005)
For questions, suggestions, or issues, please open an issue on GitHub.
