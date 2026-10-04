# High-Level Design (HLD) — Online Coding Assessment Platform

## Overview

This folder contains the complete High-Level Design (HLD) for a **Scalable Online Coding Assessment Platform** built for colleges and recruiters to conduct coding tests for thousands of concurrent students.

The documentation is written from the perspective of a student explaining their design decisions using clear, natural, and practical language.

---

## Deliverables in this Section

- [architecture.md](file:///c:/Users/varun/OneDrive/Desktop/quantumNique/week-1/HLD/architecture.md): The full design document covering all 24 system requirements, calculations, scaling, security, and 5 trade-offs.
- [architecture.mmd](file:///c:/Users/varun/OneDrive/Desktop/quantumNique/week-1/HLD/architecture.mmd): Mermaid architecture diagram visualizing clients, API gateway, microservices, message queue, worker pools, database, cache, and monitoring.
- [data-model.mmd](file:///c:/Users/varun/OneDrive/Desktop/quantumNique/week-1/HLD/data-model.mmd): Mermaid Entity-Relationship diagram showing the data model (Users, Assessments, Questions, TestCases, Submissions, Results).
- [APIs.md](file:///c:/Users/varun/OneDrive/Desktop/quantumNique/week-1/HLD/APIs.md): Major API specifications with HTTP methods, endpoints, request payloads, and response structures.

---

## The Core Submission Flow

The core lifecycle of a student's code submission follows this 6-step pipeline:

```
[1. Submit Code]
       ↓
[2. Queue Job]
       ↓
[3. Execute Sandbox]
       ↓
[4. Evaluate Verdict]
       ↓
[5. Store Result]
       ↓
[6. Return Status]
```

### What happens at every step:
1. **Submit Code**:
   - The student clicks "Submit" in the web editor.
   - The frontend sends a `POST /api/v1/submissions` request containing the code, language, question ID, and assessment ID.
   - The Submission Service verifies the student's active token and checks rate limits in Redis.
2. **Queue Job**:
   - The Submission Service creates a submission row in PostgreSQL with status `QUEUED`.
   - It pushes a task message `{submission_id, question_id, language, code}` to RabbitMQ.
   - The service immediately responds to the student with HTTP 202 Accepted and the `submission_id`.
3. **Execute Sandbox**:
   - An available worker process from the Judge Service pulls the task from RabbitMQ.
   - The worker grabs a pre-warmed sandbox container (Docker with gVisor).
   - Network access is disabled, memory is capped at 256 MB, and CPU execution time is bounded by a timer (e.g. 2.0 seconds).
   - The worker compiles (if C++/Java) and executes the code against test cases fed through standard input.
4. **Evaluate Verdict**:
   - The Result Service compares the standard output produced by the candidate's code against the expected output.
   - It verifies whether the program finished within time limits and memory limits.
   - It assigns a verdict: `ACCEPTED`, `WRONG_ANSWER`, `TIME_LIMIT_EXCEEDED`, `MEMORY_LIMIT_EXCEEDED`, or `COMPILATION_ERROR`.
5. **Store Result**:
   - The Result Service updates the submission status to `COMPLETED` and writes test breakdown and score into the `Results` table in PostgreSQL.
   - It updates the cached result in Redis so upcoming queries are fast.
6. **Return Status**:
   - The student's browser polls `GET /api/v1/submissions/{id}` or receives a notification.
   - The browser displays the final verdict, marks scored, and execution time to the student.

---

## Required System Components

1. **Client**: React web app for students and admin dashboard for test organizers.
2. **Load Balancer / API Gateway**: Routes traffic, terminates SSL, and applies rate limits.
3. **Authentication Service**: Issues and checks JWT tokens for Students and Admins.
4. **Assessment Service**: Manages exam schedules, durations, and participant enrollment.
5. **Question Service**: Serves problem descriptions and public sample test cases.
6. **Submission Service**: Validates and ingests code submissions into the queue.
7. **Judge / Execution Service**: Manages worker containers and dispatches test cases.
8. **Result Service**: Evaluates outputs, calculates points, and produces final verdicts.
9. **Database (PostgreSQL)**: Relational store for users, questions, submissions, and scores.
10. **Cache (Redis)**: Caches questions, sessions, and submission rate limits.
11. **Message Queue (RabbitMQ)**: Buffers submissions so peak bursts do not crash workers.
12. **Object Storage (S3 / MinIO)**: Stores large test case files and raw submitted code.
13. **Monitoring (Prometheus & Grafana)**: Tracks queue lag, worker CPU, and error rates.

---

## Key Design Trade-Offs Summary

1. **PostgreSQL vs NoSQL**:
   - *Choice*: PostgreSQL.
   - *Why*: The data has clear relational integrity between exams, questions, submissions, and scores. Foreign keys prevent orphan rows, and data volume is under 1 GB per test.
2. **Asynchronous Queue vs Synchronous Execution**:
   - *Choice*: Asynchronous Queue.
   - *Why*: Code execution takes 2–5 seconds. Synchronous requests would lock web threads and cause request drops during submission spikes.
3. **Redis Caching vs Direct DB Access**:
   - *Choice*: Redis Cache.
   - *Why*: All 10,000 students read the same 4 questions during a test. Caching eliminates 95% of question read traffic to PostgreSQL.
4. **Pre-warmed Container Pool vs Full Virtual Machines**:
   - *Choice*: Pre-warmed Container Pool (Docker / gVisor).
   - *Why*: Full VMs take too long to boot and consume heavy memory. Pre-warmed containers launch in milliseconds and provide strong isolation without network access.
5. **Short Polling vs Persistent WebSockets**:
   - *Choice*: Short-interval HTTP Polling (every 2 seconds for a short window).
   - *Why*: Maintaining 10,000 active WebSocket connections over flaky campus Wi-Fi causes frequent drops and reconnection complexity. Short polling is stateless, lightweight, and firewall-friendly.

---

## Viva / Interview Preparation

1. **Why do we need a message queue in an online judge?**
   - *"I used a message queue because running code takes a few seconds. If thousands of students submit code at the same time, a queue buffers the requests so the servers don't crash while workers evaluate submissions steadily."*
2. **How do you prevent malicious student code from harming the server?**
   - *"I used isolated sandbox containers with network access completely disabled. I also set strict cgroup limits on CPU time, memory, and process count so infinite loops or fork bombs get killed automatically."*
3. **How do you keep hidden test cases safe from students?**
   - *"The API that students call to get questions only returns public sample test cases. Hidden test cases are stored in object storage and fetched only by the backend Judge Service during evaluation."*
4. **Why did you pick PostgreSQL instead of MongoDB?**
   - *"I chose PostgreSQL because our data has strong relationships—assessments have questions, questions have test cases, and submissions produce results. ACID transactions also ensure student scores and submissions are never lost."*
5. **How does the system handle a sudden burst of 1,000 submissions in the last minute?**
   - *"The Submission Service saves the submission with status QUEUED and puts a message on RabbitMQ in a few milliseconds. The students get an immediate HTTP 202 response. The queue absorbs the spike while worker containers drain and process them."*

---

## Assumptions & Limitations

- **Assumptions**: A peak university test involves around 10,000 concurrent students and 4 questions per test. Average submitted code size is ~5 KB.
- **Limitations**: The design assumes a managed container environment for workers (e.g. AWS ECS/EKS or Linux worker VMs with Docker). For specialized low-level hardware tests (e.g. assembly or hardware simulation), custom virtualization would be needed.
