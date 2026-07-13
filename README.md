# BirdWatcher App

A web-based application designed for tracking bird sightings and managing user feeds. The infrastructure supports local virtualized environments and scalable cloud deployments on AWS EC2.

## Architecture & Request Flow

Multi-node architecture designed for high availability and load distribution:

* **Client Request:** Users access the web interface via a browser.
* **Load Balancer:** An NGINX reverse proxy receives all incoming traffic and distributes it across application servers.
* **Application Tier:** Multiple Flask web server instances process business logic, handle deduplication, and manage the scrolling feed.
* **Database Tier:** An isolated database instance securely stores user data, picture states, and feed entries.
* **Hosting:** Adapted for deployment on AWS EC2 instances, with support for local testing via Vagrant and Oracle VirtualBox.

## Repository Structure

* `.github/` — CI/CD workflows and GitHub Actions configurations.
* `src/` — Core application source code (frontend and backend logic).
* `.pre-commit-config.yaml` — Pre-commit hook definitions for code quality enforcement.
* `test.sh` — Execution script for automated test suites.

## Installation & Setup

### 1. Clone the repository
```bash
git clone [https://github.com/CommandLine-5336/BirdWatchingApp.git](https://github.com/CommandLine-5336/BirdWatchingApp.git)
cd BirdWatchingApp
