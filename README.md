# todo_list

A project implementing simple CRUD interface for creating a todo list. All data is stored in SQLite database(a single file) for simplicity. An item consists of `id`, `text` and `done` fields.

## Installation
```
pip3 install flask flask-sqlalchemy pytest protobuf
```

## How to run
```
python3 app.py
```
After this the server will be running on port 5000(assuming it's free)

## Available endpoints
* GET / - returns all list items
* GET /<item-id\> - returns an item by its id
* POST / - creates an item
* PUT /<item-id\> - updates an item by its id
* DELETE /<item-id\> - deletes an item by its id

Each endpoint can be used with protobuf for request/response by adding `?use_protobuf=true` to reguest path.

## Tests
To run tests simply run `pytest` .

