from inventory import update_inventory

def calculate_total(items):
    prices = {'item1': 10, 'item2': 20, 'item3': 15}
    return sum(prices[item] for item in items)

def process_order(order_items):
    total = calculate_total(order_items)
    update_inventory(order_items)
    return total
