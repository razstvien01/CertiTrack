CREATE TABLE IF NOT EXISTS Monthly_Trend_Cert_Empl
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Fiscal_Year TEXT NOT NULL,
        Buwan TEXT NOT NULL,
        CertifiedEmployees INTEGER NOT NULL,
        UNIQUE(Fiscal_Year, Buwan, CertifiedEmployees)
    )