# Azure Deployment Guide: Fuzzy Match API

## Requirements

Before beginning the deployment process, ensure the host machine executing these commands has the following:

* **Docker Engine:** Installed and actively running (required to unpack the `.tar` archive and push to ACR).
* **Azure CLI:** Installed and authenticated (`az login`).
* **ACR Access:** The executing user or Service Principal must have the `AcrPush` role assigned for the target Azure Container Registry.
* **App Service Access:** Contributor access to the target Azure App Service to modify configuration settings.
* **Deliverable:** The provided `fuzzymatch-api.tar` file downloaded to the local working directory.

---

## Deployment Steps

1. **Load the Archive:** Import the provided `.tar` file into your local Docker daemon environment.
   `docker load -i fuzzymatch-api.tar`

2. **Tag the Image:** Replace `<acr-name>` with the actual registry URL (e.g., `companyregistry.azurecr.io`).
   `docker tag fuzzymatch-api:latest <acr-name>.azurecr.io/fuzzymatch-api:latest`

3. **Push to ACR:** Authenticate with the registry and upload the image.
   `az acr login --name <acr-name>`
   `docker push <acr-name>.azurecr.io/fuzzymatch-api:latest`

4. **App Service Configuration:** Ensure these Application Settings are applied in the Azure Portal before starting the Web App for Containers:
   * `WEBSITES_PORT`: `8000`
   * `WEBSITES_CONTAINER_START_TIME_LIMIT`: `1800`

---

## Troubleshooting & Common Errors

* **"Unauthorized: authentication required" (Step 3):** The Azure CLI session lacks Push permissions to the ACR. Run `az login` to re-authenticate with an account that has the `AcrPush` role assigned.
* **"Container didn't respond to HTTP pings on port 80" (Step 4):** Azure routes web traffic to port 80 by default, but this container strictly expects port 8000. Double-check that `WEBSITES_PORT` is correctly saved in the App Service configuration variables.
* **"No space left on device" (Step 1):** The host machine lacks disk space to unpack the `.tar` file. Run `docker system prune` to clear unused Docker images and retry the load command.
* **"Cannot connect to the Docker daemon" (Step 1 or 2):** Docker is not running in the background. Start Docker Desktop (or the Docker service) and ensure it has fully initialized before running commands.