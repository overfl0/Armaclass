import armaclass


def test_nested_arrays_generation():
    items = {
        'kickTimeout': [
            [0, -1], [1, 180], [2, 180], [3, 180],
        ]
    }

    output = armaclass.generate(items)
    items_reparsed = armaclass.parse(output)

    assert items == items_reparsed
