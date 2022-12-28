## 📣 简介

该项目是清洗US投诉数据的脚本，按照特定的业务逻辑来清洗美国投诉数据，并标记*Manufacturing*的投诉。

## 📝 清洗流程

### 准备数据

1. All Divisions Monthly Complaint Report（从Insight中导出1月到报告月的数据。）
2. DIV22（从美国公盘中导出，[\willow\SPT\aaa-common\Quality\QA
   Engineering\Adrian\Monthly Trending](/willow/SPT/aaa-common/Quality/QA%20Engineering/Adrian/Monthly%20Trending)，文件名sheet 2019）

### 清洗Vendor Code

1. 删除Q列"Cause Group"中为"Duplicate"的数据。
2. DIV21 和 DIV51

   * 如果列"Material Vendor"不为纯数字，则把列"Manufacture Site"的值替换到"Material Vendor"。
   * 如果列"Manufacture Site"的值为数字，该条记录不变
3. 没有”MaterialVendor”的记录，则用Material Number& Material Lot Number作为主键，去匹配NYK中的对应vendor number。若Material Number或Material Lot Number为空，直接删除改行记录。

### 去重数据

按照Notification Number + Material Number + Material Vendor + Material Lot Number去重

## 🔰MFG筛选规则

### Div10

ColumnQ:DC:Supplier Error Asia(Medline Brand) or Cause text is "VC"

### Div30

#### Step 1: find out mft. Complaints

1. The original cause group as “DC: Supplier error Asia (Medline brand)”
2. Key words search:
   - Missing/loose
   - Bent/crack/damage
   - Motor

However, negative expressions should not be included in it. For example: not miss, not loose, didn't miss, did not miss…..

#### Step 2: delete complaints with below key words or description:

1. Notification description: cancel/blank
2. Short Text For Defect Type Code: blank
3. Defect Group: blank
4. Short Text For Cause Code:
   - With "customer", defects caused by customer use
   - End of life expectancy, normal wear/tear
   - Data entry error
5. Cause group:
   - Not a product defect
   - DC: Medline Error/mfg.*

#### Step3: clarify the column of “Investigation Notification Description”

1. Below description are not considered as mtf. reason
   - No investigation summary（意思是Notification description为空）
   - Shipping damage （最常见的描述是”this issue is most likely due to shipping damage”，一般用shipping去定位）
   - Out of warranty （一般用warranty去定位）
   - Not Medline branded product(可以参考 "Short Text For Cause Code"里面会有这个选项，但有时候只会在Notification description中出现)
   - Canceled by customer （很少遇到）
   - Products worked as designed （很少遇到）
   - Enter error（很少遇到）
   - No sample or picture received/ not have to return any sample/will not be confirm（一般用No sample去定位,常见表达” No sample was received therefore the issue cannot be confirmed at this time”，”No sample or photo of the defective product has been received therefore the issue cannot be confirmed at this time”等等）
   - Customer reason（很少遇到）
   - 字符数少于500，基本上可以判定为N

#### Step4: For the rest, define based on the description. Ex., description with "complaint is confirmed" is mft. complaint.
