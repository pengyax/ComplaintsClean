import pandas as pd


def filter(df,substr_list_step1):     

    # ("-----filter step1--------")
    not_substr_list = substr_list_step1.copy()
    not_substr_list.remove('brake')
    not_substr_list.remove('brakes')
    not_substr_list_step1 = ["Not " + value for value in not_substr_list]
    not_substr_list_step1.extend(["Didn't " + value for value in not_substr_list])
    not_substr_list_step1.extend(["Doesn't " + value for value in not_substr_list])
    not_substr_list_step1.extend(["did not " + value for value in not_substr_list])
    not_substr_list_step1.extend(["does not " + value for value in not_substr_list])

    query_1_1 = pd.Series(False,index=range(len(df)))
    query_1_2 = pd.Series(False,index=range(len(df)))
    for column_name in ["Notification Description", "Short Text For Defect Type Code", "Defect Group",
                        "Short Text For Cause Code", "Cause Group", "Investigation Notification Description"]:
        found = sum([df[column_name].str.contains(x,case=False,na=False) for x in substr_list_step1])>0
        query_1_1 = query_1_1 | found
        found = sum([df[column_name].str.contains(x,case=False,na=False) for x in not_substr_list_step1])>0
        query_1_2 = query_1_2 | found
        
    # df['step1.1'] = None
    # df['step1.2'] = None
    df.loc[query_1_1,'step1.1'] = 1
    df.loc[query_1_2,'step1.2'] = 1
    return df

if __name__ == "__main__":
    
    dme_substr_list = ["Missing", "loose", "Bent", "crack", "damage", "Motor", "brakes", "brake", "broken"]
    df = pd.read_excel('./DME Clean/DIV30.xlsx')
    result_df = filter(df,dme_substr_list)
    result_df.to_excel('./11.xlsx',index=False)
