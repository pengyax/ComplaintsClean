import pandas as pd
import numpy as np
import filter_dme as dme
import traceback


def clean_process(df,lot_vendor,vendor_mapping):
    try:
        def get_vendor(series):
            if str(series['Material Vendor']).isdigit():
                vendor_code = int(series['Material Vendor'])
            else:
                vendor_code = lot_vendor.get(str(series['Material Number']) + "|" + str(series['Material Lot Number']), np.nan)
            return vendor_code
        
        df = df.loc[df['Cause Group'] != 'Duplicate']
        df_Duplicate = df.copy()
        df_Duplicate['Material Vendor'] = df_Duplicate['Material Vendor'].map(str)
        df_Duplicate.loc[((df_Duplicate['Division'] == 21) | (df_Duplicate['Division'] == 51))&(~df_Duplicate['Material Vendor'].str.isdigit()),'Material Vendor'] = df_Duplicate['Manufacture Site']
        df_Duplicate['Material Lot Number'] = df_Duplicate['Material Lot Number'].str.lstrip('0')
        
        df_Duplicate['Material Vendor'] = df_Duplicate.apply(lambda x : get_vendor(x),axis=1)
        df_Duplicate['Vendor Name'] = df_Duplicate['Material Vendor'].map(vendor_mapping)
        df_Duplicate['If Manufacturing Complaint'] = 'N'
        df_Duplicate['Material Lot Number'] = df_Duplicate['Material Lot Number'].str.replace('nan','')
        df_Duplicate.loc[:,'Notification Created Date'] = pd.to_datetime(df_Duplicate['Notification Created Date'],format='%Y/%m/%d')
        df_Duplicate['Month'] = df_Duplicate['Notification Created Date'].dt.month
        df_Duplicate['Year'] = df_Duplicate['Notification Created Date'].dt.year
        df_Duplicate = df_Duplicate[df_Duplicate['Material Vendor'].notnull()]
        df_Duplicate['key'] = [f'{n}|{m}|{v}|{l}' for n, m, v, l in zip(df_Duplicate['Notification Number'], df_Duplicate['Material Number'], df_Duplicate['Material Vendor'], df_Duplicate['Material Lot Number'])]
        df_Duplicate.drop_duplicates(subset=['key'],inplace=True)
        df_Duplicate = df_Duplicate[['Division', 'Notification Number', 'Notification Created Date','Year','Month',
       'Notification Completion Date', 'Sample Received Date',
       'Account Number of Customer', 'Material Group', 'Material Number',
       'Material Description', 'Material Vendor', 'Vendor Name','Material Lot Number',
       'Material Serial Number', 'Notification Description',
       'Short Text For Defect Type Code', 'Defect Group',
       'Short Text For Cause Code', 'Cause Group', 'If Manufacturing Complaint','Cause Text',
       'Investigation Notification Description', 'Replacement Order Number',
       'Credit Memo Number', 'Customer Group', 'Manufacture Site'
       ]]
        return df_Duplicate
    except Exception as e:
        traceback.print_exc()

def filter_notDme(df):
    try:
        df_notdme = df.copy()
        div10_query = (df_notdme['Division'] == 10) & ((df_notdme['Cause Text'] == 'VC')|(df_notdme['Cause Group'] == 'DC:Supplier Error Asia (Medline Brand)'))
        df_notdme_not10_query = (df_notdme['Division'] != 10) & (df_notdme['Cause Group'] == 'DC:Supplier Error Asia (Medline Brand)')
        df_notdme.loc[div10_query,'If Manufacturing Complaint'] = 'Y'
        df_notdme.loc[df_notdme_not10_query,'If Manufacturing Complaint'] = 'Y'
        return df_notdme
    except Exception as e:
        traceback.print_exc()
     

