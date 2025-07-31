# TECHORA S.r.l. – Simulated Retail Sales Database Project

This project simulates the real-world workflow of a **Data Analyst** working for the fictional retail company **Techora S.r.l.**

Techora S.r.l. is a fictional Italian company that sells electronic devices for both in-house use (e.g., washing machines, hair dryers) and outdoor activities (e.g., smartphones, headphones).

---

## 🎯 Project Goals

- Build a custom database (instead of using pre-built data) using **Python**
- Analyze performance across stores using **Power BI**

All data was generated using Python, with a focus on **realism**, **scalability**, and **variety**. The second part of the project involved **data visualization** and **performance analysis** using **DAX measures** and Power BI dashboards.

---

## 📁 Files Included

1. `README.md` – Project overview and design rationale  
2. `database_generator.py` – Python script for database creation  
3. `dax_measures.txt` – DAX measures created in Power BI  

---

## 🏢 Who is Techora?

**Techora S.r.l.** is a fictional Italian retail company with **30+ stores** across Italy. Founded 10 years ago, the company has recently gone through a leadership change. The new CEO is interested in gaining a comprehensive overview of the company's performance.

The data analyst team has been asked to analyze the last **4 years of store sales** to answer questions such as:

- Is the company growing in terms of **sales volume** and **revenue**?
- Are **discounts** or **trade terms** affecting profitability?
- Which are the **best-performing stores**?
- Have the **annual targets** per Store, Region, and MacroRegion been met?

The insights will help the new CEO make data-informed strategic decisions.

---

## 🧱 Database Creation

The database simulates **4 years of sales data**, with values mostly generated **randomly** to avoid bias and ensure scalability.

Each table description below includes:
- What data it contains
- How it was created
- How it connects to other tables via primary and foreign keys (a visual model is provided in Power BI and referenced in `dax_measures.txt`)

---

## 📊 Tables Overview

### 📍 REGION TABLE

Each store belongs to a **Region**, and each Region is part of a **MacroRegion**.

- Region names were retrieved via API
- Assigned a `RegionID` and grouped into MacroRegions by geographical location

**Columns:**
- `RegionID` [PK]  
- `RegionName` [FK]  
- `MacroRegionName` [FK]  
- `MacroRegionID` [FK]  
- `StateName` [FK] – set to `"Italy"`  
- `StateID` [FK] – set to `1`

---

### 🏬 STORE TABLE

- Each Region was assigned **0–3 stores**
- Regions with 0 stores were excluded from the final model
- Store names were formatted as `REG1`, `REG2`, etc., per region
- Each store is assigned a `MacroRegionManagerID`

**Columns:**
- `StoreID` [PK]  
- `StoreName` [FK]  
- `RegionName` [FK]  
- `RegionID` [FK]  
- `MacroRegionID` [FK]  
- `StateID` [FK]  
- `MacroRegionManagerID` [FK]

---

### 👥 MACROREGIONMANAGER TABLE

- Each MacroRegion has **1 MacroRegionManager**

**Columns:**
- `MacroRegionManagerID` [PK]  
- `MacroRegionManagerName` [FK]  
- `MacroRegionName` [FK]  
- `MacroRegionID` 

---

### 👥 EMPLOYEE TABLE

- Each store has **2–4 employees**
- Always includes at least one **Seller** and one **StoreManager**

**Columns:**
- `EmployeeID` [PK]  
- `EmployeeName` [FK]  
- `StoreID` [FK]  
- `Role` (e.g., `Seller`, `StoreManager`)

---

### 🎯 TARGET TABLE

- Each store has a randomly assigned **sales target per year**

**Columns:**
- `StoreID` [PK]  
- `Year` [FK]  
- `Target` [FK] – in millions

---

### 🏢 VENDOR TABLE

Represents external companies supplying Techora's products.

**Columns:**
- `VendorID` [PK]  
- `VendorName` [FK]  
- `TradeDiscount` [FK] – randomly between `25.8%` and `55.6%`

---

### 📦 PRODUCT TABLE

- Created using combinations of predefined **Type**, **Color**, and **Power**
- Resulted in **1,088 unique products**
- Each product was randomly assigned to a `Vendor`
- Price is random (200–1,000 EUR), not tied to power level

**Columns:**
- `ProductID` [PK]  
- `ProductName` [FK]  
- `VendorID` [FK]  
- `VendorName` [FK]   
- `VAT` – fixed at `22%` (as per Italian regulation)
- `Price` [FK] 

---

### 👤 CUSTOMERS TABLE

- Each store has **50–300 customers**
- Total: **6,058 unique customers**

**Columns:**
- `CustomerID` [PK]  
- `CustomerName` [FK]  
- `StoreID` [FK]
- `StoreName` [FK]

---


---

### 🧾 ORDER TABLE (Customer Orders)

- Contains 4 years of **customer purchase data**
- Customers receive random **discounts** (5% or 10%)
- `SellerID` and `ApprovedSellerID` are identical (no approval needed)

**Columns:**
- `OrderID` [PK]  
- `OrderDate` [FK]  
- `CustomerID` [FK]  
- `CustomerName` [FK]  
- `ProductID` [FK]  
- `ProductName` [FK]  
- `VendorID` [FK]  
- `Quantity` [FK]  
- `Price` [FK]  
- `TotalAmount` [FK] – `Price * Quantity`  
- `StoreID` [FK]  
- `EmployeeID` [FK]  
- `ApprovingEmployeeID` [FK] – matches `SellerID`  
- `AppliedDiscount` – 5% or 10%

---

### 🧾 ORDER TABLE (Employee Orders)

- Same structure as customer orders
- Employee orders always receive a **30% discount**
- Purchase must be approved by a **StoreManager**

**Columns:**
- `OrderID` [PK]  
- `OrderDate` [FK]  
- `CustomerID` [FK]  
- `CustomerName` [FK]  
- `ProductID` [FK]  
- `ProductName` [FK]  
- `VendorID` [FK]  
- `Quantity` [FK]  
- `VAT` [FK]  
- `Price` [FK]  
- `TotalAmount` [FK]  
- `StoreID` [FK]  
- `EmployeeID` [FK]  
- `ApprovingEmployeeID` [FK] – set to `StoreManagerID`  
- `AppliedDiscount` – fixed at 30%

> Since the creation of these two tables was the result of many operation, the main modifications, as well as their merge, were performed in Power BI using **Power Query**. See `dax_measures.txt` for the transformation steps.

---

## ✅ Summary

This project covers 4 years of fictional sales data for an Italian retail company. It allows the analysis of key metrics like:

- Sales volume  
- Revenue trends  
- Regional and store-level performance  
- Impact of discounts and trade terms  
- Target achievement by store and region

---

## 🚀 Future Improvements

While the model is scalable and functional, there is room for enhancement:

- Add `OpeningDate` and `ClosingDate` to model store lifecycle  
- Simulate employee turnover and hiring  
- Introduce real-world data issues for cleaning practice  
- Add marketing campaign data or loyalty programs  

---

## 🔚 Final Notes

This project was created to replicate the tasks of a **data analyst**, from raw data generation to final business insights in Power BI. It showcases:

- Data modeling and schema design  
- Python-based data generation  
- Use of Power Query and DAX in Power BI  
- Business-driven analysis with a realistic use case  

Feel free to explore the data, adapt the model, and build upon it for your own projects or portfolio.

---
