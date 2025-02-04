# Test file 1: order_processing.py
def calculate_total(items):
    return sum(items)

def process_order(order_items):
    total = calculate_total(order_items)
    update_inventory(order_items)
    return total

# Test file 2: inventory.py
def update_inventory(items):
    for item in items:
        stock_levels[item] -= 1
