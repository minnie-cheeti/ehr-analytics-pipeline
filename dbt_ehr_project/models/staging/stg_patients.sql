-- This is staging model for patients 
-- To clean and standardize raw patient data 

Select 
    id AS patient_id, 
    name[1].family AS last_name,
    name[1].given[1] AS first_name,
    gender,
    birthDate AS birth_date,
     DATE_DIFF('year', CAST(birthDate AS DATE), CURRENT_DATE) AS age,
    CASE 
        WHEN DATE_DIFF('year', CAST(birthDate AS DATE), CURRENT_DATE) >= 65 THEN 'Senior'
        WHEN DATE_DIFF('year', CAST(birthDate AS DATE), CURRENT_DATE) >= 18 THEN 'Adult'
        ELSE 'Minor'
    END AS age_group
FROM {{ source('raw', 'raw_patients') }} 
     
