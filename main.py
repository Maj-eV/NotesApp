from dataIO import init_local_data, add_collection, add_task, deleteTask

def main():
    # init_local_data("test", "password123")
    add_collection("test","col1")
    add_task("task1", "test", "cos", 1)
    deleteTask("task1", "test")



if __name__ == "__main__":
    main()
