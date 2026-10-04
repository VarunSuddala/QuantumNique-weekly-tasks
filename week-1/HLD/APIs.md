# Major APIs — Online Coding Assessment Platform

This document describes the key RESTful APIs for the platform. Only the essential APIs used by students and admins are listed here.

---

## 1. Student / User Authentication

### `POST /api/v1/auth/login`
- **Purpose**: Authenticates a student or admin and returns a JWT token.
- **Request**:
```json
{
  "email": "student@college.edu",
  "password": "mySecurePassword123"
}
```
- **Response** (`200 OK`):
```json
{
  "status": "success",
  "token": "eyJhbGciOiJIUzI1NiIsIn...",
  "user": {
    "user_id": "u-101",
    "name": "Varun",
    "role": "STUDENT"
  }
}
```

---

## 2. Assessment APIs (Student Facing)

### `POST /api/v1/assessments/{assessment_id}/join`
- **Purpose**: Allows an authenticated student to enter a scheduled assessment.
- **Request Headers**: `Authorization: Bearer <token>`
- **Request**: Empty body or optional passkey:
```json
{
  "passkey": "CAMPUS2024"
}
```
- **Response** (`200 OK`):
```json
{
  "assessment_id": "asm-501",
  "title": "Data Structures Placement Test",
  "start_time": "2024-10-04T10:00:00Z",
  "end_time": "2024-10-04T12:00:00Z",
  "duration_minutes": 120,
  "status": "IN_PROGRESS"
}
```

---

### `GET /api/v1/assessments/{assessment_id}/questions`
- **Purpose**: Fetches the list of questions for an ongoing test. Only public/sample test cases are returned (hidden test cases are strictly omitted).
- **Request Headers**: `Authorization: Bearer <token>`
- **Response** (`200 OK`):
```json
{
  "assessment_id": "asm-501",
  "questions": [
    {
      "question_id": "q-1",
      "title": "Longest Subarray with Sum K",
      "description": "Given an array of integers...",
      "difficulty": "MEDIUM",
      "points": 50,
      "time_limit_ms": 2000,
      "memory_limit_mb": 256,
      "sample_test_cases": [
        {
          "input": "[10, 5, 2, 7, 1, 9]\n15",
          "expected_output": "4"
        }
      ]
    }
  ]
}
```

---

## 3. Code Submission & Execution APIs

### `POST /api/v1/submissions`
- **Purpose**: Submits candidate code for evaluation. The service puts the job onto the message queue and immediately returns `QUEUED`.
- **Request Headers**: `Authorization: Bearer <token>`
- **Request**:
```json
{
  "assessment_id": "asm-501",
  "question_id": "q-1",
  "language": "PYTHON",
  "code": "def longest_subarray_sum_k(nums, k):\n    ..."
}
```
- **Response** (`202 Accepted`):
```json
{
  "submission_id": "sub-9001",
  "status": "QUEUED",
  "message": "Submission received and queued for execution.",
  "submitted_at": "2024-10-04T10:15:30Z"
}
```

---

### `GET /api/v1/submissions/{submission_id}`
- **Purpose**: Polled by client or fetched over WebSocket to get evaluation verdict and execution details once complete.
- **Request Headers**: `Authorization: Bearer <token>`
- **Response** (`200 OK`):
```json
{
  "submission_id": "sub-9001",
  "status": "COMPLETED",
  "verdict": "ACCEPTED",
  "passed_tests": 10,
  "total_tests": 10,
  "score": 50,
  "runtime_ms": 142,
  "memory_used_kb": 18400,
  "test_details": [
    {
      "test_case_num": 1,
      "status": "PASSED",
      "is_sample": true
    },
    {
      "test_case_num": 2,
      "status": "PASSED",
      "is_sample": false
    }
  ]
}
```

---

## 4. Admin Management APIs

### `POST /api/v1/admin/assessments`
- **Purpose**: Allows recruiters or college faculty to create a new assessment.
- **Request Headers**: `Authorization: Bearer <admin-token>`
- **Request**:
```json
{
  "title": "Semester 5 Coding Assessment",
  "description": "Mid-term coding evaluation",
  "start_time": "2024-10-15T09:00:00Z",
  "end_time": "2024-10-15T11:00:00Z",
  "duration_minutes": 120
}
```
- **Response** (`201 Created`):
```json
{
  "assessment_id": "asm-777",
  "status": "CREATED",
  "title": "Semester 5 Coding Assessment"
}
```

---

### `POST /api/v1/admin/assessments/{assessment_id}/questions`
- **Purpose**: Adds a problem statement, constraints, sample test cases, and hidden test cases to an assessment.
- **Request Headers**: `Authorization: Bearer <admin-token>`
- **Request**:
```json
{
  "title": "Merge Overlapping Intervals",
  "description": "Given an array of intervals...",
  "points": 50,
  "time_limit_ms": 1500,
  "memory_limit_mb": 256,
  "test_cases": [
    {
      "input": "[[1,3],[2,6],[8,10]]",
      "expected_output": "[[1,6],[8,10]]",
      "is_hidden": false
    },
    {
      "input": "[[1,4],[4,5]]",
      "expected_output": "[[1,5]]",
      "is_hidden": true
    }
  ]
}
```
- **Response** (`201 Created`):
```json
{
  "question_id": "q-102",
  "message": "Question and test cases added successfully."
}
```

---

### `GET /api/v1/admin/assessments/{assessment_id}/results`
- **Purpose**: Admin dashboard endpoint to review all candidate scores and submissions.
- **Request Headers**: `Authorization: Bearer <admin-token>`
- **Response** (`200 OK`):
```json
{
  "assessment_id": "asm-501",
  "total_participants": 120,
  "results": [
    {
      "user_id": "u-101",
      "student_name": "Varun",
      "total_score": 100,
      "questions_solved": 2,
      "last_submission_time": "2024-10-04T10:45:10Z"
    }
  ]
}
```
