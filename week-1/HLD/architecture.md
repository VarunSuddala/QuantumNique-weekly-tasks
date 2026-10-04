# High-Level Design (HLD): Scalable Online Coding Assessment Platform

## 1. Functional Requirements

### Student Capabilities
- Students can log in and join scheduled assessments using their student credentials.
- Students can view questions, problem statements, constraints, and public sample test cases.
- Students can write and submit source code in supported languages (Python, Java, C++).
- Students can view the status of their code submission (Queued, Running, Completed) and see the verdict (Accepted, Wrong Answer, Time Limit Exceeded, etc.).
- Students can see their submission history and total marks scored during or after the test.

### Admin Capabilities (Colleges & Recruiters)
- Admins can create assessments with specific start times, end times, and duration limits.
- Admins can create and edit questions, configure memory and time limits, and attach public and hidden test cases.
- Admins can review student results, download grade reports, and view leaderboards.

---

## 2. Non-Functional Requirements

- **Reliability & Consistency**: Student submissions must never be lost, even if an execution worker crashes.
- **Fairness & Safe Execution**: Untrusted student code must run in an isolated environment without network access or file system tampering.
- **Low Latency for Reads**: Loading questions and dashboard data should take under 200 ms.
- **Predictable Execution Times**: A submission should be evaluated within 5 to 15 seconds during normal peak load.
- **Scalability**: The system should support up to 10,000 concurrent students taking an exam simultaneously without crashing.
- **Integrity**: Hidden test cases and expected answers must never leak to the client browser.

---

## 3. Assumptions

- An assessment lasts typically 90 to 120 minutes.
- Most submissions happen in bursts: when a test starts, when students finish the first question, and during the final 15 minutes of the test.
- The average code file size submitted by a student is between 2 KB and 10 KB.
- Each question has around 2 to 3 sample test cases and 10 to 20 hidden test cases.

---

## 4. Scale Estimates (Simple Calculations)

To design the system realistically, let us assume a large university exam scenario:

- **Assumed Concurrent Students**: 10,000 students taking a test simultaneously.
- **Questions per Test**: 4 coding questions.
- **Submissions per Student**: On average, a student submits code 5 times per question (testing small changes or fixes).
  - Total submissions per student = $4 \times 5 = 20\text{ submissions}$.
  - Total submissions during a 2-hour exam = $10,000 \times 20 = 200,000\text{ submissions}$.
- **Average Submission Rate**:
  - 200,000 submissions over 2 hours (7,200 seconds) = $\approx 28\text{ submissions per second (SPS)}$.
- **Peak Submission Rate**:
  - In the last 15 minutes or during bursts, traffic is 4 to 5 times the average.
  - Peak SPS = $28 \times 5 \approx 140\text{ submissions per second}$.
- **Read Requests (Viewing Questions / Status Checks)**:
  - Students read questions and check status roughly once every 10 seconds.
  - Read QPS = $10,000 / 10 = 1,000\text{ queries per second (QPS)}$.
- **Storage Calculation**:
  - 200,000 submissions $\times$ 5 KB average code size = $1,000,000\text{ KB} \approx 1\text{ GB}$ of code per test.
  - Relational database growth for 200,000 submission records is well under 500 MB per test.
  - This is very manageable for a standard relational database and object storage.

---

## 5. Potential Bottlenecks

1. **Code Execution Workers**: Compiling and running code takes CPU and memory. If 140 submissions arrive per second and each takes 2 seconds to run, we need enough worker capacity so the queue does not back up.
2. **Database Write Pressure**: If all students hit "Submit" at the same minute, writing every submission status directly to PostgreSQL without a queue can overload database connections.
3. **Hidden Test Cases I/O**: Reading large input and output files from the database for every single test case evaluation will slow down the database.

---

## 6. Service Responsibilities

### 1. Client
- Web frontend where students read questions, type code in an editor (like Monaco Editor), and view test results.
- Admin portal for college teachers and recruiters to build tests and view scores.

