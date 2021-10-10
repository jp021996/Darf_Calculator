from pdfminer.high_level import extract_text
from PyPDF2 import PdfFileReader
import tabula
import re
import pandas as pd

class Read_Note:

    def __init__(self, pdf_name):
        self.df = tabula.read_pdf(pdf_name, pages='all', stream=True, guess=False)
        self.corretora = pdf_name.split('0')[0] if pdf_name[-6] == '0' else pdf_name.split('1')[0]
    
    def get_date(self, df):
        if self.corretora == 'clear':
            date = df['Unnamed: 4'].iloc[1].strip()
        elif self.corretora == 'rico':
            date = df['Data pregão'].iloc[0].strip()
        return date

    def get_buy_sell(self, current_row, df):
        if self.corretora == 'clear':
            cell_value = df['Unnamed: 0'].iloc[current_row]
            c_vRegex = re.compile(r'(?<=\s)[a-zA-Z]\s*$')
            c_v = c_vRegex.search(cell_value).group(0).strip()
        
        elif self.corretora == 'rico':
            cell_value = df['Unnamed: 0'].iloc[current_row]
            c_v = cell_value[0]
        return c_v

    def get_stock_title(self, current_row, df):
        cell_value = df['Unnamed: 0'].iloc[current_row]
        if self.corretora == 'clear':
            if 'FRACIONARIO' in cell_value:
                stock_titleRegex = re.compile(r'(?<=FRACIONARIO\s)(.*)(?=\s\d+)')
            elif 'VISTA' in cell_value:
                stock_titleRegex = re.compile(r'(?<=VISTA\s)(.*)(?=\s\d+)')
                stock_title = stock_titleRegex.search(cell_value).group(0).strip()
            else:
                stock_title = cell_value
        elif self.corretora == 'rico':
            stock_titleRegex = re.compile(r'(?<=((V|C)\s))(.*)(?=\s\d+)')
            stock_title = stock_titleRegex.search(cell_value).group(0).strip()
        return stock_title

    def get_price(self, current_row, df):
        if self.corretora ==  'clear':
            cell_value = df['Unnamed: 0'].iloc[current_row]
            price = cell_value.strip()
            price_float = float(price.replace('.','').replace(',','.'))
        elif self.corretora == 'rico':
            cell_value = df['NOTA DE NEGOCIAÇÃO'].iloc[current_row]
            price_regex = re.compile(r'(?<=(\d\s))(.*)(?=\s((DAY TRADE|NORMAL|AJUPOS)))')
            price_float = float(price_regex.search(cell_value).group(0).strip().replace(',', '.'))
        return price_float

    def get_quatity(self, current_row, df):
        if self.corretora == 'clear':
            cell_value = df['NOTA DE CORRETAGEM'].iloc[current_row]
            quantityRegex = re.compile(r'(?<=\s)\d*\s*$')
            quantity = quantityRegex.search(cell_value).group(0).strip()
        elif self.corretora == 'rico':
            cell_value = df['NOTA DE NEGOCIAÇÃO'].iloc[current_row]
            quantity = int(cell_value.split(' ')[0])
        return quantity

    def get_operational_tax(self, current_row, df):
        if self.corretora == 'clear':
            operational_tax = float(0)
        elif self.corretora == 'rico':
            cell_value = df['Data pregão'].iloc[current_row]
            operational_tax = float(cell_value.strip().replace(',','.'))
        return operational_tax
    
    def get_operations(self, df):
        if self.corretora == 'clear':
            operations = list(df[df['Unnamed: 0'].str.contains("1-BOVESPA",na=False)].index)
            return operations
        elif self.corretora == 'rico':
            first = df[df['Unnamed: 0'].str.contains('C/V Mercadoria Vencimento', na=False)].index[0] +1
            last = df[df['Unnamed: 0'].str.contains('Venda disponível', na=False)].index[0]
            operations = [i for i in range(first,last)]
            return operations
    
    def get_operation_type(self, current_row, df):
        if self.corretora == 'clear':
            pass
        if self.corretora == 'rico':
            cell_value = df['NOTA DE NEGOCIAÇÃO'].iloc[current_row]
            operation_type = ' '.join(cell_value.split(' ')[2:])
        
        return operation_type

    def make_it(self):
        note_data = []
        for page_df in self.df:
            operations = self.get_operations(page_df)
            for current_row in operations:
                operation_type = self.get_operation_type(current_row, page_df)
                if operation_type == 'TX. PERMANÊNCIA':
                    continue
                date = self.get_date(page_df)
                c_v = self.get_buy_sell(current_row, page_df)
                stock_title = self.get_stock_title(current_row, page_df)
                price = self.get_price(current_row, page_df)
                quantity = self.get_quatity(current_row, page_df)
                operational_tax = self.get_operational_tax(current_row, page_df)
                
                row_data = [date, c_v, stock_title, price, quantity, operational_tax, operation_type]
                note_data.append(row_data)
        cols = ['Date', 'Buy/Sell Operation', 'Stock Title', 'Price', 'Quantity', 'Operational Tax', 'Operational Type']
        note_df = pd.DataFrame(data=note_data, columns=cols)
        return note_df

if __name__ == '__main__':
    # pdf = PdfFileReader('rico08.pdf')
    # print(pdf.documentInfo)
    a = Read_Note('rico07.pdf')
    # row = 20
    # print(a.get_operation_type(row))
    # print(a.get_operations())
    # print(a.df)
    # print(a.get_stock_title(row))
    # print(a.get_price(row))
    # print(a.get_quatity(row))
    print(a.make_it())
    # print(a.get_stock_title(current_row=14))
    # print(len(df))
    # for i in range(len(df)):
    #     print(i)
    #     print(df)
    # ext = extract_text('rico08.pdf', page_numbers=[0])

    # with open('nota.txt', 'w+') as nota:
    #     nota.write(df)
    # print(ext)