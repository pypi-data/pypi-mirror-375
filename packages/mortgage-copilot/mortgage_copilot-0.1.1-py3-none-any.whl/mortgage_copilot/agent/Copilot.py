from langgraph.graph import StateGraph,END
from langchain.schema import HumanMessage,BaseMessage,AIMessage,SystemMessage
from ..rag.rag_system import RAGSYSTEM
from ..utils.extractor import Extractor
from ..utils.model import create_model
from typing import List,Dict,Any,TypedDict,Optional
import os

class CopilotState(TypedDict):
    messages:Optional[List[BaseMessage]]
    bank_statement_data:Any
    image_data:Any
    identity_data:Any
    cibil_report:Any
    salary_slip_data:Any
    property_data:Any
    proof_of_income_data:Any
    proof_of_business:Any
    ITR_data:Any
    loan_purpose_data:Any
    underwriting_rules:Any
    risk_analysis:Any
    final_report:Any
class MortgageCopilot:
    def __init__(self,model_name,model_provider,api_key,rules_dir,vector_db_dir,borrower_data_dir):
        self.model = create_model(provider=model_provider,model_name=model_name,api_key=api_key)
        self.rag_system = RAGSYSTEM(rules_dir,vector_db_dir)
        self.extractor = Extractor()
        self.borrower_data_dir = borrower_data_dir
        self.workflow = self.create_workflow()
        self.rag_system.load_rules()
    def create_workflow(self):
        workflow = StateGraph(CopilotState)
        workflow.add_node("intake_agent",self.intake_agent)
        workflow.add_node("analysis_agent",self.analysis_agent)
        workflow.add_node("rules_agent",self.rules_agent)
        workflow.add_node("risk_assessment_agent",self.risk_assessment_agent)
        workflow.add_node("report_agent",self.report_agent)
        workflow.set_entry_point("intake_agent")
        workflow.add_edge("intake_agent","analysis_agent")
        workflow.add_edge("analysis_agent","rules_agent")
        workflow.add_edge("rules_agent","risk_assessment_agent")
        workflow.add_edge("risk_assessment_agent","report_agent")
        workflow.add_edge("report_agent",END)
        return workflow.compile()
    
    def intake_agent(self,state:CopilotState)->CopilotState:
        """Extracts All the neccessary Data"""
        bank_statement_pdf_path = os.path.join(self.borrower_data_dir,"bank_statement.pdf")
        if os.path.exists(bank_statement_pdf_path):
            state['bank_statement_data'] = self.extractor.extract_data_from_statement(bank_statement_pdf_path)
        print("extracted bank statement data")
        for images in os.listdir(self.borrower_data_dir):
            if images.endswith(".jpg") or images.endswith(".png"):
                image_path = os.path.join(self.borrower_data_dir,images)
                state["image_data"] += self.extractor.extract_data_from_image(image_path)
        cibil_report_path = os.path.join(self.borrower_data_dir,"cibil_report.pdf")
        if os.path.exists(cibil_report_path):
            state["cibil_report"] = self.extractor.extract_data_from_pdf(cibil_report_path)
        print("extracted cibil report data")
        property_doc_path = os.path.join(self.borrower_data_dir,"property_doc.pdf")
        if os.path.exists(property_doc_path):
            state["property_data"] = self.extractor.extract_data_from_pdf(property_doc_path)
        else:
            state["property_data"] = "" + "Check in the Image data for property documents."
        print("extracted property doc data")
        proof_of_income_path = os.path.join(self.borrower_data_dir,"proof_of_income.pdf")
        if os.path.exists(proof_of_income_path):
            state["proof_of_income_data"] = self.extractor.extract_data_from_pdf(proof_of_income_path)
        else:
            state["proof_of_income_data"] = "" + "Check in the Image data for proof of income documents."
        print("extracted proof of income data")
        loan_purpose_path = os.path.join(self.borrower_data_dir,"loan_purpose.pdf")
        if os.path.exists(loan_purpose_path):
            state["loan_purpose_data"] = self.extractor.extract_data_from_pdf(loan_purpose_path)
        print("extracted loan purpose data")
        proof_of_business_path = os.path.join(self.borrower_data_dir,"proof_of_business.pdf")
        if os.path.exists(proof_of_business_path):
            state["proof_of_business"] = self.extractor.extract_data_from_pdf(proof_of_business_path)
        print("extracted proof of business data")
        itr_path = os.path.join(self.borrower_data_dir,"itr.pdf")
        if os.path.exists(itr_path):
            state["ITR_data"] = self.extractor.extract_data_from_pdf(itr_path)
        print("extracted ITR data")
        salary_slip_path = os.path.join(self.borrower_data_dir,"salary_slips")
        for filename in os.listdir(salary_slip_path):
            if filename.endswith(".pdf") or filename.startswith("salary_slip"):
                file_path = os.path.join(salary_slip_path,filename)
                state["salary_slip_data"] += self.extractor.extract_data_from_pdf(file_path) + "\n"
        print("extracted salary slip data")
        return state
    def analysis_agent(self,state:CopilotState)->CopilotState:
        """Analyzes the extracted data and produces clean and required data"""
        bank_statement_analysis_prompt = f"""
        You are an expert financial analyst. Analyze the following bank statement data and provide insights on the borrower's financial behavior, including spending patterns, income stability, and any notable transactions. Summarize your findings in a clear and concise manner.
        Bank Statement Data:
        {state['bank_statement_data']}
        """
        messages = [
            SystemMessage(content="You are a helpful assistant that helps to analyze bank statements."),
            HumanMessage(content=bank_statement_analysis_prompt)
        ]
        response = self.model.invoke(messages)
        state['bank_statement_data'] = response.content
        cibil_report_analysis_prompt = f"""
        You are an expert credit analyst. Analyze the following CIBIL report and provide insights on the borrower's creditworthiness, including credit score, payment history, outstanding debts, and any potential red flags. Summarize your findings in a clear and concise manner.

        CIBIL Report:
        {state['cibil_report']}
        """
        messages = [
            SystemMessage(content="You are a helpful assistant that helps to analyze CIBIL reports."),
            HumanMessage(content=cibil_report_analysis_prompt)
        ]
        response = self.model.invoke(messages)
        state['cibil_report'] = response.content
        property_data_analysis_prompt = f"""
        You are an expert real estate analyst. Analyze the following property documents and provide insights on the property's value, location advantages, legal status, and any potential risks associated with the property. Summarize your findings in a clear and concise manner.

        Property Documents:
        {state['property_data']}
        """
        messages = [
            SystemMessage(content="You are a helpful assistant that helps to analyze property documents."),
            HumanMessage(content=property_data_analysis_prompt)
        ]
        response = self.model.invoke(messages)
        state['property_data'] = response.content
        proof_of_income_analysis_prompt = f"""
        You are an expert financial analyst. Analyze the following proof of income documents and provide insights on the borrower's income stability, sources of income, and overall financial health Summarize your findings in a clear and concise manner.

        Proof of Income Documents:
        {state['proof_of_income_data']} ,salary slips data {state['salary_slip_data']}, Income tax returns data: {state['ITR_data']} and proof of business {state['proof_of_business']} if available.
        """
        messages = [
            SystemMessage(content="You are a helpful assistant that helps to analyze proof of income documents. and ITR documents and extract relevant income information along with meaningful insights in Income Tax Returns."),
            HumanMessage(content=proof_of_income_analysis_prompt)
        ]
        response = self.model.invoke(messages)
        state['proof_of_income_data'] = response.content
        loan_purpose_analysis_prompt = f"""
        You are an expert loan officer. Analyze the following loan purpose information and provide insights on the borrower's intent, financial needs, and any potential risks associated with the loan purpose. Summarize your findings in a clear and concise manner.
        Loan Purpose Information:
        {state['loan_purpose_data']}
        """
        messages = [
            SystemMessage(content="You are a helpful assistant that helps to analyze loan purpose information."),
            HumanMessage(content=loan_purpose_analysis_prompt)
        ]
        response = self.model.invoke(messages)
        state['loan_purpose_data'] = response.content
        print("Completed Analysis of all data")
        return state
    def rules_agent(self,state:CopilotState)->CopilotState:
        """Uses RAG to fetch relevant underwriting rules"""
        list_of_data = [
            state['bank_statement_data'],
            state['cibil_report'],
            state['property_data'],
            state['proof_of_income_data'],
            state['loan_purpose_data'],
        ]
        extracted_rules = []
        for data in list_of_data:
            relevant_rules = self.rag_system.search_relevant_documents(data)
            extracted_rules.extend(relevant_rules)
        state['underwriting_rules'] = extracted_rules
        print("Completed rules extraction")
        return state
    def risk_assessment_agent(self,state:CopilotState)->CopilotState:
        """Assesses the risk based on the analysis and underwriting rules"""
        risk_assessment_prompt = f"""
        You are an expert risk analyst. Based on the following analyzed data and underwriting rules, assess the overall risk associated with approving a mortgage for the borrower. Consider factors such as financial stability, creditworthiness, property value, and loan purpose. Provide a detailed risk assessment report highlighting potential risks.
        Analyzed Data:
        Bank Statement Analysis: {state['bank_statement_data']}
        CIBIL Report Analysis: {state['cibil_report']}
        Property Data Analysis: {state['property_data']}
        Proof of Income Analysis: {state['proof_of_income_data']}
        Loan Purpose Analysis: {state['loan_purpose_data']}

        Underwriting Rules:
        {state['underwriting_rules']}
        """
        messages = [
            SystemMessage(content="You are a helpful assistant that helps to assess mortgage risk."),
            HumanMessage(content=risk_assessment_prompt)
        ]
        response = self.model.invoke(messages)
        state['risk_analysis'] = response.content
        print("Completed risk assessment")
        return state
    def report_agent(self,state:CopilotState)->CopilotState:
        """Generates the final report"""
        final_report_prompt = f"""
        You are an expert report writer. Based on the following analyzed data, underwriting rules, and risk assessment, generate a comprehensive mortgage report for the Borrower. The report should include an executive summary, detailed analysis of each aspect, underwriting rules applied, risk assessment, and a final recommendation regarding mortgage approval.
        Analyzed Data:
        Bank Statement Analysis: {state['bank_statement_data']}
        CIBIL Report Analysis: {state['cibil_report']}
        Property Data Analysis: {state['property_data']}
        Proof of Income Analysis: {state['proof_of_income_data']}
        Loan Purpose Analysis: {state['loan_purpose_data']}

        Underwriting Rules:
        {state['underwriting_rules']}

        Risk Assessment:
        {state['risk_analysis']}
        """
        messages = [
            SystemMessage(content="You are a helpful assistant that helps to generate a comprehensive mortgage report."),
            HumanMessage(content=final_report_prompt)
        ]
        response = self.model.invoke(messages)
        state['final_report'] = response.content
        print("Generated final report")
        return state
    def run(self,identity_data) -> CopilotState:
        initial_state:CopilotState = {
            "messages":[],
            "bank_statement_data":None,
            "image_data":"",
            "identity_data":identity_data,
            "cibil_report":None,
            "salary_slip_data":"",
            "property_data":None,
            "proof_of_income_data":None,
            "proof_of_business":None,
            "ITR_data":None,
            "loan_purpose_data":None,
            "underwriting_rules":None,
            "risk_analysis":None,
            "final_report":None
        }
        try:
            final_state = self.workflow.invoke(initial_state)
            return final_state
        except Exception as e:
            # Handle exceptions that may occur during workflow execution
            print(f"Error occurred: {e}")
            return initial_state