### 2. Load Balancer / API Gateway
- Distributes incoming HTTPS traffic evenly across service instances.
- Handles SSL termination and routes requests to the correct backend microservice based on API path.
- Performs basic rate limiting per IP or token.

### 3. Authentication Service
- Manages user login, registration, and role-based access control (Student vs Admin).
- Generates and verifies signed JSON Web Tokens (JWT).

### 4. Assessment Service
- Manages test schedules, student registrations, eligibility, and assessment metadata (start time, end time, duration).
- Enforces test window rules (students cannot join after the test ends).

### 5. Question Service
- Stores and serves problem descriptions, constraints, difficulty, and starter code templates.
- Provides only public sample test cases to students.
- Keeps hidden test cases protected from student queries.

### 6. Submission Service
- Receives submitted code from students.
- Saves the initial submission record with status `QUEUED` in PostgreSQL.
- Pushes a job message into the Message Queue.
- Returns an immediate HTTP 202 response with a `submission_id` to the student.

### 7. Judge / Execution Service
- Consumes jobs from the Message Queue.
- Sends the code and test cases to isolated worker sandboxes.
- Monitors execution time, memory usage, and captures standard output and error.

### 8. Result Service
- Compares the worker output against expected outputs.
- Computes final score and verdict (`ACCEPTED`, `WRONG_ANSWER`, `TIME_LIMIT_EXCEEDED`, `MEMORY_LIMIT_EXCEEDED`, `COMPILATION_ERROR`).
- Updates the database record and publishes a notification or updates Redis so the student's status check sees the result.

### 9. Database (PostgreSQL)
- Stores structured relational data: users, assessments, questions, submissions, test metadata, and final student scores.

### 10. Cache (Redis)
- Stores active assessment questions and user sessions in memory so the database is not hit repeatedly for read queries.
- Tracks submission rate limits per user.

### 11. Message Queue (RabbitMQ / Kafka)
- Decouples fast submission intake from slower code compilation and execution.
- Prevents system crashes during sudden submission spikes.

### 12. Object Storage (S3 / MinIO)
- Stores large test case input and output files (files > 1 MB) that are too big to store cleanly in relational database tables.
- Stores historical raw source code files.

### 13. Monitoring (Prometheus & Grafana)
- Tracks queue length, worker CPU and RAM usage, API response times, and failure rates.

---

## 7. High-Level Data Model

The data model connects users, tests, questions, test cases, and evaluation results:

1. **Users**: `user_id` (PK), `full_name`, `email`, `password_hash`, `role` (Student, Admin), `created_at`.
2. **Assessments**: `assessment_id` (PK), `title`, `description`, `start_time`, `end_time`, `duration_minutes`, `created_by` (FK -> Users).
3. **Questions**: `question_id` (PK), `assessment_id` (FK -> Assessments), `title`, `description`, `time_limit_ms`, `memory_limit_mb`, `points`.
4. **TestCases**: `test_case_id` (PK), `question_id` (FK -> Questions), `input_data`, `expected_output`, `is_hidden` (boolean), `weight_points`.
5. **Submissions**: `submission_id` (PK), `user_id` (FK -> Users), `assessment_id` (FK -> Assessments), `question_id` (FK -> Questions), `language`, `code_content`, `status`, `submitted_at`.
6. **Results**: `result_id` (PK), `submission_id` (FK -> Submissions), `verdict`, `passed_tests`, `total_tests`, `score_awarded`, `runtime_ms`, `memory_used_kb`, `evaluated_at`.

---

## 8. Database Choice: Why PostgreSQL?

I chose PostgreSQL as the primary database for the following reasons:

