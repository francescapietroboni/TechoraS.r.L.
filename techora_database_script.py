import random
from datetime import datetime, timedelta

import numpy as np
import os
import pandas as pd
import requests
from faker import Faker

# Initialising fake data generators for English and Italian
fake_it = Faker('it_IT') #for Customers and Employees
fake_en = Faker('en_UK') #for Vendors 

# 1 . Creating the Region Table === 

# Step 1. Retrieving the list of regions in Italy via API
url = 'https://axqvoqvbfjpaamphztgd.functions.supabase.co/regioni'
regions = requests.get(url)
regions.status_code
RegionName = regions.json()

RegionName



# Step 2. Creating a list of MacroRegion and MacroRegionID
def assign_macroregion(col):

   NorthWest = ['Piemonte', "Valle d'Aosta", 'Lombardia', 'Liguria']
   NorthEast = ['Trentino Alto Adige', 'Veneto', 'Friuli Venezia Giulia', 'Emilia Romagna']
   Center = ['Toscana', 'Umbria', 'Marche', 'Lazio','Abruzzo', 'Molise']
   South = ['Campania', 'Puglia', 'Basilicata', 'Calabria', 'Sicilia', 'Sardegna']

   if col in NorthWest:
     return 'NorthWest',1
   elif col in (NorthEast):
        return 'NorthEast',2
   elif col in (Center):
        return 'Center',3
   elif col in (South):
       return 'South',4 
   else:
       return 'Not Defined',0
      

sumofregions = len(RegionName)
# Step 3. Saving the results and call the function
macroregion = []
macroregion_id = []

for el in RegionName:
    region,id  = assign_macroregion(el)
    macroregion.append(region)
    macroregion_id.append(id)



# Step 4. Creating the Region Table  
RegionTable = pd.DataFrame.from_dict({ 'RegionID' : range (1,len(RegionName) +1 ),
                                'RegionName' : RegionName,
                                'MacroRegionName' : macroregion,
                             'MacroRegionID' : macroregion_id,
                               'StateName' : 'Italy',
                               'StateID' : 1
                               })

RegionTable


# 2. Creating the Store Table ===

def create_store(RegionTable: pd.DataFrame) -> pd.DataFrame:
    """
    The function creates the Store Table starting from the Region Table.
    Every region has 0 to 3 Stores.
    Each Store's name is composed of the first 3 letters of their Region + sequence number.
    """
    np.random.seed(5)

    # Each Region is assigned a random number of Store (between 0 and 3) 
    RegionTable = RegionTable.copy()
    RegionTable['Store'] = np.random.randint(0, 4, size=len(RegionTable))

    # Calculate the number of Stores
    num_stores = RegionTable['Store'].sum()

    # Naming the Stores according to their Region 
    store_names = []
    region_names = []

    for _, row in RegionTable.iterrows():
        region_name = row['RegionName']
        n_stores = row['Store']
        prefix = region_name[:3].upper()
        for i in range(1, n_stores + 1):
            store_names.append(f"{prefix}{i}")
            region_names.append(region_name)

    # Assegna MacroRegionID e ManagerID corretti
    macroregion_ids = []
    manager_ids = []
    for region_name in region_names:
        _, macro_id = assign_macroregion(region_name)
        macroregion_ids.append(macro_id)
        manager_ids.append(macro_id)  # ManagerID uguale a MacroRegionID

    # Building the Store Table 
    StoreTable = pd.DataFrame({
        'StoreID': range(1, num_stores + 1),
        'StoreName': store_names,
        'RegionName': region_names,
        'MacroRegionID': macroregion_ids,
        'StateID': [1] * num_stores,  # fixed value for now
        'ManagerID': manager_ids
    })

    return StoreTable

StoreTable = create_store(RegionTable)



StoreTable = StoreTable.merge(RegionTable[['RegionID', 'RegionName']], how='left', left_on='RegionName', right_on='RegionName')

StoreTable = StoreTable[["StoreID", "StoreName", "RegionName", "RegionID", "MacroRegionID", "StateID", "ManagerID"]]

