import pandas as pd
import numpy as np
import easyocr
import PyPDF2
import tabulate
import re
import camelot
import os
import cv2
from typing import List,Dict,Any
class Extractor:
    def __init__(self):
        self.reader = easyocr.Reader(["en"])
    def extract_data_from_statement(self,pdf_path):
        tables = camelot.read_pdf(pdf_path,pages="all",flavor="stream")
        df = pd.concat([table.df[1:] for table in tables],ignore_index=True)
        df[df.columns[-1]] =  df[df.columns[-1]].replace(r'[^0-9.\-]', '', regex=True).apply(pd.to_numeric, errors="coerce")
        df[df.columns[-2]] = df[df.columns[-2]].replace(r'[^0-9.\-]', '', regex=True).apply(pd.to_numeric, errors="coerce")
        df[df.columns[-3]] = df[df.columns[-3]].replace(r'[^0-9.\-]', '', regex=True).apply(pd.to_numeric, errors="coerce")
        avg_balance = df[df.columns[-1]].mean()
        avg_credit = df[df.columns[-2]].mean()
        avg_debit = df[df.columns[-3]].mean()
        top_credits = df.nlargest(5,df.columns[-2])
        top_debits = df.nlargest(5,df.columns[-3])
        with open(pdf_path,"rb") as f:
            bank_data = PyPDF2.PdfReader(f).pages[0].extract_text()

        return {
            "avg_balance":avg_balance,
            "avg_credit":avg_credit,
            "avg_debit":avg_debit,
            "top_credits":top_credits.values.tolist(),
            "top_debits":top_debits.values.tolist()
        }
    def extract_data_from_pdf(self,pdf_path):
        with open(pdf_path,"rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + " "
        return text
    def extract_data_from_pdfdir(self,pdf_dir):
        full_text = ""
        for filename in os.listdir(pdf_dir):
            pdf_path = os.path.join(pdf_dir,filename)
            with open(pdf_path,"rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    full_text += page.extract_text() + " "
        return full_text
    def extract_data_from_image(self,image_path):
        reader = easyocr.Reader(["en"])
        result = reader.readtext(image_path)
        text = ""
        for bbox, text, conf in result:
            text += f"{text} "
        return text.strip()
    def extract_data_from_imagedir(self,image_dir):
        try:
            full_text = ""
            for filename in os.listdir(image_dir):
                image_path = os.path.join(image_dir,filename)
                reader = easyocr.Reader(["en"])
                result = reader.readtext(image_path)
                for bbox,text,conf in result:
                    full_text += f"{text} "
            return full_text.strip()
        except Exception as e:
            print(e)
            return ""
    def extract_data_from_bytes(self,image_bytes:List[bytes])-> str:
        try:
            full_text = ""
            for image_byte in image_bytes:
                nparr = np.frombuffer(image_byte,np.uint8)
                image = cv2.imdecode(nparr,cv2.IMREAD_COLOR)
                if image is None:
                    raise ValueError("Invalid image data")
                reader = easyocr.Reader(["en"])
                result = reader.readtext(image)
                for bbox,text,conf in result:
                    full_text+=text + " "
            return full_text.strip()
        except Exception as e:
            print(e)
            return ""
    





        