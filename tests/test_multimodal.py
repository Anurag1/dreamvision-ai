import unittest
from dreamvision import analyze_scene
from dreamvision.prompting import direct_prompt, structured_prompt

class PromptingTests(unittest.TestCase):
    def test_direct_baseline_preserves_input(self):
        text = "A red bicycle beside a bench."
        self.assertEqual(direct_prompt(text), text)

    def test_structured_prompt_contains_scene_graph_facts(self):
        text = "A red bicycle stands beside a wooden bench."
        prompt = structured_prompt(text, analyze_scene(text))
        self.assertIn("bicycle", prompt)
        self.assertIn("bench", prompt)
        self.assertIn("beside", prompt)
        self.assertIn("red", prompt)

    def test_structured_prompt_does_not_claim_missing_details(self):
        prompt = structured_prompt("A dog beside a chair.", analyze_scene("A dog beside a chair."))
        self.assertIn("Do not invent specific details", prompt)

if __name__ == "__main__":
    unittest.main()