# 3. Creating the MacroRegionManager Table ===

# Defining the MacroRegions and their IDs
macroregions = ['NorthWest', 'NorthEast', 'Center', 'South']
macroregion_ids = list(range(1, len(macroregions) + 1))

# Using the Italian Faker to generate the MacroRegionManagers' names
Manager_Name = [fake_it.name() for _ in macroregions]

ManagerTable = pd.DataFrame({
    'MacroRegionManagerID': macroregion_ids,
    'MacroRegionManagerName': Manager_Name,
    'MacroRegionName': macroregions,
    'MacroRegionID': macroregion_ids
})

ManagerTable

# 4. Creating the Employee Table ===

# Step 1. Creating a random number of employees
employee_per_shop = pd.DataFrame(StoreTable[['StoreID', 'StoreName']])
np.random.seed(5)
employee_per_shop['NumOfEmployee'] = np.random.randint(2, 5, size=len(employee_per_shop))

total_employee = employee_per_shop['NumOfEmployee'].sum()

# Step 2. Naming the employees
employee_names = [fake_it.name() for _ in range(total_employee)]

# Step 3. Assigning employees to a shop
def assign_employee(names, store_ids, num_employee):
    data = []
    idx = 0
    for sid, n in zip(store_ids, num_employee):
        for _ in range(n):
            if idx >= len(names):
                raise ValueError("Not enough employee to assign")
            data.append({'EmployeeName': names[idx], 'StoreID': sid})
            idx += 1
    return pd.DataFrame(data)

EmployeeTable = assign_employee(employee_names, employee_per_shop['StoreID'], employee_per_shop['NumOfEmployee'])
EmployeeTable['EmployeeID'] = range(1, len(EmployeeTable) + 1)

# Step 4. Cleaning "EmployeeName" column
EmployeeTable['EmployeeName'] = (
    EmployeeTable['EmployeeName']
    .str.replace(r'Sig\.?\.?ra?', '', regex=True)
    .str.replace(r'Dott\.?', '', regex=True)
    .str.replace(r'Sig\.?', '', regex=True)
    .str.replace(r'\.', '', regex=True)
    .str.strip()
)

# Step 5. Defining Roles (one employee per store will be StoreManager)
def assign_role(EmployeeTable):
    roles = []
    grouped = EmployeeTable.groupby('StoreID')['EmployeeID'].apply(list)
    for store_id, emp_ids in grouped.items():
        manager_id = random.choice(emp_ids)
        for emp_id in emp_ids:
            role = 'ShopManager' if emp_id == manager_id else 'Seller'
            roles.append({'EmployeeID': emp_id, 'StoreID': store_id, 'Role': role})
    return pd.DataFrame(roles)

roles_df = assign_role(EmployeeTable)
EmployeeTable = EmployeeTable.merge(roles_df, on=['EmployeeID', 'StoreID'])
EmployeeTable = EmployeeTable[['EmployeeID', 'EmployeeName', 'StoreID', 'Role']]


# 5. Creating the Target Table ===

# List of years
years = [2021, 2022, 2023, 2024]

# Creating the TargetTable + target per year
TargetTable = []
for store_id in StoreTable['StoreID']:
    for year in years:
        TargetTable.append({'StoreID': store_id, 'Year': year})

TargetTable = pd.DataFrame(TargetTable)

# Creating random target per shop per year
np.random.seed(7) 
TargetTable['Target'] = np.round(np.random.uniform(1000000, 10000000, size=len(TargetTable)), 2)

TargetTable

# 6. Creating the Vendor Table ===

# Creating 20 Company names (in English)
vendor_names = [fake_en.company() for _ in range(20)]

# Creating the Vendor Table
VendorTable = pd.DataFrame({
    'VendorID': range(1, 21),
    'VendorName': vendor_names
})

# Assigning each Vendor a trade discount between 25.8 and 55.6
np.random.seed(10)  
VendorTable['TradeDiscount'] = np.round(np.random.uniform(25.8, 55.6, size=20), 2)

VendorTable

# 7. Creating the Product Table ===

