stock_levels = {
    'item1': 100,
    'item2': 150,
    'item3': 200
}

def update_inventory(items):
    for item in items:
        if item in stock_levels:
            stock_levels[item] -= 1
    return stock_levels
