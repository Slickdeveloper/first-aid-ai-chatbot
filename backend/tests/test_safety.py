"""Safety-rule tests.

These tests verify that dangerous phrasing triggers the emergency pathway used by
both the backend response and the frontend emergency banner.
"""

from app.services.safety_service import is_emergency


def test_emergency_detection_catches_breathing_distress() -> None:
    # Breathing problems are one of the highest-priority emergency categories.
    assert is_emergency("I cant breathe")
    assert is_emergency("I can't breathe")
    assert is_emergency("I have trouble breathing")
    assert is_emergency("He is gasping")
    assert is_emergency("She has breathing difficulties")


def test_emergency_detection_catches_other_high_risk_symptoms() -> None:
    # Cover several emergency categories in one place so safety logic stays visible.
    assert is_emergency("I have crushing chest pain")
    assert is_emergency("heartache")
    assert is_emergency("His chest hurts")
    assert is_emergency("He passed out")
    assert is_emergency("My father's face is drooping and his speech is slurred")
    assert is_emergency("She has stroke symptoms")
    assert is_emergency("There is heavy bleeding from the wound")
    assert is_emergency("There is gushing blood")
    assert is_emergency("The child is choking and cannot swallow")
    assert is_emergency("This looks like a severe allergic reaction with throat swelling")
    assert is_emergency("These are severe allergic reactions with tongue swelling")
    assert is_emergency("The person is having convulsions")
    assert is_emergency("The person is unresponsive")
