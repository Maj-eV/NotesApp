import pytest
import json
from pathlib import Path
from dataIO import init_local_data, add_collection, add_task, delete_collection, delete_task, get_collections, get_tasks
from errors import EmptyValueError

@pytest.fixture
def isolated_fs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _read_user_file(user):
    with open(f"usrAppData_{user}.json", "r", encoding="utf-8") as file_handler:
        return json.load(file_handler)


def test_init_local_data_success_creates_file(isolated_fs):
    assert init_local_data("alice", "secret") == 0
    user_file = Path("usrAppData_alice.json")
    assert user_file.exists()

    data = _read_user_file("alice")
    assert data["collections"] == []
    assert data["number_of_collections"] == 0
    assert data["tasks"] == []
    assert isinstance(data["pswd"], str)
    assert data["pswd"] != "secret"


def test_init_local_data_empty_values_raise_empty_value_error(isolated_fs):
    with pytest.raises(EmptyValueError):
        init_local_data("", "secret")

    with pytest.raises(EmptyValueError):
        init_local_data("alice", "")


def test_init_local_data_wrong_types_raise_type_error(isolated_fs):
    with pytest.raises(TypeError):
        init_local_data(123, "secret")

    with pytest.raises(TypeError):
        init_local_data("alice", 123)


def test_init_local_data_existing_file_raises_value_error(isolated_fs):
    init_local_data("alice", "secret")
    with pytest.raises(ValueError):
        init_local_data("alice", "other")


def test_add_collection_success_and_incremented_ids(isolated_fs):
    init_local_data("alice", "secret")
    assert add_collection("alice", "Work") == 0
    assert add_collection("alice", "Home") == 0

    data = _read_user_file("alice")
    assert data["number_of_collections"] == 2
    assert data["collections"][0]["collection_id"] == 1
    assert data["collections"][1]["collection_id"] == 2
    assert data["collections"][0]["name"] == "Work"
    assert data["collections"][1]["name"] == "Home"


def test_add_collection_invalid_inputs(isolated_fs):
    init_local_data("alice", "secret")

    with pytest.raises(EmptyValueError):
        add_collection("", "Work")
    with pytest.raises(EmptyValueError):
        add_collection("alice", "")

    with pytest.raises(TypeError):
        add_collection(123, "Work")
    with pytest.raises(TypeError):
        add_collection("alice", 123)


def test_add_collection_missing_user_file_raises_file_not_found(isolated_fs):
    with pytest.raises(FileNotFoundError):
        add_collection("missing", "Work")


def test_add_task_success_duplicate_handling_and_cross_collection_behavior(isolated_fs):
    init_local_data("alice", "secret")
    add_collection("alice", "Work")
    add_collection("alice", "Home")

    assert add_task("Buy milk", "alice", "2L", 1) == 0
    assert add_task("Buy milk", "alice", "different content", 1) == 0
    assert add_task("Buy milk", "alice", "allowed in another collection", 2) == 0

    data = _read_user_file("alice")
    assert len(data["tasks"]) == 2
    assert data["tasks"][0]["title"] == "Buy milk"
    assert data["tasks"][0]["collection"] == 1
    assert data["tasks"][1]["collection"] == 2


def test_add_task_invalid_inputs(isolated_fs):
    init_local_data("alice", "secret")

    with pytest.raises(EmptyValueError):
        add_task("", "alice", "content", 1)
    with pytest.raises(EmptyValueError):
        add_task("Task", "", "content", 1)
    with pytest.raises(EmptyValueError):
        add_task("Task", "alice", "", 1)
    with pytest.raises(EmptyValueError):
        add_task("Task", "alice", "content", 0)

    with pytest.raises(TypeError):
        add_task(123, "alice", "content", 1)
    with pytest.raises(TypeError):
        add_task("Task", "alice", 123, 1)
    with pytest.raises(TypeError):
        add_task("Task", "alice", "content", "1")


def test_add_task_missing_user_file_raises_file_not_found(isolated_fs):
    with pytest.raises(FileNotFoundError):
        add_task("Task", "missing", "content", 1)


def test_delete_task_deletes_matching_item_only(isolated_fs):
    init_local_data("alice", "secret")
    add_collection("alice", "Work")
    add_collection("alice", "Home")
    add_task("Keep", "alice", "content", 1)
    add_task("Drop", "alice", "content", 1)
    add_task("Drop", "alice", "content", 2)

    assert delete_task("Drop", "alice", 1) == 0

    data = _read_user_file("alice")
    remaining = {(task["title"], task["collection"]) for task in data["tasks"]}
    assert remaining == {("Keep", 1), ("Drop", 2)}


def test_delete_task_non_existing_item_still_returns_zero(isolated_fs):
    init_local_data("alice", "secret")
    add_collection("alice", "Work")
    add_task("Keep", "alice", "content", 1)

    assert delete_task("Missing", "alice", 1) == 0
    data = _read_user_file("alice")
    assert len(data["tasks"]) == 1


def test_delete_task_missing_user_file_raises_file_not_found(isolated_fs):
    with pytest.raises(FileNotFoundError):
        delete_task("Task", "missing", 1)


def test_delete_collection_deletes_matching_collection_only(isolated_fs):
    init_local_data("alice", "secret")
    add_collection("alice", "Work")
    add_collection("alice", "Home")

    assert delete_collection("alice", 1) == 0
    data = _read_user_file("alice")
    assert [collection["collection_id"] for collection in data["collections"]] == [2]


def test_delete_collection_non_existing_item_still_returns_zero(isolated_fs):
    init_local_data("alice", "secret")
    add_collection("alice", "Work")

    assert delete_collection("alice", 999) == 0
    data = _read_user_file("alice")
    assert len(data["collections"]) == 1


def test_delete_collection_missing_user_file_raises_file_not_found(isolated_fs):
    with pytest.raises(FileNotFoundError):
        delete_collection("missing", 1)


def test_get_collections_returns_names_and_empty_when_file_missing(isolated_fs):
    init_local_data("alice", "secret")
    add_collection("alice", "Work")
    add_collection("alice", "Home")

    assert get_collections("alice") == ["Work", "Home"]
    assert get_collections("missing") == []


def test_get_tasks_returns_filtered_tuples_and_empty_when_missing(isolated_fs):
    init_local_data("alice", "secret")
    add_collection("alice", "Work")
    add_collection("alice", "Home")
    add_task("Task 1", "alice", "work-content", 1)
    add_task("Task 2", "alice", "home-content", 2)

    assert get_tasks("alice", 1) == [("Task 1", "work-content")]
    assert get_tasks("alice", 999) == []
    assert get_tasks("missing", 1) == []