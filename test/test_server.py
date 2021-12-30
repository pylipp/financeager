import os.path
import tempfile
import unittest

from financeager import (
    DEFAULT_POCKET_NAME,
    DEFAULT_TABLE,
    RECURRENT_TABLE,
    entries,
    exceptions,
    server,
)


class AddEntryToServerTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = server.Server()
        cls.server.run(
            "add", name="Hiking boots", value=-111.11, category="outdoors", pocket="0"
        )

    def test_pocket_name(self):
        self.assertEqual("0", self.server._pockets["0"].name)

    def test_pockets(self):
        response = self.server.run("pockets")
        self.assertListEqual(response["pockets"], ["0"])

    def test_unknown_command(self):
        response = self.server.run("peace")
        self.assertIn("peace", response["error"])


class RecurrentEntryServerTestCase(unittest.TestCase):
    def setUp(self):
        self.server = server.Server()
        self.pocket = "2000"
        self.entry_id = self.server.run(
            "add",
            name="rent",
            value=-1000,
            table_name=RECURRENT_TABLE,
            frequency="monthly",
            start="2000-01-02",
            end="2000-07-01",
            pocket=self.pocket,
        )["id"]

    def test_recurrent_entries(self):
        elements = self.server.run(
            "list", pocket=self.pocket, filters={"name": "rent"}
        )["elements"][RECURRENT_TABLE][self.entry_id]
        self.assertEqual(len(elements), 6)

    def test_recurrent_copy(self):
        destination_pocket = "2001"
        response = self.server.run(
            "copy",
            source_pocket=self.pocket,
            table_name=RECURRENT_TABLE,
            destination_pocket=destination_pocket,
            eid=self.entry_id,
        )
        copied_entry_id = response["id"]
        # copied and added as first element, hence ID 1
        self.assertEqual(copied_entry_id, 1)

        source_entry = self.server.run(
            "get", pocket=self.pocket, table_name=RECURRENT_TABLE, eid=self.entry_id
        )["element"]
        destination_entry = self.server.run(
            "get",
            table_name=RECURRENT_TABLE,
            pocket=destination_pocket,
            eid=copied_entry_id,
        )["element"]
        self.assertDictEqual(source_entry, destination_entry)


class FindEntryServerTestCase(unittest.TestCase):
    def setUp(self):
        self.server = server.Server()
        self.pocket = "0"
        self.entry_id = self.server.run(
            "add", name="Hiking boots", value=-111.11, pocket=self.pocket
        )["id"]

    def test_get_pocket(self):
        pocket = self.server._get_pocket(self.pocket)
        self.assertEqual(pocket.name, self.pocket)

        another_pocket = "foo"
        pocket = self.server._get_pocket(another_pocket)
        self.assertEqual(pocket.name, another_pocket)

        pocket = self.server._get_pocket(None)
        self.assertEqual(pocket.name, DEFAULT_POCKET_NAME)

    def test_get_nonexisting_entry(self):
        response = self.server.run("get", pocket=self.pocket, eid=-1)
        error = response["error"]
        self.assertIsInstance(error, exceptions.PocketEntryNotFound)
        self.assertEqual(str(error), "Entry not found.")

    def test_invalid_update(self):
        response = self.server.run("update", pocket=self.pocket, value="one", eid=1)
        error = response["error"]
        self.assertIsInstance(error, exceptions.PocketValidationFailure)
        self.assertEqual(str(error), "Invalid input data:\nvalue: Not a valid number.")

    def test_query_and_reset_response(self):
        category = entries.CategoryEntry.DEFAULT_NAME
        response = self.server.run(
            "list", pocket=self.pocket, filters={"category": category}
        )
        self.assertGreater(len(response), 0)
        self.assertIsInstance(response, dict)
        self.assertIsInstance(response["elements"], dict)
        self.assertIsInstance(response["elements"][DEFAULT_TABLE], dict)
        self.assertIsInstance(response["elements"][RECURRENT_TABLE], dict)

    def test_response_is_none(self):
        response = self.server.run("get", pocket=self.pocket, eid=self.entry_id)
        self.assertIn("element", response)
        self.assertEqual(response["element"].doc_id, self.entry_id)

        response = self.server.run("remove", pocket=self.pocket, eid=self.entry_id)
        self.assertEqual(response["id"], self.entry_id)

        response = self.server.run(
            "list",
            pocket=self.pocket,
            filters={
                "name": "Hiking boots",
                "category": entries.CategoryEntry.DEFAULT_NAME,
            },
        )
        self.assertDictEqual(response["elements"][DEFAULT_TABLE], {})
        self.assertDictEqual(response["elements"][RECURRENT_TABLE], {})

    def test_update(self):
        new_category = "Outdoorsy shit"
        self.server.run(
            "update", eid=self.entry_id, pocket=self.pocket, category=new_category
        )
        element = self.server.run("get", eid=self.entry_id, pocket=self.pocket)[
            "element"
        ]
        self.assertEqual(element["category"], new_category.lower())

    def test_copy(self):
        destination_pocket = "1"
        response = self.server.run(
            "copy",
            source_pocket=self.pocket,
            destination_pocket=destination_pocket,
            eid=self.entry_id,
        )
        copied_entry_id = response["id"]
        # copied and added as first element, hence ID 1
        self.assertEqual(copied_entry_id, 1)

        source_entry = self.server.run("get", pocket=self.pocket, eid=self.entry_id)[
            "element"
        ]
        destination_entry = self.server.run(
            "get", pocket=destination_pocket, eid=copied_entry_id
        )["element"]
        self.assertDictEqual(source_entry, destination_entry)

    def test_unsuccessful_copy(self):
        self.assertRaises(
            exceptions.PocketEntryNotFound,
            self.server._copy_entry,
            source_pocket=self.pocket,
            destination_pocket="1",
            eid=42,
        )


class JsonPocketsServerTestCase(unittest.TestCase):
    def test_pockets(self):
        tmp_dir = tempfile.mkdtemp()
        self.server = server.Server(data_dir=tmp_dir)

        self.assertDictEqual(self.server.run("pockets"), {"pockets": []})

        # Create dummy JSON files
        pockets = ["1000", "1500"]
        for p in pockets:
            open(os.path.join(tmp_dir, f"{p}.json"), "w").close()

        self.assertDictEqual(self.server.run("pockets"), {"pockets": pockets})


if __name__ == "__main__":
    unittest.main()
