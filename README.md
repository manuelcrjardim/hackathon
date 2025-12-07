# **Neo x SpoonOS Hackathon Project**

## **📖 Overview**

This repository contains a full-stack decentralized application developed for the hackathon. It leverages the **Neo N3** blockchain for logic and settlement, **NeoFS** for decentralized data storage, and the **Spoon** framework for AI agent interactions.  
The project is an integrated ecosystem consisting of four main components:

1. **Neo Smart Contracts:** Python-based contracts governing the on-chain logic.  
2. **NeoFS Dev Environment:** A dockerized environment for interacting with Neo's distributed file system.  
3. **Spoon Core:** The backend AI agent logic and database management.  
4. **SpoonOS (Interview Avatar):** A web-based frontend featuring a live interactive avatar.

## **📂 Project Structure**

The repository is organized into specific modules for the Blockchain, Storage, AI, and Frontend layers.  
hackathon/  
└── neo/  
    ├── smart\_contract/           \# Neo N3 Smart Contracts (Python)  
    │   ├── agent.py              \# Main Agent logic contract  
    │   ├── campaign\_manager.py   \# Campaign management contract  
    │   ├── default.neo-express   \# Neo Express private net configuration  
    │   └── ...                   \# Compiled .nef and .manifest.json files  
    │  
    ├── NeoFS/  
    │   └── neofs-dev-env/        \# NeoFS Dockerized Development Environment  
    │       ├── services/         \# Docker services for NeoFS  
    │       ├── deploy\_contract.sh\# Scripts to deploy contracts to NeoFS  
    │       ├── upload\_transcript.sh \# Script to store data on NeoFS  
    │       └── Makefile          \# Make commands for NeoFS management  
    │  
    ├── spoon-core/               \# Backend AI Framework  
    │   ├── spoon\_ai/             \# Core AI logic  
    │   ├── requirements.txt      \# Python dependencies  
    │   ├── alembic.ini           \# Database migration config  
    │   └── librocksdb.so         \# Required shared libraries for RocksDB  
    │  
    ├── SpoonOS/  
    │   └── interview\_avatar/     \# Frontend Web SDK (Monorepo)  
    │       ├── liveavatar-web-sdk/  
    │       ├── apps/             \# Frontend applications  
    │       ├── packages/         \# Shared libraries  
    │       └── turbo.json        \# Turborepo build configuration  
    │  
    └── \*.py                      \# Root orchestration scripts (run\_python\_tool\_spoon.py, etc.)

## **🛠 Prerequisites**

Before running the project, ensure you have the following installed on your machine:

* **Docker & Docker Compose** (Required for running the NeoFS simulation and Neo Express containers).  
* **Python 3.8+** (Required for Smart Contracts and Spoon Core).  
* **Node.js & pnpm** (Required for the SpoonOS frontend).  
* **Neo Express** (For running a local Neo N3 blockchain).  
  * *Note: A Linux binary Neo.Express-linux-x64...tar.gz is included in neo/ directory, but installing globally via the .NET SDK is recommended.*

## **🚀 Installation & Setup**

### **1\. Smart Contracts (Neo N3)**

Located in neo/smart\_contract. This directory contains the logic for the Agent, Campaign Manager, and Hello World contracts.  
**Setup:**  
cd neo/smart\_contract

\# Install python dependencies (ensure virtual env is active)  
pip install neo3-boa

\# Start the private blockchain (Neo Express)  
neoxp run default.neo-express \-s 1

Deployment:  
You can deploy the .nef files using Neo Express or the provided python scripts.  
\# Example deployment command  
neoxp contract deploy campaign\_manager.nef wallet\_name

### **2\. Spoon Core (AI Backend)**

Located in neo/spoon-core. This handles the AI processing, database interactions, and agent logic.  
**Setup:**  
cd neo/spoon-core

\# Install dependencies  
pip install \-r requirements.txt

**System Dependencies:**

* The folder contains librocksdb.so, librocksdb-musl.so, and librocksdb-jemalloc.so. Ensure your system can locate these libraries if the Python bindings require them.  
* Alternatively, install RocksDB via your system package manager (e.g., apt-get install librocksdb-dev).

**Database Migrations:**  
alembic upgrade head

### **3\. NeoFS (Storage Layer)**

Located in neo/NeoFS/neofs-dev-env. This sets up a local NeoFS network for decentralized file storage.  
**Setup:**  
cd neo/NeoFS/neofs-dev-env

\# Start the Docker services  
make up  
\# OR  
docker-compose up \-d

**Helper Scripts:**

* ./deploy\_contract.sh: Deploys necessary storage contracts to the local chain.  
* ./upload\_transcript.sh: Uploads generated AI transcripts to NeoFS.  
* ./get\_transcript.sh: Retrieves data from NeoFS.

### **4\. SpoonOS (Frontend Avatar)**

Located in neo/SpoonOS/interview\_avatar. This is a Monorepo managed by turbo and pnpm.  
**Setup:**  
cd neo/SpoonOS/interview\_avatar/liveavatar-web-sdk

\# Install dependencies  
pnpm install

\# Run the development server  
pnpm turbo run dev

## **🏃‍♂️ Running the Full Ecosystem**

To run the complete hackathon demo, you generally need to run the services in parallel across multiple terminal windows:

1. **Terminal 1 (Blockchain):** Start Neo Express inside smart\_contract/.  
2. **Terminal 2 (Storage):** Start Docker containers inside NeoFS/neofs-dev-env/.  
3. **Terminal 3 (Backend):** Run the Spoon agent.  
   * Use the root orchestration scripts provided in neo/:

python simple\_spoon\_agent.py  
\# OR  
python run\_python\_tool\_spoon.py

4. **Terminal 4 (Frontend):** Start the SpoonOS web interface to interact with the Avatar.

## **🧩 Key Libraries & Packages Used**

### **Blockchain**

* **neo3-boa**: Python compiler for the Neo N3 Virtual Machine.  
* **neo-express**: Local private Neo N3 blockchain instance.

### **Backend / AI**

* **SQLAlchemy**: Python SQL toolkit and Object Relational Mapper.  
* **Alembic**: Lightweight database migration tool for usage with SQLAlchemy.  
* **RocksDB**: Embedded key-value store for fast storage.  
* **Spoon AI**: Custom framework for agentic workflows.

### **Frontend**

* **Next.js**: The React Framework for the Web.  
* **Turbo**: High-performance build system for JavaScript/TypeScript monorepos.  
* **PNPM**: Fast, disk space efficient package manager.

## **📜 License**

See the LICENSE file in the root directory for more details.
