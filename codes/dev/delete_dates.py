import pickle


def delete_element_from_dict(file_path):
    # Load the dictionary from the pickle file
    with open(file_path, 'rb') as f:
        data = pickle.load(f)

    # Print the current dictionary
    print("Current dictionary:")
    for key, value in data.items():
        print(f"{key}: {value}")

    # Ask the user for the key of the element to delete
    key_to_delete = input("Enter the key of the element you want to delete: ")

    # Delete the element if the key exists
    if key_to_delete in data:
        del data[key_to_delete]
        print(f"Element with key '{key_to_delete}' has been deleted.")
    else:
        print(f"No element with key '{key_to_delete}' found.")

    # Save the updated dictionary back to the pickle file
    with open(file_path, 'wb') as f:
        pickle.dump(data, f)


if __name__ == '__main__':
    delete_element_from_dict('../data/.update_file.pkl')