1. **Clear Relationships**: Assessments have questions, questions have test cases, students make submissions, and submissions generate results. These entities naturally fit relational tables with foreign keys.
2. **ACID Transactions**: When an assessment finishes or a student submits, marking status and scores must be consistent. PostgreSQL ensures no partial data writes.
3. **Structured Constraints**: Foreign key constraints prevent orphaned records (for example, a submission for a non-existent question).
4. **Volume is Manageable**: As calculated in the scale estimates, a 10,000-student exam creates around 200,000 submission rows and under 500 MB of data. A single PostgreSQL database with read replicas easily handles this volume.
5. **JSON Support**: PostgreSQL supports `JSONB`, which allows storing custom test case outputs or language compiler flags without altering table schemas.

---

## 9. Cache Strategy

I used Redis as an in-memory cache to protect the database from repeated reads:

1. **Active Questions Cache**: During a test, all 10,000 students read the same 4 questions. When the test starts, the question details and sample test cases are cached in Redis under `assessment:{id}:questions`. This eliminates 95% of question read queries to the database.
2. **Session / Token Verification**: User roles and active test sessions are cached to validate API requests in sub-millisecond time.
3. **Rate Limiting Counters**: Redis keys with TTL are used to count submissions per student per minute.

---

## 10. Message Queue Strategy

I used a message queue (such as RabbitMQ or Kafka) because running code takes significant time:

- An API request must respond in under 300 ms. But compiling and running code against 15 test cases takes 2 to 5 seconds.
- If the API waited synchronously for the code to run, all web server connections would quickly become busy, causing incoming requests to drop.
- **Workflow**:
  1. The Submission Service writes the submission record to the database with status `QUEUED`.
  2. The Submission Service pushes `{submission_id, code_url, question_id, language}` into the queue.
  3. The API immediately returns HTTP 202 (Accepted) to the student.
  4. Worker nodes pull jobs from the queue at their own comfortable pace.
  5. If 1,000 submissions arrive at once, the queue simply grows in memory while workers drain it steadily without server crashes.

---

## 11. Safe Code Execution (Sandbox Design)

Running user-submitted code is dangerous because code could contain infinite loops, fork bombs, memory-hogging arrays, or malicious commands trying to access the host server.

I designed safe execution around these principles:

1. **Isolated Containers**: Each submission executes inside an isolated container (such as a Docker container restricted with gVisor or Linux cgroups and namespaces).
2. **No Network Access**: The container network is disabled (`--net=none`). The submitted code cannot make external network calls, call home, or connect to the internal database.
3. **Resource Limits**:
   - **CPU Time Limit**: A process timeout kills any execution that runs longer than the allowed time (e.g., 2.0 seconds) and returns `TIME_LIMIT_EXCEEDED`.
   - **Memory Limit**: Linux cgroups restrict memory (e.g., 256 MB). If the program tries to allocate more, the operating system kills it with `MEMORY_LIMIT_EXCEEDED`.
   - **Process Limit (Fork Bomb Defense)**: The maximum number of child processes is capped at 10 to prevent `while(1) { fork(); }`.
4. **Read-Only File System**: The root file system is mounted read-only. The code can only read input from `stdin` and write to `stdout`/`stderr`. No files can be written to disk.
5. **Disposable Sandbox**: The container is destroyed immediately after execution so no state lingers for the next submission.

---

## 12. Worker Pools and Worker Management

- Rather than booting a whole new Docker container from scratch for every submission (which takes 500 ms to 1 second), the Judge Service maintains a **pre-warmed worker pool**.
- A fixed number of idle sandbox containers for Python, C++, and Java are kept ready in memory.
- When a job arrives:
  1. An idle sandbox container is assigned.
  2. The source code is injected through standard input or a temporary ramdisk.
  3. Code is compiled and run against inputs.
  4. The container is reset or replaced back into the idle pool.

---

## 13. Horizontal Scaling

- **API and Submission Services**: These services are stateless. If traffic increases, the Load Balancer adds more service instances behind it.
- **Execution Workers**: Worker nodes can be added or removed based on queue length. If the queue has more than 100 pending submissions, the auto-scaler launches more worker virtual machines.
- **Database**: A primary PostgreSQL instance handles writes (submissions, results). Read replicas handle read queries (leaderboards, question details, submission history).

