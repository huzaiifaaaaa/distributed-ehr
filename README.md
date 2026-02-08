### Overview:
A lightweight system simulating multiple hospitals sharing patient records while preserving privacy and data consistency. It uses Python + Flask as the web server, SQLite per hospital node for local storage, and a simple Raft-based consensus mechanism to replicate and keep records consistent across nodes. The system demonstrates secure inter hospital data exchange and fault tolerance in a distributed EHR setting.

### Features:
- Single hospital node: CRUD operations (Create, Read, Update, Delete) on patient records via Flask REST API.
- Multi-node simulation: 3–4 "hospitals" running as separate Flask instances (different ports or Docker containers).
- Secure sharing: Nodes communicate via HTTP/gRPC-like calls (with basic TLS/self-signed certs or API keys) to query/share patient data.
- Consensus & replication: Use a lightweight Python Raft library (e.g., raft-lite, pysyncobj, or simple custom leader-based replication) to ensure writes are replicated consistently across nodes. Leader handles writes → appends to log → replicates to followers → commits on majority ack.
- Fault tolerance demo: Kill one node → Raft elects new leader → system continues (reads may be stale briefly, writes via new leader).

### Tech Stack:
- Backend: Python 3 + Flask (REST API endpoints)
- Database: SQLite (one .db file per node, file based for simplicity)
- Consensus: Lightweight Raft impl (e.g., nikwl/raft-lite from GitHub, or PySyncObj for easiest replication)
- Communication: HTTP requests between nodes (Flask + requests lib)
- Deployment: Local processes or Docker Compose (4 containers)
- Testing: Postman for API, manual node kill for fault demo