# Step 1. Product categories
TypeOfProduct = ['Dishwasher','Laundry Machine', 'Smartphone', 'Coffee Machine', 'Dryer',
                 'Fridge', 'Oven','Laptop', 'Hair Dryer', 'Smart TV', 'Smart Watch',
                 'Headphones','Smart Glasses','Case','Screen','Refrigerator','Mouse']
Color = ['Black', 'White', 'Silver', 'Light Gray', 'Dark Gray','Red','Blue','Green']
Power = [300,350,400,450,500,550,600,650]

# Step 2. Combining categories to create products' names
def generate_product_names(types, colors, powers):
    return [f"{t},{c},{p}" for t in types for c in colors for p in powers]

product_names = generate_product_names(TypeOfProduct, Color, Power)
num_products = len(product_names)

# Step 3. Distributing the products across Vendors
def assign_items_to_vendors(vendors, total_items, min_items, max_items):
    n = len(vendors)
    assigned = [int(min_items)] * n
    remaining = total_items - sum(assigned)
    margins = [int(max_items - min_items)] * n
    
    while remaining > 0:
        i = random.randint(0, n - 1)
        if margins[i] > 0:
            assigned[i] += 1
            margins[i] -= 1
            remaining -= 1

    return pd.DataFrame({'VendorName': vendors, 'NumAssigned': assigned})

assigned_items = assign_items_to_vendors(
    VendorTable['VendorName'],
    total_items=num_products,
    min_items=num_products/20 - 15,
    max_items=num_products/20 + 15
)

# Step 4. Assigning the products
random.shuffle(product_names)

assigned_products = []
index = 0
for vendor, num in zip(assigned_items['VendorName'], assigned_items['NumAssigned']):
    for _ in range(num):
        if index >= len(product_names): break
        assigned_products.append({'VendorName': vendor, 'ProductName': product_names[index]})
        index += 1

ProductTable = pd.DataFrame(assigned_products)
ProductTable['ProductID'] = range(1, len(ProductTable) + 1)

# Step 5. Apply VendorID 
ProductTable = ProductTable.merge(VendorTable[['VendorID', 'VendorName']], on='VendorName', how='left')

# Step 6. Apply VAT and Price 
np.random.seed(15)
ProductTable['Price'] = np.round(np.random.uniform(200, 1000, size=len(ProductTable)), 2)
ProductTable['VAT'] = 22

# Step 7. Organising the Table 
ProductTable = ProductTable[['ProductID', 'ProductName', 'VendorName', 'VendorID', 'Price', 'VAT']]

ProductTable

# 8. Creating the Customer Table ===

# Step 1. Customer per store (temporary table)
customerpershop = pd.DataFrame(StoreTable[['StoreID', 'StoreName']])
np.random.seed(5)
customerpershop['NumOfCustomers'] = np.random.randint(50, 300, size=len(customerpershop))

sumofcustomers = customerpershop['NumOfCustomers'].sum()

# Step 2. Creating customers
customers = [fake_it.name() for _ in range(sumofcustomers)]
customerIDs = range(1, sumofcustomers + 1)

# Step 3. Names cleaning
cleaned_customers = (
    pd.Series(customers)
    .str.replace(r'Sig\.?\.?ra?', '', regex=True)
    .str.replace(r'Dott\.?', '', regex=True)
    .str.replace(r'Sig\.?', '', regex=True)
    .str.replace(r'\.', '', regex=True)
    .str.strip()
)

# Step 4. Creating the final version of the Customer Table 
def assign_customers_to_stores(customer_ids, customer_names, shop_ids, shop_names, num_customers):
    assigned = []
    available = list(zip(customer_ids, customer_names))
    random.shuffle(available)
    idx = 0

    for sid, sname, num in zip(shop_ids, shop_names, num_customers):
        for _ in range(num):
            if idx >= len(available):
                raise ValueError("Non ci sono abbastanza clienti disponibili!")
            cid, cname = available[idx]
            assigned.append({
                'CustomerID': cid,
                'CustomerName': cname,
                'StoreID': sid,
                'StoreName': sname
            })
            idx += 1

    return pd.DataFrame(assigned)

