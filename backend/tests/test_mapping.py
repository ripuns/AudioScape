from app.mapping import select_layers
from app.models import Box, Detection


def det(label, score=0.9, x=0.8):
    return Detection(label, score, Box(x - 0.1, 0.2, 0.2, 0.2))


def sounds(layers):
    return [layer.sound for layer in layers]


def test_beach_scene_layers():
    assert sounds(select_layers("beach", [])) == ["waves", "wind", "seagulls", "footsteps"]


def test_forest_city_rainy_street_layers():
    assert sounds(select_layers("forest", [])) == ["birds", "wind", "insects", "leaves"]
    assert sounds(select_layers("city", [])) == ["traffic", "horns", "crowd", "construction"]
    assert sounds(select_layers("rainy_street", [])) == ["rain", "traffic", "umbrella", "footsteps"]


def test_bird_on_beach_maps_to_seagulls_and_keeps_position():
    layers = {layer.sound: layer for layer in select_layers("beach", [det("bird", x=0.82)])}
    assert "birds" not in layers
    assert layers["seagulls"].position == (0.82, 0.3)
    assert "object:bird" in layers["seagulls"].sources


def test_person_adds_footsteps_without_duplicates():
    layers = select_layers("park", [det("person"), det("person", 0.6)])
    assert sounds(layers).count("footsteps") == 1


def test_object_adds_new_layer():
    layers = select_layers("beach", [det("dog")])
    assert "barking" in sounds(layers)
