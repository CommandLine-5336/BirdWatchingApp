# BirdWatcher App

A web-based application designed for tracking bird sightings and managing user feeds. The infrastructure supports local virtualized environments and automated deployment pipelines.

## Architecture & Request Flow

Multi-node architecture designed for high availability and load distribution:

* **Client Request:** Users access the web interface via a browser.
* **Load Balancer:** An NGINX reverse proxy receives all incoming traffic and distributes it across application servers.
* **Application Tier:** Multiple Flask web server instances process business logic, handle deduplication, and manage the scrolling feed.
* **Database Tier:** An isolated database instance securely stores user data, picture states, and feed entries.
* **Hosting:** Supports local testing via Vagrant and Oracle VirtualBox, with CI/CD automated via Jenkins.

## Repository Structure

* `scripts/` — Provisioning and infrastructure configuration files.
* `src/` — Core application source code (frontend and backend logic).
* `.github/` — Github workflows.
* `.pre-commit-config.yaml` — Pre-commit hook definitions.
* `test.sh` — Execution script for automated test suites.

---

## APP Infrastructure as Code

### Pre-commit hook installation

In order to install pre-commit hooks in terminal execute following commands:

* **For Ubuntu:** `sudo apt install pre-commit`
* **For Windows:** `pip install pre-commit`
* **For Mac:** `brew install pre-commit`

Run `pre-commit install` inside of the folder with `.pre-commit-config.yaml`.
Done.

### Local deployment

1. Download `scripts` folder.
2. Execute `vagrant up` in terminal.
3. Pass double proxying.
4. Open application on `10/11/12` ports in browser.
5. Done.

### How to set up Jenkins with Ansible

**Install Jenkins:**
1. Go to `http://jenkins_machine_ip:8080` (or `http://localhost:8080` if setting up on a host machine) and follow installation guide.
2. When prompted, install recommended plugins.

**Install Ansible & Plugin:**
1. Install Ansible globally.
2. Go to **Manage Jenkins** -> **Plugins** -> **Available plugins**.
3. Search 'Ansible' and download first option.
4. Go to **Manage Jenkins** -> **Tools** -> **Ansible installation** -> **Add Ansible**.
5. Name the installation `Ansible` and use `/usr/bin` as path.
6. Click **Save**.

**Import pipeline:**
1. Click **New Item** on the home page.
2. Select **Pipeline** item type and name your pipeline.
3. Go to **Pipeline** -> **Definition** and choose **Pipeline script from SCM**.
4. Choose **Git** and paste this repository URL.
5. Paste `refs/heads/main` as **Branch Specifier**.
6. Click **Save**.

**Set up secrets:**
Go to **Manage Jenkins** -> **Credentials** -> **System** -> **Global credentials** -> **Add Credentials**:
* Add SSH key for the virtual machines and use `vm_ssh_key` as the credentials' ID.
* Add AWS region `app_s3_region` and bucket name `app_s3_bucket`.
* Add secrets for the playbooks with the following IDs:
  * `database_name` (Secret text)
  * `database_credentials` (Username with password)
  * `flask_secret_key` (Secret text)
  * `app_s3_bucket` (Secret text)
  * `app_s3_region` (Secret text)
  * `gossip_key` (Secret text) - it should be previously generated on the Consul server.
  * `agent_token` (Secret text) - it should be previously generated on the Consul server.

### How pipeline builds and runs the application

1. Push changes to Git repository.
2. Jenkins triggers automatically.
3. Jenkins executes Ansible playbooks.
4. Pipeline rebuilds components with new changes.
5. Application runs automatically with updates.
