"""Test the metric value class."""

import unittest

from pydantic import ValidationError
from aind_qcportal_schema.metric_value import (
    DropdownMetric,
    CheckboxMetric,
    RulebasedMetric,
    MultiAssetMetric,
)


class MetricValueTest(unittest.TestCase):
    """Test the metric value class."""

    def test_constructors(self):
        """Build valid versions of each metric."""

        v = DropdownMetric(value="a", options=["a", "b"])
        self.assertIsNotNone(v)

        v = CheckboxMetric(value=["a"], options=["a", "b"])
        self.assertIsNotNone(v)

        v = RulebasedMetric(value="a", rule="a")
        self.assertIsNotNone(v)

    def test_multi_asset(self):
        """Ensure multi_asset validators work"""

        with self.assertRaises(ValidationError):
            MultiAssetMetric(
                values=[1, 2, 3],
                options=[0, 1, 2, 3],
            )

        mam = MultiAssetMetric(
            values=[1, 2, 3], options=[0, 1, 2, 3], type="dropdown"
        )

        self.assertIsNotNone(mam)

    def test_checkbox_metric_valid(self):
        """Test valid CheckboxMetric instances."""
        cm = CheckboxMetric(value=["a"], options=["a", "b"])
        self.assertIsNotNone(cm)

        cm = CheckboxMetric(value=[], options=["a", "b"])
        self.assertIsNotNone(cm)

    def test_checkbox_metric_invalid(self):
        """Test invalid CheckboxMetric instances."""
        with self.assertRaises(ValidationError):
            CheckboxMetric(value=["c"], options=["a", "b"])

        with self.assertRaises(ValidationError):
            CheckboxMetric(value=["a", "c"], options=["a", "b"])

    def test_dropdown_metric_valid(self):
        """Test valid DropdownMetric instances."""
        dm = DropdownMetric(value="a", options=["a", "b"])
        self.assertIsNotNone(dm)

        dm = DropdownMetric(value="", options=["a", "b"])
        self.assertIsNotNone(dm)

    def test_dropdown_metric_invalid(self):
        """Test invalid DropdownMetric instances."""
        with self.assertRaises(ValidationError):
            DropdownMetric(value="c", options=["a", "b"])

        with self.assertRaises(ValidationError):
            DropdownMetric(value="a", options=[])


if __name__ == "__main__":
    unittest.main()