if __name__ == "__main__":
   
    dme_substr_list = ["Missing", "loose", "Bent", "crack", "damage", "Motor", "brakes", "brake", "broken"]
    
    df_vendor_lot_2021 = pd.read_excel('../data/lot_vendor/vendor_lot_2021.xlsx',sheet_name=0,usecols=[9,11,15])
    df_vendor_lot_2022 = pd.read_excel('../data/lot_vendor/vendor_lot_2022.xlsx',sheet_name=0,usecols="J,L,P")
    df_vendor_lot_2023 = pd.read_excel('../data/lot_vendor/vendor_lot_2023.xlsx',sheet_name=0,usecols="J,L,P")
    df_vendor_lot_2020 = pd.read_excel('../data/lot_vendor/vendor_lot_2019_20.xlsx',sheet_name=0,usecols="J,L,P")
    df_lot_vendor = pd.concat([df_vendor_lot_2023,df_vendor_lot_2022,df_vendor_lot_2021,df_vendor_lot_2020],ignore_index=True)
    # df_lot_vendor = pd.concat([df_vendor_lot_2023])
    df_lot_vendor.dropna(subset=['LOT #'],inplace=True)
    df_lot_vendor['VENDOR #'] = df_lot_vendor['VENDOR #'].map(str)
    df_lot_vendor['ITEM'] = df_lot_vendor['ITEM'].map(str)
    df_lot_vendor = df_lot_vendor[df_lot_vendor['VENDOR #'].str.isdigit()]
    df_lot_vendor['LOT #'] = df_lot_vendor['LOT #'].apply(lambda x: str(x).lstrip('0'))
    df_lot_vendor['key'] = df_lot_vendor['ITEM'].str.cat(df_lot_vendor['LOT #'],sep='|')
    lot_vendor_dict = dict(zip(df_lot_vendor['key'],df_lot_vendor['VENDOR #'].map(int)))
    print("lot_vendor Loaded, ready to go!")
    print('='*20,'>>>')
    
    vendor_mapping = pd.read_excel(r'C:\Medline\CPM\data\vendor_mapping\Vendor _mapping 2023_v1.xlsx')
    vendor_mapping_dict = dict(zip(vendor_mapping['Vendor Number'],vendor_mapping['Cleaned Vendor Name']))
    
    print("vendor_mapping Loaded and ready for start-up!")
    print('='*20,'>>>')
    
    df_div22_ori = pd.read_excel('../data/div_22/Asia Div 22 Complaints, 2023-06-03.xlsx',sheet_name=0)
    div22_map = {
            "Division": "Division",
            "Notification Number": "Notification Number",
            "Notification Created Date": "Notification Created Date",
            "Notification Completion Date": "Notification Completion Date",
            "Material Group": "Material Group",
            "Component": "Material Number",
            "Component Description": "Material Description",
            "Component Vendor": "Material Vendor",
            # "Vendor Name": "Vendor Name",
            "Notification Description": "Notification Description",
            "Short Text For Defect Type Code": "Short Text For Defect Type Code",
            "Defect Group":'Defect Group',
            "Short Text For Cause Code": "Short Text For Cause Code",
            "Cause Group": "Cause Group",
            "Manufacture Site": "Manufacture Site",
            "Investigation Notification Description":'Investigation Notification Description'
        }
    df_div22_ori.loc[df_div22_ori['Division'] !=22,'Division'] = 22
    df_div22_ori.drop(columns=['Material Number','Material Description'],inplace=True)
    df_div22_ori.rename(columns=div22_map,inplace=True)
    df_div22 = df_div22_ori[list(div22_map.values())]
    print("div22 combine!")
    print(df_div22.info())
    print('='*20,'>>>')
    
    df_complaints_ori = pd.read_excel('../data/ori_complaints//2023/06/All Divisions Monthly Complaint Report_06.xlsx',sheet_name=0)
    df_complaints_ori_not22 = df_complaints_ori.loc[df_complaints_ori['Division'] != 22] 
    df_complaints_unclean = pd.concat([df_complaints_ori_not22,df_div22],ignore_index=True)
    df_complaints_unclean.to_excel('../data/Complaint Raw Data Uncleaned.xlsx', index = False)
    print("complaints_unclean completed, start cleaning!")
    print('='*20,'>>>')
    
    df_complaints_unclean.loc[df_complaints_unclean['Division'].isin([32,34]),'Division'] = 30
    
    name_map = pd.read_excel('../data/name_map/name_map.xlsx',sheet_name=0)
    name_map = name_map.loc[name_map['code'].notnull(),]
    name_map['code'] = name_map['code'].map(int)
    name_map_list = dict(zip(name_map['key'],name_map['code']))
    df_complaints_unclean['Material Vendor']  = df_complaints_unclean['Material Vendor'].replace(name_map_list)
    
    df_14_81 = pd.read_excel(r'C:\Medline\CPM\DIV14&DIV81.xlsx')
    df_14_81_map=  df_14_81.loc[:,~df_14_81.columns.str.contains('unnamed',case=False)]
    div14_81_ditc = dict(zip(df_14_81_map['Material Group'],df_14_81_map['div']))
    df_complaints_unclean['newdiv'] = df_complaints_unclean.loc[df_complaints_unclean['Division'].isin([14,81])].apply(lambda x: div14_81_ditc.get(x['Material Group'],x['Division']),axis=1)
    df_complaints_unclean.loc[df_complaints_unclean['newdiv'].notnull(),'Division'] = df_complaints_unclean['newdiv']
    df_complaints_unclean.drop(columns='newdiv',inplace=True,axis=1)
    
    
    df_all = clean_process(df_complaints_unclean,lot_vendor_dict,vendor_mapping_dict) 
    
    vendor_mapping_inspection = vendor_mapping.loc[(~vendor_mapping['Regional Manager'].isin(['Exemption','US vendor']))&(vendor_mapping['Regional Manager'].notnull()),'Vendor Number'].to_list()
    df_all = df_all.loc[df_all['Material Vendor'].isin(vendor_mapping_inspection)]
    # df_all.to_excel('../data/all2023.xlsx',index = False)
    
    print("Vendor code added!")
    print('='*20,'>>>')
    
    df_notdme = df_all.loc[df_all['Division'] != 30]
    df_notdme = filter_notDme(df_notdme)
    # df_notdme.to_excel('../data/notdme2023.xlsx',index = False)
    print("NotDme completed!")
    print('='*20,'>>>')
    
    df_dme_ori = df_all.loc[df_all['Division'] == 30]
    df_dme_ori.reset_index(drop = True ,inplace = True)
    print(len(df_dme_ori))
    df_dme_ori.to_excel('../data/DmeData2023.xlsx',index = False)
    # df_dme_ori = pd.read_excel('../data/DmeData.xlsx')
    df_dme = dme.filter(df_dme_ori)
    print("DME clean completed!")
    print('='*20,'>>>')
    
    df_result = pd.concat([df_notdme,df_dme],ignore_index=True)
    df_columns =  df_result.columns.to_list()
    df_columns.remove('Notification Number')
    df_result.drop_duplicates(subset=df_columns,inplace=True)
    
    path_preceding = r'C:\Medline\CPM\2023\202305 Complaint Data.xlsx'
    df_preceding = pd.read_excel(path_preceding,sheet_name='2023 Complaint Database')
    df_preceding_list = df_preceding.loc[df_preceding['If Manufacturing Complaint']=='Y','Notification Number'].to_list()
    df_result.loc[(~df_result['Notification Number'].isin(df_preceding_list))&(df_result['If Manufacturing Complaint'] =='Y'),'New manufacturing complaints'] = 'Y'
    df_result.insert(0,'New manufacturing complaints',df_result.pop('New manufacturing complaints'))
    
    # df_result.loc[df_result['Notification Number'].isin([200541987]),'If Manufacturing Complaint'] = 'Y'
    df_result.to_excel('../data/resultAll.xlsx', index = False)
    print("Finished!")
    print('='*20,'>>>')