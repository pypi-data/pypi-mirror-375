from gyb_classification_model import predictor

text = "Jordan Fersel MD PC 900 B East Tremont Ave, Bronx NY 10460 Phone No .: 347 918-8822 x FAX: 347 918-8821 x alva.gbtherapy@gmail.com PRESCRIPTIONS PATIENT DEMOGRAPHICS Patient: Jackson, Laverne DOB: 09-12-1968 Cell Phone: 347 977-5497 x Visit Date: 08-08-2025 PHARMACY: TURNPIKE MEDS RX INC Tel: 7187499915 Fax: 7187499916 Allergies: No Known Drug Allergies. GUARANTOR & INSURANCE INFORMATION Insurance: Old Republic Insurance Company Guarantor: Jackson, Laverne START DATE 08-13-2025 MEDICATION SIG REFILLS diclofenac potassium 25 mg tablet 1 Tablet Twice A Day PRN for 30 Days, Dispense 60 Tablet No Refill Substitution Permissible Jorden de Acusel IMO. Prescriptions will be filled generically unless Jordan Fersel, M.D. DEA No .: FF5989605 This is an electronic signature. prescriber writes D.A.W (Dispense As Written) or other notation as required by law Schedule 2 medications require an original signature. Jordan Fersel MD PC The information on this page is CONFIDENTIAL. Any release of this information requires the expressed written authorization of the patient listed above. For questions regarding this prescription, please contact the practice."

# processed_text = predictor.preprocess_text(text)
category = predictor.predict_text(text)

print(category)