CustomerTable = assign_customers_to_stores(
    customerIDs,
    cleaned_customers,
    customerpershop['StoreID'],
    customerpershop['StoreName'],
    customerpershop['NumOfCustomers']
)


# 9. Creating Order Table (Customer) ===

# Step 1. Defining the number of orders per customer
orderpercustomer = pd.DataFrame(CustomerTable[['CustomerID', 'CustomerName', 'StoreID']])
np.random.seed(6)
orderpercustomer['NumOfOrders'] = np.random.randint(1, 100, size=len(orderpercustomer))
total_orders = orderpercustomer['NumOfOrders'].sum()

# Step 2. Generating random data for each order
startdate = datetime(2021, 1, 1)
enddate = datetime(2024, 12, 31)
def random_date(start, end, n):
    delta = end - start
    total_seconds = delta.total_seconds()
    return [start + timedelta(seconds=random.randint(0, int(total_seconds))) for _ in range(n)]

order_dates = random_date(startdate, enddate, total_orders)

# Step 3. Assign a random amount of product to each customer
def assign_orders(CustomerTable, ProductTable):
    assigned = []
    prod_list = ProductTable['ProductName'].tolist()
    prod_lookup = ProductTable.set_index('ProductName')['ProductID'].to_dict()

    for _, row in CustomerTable.iterrows():
        customer_id = row['CustomerID']
        customer_name = row['CustomerName']
        store_id = row['StoreID']
        n_orders = row['NumOfOrders']
        selected_products = random.choices(prod_list, k=n_orders)
        for prod in selected_products:
            assigned.append({
                'CustomerID': customer_id,
                'CustomerName': customer_name,
                'StoreID': store_id,
                'ProductName': prod,
                'ProductID': prod_lookup[prod]
            })
    return pd.DataFrame(assigned)

assigned_orders_employee = assign_orders(orderpercustomer, ProductTable)
assigned_orders_employee['OrderDate'] = order_dates

# Step 4. Adding products' details
OrderTableCustomer = assigned_orders_employee.merge(
    ProductTable[['ProductID', 'ProductName', 'VendorID', 'VendorName', 'Price', 'VAT']],
    on='ProductID', how='left'
)

# Step 5. Quantity per order
np.random.seed(42)
OrderTableCustomer['Quantity'] = np.random.randint(1, 3, size=len(OrderTableCustomer))

# Step 6. Adding Total
OrderTableCustomer['Total'] = OrderTableCustomer['Price'] * OrderTableCustomer['Quantity']

# Step 7. Adding an Employee per order according to the shop the order was placed
def assign_sellers(OrderTableCustomer, EmployeeTable):
    sellers = EmployeeTable[EmployeeTable['Role'] == 'Seller']
    seller_map = sellers.groupby('StoreID')['EmployeeID'].apply(list).to_dict()
    
    assigned = []
    for store_id in OrderTableCustomer['StoreID']:
        available = seller_map.get(store_id, [None])
        assigned.append(random.choice(available))
    return assigned

OrderTableCustomer['EmployeeID'] = assign_sellers(OrderTableCustomer, EmployeeTable)
OrderTableCustomer['ApprovingEmployeeID'] = OrderTableCustomer['EmployeeID']


# Step 8. Add an AppliedDiscount column (5 or 10%) in a range of 15-25% of orders 
np.random.seed(100)
OrderTableCustomer['AppliedDiscount'] = 'None'
n_discount = int(len(OrderTableCustomer) * np.random.uniform(0.15, 0.25))
discount_ids = OrderTableCustomer.sample(n=n_discount).index
OrderTableCustomer.loc[discount_ids, 'AppliedDiscount'] = [
    random.choices([5, 10], weights=[5, 3])[0] for _ in range(n_discount)
]

# Step 9. Adding OrderID and customising column order
OrderTableCustomer.sort_values('OrderDate', inplace=True)
OrderTableCustomer.reset_index(drop=True, inplace=True)
OrderTableCustomer['OrderID'] = range(1, len(OrderTableCustomer) + 1)

