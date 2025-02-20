CREATE TABLE IF NOT EXISTS OverallCompletion
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        FiscalYear TEXT NOT NULL,
        Completion_Rate FLOAT NOT NULL,
        FY22 FLOAT NOT NULL,
        FY21 FLOAT NOT NULL,
        FY20 FLOAT NOT NULL,
        UNIQUE(FiscalYear, Completion_Rate, FY22, FY21, FY20)
    )