CREATE TABLE IF NOT EXISTS TrainedEmployees
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ProjectName TEXT NOT NULL,
        NumberOfTrainedEmployees INTEGER NOT NULL,
        UNIQUE(ProjectName, NumberOfTrainedEmployees)
    )