---

## 14. Concurrent Submissions Handling

- If multiple students submit at the exact same moment, the Submission Service receives them concurrently because each web worker handles a separate thread/process.
- Submissions are assigned a unique UUID (`submission_id`) and pushed onto the message queue.
- Message queues are designed to accept thousands of messages per second without blocking.
- The student's browser listens for updates using WebSocket or polls `GET /api/v1/submissions/{id}` every 2 seconds until the status changes from `QUEUED` to `COMPLETED`.

---

## 15. Retries and Dead Letter Queue

- If a worker crashes mid-execution (for example, power loss on a worker node):
  - The message acknowledgment is not sent back to RabbitMQ.
  - RabbitMQ detects the lost worker connection and re-queues the message to another worker.
- **Retry Limit**: Each submission job has a `retry_count` header. If a job fails 3 times due to system crashes, it is moved to a **Dead Letter Queue (DLQ)**.
- The submission status is updated to `FAILED (SYSTEM_ERROR)` so the student can retry, and an alert is sent to engineering.

---

## 16. Idempotency

- If a student's network lags and they accidentally click "Submit" twice within 2 seconds, we must avoid running the same code twice.
- The client sends a unique client-generated token or hash: `hash(user_id + question_id + code_content)`.
- If the Submission Service receives a request with the same hash within 5 seconds, it returns the existing `submission_id` instead of enqueuing a duplicate job.

---

## 17. Rate Limiting

- To prevent spamming and denial-of-service, rate limits are enforced at the API Gateway using Redis token bucket counters:
  - **Per-Student Limit**: Maximum 1 code submission every 10 seconds.
  - **Status Poll Limit**: Maximum 1 status check per 2 seconds.
- If a student exceeds the limit, the server responds with HTTP 429 (`Too Many Requests`) with a clear message: "Please wait 10 seconds before submitting again."

---

## 18. High Availability

- **No Single Point of Failure**:
  - Load balancers run in active-passive pairs.
  - Core services run across at least two availability zones.
  - PostgreSQL uses continuous streaming replication to a standby replica that can be promoted if the primary fails.
  - Redis runs in Sentinel / Cluster mode with automatic failover.

---

## 19. Failure Recovery

- **Worker Node Failure**: Worker crashes do not lose jobs because messages stay in the message queue until explicitly acknowledged after successful evaluation.
- **Database Temporary Failure**: The Submission Service can still buffer messages into the queue while waiting for database reconnects.
- **Frontend State Recovery**: The student's latest code drafts are auto-saved in local browser storage (`localStorage`) every 15 seconds. If the browser tab crashes, the code is restored upon refresh.

---

## 20. Hidden-Test Protection

- **The Problem**: If hidden test case inputs and outputs are sent to the student's browser, a clever student can inspect browser network traffic and hardcode answers.
- **The Solution**:
  1. The API endpoint `GET /api/v1/assessments/{id}/questions` only queries test cases where `is_hidden = false`.
  2. Hidden test cases are stored in the database or Object Storage and are ONLY fetched directly by the internal Judge Service.
  3. When returning results to the student, the response only contains:
     - `test_case_number: 1, status: PASSED`
     - `test_case_number: 2, status: FAILED`
  4. The actual hidden inputs, expected outputs, and actual student outputs for hidden tests are NEVER returned in the API response.

---

## 21. Security

- **JWT Authentication**: Secure tokens signed with HS256 / RS256 containing expiration times.
- **Input Sanitization**: API inputs are validated to prevent SQL injection and cross-site scripting (XSS).
- **Network Segmentation**: Execution worker containers have no access to the internal network or other microservices.
- **Role Verification**: Admin endpoints (`/api/v1/admin/*`) strictly check for `role == 'ADMIN'` in the token claims.

---

## 22. High-Level Plagiarism Controls