# Step 10. Final version of the Order Table
OrderTableCustomer = OrderTableCustomer[[
    'OrderID', 'OrderDate', 'CustomerID', 'CustomerName', 'ProductID', 'ProductName_x',
    'VendorID', 'VendorName', 'Quantity', 'Price', 'VAT', 'Total',
    'AppliedDiscount', 'StoreID', 'EmployeeID', "ApprovingEmployeeID"
]]


# 10. Creating Order Table (Employee) ===

# Step 1. Defining the number of orders per employee
orderperemployee = pd.DataFrame(EmployeeTable[['EmployeeID', 'EmployeeName', 'StoreID']])
np.random.seed(6)
orderperemployee['NumOfOrders'] = np.random.randint(1, 20, size=len(orderperemployee))
total_orders_employee = orderperemployee['NumOfOrders'].sum()

# Step 2. Generating random data for each order
startdate = datetime(2021, 1, 1)
enddate = datetime(2024, 12, 31)
def random_date(start, end, n):
    delta = end - start
    total_seconds = delta.total_seconds()
    return [start + timedelta(seconds=random.randint(0, int(total_seconds))) for _ in range(n)]

order_dates = random_date(startdate, enddate, total_orders_employee)

# Step 3. Assigning a random amount of product to each employee
def assign_orders_employee(EmployeeTable, ProductTable):
    assigned_employee = []
    prod_list_employee = ProductTable['ProductName'].tolist()
    prod_lookup_employee = ProductTable.set_index('ProductName')['ProductID'].to_dict()


    for _, row in EmployeeTable.iterrows():
        employee_id = row['EmployeeID']
        employee_name = row['EmployeeName']
        store_id_employee = row['StoreID']
        n_orders_employee = row['NumOfOrders']
        selected_products_employee = random.choices(prod_list_employee, k=n_orders_employee)
        for prod in selected_products_employee:
            assigned_employee.append({
                'EmployeeID': employee_id,
                'EmployeeName': employee_name,
                'StoreID': store_id_employee,
                'ProductName': prod,
                'ProductID': prod_lookup_employee[prod]
            })
    return pd.DataFrame(assigned_employee)

assigned_orders_employee = assign_orders_employee(orderperemployee, ProductTable)
assigned_orders_employee['OrderDate'] = order_dates

# Step 4. Updaiting the Customer Table 

employee_to_customer_id = {}
max_id = CustomerTable['CustomerID'].max()

# Obtaining the Employee who purchased an order
employees_with_orders = assigned_orders_employee[['EmployeeID', 'EmployeeName', 'StoreID']].drop_duplicates()

# Recalling the StoreID 
store_map = store_map = StoreTable.set_index('StoreID')['StoreName'].to_dict()

new_customers = []

for _, row in employees_with_orders.iterrows():
    max_id += 1
    new_customer = {
        'CustomerID': max_id,
        'CustomerName': row['EmployeeName'],
        'StoreID': row['StoreID'],
        'StoreName': store_map.get(row['StoreID'], '')
    }
    employee_to_customer_id[row['EmployeeID']] = max_id
    new_customers.append(new_customer)

# Updating the Customer Table
CustomerTable = pd.concat([CustomerTable, pd.DataFrame(new_customers)], ignore_index=True)



# Step 5. Adding products' details
OrderTableEmployee = assigned_orders_employee.merge(
    ProductTable[['ProductID', 'ProductName', 'VendorID', 'VendorName', 'Price', 'VAT']],
    on='ProductID', how='left'
)

OrderTableEmployee['CustomerID'] = OrderTableEmployee['EmployeeID'].map(employee_to_customer_id)

OrderTableEmployee.rename(columns={
    'EmployeeID': 'CustomerEmployeeID',  # l'ID dell'employee che ha fatto l'ordine come cliente
    'EmployeeName': 'CustomerEmployeeName'
}, inplace=True)



# Step 6. Quantity per order
np.random.seed(42)
OrderTableEmployee['Quantity'] = np.random.randint(1, 3, size=len(OrderTableEmployee))

