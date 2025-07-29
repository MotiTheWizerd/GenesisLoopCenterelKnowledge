import json
import os

file_path = '/ray_moti_conv/chats.json' # Make sure to replace this with your actual file name

# Check if the file exists
if not os.path.exists(file_path):
    print(f"Error: The file '{file_path}' was not found.")
else:
    try:
        print(f"Attempting to load JSON from: {file_path}")
        # Open the file and load its content
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("JSON file loaded successfully.")

        # --- Now you can start "viewing" or inspecting the data ---

        # 2. Inspecting the top-level structure:
        print("\n--- Top-level structure ---")
        if isinstance(data, dict):
            print("The top-level element is a dictionary.")
            print(f"Number of top-level keys: {len(data)}")
            print(f"Top-level keys: {list(data.keys())[:5]}...") # Show first 5 keys
        elif isinstance(data, list):
            print("The top-level element is a list.")
            print(f"Number of top-level items: {len(data)}")
            # If it's a list of dictionaries, check the keys of the first item
            if len(data) > 0 and isinstance(data[0], dict):
                print(f"Keys of the first item (if dictionary): {list(data[0].keys())[:5]}...")
            elif len(data) > 0:
                print(f"Type of first item: {type(data[0])}")
        else:
            print(f"The top-level element is of type: {type(data)}")
            print(f"Value: {str(data)[:200]}...") # Show first 200 chars if not dict/list

        # 3. Accessing specific parts (example: assuming it's a list of dicts)
        # You'll need to adapt this based on your actual JSON structure
        print("\n--- Sample data from the file (first 3 items/keys) ---")
        if isinstance(data, list) and len(data) > 0:
            for i, item in enumerate(data[:3]): # Print first 3 items
                print(f"\nItem {i}:")
                if isinstance(item, dict):
                    # For dictionaries, print a few key-value pairs
                    for key, value in list(item.items())[:3]: # Print first 3 key-value pairs
                        print(f"  {key}: {str(value)[:100]}...") # Limit value preview
                else:
                    print(f"  {str(item)[:200]}...")
        elif isinstance(data, dict):
            for i, (key, value) in enumerate(list(data.items())[:3]): # Print first 3 top-level key-value pairs
                print(f"\nKey: {key}")
                print(f"  Value (type={type(value)}): {str(value)[:200]}...")
        else:
            print("Data structure not easily sampled in this generic way.")


        # 4. Searching for specific data (example)
        # If you know what you're looking for, you can implement search logic
        # For example, if it's a list of dictionaries and you want to find items
        # where a 'name' key has a specific value:
        # print("\n--- Searching for a specific value (example) ---")
        # search_key = 'some_field'
        # search_value = 'some_value'
        # found_count = 0
        # if isinstance(data, list):
        #     for item in data:
        #         if isinstance(item, dict) and item.get(search_key) == search_value:
        #             found_count += 1
        #             # print(item) # Uncomment to print the full item
        # print(f"Found {found_count} items with '{search_key}': '{search_value}'")


    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print("This might mean the file is corrupted or not valid JSON.")
    except MemoryError:
        print(f"Error: Not enough memory to load the entire {file_path} into RAM.")
        print("Consider using a streaming parser for very large files.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")