- After the assessment concludes, submissions for each question are analyzed:
  1. **Tokenization**: Code is parsed into language tokens (keywords, identifiers, operators) ignoring variable names, whitespace, and comments.
  2. **Fingerprinting (Winnowing Algorithm)**: Token n-grams are hashed to generate document fingerprints (similar to the MOSS algorithm).
  3. **Similarity Comparison**: Fingerprints are compared across candidate pairs. Any pair with similarity > 80% is flagged for teacher review.
  4. **Time & Keystroke Logs**: Timestamp analysis flags submissions where 100 lines of complex code appeared within 30 seconds without intermediate keystroke saves.

---

## 23. Monitoring & Alerting

- **Prometheus** scrapes metrics from services and workers:
  - `queue_size`: Number of pending submissions waiting to be judged.
  - `worker_utilization`: Percentage of active vs idle execution workers.
  - `evaluation_latency`: Time from submission received to result stored.
  - `api_http_5xx_rate`: Server error rates.
- **Grafana Dashboards**: Give college coordinators and system admins live visibility into test activity.
- **Alerts**: If `queue_size > 500` for more than 2 minutes, alerts fire via Slack / PagerDuty to scale worker capacity immediately.

---

## 24. Five Key Design Trade-Offs

### Trade-off 1: Relational Database (PostgreSQL) vs NoSQL (MongoDB)
- **Option A**: NoSQL (MongoDB) for flexible schema.
- **Option B**: Relational Database (PostgreSQL) with structured tables and foreign keys.
- **Selected Option**: Option B (PostgreSQL).
- **Why**: The data has clear relational integrity: assessments link to questions, questions link to test cases, and users link to submissions and results. Foreign keys prevent invalid submissions. The total data volume (under 1 GB per test) does not require the massive horizontal sharding of NoSQL.

### Trade-off 2: Synchronous Execution vs Asynchronous Message Queue
- **Option A**: Synchronous execution (keep the student HTTP connection open until code compiles and runs).
- **Option B**: Asynchronous execution using a Message Queue (RabbitMQ) with polling or WebSockets.
- **Selected Option**: Option B (Asynchronous Execution).
- **Why**: Running code takes several seconds. Keeping HTTP requests open ties up server threads and crashes the server under burst loads. An asynchronous queue absorbs spikes and allows workers to evaluate submissions steadily.

### Trade-off 3: Redis In-Memory Cache vs Direct Database Access
- **Option A**: Query PostgreSQL directly every time a student reads a question or checks test info.
- **Option B**: Cache questions and active test data in Redis with a 10-minute TTL.
- **Selected Option**: Option B (Redis Cache).
- **Why**: In a test with 10,000 students, all students read the exact same 4 questions. Caching these questions in Redis prevents 40,000+ identical read queries from reaching PostgreSQL, keeping database CPU low.

### Trade-off 4: Docker Containers vs VM per Submission
- **Option A**: Boot a complete lightweight Virtual Machine (like AWS Firecracker microVM) for each submission.
- **Option B**: Use lightweight Linux containers (Docker with gVisor / cgroups) from a pre-warmed pool.
- **Selected Option**: Option B (Container Worker Pool).
- **Why**: Full virtual machines consume more memory and take longer to start. A pre-warmed container starts in milliseconds and consumes minimal RAM while providing enough isolation (no network, restricted CPU, restricted memory, read-only disk) for student coding tests.

### Trade-off 5: HTTP Polling vs WebSockets for Submission Status
- **Option A**: Persistent WebSocket connection for every online student.
- **Option B**: Short-interval HTTP polling (client polls every 2 seconds for up to 30 seconds after submitting).
- **Selected Option**: Option B (Short-interval HTTP Polling, with WebSocket as an optional progressive enhancement).
- **Why**: Maintaining 10,000 persistent open WebSocket connections across unstable campus Wi-Fi networks requires complex connection state management and reconnect logic. HTTP polling for 5 to 10 seconds after a submission is simple, stateless, works cleanly through campus firewalls, and can be easily cached or rate-limited.
