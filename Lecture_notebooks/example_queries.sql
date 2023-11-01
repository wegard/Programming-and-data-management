SELECT *
FROM Employees;

SELECT *
FROM Sales
WHERE Price > 1000;

SELECT FirstName, Price, CustomerId,  Commission, Address, Phone
FROM Sales
INNER JOIN Employees
ON Sales.EmployeeId = Employees.id
INNER JOIN Customers
ON Sales.CustomerId = Customers.id;

SELECT  *
FROM Sales
ORDER BY Price DESC;

SELECT FirstName, Price, Commission
FROM Sales
INNER JOIN Employees
ON Sales.EmployeeId = Employees.id
INNER JOIN Customers
ON Sales.CustomerId = Customers.id
WHERE Employees.FirstName = 'Lisa';