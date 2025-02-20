CREATE TABLE IF NOT EXISTS Cert_HiNum_Employees
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Name_of_Cert TEXT NOT NULL,
        Number_Passed INTEGER NOT NULL,
        UNIQUE(Name_of_Cert, Number_Passed)
    )