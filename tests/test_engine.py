import unittest
from dreamvision import analyze_scene

class DreamVisionTests(unittest.TestCase):
    def test_extracts_objects_and_attributes(self):
        result = analyze_scene("A red bicycle beside a wooden bench.")
        self.assertGreaterEqual(len(result.objects), 2)
        bicycle = next(o for o in result.objects if o["name"] == "bicycle")
        self.assertIn({"type": "color", "value": "red"}, bicycle["attributes"])

    def test_detects_spatial_relation(self):
        result = analyze_scene("A bicycle beside a bench.")
        self.assertTrue(any(r["relation"] == "beside" for r in result.relations))

    def test_reports_unknowns(self):
        result = analyze_scene("A dog sits beside a chair.")
        self.assertIn("lighting / time of day", result.unknowns)

    def test_rejects_empty_input(self):
        with self.assertRaises(ValueError):
            analyze_scene("  ")

    def test_scores_are_bounded(self):
        result = analyze_scene("A bright red car in a city street.")
        for score in result.scores.values():
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)

if __name__ == "__main__":
    unittest.main()
