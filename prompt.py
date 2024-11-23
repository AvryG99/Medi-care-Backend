def generate_prompt(question, db_config):
    examples = """
    Example 1:
    Question: "What are all the dianosis of all the female patients? (Male patient are represented as 'F' value in the database)"
    Code:
    ```
    def query_database(connection_string):
        import pyodbc

    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        query = \"""
        SELECT d.DiagnosisCode, d.DiagnosisDescription
        FROM Diagnoses d
        JOIN PatientDiagnoses pd ON d.DiagnosisID = pd.DiagnosisID
        JOIN Patients p ON pd.PatientID = p.PatientID
        WHERE p.Gender = 'M'
        \"""

        cursor.execute(query)
        result = cursor.fetchall()
        conn.close()

        return [(row.DiagnosisCode, row.DiagnosisDescription) for row in result]
    except pyodbc.Error as e:
        print("Error executing query: ", e)
        return []
    ```

    Example 2:
    Question: "What is the medicine used to treat Acute sinusitis?"
    Code:
    ```
    def query_database(connection_string):
        import pyodbc

    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        query = \"""
        SELECT m.MedicineName, pm.Dosage
        FROM Medicines m
        JOIN PatientMedicines pm ON m.MedicineID = pm.MedicineID
        JOIN PatientDiagnoses pd ON pm.PatientID = pd.PatientID
        JOIN Diagnoses d ON pd.DiagnosisID = d.DiagnosisID
        WHERE d.DiagnosisDescription = 'Acute sinusitis'
        \"""

        cursor.execute(query)
        result = cursor.fetchall()
        conn.close()

        return [(row.MedicineName, row.Dosage) for row in result]
    except pyodbc.Error as e:
        print("Error executing query: ", e)
        return []
    ```
    """
    
    tables_info = """
    Tables:
    - Patients (PatientID, FirstName, LastName, DateOfBirth, Gender, Address, PhoneNumber)
    - Diagnoses (DiagnosisID, DiagnosisCode, DiagnosisDescription)
    - Medicines (MedicineID, MedicineName, Dosage, SideEffects)
    - PatientDiagnoses (PatientDiagnosisID, PatientID, DiagnosisID, DiagnosisDate)
    - PatientMedicines (PatientMedicineID, PatientID, MedicineID, PrescriptionDate, Dosage)
    - Doctors (DoctorID, FirstName, LastName, Specialty, PhoneNumber)
    - PatientDoctor (PatientDoctorID, PatientID, DoctorID, AssignmentDate)
    """
    
    prompt = f"""
    You are a Python programming assistant. The doctor has asked the following question:
    "{question}"
    Write a Python script to query an SQL Server database with the following details:
    {tables_info}

    The connection string is:
    driver={db_config['driver']};server={db_config['server']};database={db_config['database']};UID={db_config['user']};PWD={db_config['password']};

    Make sure to use appropriate SQL queries and handle any potential errors.

    Use the examples below as a reference, tailored to your EHR database structure:
    {examples}
    """
    return prompt
