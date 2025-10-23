import streamlit as st
import json
import os
from inventory_data import inventory as fallback_inventory

# -------------------------------
# 📦 Load Inventory from JSON or fallback
# -------------------------------
def load_inventory():
    if os.path.exists("inventory.json"):
        try:
            with open("inventory.json", "r") as f:
                data = json.load(f)
                if data:
                    return data
                else:
                    st.info("📁 inventory.json is empty. Using fallback inventory.")
        except json.JSONDecodeError:
            st.warning("⚠️ inventory.json is corrupted. Using fallback inventory.")
    else:
        st.info("📁 inventory.json not found. Using fallback inventory.")
    return fallback_inventory

# -------------------------------
# 💾 Save Inventory to JSON
# -------------------------------
def save_inventory(inventory):
    with open("inventory.json", "w") as f:
        json.dump(inventory, f, indent=2)

# -------------------------------
# 📊 Summary Statistics
# -------------------------------
def show_summary(inventory):
    st.subheader("📊 Summary Statistics")
    st.write(f"Total items: {len(inventory)}")
    if inventory:
        avg_price = sum(item['price'] for item in inventory) / len(inventory)
        st.write(f"Average price: ${avg_price:.2f}")
        highest = max(inventory, key=lambda x: x['rating'])
        st.write(f"Highest rated item: {highest['name']} ({highest['rating']})")
        total_stock = sum(item['stock'] for item in inventory)
        st.write(f"Total stock: {total_stock}")

# -------------------------------
# 📈 Chart Visualization
# -------------------------------
def show_charts(inventory):
    st.subheader("📈 Category Distribution")
    categories = [item['category'] for item in inventory]
    if categories:
        st.bar_chart({cat: categories.count(cat) for cat in set(categories)})

# -------------------------------
# 🔍 Filter Inventory
# -------------------------------
def filter_inventory(inventory):
    st.subheader("🔍 Filter Inventory")

    category_options = sorted(set(item['category'] for item in inventory))
    category = st.selectbox("Select Category", ["All"] + category_options)
    max_price = st.number_input("Max Price", min_value=0.0, value=0.0)
    min_rating = st.number_input("Min Rating", min_value=0.0, value=0.0)
    min_stock = st.number_input("Min Stock", min_value=0, value=0)

    filtered = []
    for item in inventory:
        if category != "All" and item['category'].lower() != category.lower():
            continue
        if max_price > 0 and item['price'] > max_price:
            continue
        if min_rating > 0 and item['rating'] < min_rating:
            continue
        if min_stock > 0 and item['stock'] < min_stock:
            continue
        filtered.append(item)

    st.subheader("📋 Filtered Results")
    if filtered:
        for item in filtered:
            st.write(f"- {item['name']} | {item['category']} | ${item['price']:.2f} | Stock: {item['stock']} | Rating: {item['rating']}")
    else:
        st.info("No items matched your filters.")

# -------------------------------
# ✏️ Add/Edit/Delete Items
# -------------------------------
def manage_inventory(inventory):
    st.subheader("✏️ Manage Inventory")
    action = st.selectbox("Choose action", ["None", "Add", "Edit by Name", "Delete by Name"])

    if action == "Add":
        with st.form("add_form"):
            name = st.text_input("Name")
            category = st.text_input("Category")
            price = st.number_input("Price", min_value=0.0)
            stock = st.number_input("Stock", min_value=0)
            rating = st.number_input("Rating", min_value=0.0, max_value=5.0)
            submitted = st.form_submit_button("Add Item")
            if submitted:
                inventory.append({
                    "name": name,
                    "category": category,
                    "price": price,
                    "stock": stock,
                    "rating": rating
                })
                save_inventory(inventory)
                st.success("✅ Item added!")

    elif action == "Edit by Name":
        name_to_edit = st.text_input("Enter item name to edit").lower()
        match = next((item for item in inventory if item['name'].lower() == name_to_edit), None)
        if match:
            with st.form("edit_form"):
                price = st.number_input("New Price", value=match['price'])
                stock = st.number_input("New Stock", value=match['stock'])
                rating = st.number_input("New Rating", value=match['rating'])
                submitted = st.form_submit_button("Update Item")
                if submitted:
                    match['price'] = price
                    match['stock'] = stock
                    match['rating'] = rating
                    save_inventory(inventory)
                    st.success("✅ Item updated!")
        else:
            st.warning("❌ Item not found.")

    elif action == "Delete by Name":
        name_to_delete = st.text_input("Enter item name to delete").lower()
        if st.button("Delete"):
            original_len = len(inventory)
            inventory[:] = [item for item in inventory if item['name'].lower() != name_to_delete]
            if len(inventory) < original_len:
                save_inventory(inventory)
                st.success("✅ Item deleted.")
            else:
                st.warning("❌ Item not found.")

# -------------------------------
# 🚀 Main App
# -------------------------------
def main():
    st.title("🧠 Inventory Manager App")
    inventory = load_inventory()

    filter_inventory(inventory)
    show_summary(inventory)
    show_charts(inventory)
    manage_inventory(inventory)

if __name__ == "__main__":
    main()