from django.test import TestCase
from shilat.services.meter import detect_bahr

class MeterDetectionTests(TestCase):
    def test_non_empty(self):
        text = "قفا نبك من ذكرى حبيب ومنزل\nبسقط اللوى بين الدخول فحومل"
        bahr, conf, details = detect_bahr(text)
        self.assertTrue(conf >= 0.1)
        self.assertTrue(isinstance(details, dict))

    def test_empty(self):
        bahr, conf, details = detect_bahr("")
        self.assertEqual(bahr, "")
        self.assertEqual(conf, 0.0)
