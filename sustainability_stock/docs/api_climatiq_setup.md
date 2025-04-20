# 🌱 Configuring the Climatiq API for the `sustainability_stock` Module

This guide explains how to configure and use the Climatiq API in the context of the `sustainability_stock` module from MyCompanyCO2.

---

## 📌 Purpose

The `sustainability_stock` module enriches Odoo logistics workflows with carbon emissions automatic computation using the [Climatiq](https://www.climatiq.io/transportation-carbon-emissions) API. It allows you to calculate emissions related to the transportation of goods automatically every time a reception or a delivery is being performed by the logistic team.

---

## 🔧 Requirements

- A Climatiq account with a valid API key ([create one here](https://www.climatiq.io/))
- Odoo (16, 17 or 18) with the `sustainability_stock` module installed
- Administrator access to your Odoo instance

---

## ⚙️ Setup Steps

### 1. Install the Module

Make sure the `sustainability_stock` module is installed in your Odoo instance.

### 2. Configure the Module

In the Sustainability setup screen define the url API https://api.climatiq.io/freight/v2/intermodal and your key. The additional setups may differ depending on your context but here's an example of configuration ![{BF83471A-564A-4FC0-ADB8-0E407B424202}](https://github.com/user-attachments/assets/1c34ef9b-605f-4012-9646-f6dcf5a242f1)

## 🔗 Useful resources

- [Climatiq freight and shipping website](https://www.climatiq.io/transportation-carbon-emissions)
- [Interactive demo](https://intermodal.climatiq.io/v2)
- [API demo](https://www.climatiq.io/docs/api-reference/intermodal-freight)
- [Documentation officielle Climatiq](https://docs.climatiq.io/)
