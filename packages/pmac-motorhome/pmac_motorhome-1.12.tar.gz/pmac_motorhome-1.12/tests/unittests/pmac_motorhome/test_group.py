import unittest

from pmac_motorhome.constants import ControllerType, PostHomeMove
from pmac_motorhome.group import Group


class TestMotionArea(unittest.TestCase):
    def test_all_motors_have_same_post_move_type_returns_correct_tuple_if_no_motors(
        self,
    ):
        # Arrange
        group = Group(2, 11, ControllerType.brick)
        group.all_motors = []

        # Act
        result = group.all_motors_have_same_post_move_type()

        # Assert
        self.assertFalse(result[0])
        self.assertEqual(result[1], PostHomeMove.none)
