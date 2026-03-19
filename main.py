from dataIO import init_local_data, add_collection, add_task

def main():
    # init_local_data("test", "password123")
    add_collection("test","col1")
    add_task("task1", "test", "cos",collection=1)



if __name__ == "__main__":
    main()
