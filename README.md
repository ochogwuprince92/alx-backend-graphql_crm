# ALX Backend GraphQL CRM

A Django-based CRM backend using **GraphQL** with **Graphene-Django** and **django-filter**.  
This project demonstrates creating a GraphQL endpoint, defining a schema, and enabling filtering for customers, products, and orders.

---

## 📌 Features
- GraphQL endpoint (`/graphql`) with GraphiQL interface.
- Query customers, products, and orders.
- Advanced filtering with **django-filter**:
  - Search by name, email, creation date, and more.
  - Range filters (e.g., price, total amount).
  - Related field lookups (e.g., customer name in orders).
  - Sorting with `order_by` parameter.

---

## 🛠 Installation

### 1️⃣ Clone the repository
git clone https://github.com/ochogwuprince92/alx-backend-graphql_crm.git
cd alx-backend-graphql_crm
