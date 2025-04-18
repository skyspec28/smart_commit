def process_data(data=None):
    if data is None:  # Check if data is specifically None
        print("No data provided.")
        return

    if not data:  # Check if data is empty or falsy
        print("Data is empty.")
        return

    # Process the data here
    print("Processing data:", data)

process_data()  # Output: No data provided.
process_data([])  # Output: Data is empty.
process_data([1, 2, 3])  # Output: Processing data: [1, 2, 3]

def add():
    pass