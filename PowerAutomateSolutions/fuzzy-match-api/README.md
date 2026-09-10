you have mentioned that push Azure Container Registry (ACR) then what kind of info i needed from them to do this encloding login as well (full steps)

# Fuzzy Match API

Checks whether `text1` is present in `text2` (case-insensitive), scored with
[rapidfuzz](https://github.com/rapidfuzz/RapidFuzz) `partial_ratio` against a
configurable threshold.

## API

### `POST /fuzzymatchapi`

Request:

```json
{
  "text1": " Miami Dade Police Department",
  "text2": "JASMINE PHILLIPS vs MIAMI DADE POLICE DEPARTMENT et al",
  "threshold": 0.6
}
```

- `text1`, `text2`: required, non-empty strings.
- `threshold`: optional, `0`-`1`, defaults to `0.6`.

Response:

```json
{
  "result": "Match Found",
  "score": 100.0
}
```

### `GET /health`

Liveness check, returns `{"status": "ok"}`.

---

## Run locally (Terminal & VS Code)

### 1. Prerequisites & Installation
Ensure you are in the root directory (the folder containing the `app/` folder, not inside `app/` itself).
```bash
pip install -e ".[dev]"
```
*(Note: If you run into `ModuleNotFoundError`, you can install dependencies manually using `pip install rapidfuzz fastapi uvicorn`).*

### 2. Start the Server
Run Uvicorn as a Python module to ensure correct path resolution:
```bash
uvicorn app.main:app --reload
python -m uvicorn app.main:app --reload
```

### 3. Testing in VS Code (REST Client)
Instead of using `curl`, you can test the API directly inside VS Code:
1. Install the **REST Client** extension.
2. Create a file named `test.http` in your project root.
3. Paste the following into the file:
   ```http
   ### Test Fuzzy Match API
   POST http://127.0.0.1:8000/fuzzymatchapi
   Content-Type: application/json

   {
       "text1": " Miami Dade Police Department",
       "text2": "JASMINE PHILLIPS vs MIAMI DADE POLICE DEPARTMENT et al",
       "threshold": 0.6
   }
   ```
4. Click the **Send Request** button that appears above the URL.

Interactive docs are also available at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## Docker & Deployment

### Option 1: Docker Compose (Recommended for VS Code)
Using the included `docker-compose.yml` file, you can start the API with a single click.
* **In VS Code:** Open `docker-compose.yml`, right-click inside the file, and select **Compose Up** (or click the **Start All Services** prompt if you have the Docker extension installed).
* **In Terminal:** 
  ```bash
  docker-compose up -d
  ```

### Option 2: Standard Docker Commands
```bash
docker build -t fuzzymatch-api .
docker run -p 8000:8000 fuzzymatch-api
```

### Exporting for Azure Deployment
To share the compiled container image with the Azure infrastructure team:
1. Build the image locally (`docker build -t fuzzymatch-api .`).
2. Export it to a `.tar` archive:
```bash
docker save -o fuzzymatch-api.tar fuzzymatch-api
```
3. Share the `.tar` file with the team. They can load it into their environment using `docker load -i fuzzymatch-api.tar`.

---

## Tests

```bash
pytest -v
```
