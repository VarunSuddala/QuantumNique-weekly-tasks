# PostgreSQL Assignment Queries

This file contains the queries for all 10 problems.

## 1. Department Salary Summary
```sql
SELECT 
    d.dept_name,
    COUNT(e.emp_id) AS employee_count,
    ROUND(AVG(e.salary), 2) AS avg_salary,
    MIN(e.salary) AS min_salary,
    MAX(e.salary) AS max_salary
FROM Departments d
LEFT JOIN Employees e ON d.dept_id = e.dept_id
GROUP BY d.dept_id, d.dept_name
ORDER BY d.dept_name;
```

## 2. Second Highest Salary per Department
```sql
WITH RankedSalaries AS (
    SELECT 
        emp_id,
        emp_name,
        dept_id,
        salary,
        DENSE_RANK() OVER (
            PARTITION BY dept_id 
            ORDER BY salary DESC
        ) AS salary_rank
    FROM Employees
)
SELECT 
    emp_id,
    emp_name,
    dept_id,
    salary
FROM RankedSalaries
WHERE salary_rank = 2
ORDER BY dept_id, emp_id;
```

## 3. Employees Above Department Average
```sql
WITH DeptAvg AS (
    SELECT 
        emp_id,
        emp_name,
        dept_id,
        salary,
        AVG(salary) OVER (PARTITION BY dept_id) AS dept_avg_salary
    FROM Employees
)
SELECT 
    emp_id,
    emp_name,
    dept_id,
    salary,
    ROUND(dept_avg_salary, 2) AS dept_avg_salary
FROM DeptAvg
WHERE salary > dept_avg_salary
ORDER BY dept_id, salary DESC;
```

## 4. Manager vs Team Salary
```sql
SELECT 
    m.emp_id AS manager_id,
    m.emp_name AS manager_name,
    COUNT(e.emp_id) AS direct_report_count,
    SUM(e.salary) AS total_team_salary,
    m.salary AS manager_salary
FROM Employees m
JOIN Employees e ON e.manager_id = m.emp_id
GROUP BY m.emp_id, m.emp_name, m.salary
HAVING COUNT(e.emp_id) >= 2
ORDER BY m.emp_id;
```

## 5. Top Project Contributors
```sql
WITH ProjectContributorRanks AS (
    SELECT 
        ep.project_id,
        p.project_name,
        ep.emp_id,
        e.emp_name,
        ep.hours_worked,
        DENSE_RANK() OVER (
            PARTITION BY ep.project_id 
            ORDER BY ep.hours_worked DESC
        ) AS contributor_rank
    FROM EmployeeProjects ep
    JOIN Projects p ON ep.project_id = p.project_id
    JOIN Employees e ON ep.emp_id = e.emp_id
)
SELECT 
    project_id,
    project_name,
    emp_id,
    emp_name,
    hours_worked,
    contributor_rank
FROM ProjectContributorRanks
WHERE contributor_rank <= 2
ORDER BY project_id, contributor_rank, emp_id;
```

## 6. Departments Without Active Projects
```sql
SELECT 
    d.dept_id,
    d.dept_name
FROM Departments d
WHERE EXISTS (
    SELECT 1 
    FROM Employees e 
    WHERE e.dept_id = d.dept_id
)
AND NOT EXISTS (
    SELECT 1 
    FROM Projects p 
    WHERE p.dept_id = d.dept_id
)
ORDER BY d.dept_id;
```

## 7. Running Order Revenue
```sql
WITH DailyRevenue AS (
    SELECT 
        order_date,
        SUM(amount) AS daily_revenue
    FROM Orders
    WHERE status = 'Completed'
    GROUP BY order_date
)
SELECT 
    order_date,
    daily_revenue,
    SUM(daily_revenue) OVER (
        ORDER BY order_date 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_revenue
FROM DailyRevenue
ORDER BY order_date;
```

## 8. Customer Order Classification
```sql
SELECT 
    customer_id,
    COALESCE(SUM(CASE WHEN status = 'Completed' THEN amount ELSE 0 END), 0) AS total_completed_value,
    CASE 
        WHEN COALESCE(SUM(CASE WHEN status = 'Completed' THEN amount ELSE 0 END), 0) >= 100000 THEN 'PLATINUM'
        WHEN COALESCE(SUM(CASE WHEN status = 'Completed' THEN amount ELSE 0 END), 0) >= 50000  THEN 'GOLD'
        WHEN COALESCE(SUM(CASE WHEN status = 'Completed' THEN amount ELSE 0 END), 0) >= 20000  THEN 'SILVER'
        ELSE 'BRONZE'
    END AS customer_tier
FROM Orders
GROUP BY customer_id
ORDER BY total_completed_value DESC, customer_id;
```

## 9. Consecutive Monthly Orders
```sql
WITH DistinctCustomerMonths AS (
    SELECT DISTINCT 
        customer_id,
        DATE_TRUNC('month', order_date)::DATE AS order_month
    FROM Orders
),
MonthlySequences AS (
    SELECT 
        customer_id,
        order_month,
        LAG(order_month, 1) OVER (
            PARTITION BY customer_id 
            ORDER BY order_month
        ) AS prev_month_1,
        LAG(order_month, 2) OVER (
            PARTITION BY customer_id 
            ORDER BY order_month
        ) AS prev_month_2
    FROM DistinctCustomerMonths
)
SELECT DISTINCT customer_id
FROM MonthlySequences
WHERE prev_month_1 = order_month - INTERVAL '1 month'
  AND prev_month_2 = order_month - INTERVAL '2 month'
ORDER BY customer_id;
```

## 10. Salary Gap Analysis
```sql
WITH DeptSalaryExtremes AS (
    SELECT 
        dept_id,
        MAX(salary) AS max_salary,
        MIN(salary) AS min_salary,
        MAX(salary) - MIN(salary) AS salary_difference
    FROM Employees
    GROUP BY dept_id
),
HighestEarners AS (
    SELECT 
        e.dept_id,
        STRING_AGG(e.emp_name, ', ' ORDER BY e.emp_name) AS highest_paid_employees,
        e.salary AS highest_salary
    FROM Employees e
    JOIN DeptSalaryExtremes m ON e.dept_id = m.dept_id AND e.salary = m.max_salary
    GROUP BY e.dept_id, e.salary
),
LowestEarners AS (
    SELECT 
        e.dept_id,
        STRING_AGG(e.emp_name, ', ' ORDER BY e.emp_name) AS lowest_paid_employees,
        e.salary AS lowest_salary
    FROM Employees e
    JOIN DeptSalaryExtremes m ON e.dept_id = m.dept_id AND e.salary = m.min_salary
    GROUP BY e.dept_id, e.salary
)
SELECT 
    d.dept_id,
    d.dept_name,
    h.highest_paid_employees,
    m.max_salary AS highest_salary,
    l.lowest_paid_employees,
    m.min_salary AS lowest_salary,
    m.salary_difference
FROM Departments d
JOIN DeptSalaryExtremes m ON d.dept_id = m.dept_id
JOIN HighestEarners h ON d.dept_id = h.dept_id
JOIN LowestEarners l ON d.dept_id = l.dept_id
ORDER BY d.dept_id;
```