from dataIO import init_local_data, add_collection

def main():
    init_local_data("test", "password123")
    add_collection("test","col1")


if __name__ == "__main__":
    main()
