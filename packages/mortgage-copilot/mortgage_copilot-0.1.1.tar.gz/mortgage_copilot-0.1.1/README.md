# Mortgage Copilot

An AI-powered copilot for the mortgage industry, designed to streamline the origination process. This tool leverages generative AI agents to ingest and analyze borrower documents, reason over underwriting rules, and produce comprehensive reports.

## Features

- **Document Ingestion**: Extracts data from various document formats, including PDFs and images.
- **Data Analysis**: Analyzes borrower data using powerful AI models to provide insights into financial behavior, creditworthiness, and property value.
- **RAG-Powered Reasoning**: Utilizes a Retrieval-Augmented Generation (RAG) system to fetch and apply relevant underwriting rules.
- **Risk Assessment**: Assesses the overall risk associated with a mortgage application, considering financial stability, credit history, and property value.
- **Automated Reporting**: Generates detailed mortgage reports, including an executive summary, data analysis, underwriting rules, risk assessment, and a final recommendation.

## Technologies Used

- **[LangChain](https://www.langchain.com/)**: A framework for developing applications powered by language models.
- **[LangGraph](https://langchain-ai.github.io/langgraph/)**: A library for building stateful, multi-actor applications with LLMs.
- **[FAISS](https://github.com/facebookresearch/faiss)**: A library for efficient similarity search and clustering of dense vectors.
- **[Hugging Face Transformers](https://huggingface.co/transformers/)**: A library for state-of-the-art Natural Language Processing (NLP).
- **[PyTorch](https://pytorch.org/)**: An open source machine learning framework that accelerates the path from research prototyping to production deployment.
- **[EasyOCR](https://github.com/JaidedAI/EasyOCR)**: A ready-to-use OCR with 80+ supported languages and all popular writing scripts including Latin, Chinese, Arabic, Devanagari, Cyrillic and etc.
- **[Camelot](https://camelot-py.readthedocs.io/en/master/)**: A Python library that can help you extract tables from PDFs.

## Installation

You can install Mortgage-Copilot in two ways:

1. **Direct Installation from PyPI**:
    ```bash
    pip install mortgage-copilot
    ```

2. **Installation from Source**:
    ```bash
    # Clone the repository
    git clone https://github.com/54g0/Mortgage-Copilot.git
    
    # Install dependencies
    cd Mortgage-Copilot
    pip install -r requirements.txt
    ```
## Configuration

1.  Create a `.env` file in the root directory of the project.
2.  Add your API keys to the `.env` file:
    ```
    OPENAI_API_KEY="your_openai_api_key"
    GOOGLE_API_KEY="your_google_api_key"
    GROQ_API_KEY="your_groq_api_key"
    ```

## Usage

Here's a simple example of how to use the `MortgageCopilot`:

```python
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("google_api_key")
from mortgage_copilot import MortgageCopilot
identity_data = """Aadhaar Number: 1234 5678 9012
Name: Rajesh Kumar Sharma
Father's Name: Suresh Kumar Sharma
Date of Birth: 15/03/1988
Gender: Male
Address:
#204, Green Valley Apartments
Koramangala 5th Block
Bangalore Urban - 560095
Karnataka, India
Mobile Number: +91-9876543210
Email: raj***@email.com
Enrollment Date: 12/05/2010
Last Updated: 18/01/2024
Biometric Details: Fingerprints and Iris captured
Authentication Status: Verified
UID Token: XXXXXXXXXXXXXXXX
PAN: ABCDE1234F
Name: RAJESH KUMAR SHARMA
Father's Name: SURESH KUMAR SHARMA
Date of Birth: 15/03/1988
Date of Issue: 22/08/2015
Name Printed on Card: RAJESH KUMAR SHARMA
Signature on Card: Yes
Photo on Card: Yes
Card Status: Active"""
agent = MortgageCopilot(model_name="gemini-2.0-flash-lite",model_provider = "google",api_key=api_key,
                        rules_dir="src/underwriting_rules",vector_db_dir="src/vector_db",
                        borrower_data_dir="src/borrower_data_dir")
result = agent.run(identity_data=identity_data)
print(result.get("final_report"))
with open("src/final_report.txt","w") as f:
    f.write(result.get("final_report",""))
```
## Generated Report:

## Mortgage Report: Rajesh Kumar Sharma

**Date:** October 26, 2024

**Prepared for:** Loan Underwriting Department

**Applicant:** Rajesh Kumar Sharma

**Loan Amount Requested:** ₹50,00,000

**Property Type:** Residential Apartment (Under Construction)

**Executive Summary:**

This report provides a comprehensive analysis of Rajesh Kumar Sharma's mortgage application, encompassing financial standing, creditworthiness, property assessment, and loan purpose. The applicant exhibits a strong financial profile, characterized by a high credit score, consistent income, and healthy savings. However, the high proposed EMI-to-Income ratio (65.2%) and the under-construction nature of the property present significant risks. Therefore, a thorough manual review, stringent due diligence, and potential loan modifications are **required** before a final decision can be made. The overall risk assessment is categorized as **MEDIUM-HIGH**.

**I. Detailed Analysis:**

**A. Borrower Profile:**

1.  **Income:**

    *   **Primary Income:** Monthly salary of ₹85,000 from XYZ Tech Ltd. (consistent).
    *   **Additional Income:** Interest income from fixed deposits (small, consistent).
    *   **Income Stability:** Stable employment since March 15, 2021, with XYZ Tech Ltd. Salary increments and promotions indicate career progression.
    *   **Income Risk:** The applicant is employed by a private company, which is considered a `MEDIUM_HIGH_RISK` factor according to `INCOME_RISK_FACTORS`.
    *   **Annual Income (FY 2024-25):** Total Annual Income: ₹11,30,000, Net Annual Income: ₹9,80,000
    *   **YTD Income (April-July 2025):** YTD Gross: ₹3,40,000, YTD Net Pay: ₹2,65,048
    *   **ITR Details (FY 2024-25):** Salary Income: ₹9,33,400, Other Income: ₹34,300, Gross Total Income: ₹9,67,700, Taxable Income: ₹7,09,200, Total Tax Liability: ₹26,957, Refund Due: ₹1,23,043
2.  **Expenses:**

    *   **Rent:** ₹25,000 per month (significant and consistent).
    *   **Medical Insurance:** ₹18,500 per month (significant and consistent).
    *   **Mutual Fund SIP:** ₹15,000 per month (consistent investment).
    *   **Existing EMIs:** Car Loan, Education Loan (impacts repayment capacity).
    *   **Education Expenses:** High education expenses for his child should be considered.
3.  **Savings & Investments:**

    *   **Average Bank Balance:** High average balance of ₹321,159.09, indicating strong savings.
    *   **Savings Trend:** Savings appear to be increasing over time.
    *   **Financial Planning:** Investments in EPF, PPF, and Life Insurance. Utilizing deductions under Chapter VI-A. Eligible for a significant tax refund.
4.  **Employment:**

    *   **Employer:** XYZ Technologies Private Limited (established IT services company).
    *   **Company Stability:** Good credit rating (CRISIL A+/Stable) and a large employee base (2,500+), suggesting a stable work environment.
    *   **Employment Type:** Permanent Full-time.
    *   **Employment Tenure:** Since March 15, 2021.

**B. Creditworthiness:**

1.  **CIBIL Report Analysis:**

    *   **CIBIL Score:** 785 (Excellent) - `MEDIUM_LOW_RISK` according to `CREDIT_RISK_SCORING`.
    *   **Payment History:** Excellent payment history on all accounts (Car Loan, Credit Card, Education Loan, Personal Loan - closed).
    *   **Credit Utilization:** 18.6% (Good).
    *   **Credit Mix:** Diversified credit portfolio.
    *   **Credit History:** Over 3 years.
    *   **Recent Enquiries:** Three credit inquiries in the last 12 months (potential, but not a major concern).
2.  **Debt-to-Income Ratios:**

    *   **MAX_TOTAL_EMI_RATIO:** 0.50 (50%) - Rule Met.
    *   **MAX_EXISTING_EMI_RATIO:** 0.40 (40%) - Rule Met.
    *   **MAX_PROPOSED_EMI_RATIO:** 0.50 (50%) - Rule Met.
    *   **EMI-to-Income Ratio (Proposed):** 65.2% - **VIOLATES RULE** - This is a **major red flag**.

**C. Loan Purpose and Property Details:**

1.  **Loan Purpose:** Purchase of a residential apartment (under construction) for self-occupation.
2.  **Property:**

    *   **Property Type:** Residential apartment (under construction) - `MEDIUM_HIGH_RISK` according to `PROPERTY_TYPE_RISK`.
    *   **Builder:** Prestige Estates Projects Ltd. (Requires due diligence).
    *   **Location:** (Requires analysis of the property documents to determine the location and assess its risk based on the `PROPERTY_LOCATION_RISK` rule).
3.  **Loan Details:**

    *   **Loan Amount:** ₹50,00,000 - Triggers a `MANUAL_REVIEW_REQUIRED` event.
    *   **Interest Rate:** 8.75% per annum (floating).
    *   **Tenure:** 20 years (240 months).
    *   **Expected EMI:** ₹43,200.
    *   **Down Payment:** ₹28,38,000 (36.4% of property value) - Positive factor.
4.  **Risks Associated with Under-Construction Property:**

    *   **Construction Delays:** Potential impact on move-in timeline and costs.
    *   **Builder Risk:** Financial stability and track record of Prestige Estates Projects Ltd. is crucial.
    *   **Reliance on Future Income:** The applicant is expecting a promotion and salary increase, which is not guaranteed.
    *   **Dependency on Spouse's Income:** The loan repayment relies solely on the applicant's income.
    *   **Education Expenses:** High education expenses for his child should be considered.

**II. Underwriting Rules Applied:**

The following underwriting rules from the provided document were applied in this analysis:

*   **Eligibility Rules:**
    *   `MIN_AGE`: 21 (Applicant meets this).
    *   `MAX_AGE_AT_MATURITY_SALARIED`: 65 (Applicant meets this).
    *   `MIN_MONTHLY_INCOME_METRO`: 30000 (Applicant meets this).
    *   `MIN_ANNUAL_INCOME`: 360000 (Applicant meets this).
    *   `MIN_EMPLOYMENT_TENURE_SALARIED`: 12 (Applicant meets this).
    *   `MIN_EMPLOYMENT_CURRENT_COMPANY`: 12 (Applicant meets this).
    *   `MIN_CIBIL_SCORE`: 650 (Applicant meets this - 785).
    *   `CIBIL_REPORT_MAX_AGE_DAYS`: 30 (CIBIL report is recent).
*   **Debt-to-Income Ratios:**
    *   `MAX_TOTAL_EMI_RATIO`: 0.50 (Applicant meets this).
    *   `MAX_EXISTING_EMI_RATIO`: 0.40 (Applicant meets this).
    *   `MAX_PROPOSED_EMI_RATIO`: 0.50 (Applicant **VIOLATES** this).
    *   `STRESS_TEST_RATE_ADDITION`: 2.0 (To be used in stress testing).
*   **Credit Risk Factors:** (Used for risk scoring)
    *   `CREDIT_RISK_SCORING` (CIBIL score, Payment history, Debt-to-income, Employment stability).
*   **Manual Review Triggers:**
    *   `LOAN_AMOUNT_ABOVE_5000000` (Triggered).
    *   `CIBIL_SCORE_650_TO_749` (Not Triggered, but requires manual review).
    *   `SELF_EMPLOYED_APPLICANT` (Not Triggered).
    *   `UNDER_CONSTRUCTION_PROPERTY` (Triggered).
    *   `EMI_RATIO_ABOVE_40_PERCENT` (Triggered).
    *   `EMPLOYMENT_TENURE_BELOW_24_MONTHS` (Not Triggered).
    *   `PROPERTY_VALUE_ABOVE_10000000` (Not Triggered).
    *   `MULTIPLE_LOAN_ENQUIRIES_IN_3_MONTHS` (Not Triggered).
    *   `INCOME_DOCUMENTATION_INCONSISTENCY` (Not Triggered).
*   **Income Risk Assessment:**
    *   `INCOME_RISK_FACTORS` (Used to assess income risk based on employment type).
    *   `INDUSTRY_RISK_CLASSIFICATION` (Used to assess industry risk).
*   **Property Risk Assessment:**
    *   `PROPERTY_LOCATION_RISK` (Needs further analysis based on property location).
    *   `PROPERTY_TYPE_RISK` (Used to assess risk based on property type).
    *   `BUILDER_REPUTATION_RISK` (Used to assess risk based on builder reputation).
*   **Business Validation Rules:**
    *   `LOAN_AMOUNT_LIMITS` (Used to validate the loan amount).
*   **Document Verification Rules:**
    *   `IDENTITY_DOCUMENTS_REQUIRED` (Compliance with document requirements).
    *   `SALARIED_INCOME_DOCUMENTS` (Compliance with document requirements).
*   **Compliance and Fraud Prevention Rules:**
    *   `COMPLIANCE_REQUIREMENTS` (KYC, PMLA, RERA, FEMA, Income Tax).
    *   `FRAUD_DETECTION_CHECKS` (To be performed).
    *   `SUSPICIOUS_PATTERN_INDICATORS` (To be checked).

**III. Risk Assessment:**

*   **Overall Risk:** **MEDIUM-HIGH**
*   **Risk Breakdown:**
    *   **Credit Risk:** `MEDIUM_LOW_RISK` (Excellent CIBIL score and payment history).
    *   **Income Risk:** `MEDIUM_HIGH_RISK` (due to being a private company employee).
    *   **Property Risk:** `MEDIUM_HIGH_RISK` (under construction).
    *   **Debt-to-Income Risk:** `VERY_HIGH_RISK` (due to the high EMI-to-income ratio).

**IV. Recommendations:**

1.  **Mandatory Manual Review:** Due to the high EMI-to-income ratio, the under-construction property, and the loan amount exceeding ₹5,000,000, a thorough manual review is **mandatory**.
2.  **Income Verification:** Verify the applicant's income and employment history with XYZ Tech Ltd.
3.  **Builder Due Diligence:** Conduct a thorough investigation of the financial stability, track record, and RERA compliance of Prestige Estates Projects Ltd.
4.  **Repayment Capacity Assessment:** Re-evaluate the applicant's ability to manage the high EMI-to-Income ratio. This should include a detailed analysis of the applicant's monthly expenses, including the impact of existing EMIs and education expenses.
5.  **Loan Modification (If Necessary):**
    *   **Reduce Loan Amount:** Consider a lower loan amount to bring the EMI within acceptable limits (ideally below 50% of the net monthly income).
    *   **Shorter Loan Tenure:** Explore options for a shorter loan tenure to reduce the total interest paid and improve the EMI-to-income ratio.
6.  **Additional Security:** Review the guarantor's (father) financial standing and assets.
7.  **Documentation:** Ensure all required documents are obtained and verified.
8.  **Stress Test:** Perform a stress test using the `STRESS_TEST_RATE_ADDITION` (2.0%) to assess the impact of interest rate increases on the applicant's ability to repay.
9.  **Contingency Planning:** Discuss potential financial challenges with the applicant and explore contingency plans, such as a plan to manage potential construction delays or unexpected expenses.
10. **Fraud Prevention:** Implement all standard fraud detection checks, including income verification, property valuation, and identity verification.

**V. Conclusion:**

While Rajesh Kumar Sharma presents a strong credit profile and demonstrates financial discipline, the high EMI-to-income ratio and the under-construction property significantly increase the risk associated with this mortgage. The loan should **not** be approved without addressing the concerns outlined above and implementing the recommended mitigation strategies. The loan officer must carefully evaluate the applicant's repayment capacity, the builder's credentials, and potential risks before making a final decision. A prudent approach is essential to protect the lender's interests and ensure the applicant's ability to successfully repay the loan.

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is licensed under the MIT License