# Step 7. Adding Total
OrderTableEmployee['Total'] = OrderTableEmployee['Price'] * OrderTableEmployee['Quantity']

# Step 8. Adding an Employee per order according to the shop the order was placed
def assign_sellers_employee(OrderTableEmployee, EmployeeTable):
    sellers_employee = EmployeeTable[EmployeeTable['Role'] == 'Seller']
    seller_map_employee = sellers_employee.groupby('StoreID')['EmployeeID'].apply(list).to_dict()
    
    assigned_employee = []
    for store_id in OrderTableEmployee['StoreID']:
        available = seller_map_employee.get(store_id, [None])
        assigned_employee.append(random.choice(available))
    return assigned_employee

OrderTableEmployee['EmployeeID'] = assign_sellers_employee(OrderTableEmployee, EmployeeTable)

# Step 9. Adding an AppliedDiscount column (5 or 10%) in a range of 15-25% of orders 
OrderTableEmployee['AppliedDiscount'] = 30

# Step 10. Adding OrderID and customising column order
OrderTableEmployee.sort_values('OrderDate', inplace=True)
OrderTableEmployee.reset_index(drop=True, inplace=True)
OrderTableEmployee['OrderID'] = range(1, len(OrderTableEmployee) + 1)

# Step 11. Adding the ApprovingEmployeeID column to Employee Table

shop_managers = EmployeeTable[EmployeeTable['Role'] == 'ShopManager']

def assign_shop_manager(shop_ids, manager_table):
    manager_lookup = manager_table.set_index('StoreID')[['EmployeeName', 'EmployeeID']].to_dict(orient='index')
    assigned = []
    for storeID in shop_ids:
        info = manager_lookup.get(storeID, {'EmployeeName': None, 'EmployeeID': None})
        assigned.append({
            'StoreID': storeID,
            'StoreManagerName': info['EmployeeName'],
            'StoreManagerID': info['EmployeeID']
        })
    return pd.DataFrame(assigned)

assigned_managers = assign_shop_manager(OrderTableEmployee['StoreID'], shop_managers)

OrderTableEmployee['ApprovingEmployeeID'] = assigned_managers['StoreManagerID']


# Step 12. Final version of the Order Table
OrderTableEmployee = OrderTableEmployee[[
     'OrderID', 'OrderDate', 'CustomerID', 'CustomerEmployeeID', 'CustomerEmployeeName',
    'ProductID', 'ProductName_x', 'VendorID', 'VendorName', 'Quantity',
    'Price', 'VAT', 'Total', 'AppliedDiscount', 'StoreID',
    'ApprovingEmployeeID'
]]


# 12. Saving all files locally ===

# Defining the base folder path
base_path = **insert_personal_path_here**

# List of files to save
files_to_save = [
    (RegionTable,        os.path.join(base_path, "RegionTable.xlsx")),
    (StoreTable,         os.path.join(base_path, "StoreTable.xlsx")),
    (ManagerTable,       os.path.join(base_path, "ManagerTable.xlsx")),
    (EmployeeTable,      os.path.join(base_path, "EmployeeTable.xlsx")),
    (TargetTable,        os.path.join(base_path, "TargetTable.xlsx")),
    (VendorTable,        os.path.join(base_path, "VendorTable.xlsx")),
    (ProductTable,       os.path.join(base_path, "ProductTable.xlsx")),
    (CustomerTable,      os.path.join(base_path, "CustomerTable.xlsx")),
    (OrderTableCustomer, os.path.join(base_path, "OrderTableCustomer.xlsx")),
    (OrderTableEmployee, os.path.join(base_path, "OrderTableEmployee.xlsx"))
]


errors = []

for df, path in files_to_save:
    try:
        df.to_excel(path, index=False)
    except Exception as e:
        errors.append((path, str(e)))

if not errors:
    print("✅ All files have been saved")
else:
    print("❌ Warning: some files have not been saved")
    for path, err in errors:
        print(f" An Error occurred on {os.path.basename(path)}: {err}")

