import csv, json, tempfile, unittest
from pathlib import Path
from fbosint.core import validate_facebook_url, sha256_file
from fbosint.storage import Store
from fbosint.reports import export_case

class CoreTests(unittest.TestCase):
    def test_valid_url(self):
        self.assertEqual(validate_facebook_url("https://www.facebook.com/page#section"),
                         "https://www.facebook.com/page")
    def test_rejects_non_facebook_and_http(self):
        for url in ("http://facebook.com/x", "https://evil.example/facebook.com",
                    "https://facebook.com.evil.example/x", "javascript:alert(1)"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_facebook_url(url)
    def test_rejects_credentials(self):
        with self.assertRaises(ValueError):
            validate_facebook_url("https://user:pass@facebook.com/page")
    def test_case_and_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Store(Path(tmp)/"db.sqlite")
            case_id = store.create_case("Test case", "Analyst")
            store.add_url(case_id, "https://facebook.com/example", "Example page")
            store.add_note(case_id, "Needs independent verification.")
            case = store.get_case(case_id)
            jp = export_case(case, "json", tmp)
            cp = export_case(case, "csv", tmp)
            self.assertEqual(json.loads(jp.read_text())["id"], case_id)
            with cp.open(encoding="utf-8-sig") as f:
                self.assertGreaterEqual(len(list(csv.reader(f))), 3)
    def test_hash_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/"evidence.txt"; p.write_text("authorized evidence")
            digest, size = sha256_file(p)
            self.assertEqual(len(digest), 64)
            self.assertEqual(size, len("authorized evidence"))

if __name__ == "__main__":
    unittest.main()
