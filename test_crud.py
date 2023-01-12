import pytest

from app import Item, app, db
from todo_list_pb2 import ListItem as ProtobufItem
from todo_list_pb2 import ToDoList


@pytest.fixture()
def init_db():
    db.create_all()

    yield

    db.session.remove()
    db.drop_all()


@pytest.fixture(scope="session")
def app_client():
    app.config.update({"TESTING": True})
    app.app_context().push()

    with app.test_client() as client:
        yield client


@pytest.fixture()
def valid_items(init_db):
    item = Item(text="Task 1")
    db.session.add(item)

    item = Item(text="Task 2")
    db.session.add(item)

    item = Item(text="Task 3")
    db.session.add(item)

    db.session.commit()


def test_add_item_json(app_client, init_db):
    res = app_client.post(
        "/", json={"text": "Test task"}, content_type="application/json"
    )

    assert res.status_code == 201

    item = Item.query.filter_by(id=res.json["id"]).first()
    assert item.text == "Test task"


def test_add_item_protobuf(app_client, init_db):
    protobuf_item = ProtobufItem()
    protobuf_item.text = "Test task"
    res = app_client.post(
        "/?use_protobuf=true",
        data=protobuf_item.SerializeToString(),
        content_type="application/protobuf",
    )

    assert res.status_code == 201

    protobuf_item.ParseFromString(bytes(res.text, "utf-8"))
    item = Item.query.filter_by(id=protobuf_item.id).first()
    assert item.text == "Test task"


def test_get_item_json(app_client, valid_items):
    res = app_client.get("/1")

    assert res.status_code == 200
    assert res.json["text"] == "Task 1"

    res = app_client.get("/2")

    assert res.status_code == 200
    assert res.json["text"] == "Task 2"

    res = app_client.get("/3")

    assert res.status_code == 200
    assert res.json["text"] == "Task 3"


def test_get_item_protobuf(app_client, valid_items):
    protobuf_item = ProtobufItem()

    res = app_client.get("/1?use_protobuf=true")
    protobuf_item.ParseFromString(bytes(res.text, "utf-8"))

    assert res.status_code == 200
    assert protobuf_item.text == "Task 1"

    res = app_client.get("/2?use_protobuf=true")
    protobuf_item.ParseFromString(bytes(res.text, "utf-8"))

    assert res.status_code == 200
    assert protobuf_item.text == "Task 2"

    res = app_client.get("/3?use_protobuf=true")
    protobuf_item.ParseFromString(bytes(res.text, "utf-8"))

    assert res.status_code == 200
    assert protobuf_item.text == "Task 3"


def test_get_all_items_protobuf(app_client, valid_items):
    todo_list = ToDoList()
    res = app_client.get("/?use_protobuf=true")
    todo_list.ParseFromString(bytes(res.text, "utf-8"))

    assert res.status_code == 200
    assert len(todo_list.items) == 3


def test_get_all_items_json(app_client, valid_items):
    res = app_client.get("/")

    assert res.status_code == 200
    assert len(res.json) == 3


def test_delete_item(app_client, valid_items):
    res = app_client.delete("/1")

    assert res.status_code == 204

    res = app_client.get("/")

    assert res.status_code == 200
    assert len(res.json) == 2


def test_update_item_json(app_client, init_db):
    item = Item(text="Task 1")
    db.session.add(item)

    res = app_client.put(
        "/1", json={"text": "Test task"}, content_type="application/json"
    )

    assert res.status_code == 200

    item = Item.query.filter_by(id=res.json["id"]).first()
    assert item.text == "Test task"


def test_update_item_protobuf(app_client, init_db):
    item = Item(text="Task 1")
    db.session.add(item)

    protobuf_item = ProtobufItem()
    protobuf_item.text = "Test task"
    protobuf_item.id = 1
    res = app_client.put(
        "/1?use_protobuf=true",
        data=protobuf_item.SerializeToString(),
        content_type="application/protobuf",
    )

    assert res.status_code == 200

    protobuf_item.ParseFromString(bytes(res.text, "utf-8"))
    item = Item.query.filter_by(id=protobuf_item.id).first()
    assert item.text == "Test task"
