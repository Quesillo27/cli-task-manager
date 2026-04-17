"""Unit tests for validators."""

import unittest

from task_manager.validators import (
    ValidationError,
    validate_due_date,
    validate_export_format,
    validate_order,
    validate_priority,
    validate_sort_key,
    validate_status,
    validate_task_ids,
    validate_title,
)


class TestValidators(unittest.TestCase):
    # ---- priority ---------------------------------------------------------

    def test_priority_valid(self):
        self.assertEqual(validate_priority("high"), "high")

    def test_priority_none_passthrough(self):
        self.assertIsNone(validate_priority(None))

    def test_priority_invalid(self):
        with self.assertRaises(ValidationError):
            validate_priority("nope")

    # ---- status -----------------------------------------------------------

    def test_status_valid(self):
        self.assertEqual(validate_status("done"), "done")

    def test_status_invalid(self):
        with self.assertRaises(ValidationError):
            validate_status("maybe")

    # ---- due date ---------------------------------------------------------

    def test_due_date_valid(self):
        self.assertEqual(validate_due_date("2026-04-17"), "2026-04-17")

    def test_due_date_empty_is_none(self):
        self.assertIsNone(validate_due_date(""))
        self.assertIsNone(validate_due_date(None))

    def test_due_date_wrong_format(self):
        with self.assertRaises(ValidationError):
            validate_due_date("17/04/2026")

    def test_due_date_invalid_month(self):
        with self.assertRaises(ValidationError):
            validate_due_date("2026-13-01")

    # ---- sort/order/format -----------------------------------------------

    def test_sort_key_maps_to_column(self):
        self.assertEqual(validate_sort_key("created"), "created_at")
        self.assertEqual(validate_sort_key("title"), "title")

    def test_sort_key_invalid(self):
        with self.assertRaises(ValidationError):
            validate_sort_key("evil")

    def test_order_normalized(self):
        self.assertEqual(validate_order("asc"), "ASC")
        self.assertEqual(validate_order("DESC"), "DESC")

    def test_order_invalid(self):
        with self.assertRaises(ValidationError):
            validate_order("random")

    def test_export_format_valid(self):
        self.assertEqual(validate_export_format("JSON"), "json")

    def test_export_format_invalid(self):
        with self.assertRaises(ValidationError):
            validate_export_format("pdf")

    # ---- title + task IDs -------------------------------------------------

    def test_title_trimmed(self):
        self.assertEqual(validate_title("  hello  "), "hello")

    def test_title_empty(self):
        with self.assertRaises(ValidationError):
            validate_title("")

    def test_title_whitespace(self):
        with self.assertRaises(ValidationError):
            validate_title("   ")

    def test_title_too_long(self):
        with self.assertRaises(ValidationError):
            validate_title("a" * 501)

    def test_task_ids_valid(self):
        self.assertEqual(validate_task_ids([1, 2, "3"]), [1, 2, 3])

    def test_task_ids_empty(self):
        with self.assertRaises(ValidationError):
            validate_task_ids([])

    def test_task_ids_negative(self):
        with self.assertRaises(ValidationError):
            validate_task_ids([1, -2])

    def test_task_ids_non_integer(self):
        with self.assertRaises(ValidationError):
            validate_task_ids(["abc"])


if __name__ == "__main__":
    unittest.main()
