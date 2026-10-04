### `POST /auth/login`

Request:

```json
{
  "email": "student@college.edu",
  "password": "password123"
}
```

Response: `200 OK`

```json
{
  "token": "jwt-token",
  "user": {
    "id": "u-101",
    "name": "Varun",
    "role": "STUDENT"
  }
}
```

## Student APIs

### Join an assessment

`POST /assessments/{assessment_id}/join`

Optional body:

```json
{
  "passkey": "CAMPUS2024"
}
```

Response: `200 OK`

```json
{
  "assessment_id": "asm-501",
  "title": "Data Structures Test",
  "status": "IN_PROGRESS",
  "duration_minutes": 120
}
```

### Get questions

`GET /assessments/{assessment_id}/questions`

Returns question details and sample test cases. Hidden test cases are not returned.

Response: `200 OK`

```json
{
  "assessment_id": "asm-501",
  "questions": [
    {
      "question_id": "q-1",
      "title": "Longest Subarray with Sum K",
      "description": "Given an array of integers...",
      "points": 50,
      "sample_test_cases": []
    }
  ]
}
```

### Submit code

`POST /submissions`

Request:

```json
{
  "assessment_id": "asm-501",
  "question_id": "q-1",
  "language": "PYTHON",
  "code": "def solve(nums, k): ..."
}
```

Response: `202 Accepted`

```json
{
  "submission_id": "sub-9001",
  "status": "QUEUED"
}
```

### Get submission result

`GET /submissions/{submission_id}`

Response: `200 OK`

```json
{
  "submission_id": "sub-9001",
  "status": "COMPLETED",
  "verdict": "ACCEPTED",
  "score": 50,
  "passed_tests": 10,
  "total_tests": 10
}
```

Submission statuses: `QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`.

## Admin APIs

### Create an assessment

`POST /admin/assessments`

Request:

```json
{
  "title": "Semester 5 Coding Assessment",
  "description": "Mid-term coding evaluation",
  "start_time": "2026-10-15T09:00:00Z",
  "end_time": "2026-10-15T11:00:00Z",
  "duration_minutes": 120
}
```

Response: `201 Created`

```json
{
  "assessment_id": "asm-777",
  "status": "CREATED"
}
```

### Add a question

`POST /admin/assessments/{assessment_id}/questions`

Request:

```json
{
  "title": "Merge Overlapping Intervals",
  "description": "Given an array of intervals...",
  "points": 50,
  "test_cases": [
    {
      "input": "[[1,3],[2,6]]",
      "expected_output": "[[1,6]]",
      "is_hidden": false
    }
  ]
}
```

Response: `201 Created`

```json
{
  "question_id": "q-102",
  "status": "CREATED"
}
```

### View results

`GET /admin/assessments/{assessment_id}/results`

Response: `200 OK`

```json
{
  "assessment_id": "asm-501",
  "total_participants": 120,
  "results": [
    {
      "user_id": "u-101",
      "student_name": "Varun",
      "total_score": 100
    }
  ]
}
```

## Common status codes 
`200` -  Success 
`201` -  Created 
`202` -  Accepted for processing 
`400` -  Invalid request 
`401` -  Not authenticated 
`403` -  Not authorized 
`404` -  Not found |
