import pandas as pd

def filter(df):     
    df.reset_index(inplace=True,drop=True)
    df_dme = df.copy()
    substr_list_step1 = ["Missing", "loose", "Bent", "crack", "damage", "Motor", "brakes", "brake", "broken"]
    substr_list_step2 = ["End of life expectancy", "normal wear", "tear", "customer", "Data entry error", "Data error"]
    substr_list_step3 = [
    "No investigation summary", 
    "Not Medline branded product",
    "Not Medline branded",
    "Non-Medline labeled",
    "not Medline labeld items",
    "Canceled by customer",
    "closed by the customer",
    "customer cancelled",
    "Customer reason",
    "Enter error",
    "Input error",
    "Entering error",
    "Products worked as designed",
    "Products operate as designed",
    "Products work according to design",
    "Out of warranty",
    "outside the warranty",
    "is not in warranty",
    "Beyond the warranty period",
    "Shipping damage",
    "happened during shipping",
    "freight damage",
    "transportation damage",
    "transport damage",
    "shipment damage",
    "shipping  damage",
    "happened during shipping",
    "during shipping",
    "It is possible this may have happened duringshipping",
    "duringshipping",
    "It may have been lost during shipping",
    "transportation leakage",
    "Shipping leakage",
    "Transport leakage",
    "no pictures received",
    "No sample or photo of the defective product",
    "No sample or picture received",
    "No sample or photo",
    "No sample was received"
                 ]
    substr_list_Manufacturing = [
    "complaint has been confirmed", 
    "Investigation results: Confirmed"
    # "are missing",
    # "is missing",
    # "was missing",
    # "were missing",
    # "are ripped",
    # "is ripped",
    # "missing parts",
    # "missing part",
    # "Therefore, no sample is required",
    # "absence of",
    # "be bent",
    # "was bent",
    # "fractured"
    # "stuck"
    # "not working"
                 ]
    substr_list_notManufacturing = [
    # "The root cause of this issue is unknown"
    # "No sample or photo",
    # "No photo",
    # "issue is unknown",
    # "issue cannot be confirmed"
    # "functional or dimensional inspection cannot be executed via a photo"
    "dark souls"
                 ]
    
    not_substr_list = substr_list_step1.copy()
    not_substr_list.remove('brake')
    not_substr_list.remove('brakes')
    not_substr_list_step1 = ["Not " + value for value in not_substr_list]
    not_substr_list_step1.extend(["Didn't " + value for value in not_substr_list])
    not_substr_list_step1.extend(["Doesn't " + value for value in not_substr_list])
    not_substr_list_step1.extend(["did not " + value for value in not_substr_list])
    not_substr_list_step1.extend(["does not " + value for value in not_substr_list])

    query_1_1 = pd.Series(False,index=range(len(df_dme)))
    query_1_2 = pd.Series(False,index=range(len(df_dme)))
    for column_name in ["Notification Description", "Short Text For Defect Type Code", "Defect Group",
                        "Short Text For Cause Code", "Cause Group", "Investigation Notification Description"]:
        found = sum([df_dme[column_name].str.contains(x,case=False,na=False) for x in substr_list_step1])>0
        query_1_1 = query_1_1 | found
        found = sum([df_dme[column_name].str.contains(x,case=False,na=False) for x in not_substr_list_step1])>0
        query_1_2 = query_1_2 | found
        
    query_case_group = df_dme['Cause Group'] == 'DC:Supplier Error Asia (Medline Brand)'    
    query_1 = (query_1_1 & ~query_1_2) | query_case_group
    
    query_2_1 = df_dme['Notification Description'].isnull() | df_dme['Notification Description'].str.contains('cancel',case=False,na=False)
    query_2_2 = df_dme['Short Text For Defect Type Code'].isnull()
    query_2_3 = df_dme['Defect Group'].isnull()
    query_2_4 = sum([df_dme['Short Text For Cause Code'].str.contains(x,case=False,na=False) for x in substr_list_step2])>0
    query_2_5 =  df_dme['Cause Group'].str.contains('Not a product defect',case=False,na=False) | df_dme['Cause Group'].str.contains('DC:Medline Error/Mfg.',case=False,na=False)
    query_2 = query_2_1 | query_2_2 | query_2_3 | query_2_4 | query_2_5
    
    df_dme['Investigation Notification Description'] =  df_dme['Investigation Notification Description'].str.replace('*','',regex=True)
    query_3_1 = sum([df_dme['Investigation Notification Description'].str.contains(x,case=False,na=False) for x in substr_list_step3])>0
    query_3_2 = df_dme['Investigation Notification Description'].str.len().fillna(0)<500
    query_3 = query_3_1 | query_3_2
    
    query_4_1 = sum([df_dme['Investigation Notification Description'].str.contains(x,case=False,na=False) for x in substr_list_Manufacturing])>0
    query_4_2 = sum([df_dme['Investigation Notification Description'].str.contains(x,case=False,na=False) for x in substr_list_notManufacturing])>0
    query_4_3 = df_dme['Investigation Notification Description'].str[:1000].str.contains('Investigation results: Confirmed',case=False,na=False)
    query_4 = query_4_1 & ~query_4_2 & query_4_3
    
    # df_dme.loc[query_1,'step1'] = 1
    # df_dme.loc[query_2,'step2'] = 1
    # df_dme.loc[query_3,'step3'] = 1
    # df_dme.loc[query_4,'step4'] = query_4
    # df_dme.loc[query_4_1,'step4.1'] = query_4_1
    # df_dme.loc[query_4_2,'step4.2'] = query_4_2
    
    query_dme = query_1 & ~query_2 & ~query_3 & query_4
    df_dme.loc[query_dme,'If Manufacturing Complaint'] = 'Y'
    return df_dme

if __name__ == "__main__":
    
    df_dme = pd.read_excel('../data/DmeData2023.xlsx')
    result_df_dme = filter(df_dme)
    dme_Manufacturing = result_df_dme.loc[result_df_dme['If Manufacturing Complaint'] == 'Y']
    dme_Manufacturing_gy = dme_Manufacturing.groupby('Month').size()
    print(dme_Manufacturing_gy)
    print(sum(dme_Manufacturing_gy[:12]))
    result_df_dme.to_excel('../data/dme2023.xlsx',index=False)
