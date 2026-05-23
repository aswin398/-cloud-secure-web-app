# Cloud-Secure-Web-App (Multi-Tier DevSecOps Deployment)

This repository contains a production-hardened, three-tier Flask web service deployed natively on AWS infrastructure. The application architecture enforces strict network isolation, cryptographically secure data storage, and automated static security analysis.

## 🏗️ Architecture & Security Controls

* **Network Subnet Isolation (VPC):** The application compute tier sits securely within public subnets, while the Amazon RDS MySQL database engine is entirely locked within isolated private subnets with no public route to the internet.
* **Least-Privilege Firewalls (Security Groups):** The database layer is restricted to accept traffic *only* on port 3306 originating directly from the web tier security group. 
* **Nginx Reverse Proxy Shield:** Nginx acts as a front-facing security gateway on port 80, reverse-proxying incoming requests to Gunicorn/Flask on port 5000 while injecting security defense headers (`X-Frame-Options`, `X-Content-Type-Options`, `Content-Security-Policy`).
* **Cryptographic Data Hashing:** User account passwords undergo high-entropy salting and hashing utilizing `Flask-Bcrypt` before committing entries to disk.

## 🤖 DevSecOps CI/CD Automation Pipeline
This project integrates an automated GitHub Actions workflow (`devsecops.yml`) that executes on every codebase push to `main`. The pipeline runs:
1. **Flake8:** Comprehensive static analysis and code quality checks.
2. **Bandit:** Automated Static Application Security Testing (SAST) to detect vulnerable dependencies, cleartext variables, or code flaws.
3. **Trivy:** Complete file-system and container layer structural risk scanning.

## 📊 Live Monitoring & Observability
Centralized application logging is handled natively via the AWS CloudWatch Agent daemon, streaming production telemetry directly to custom log groups:
* `capstone-nginx-web-traffic` (Tracks API endpoint validation requests)
* `capstone-system-auth-logs` (Tracks server authentication/SSH attempts)
