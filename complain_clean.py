import pandas as pd
import numpy as np
import filter_dme as dme
import traceback



def main(df,lot_vendor,vendor_mapping):
    try:
        def get_vendor(series):
            if str(series['Material Vendor']).isdigit():
                vendor_code = int(series['Material Vendor'])
            else:
                vendor_code = lot_vendor.get(str(series['Material Number']) + "|" + str(series['Material Lot Number']), '')
            return vendor_code


        

    except Exception as e:
        traceback.print_exc()

     





if __name__ == "__main__":
    dme_substr_list = ["Missing", "loose", "Bent", "crack", "damage", "Motor", "brakes", "brake", "broken"]
    
    
    lot_vendor = pd.read_excel('./DME Clean/Lot NO- Vendor no.xlsx')
    lot_vendor.dropna(subset=['LOT #'],inplace=True)
    lot_vendor['key'] = lot_vendor['ITEM'].map(str)+ "|" + lot_vendor['LOT #'].map(str)
    lot_vendor_dict = dict(zip(lot_vendor['key'],lot_vendor['VENDOR #']))
    
    vendor_mapping = pd.read_excel('./DME Clean/Vendor _mapping.xlsx')
    vendor_mapping_dict = dict(zip(vendor_mapping['Vendor Number'],vendor_mapping['Cleaned Vendor Name']))
    
    df = pd.read_excel('./DME Clean/All Divisions Monthly Complaint Report.xlsx')
    df_not22 = df[df['Division'] != 22]

    
    main(df,lot_vendor_dict,vendor_mapping_dict)
    # df = pd.read_excel('./DME Clean/DIV30.xlsx')
    # df_dme = dme.filter(df,dme_substr_list)
    # df_dme.to_excel('./111.xlsx')
 