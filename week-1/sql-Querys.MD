## 1. Department Salary Summary
# -- Show department name, employee count, average, minimum and maximum salary. Include 
``` sql 
departments with no employees.
select  d.dept_name ,count(e.emp_id) as employee_count , avg(e.salary), min(e.salary),max(e.salary) from Departments d left join  Employees e on d.dept_id = e.dept_id 
group by d.dept_name ;
```

## 2. Second Highest Salary per Department
# -- Using a window function, return employee(s) earning the second distinct highest salary in each department.


## 3. Employees Above Department Average
# -- Find employees earning more than their own department average without hard-coding departments.
```sql
select emp_id , emp_name from Employees e join (select avg(salary) as average_salary ,dept_id from Employees group by dept_id) as x 
on e.dept_id = x.dept_id
where  e.salary > x.average_salary ;
```

## 4. Manager vs Team Salary
# -- For each manager, show direct-report count, total team salary and manager salary; keep managers with at least two reports.
``` sql
select m.emp_id AS manager_id,
    m.emp_name AS manager_name,
    m.salary as manager_salary,
    count(e.emp_id) as reports , 
    sum(e.salary)as total_team_salary  
    from Employees m join
     Employees e  on e.manager_id = m.emp_id
     group by  m.emp_id, m.emp_name, m.salary
     having COUNT(e.emp_id) > 2;
```

    