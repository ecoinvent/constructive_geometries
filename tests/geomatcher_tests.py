from copy import deepcopy

import pytest

from constructive_geometries import ConstructiveGeometries, Geomatcher, resolved_row


def test_default_setup():
    cg = ConstructiveGeometries()

    geomatcher = Geomatcher()
    assert "GLO" in geomatcher
    assert "RoW" not in geomatcher
    assert geomatcher["RoW"] == set()
    assert len(geomatcher["GLO"]) > 400
    assert geomatcher["AS"] == set(cg.data["AS"])
    assert geomatcher[("ecoinvent", "Russia (Europe)")] == set(
        cg.data["Russia (Europe)"]
    )
    assert geomatcher["Japan"] == set(cg.data["JP"])

    with pytest.raises(KeyError):
        geomatcher["Nope"]


def test_magic_methods():
    g = Geomatcher()
    assert len(g) > 400
    for _ in g:
        pass

    assert "NO" in g
    assert g["NO"]

    del g["NO"]
    del g["Russia (Europe)"]

    g["foo"] = {1, 2, 3}
    assert "foo" in g


def test_provide_topology():
    given = {
        "A": {1, 2, 3},
        "B": {2, 3, 4},
    }
    g = Geomatcher(given.copy())
    assert g.topology == given


def test_split_faces():
    given = {
        "A": {1, 2, 3},
        "B": {2, 3, 4},
    }
    expected = {
        "A": {1, 2, 5, 6},
        "B": {2, 5, 6, 4},
    }
    g = Geomatcher(given)
    g.split_face(3)
    assert g.topology == expected
    assert 3 not in g.faces
    assert 5 in g.faces

    given = {
        "A": {1, 2, 3},
        "B": {2, 3, 4},
    }
    expected = {
        "A": {1, 2, 5, 6, 7},
        "B": {2, 5, 6, 7, 4},
    }
    g = Geomatcher(given)
    g.split_face(3, number=3)
    assert g.topology == expected

    given = {
        "A": {1, 2, 3},
        "B": {2, 3, 4},
    }
    expected = {
        "A": {1, 2, 10, 11},
        "B": {2, 10, 11, 4},
    }
    g = Geomatcher(given)
    g.split_face(3, ids={10, 11})
    assert g.topology == expected

    given = {
        "A": {1, 2, 3},
        "B": {2, 3, 4},
    }
    expected = {
        "A": {1, 2, 10, 11},
        "B": {2, 10, 11, 4},
    }
    g = Geomatcher(given)
    g.split_face(3, number=5, ids={10, 11})
    assert g.topology == expected


def test_empty_topology():
    g = Geomatcher({})
    assert g.topology == {}
    assert g.faces == set()
    assert "NO" not in g
    assert "GLO" not in g


def test_add_definitions():
    g = Geomatcher({})
    given = {
        "A": {1, 2, 3},
        "B": {2, 3, 4},
    }
    g.add_definitions(given, "foo", False)
    assert ("foo", "A") in g.topology
    assert g.faces == {1, 2, 3, 4}
    assert "NO" not in g
    assert "GLO" not in g


def test_add_definitions_relative():
    given = {
        "A": {1, 2, 3},
        "B": {2, 3, 4},
    }
    extra = {"C": ["A", "B"]}
    g = Geomatcher(given)
    g.add_definitions(extra, "foo")
    assert g.topology[("foo", "C")] == {1, 2, 3, 4}
    assert "A" in g.topology
    assert "NO" not in g
    assert "GLO" not in g


def test_actual_key():
    given = {
        "A": {1, 2, 3},
        ("silly", "B"): {2, 3, 4},
    }
    g = Geomatcher(given, "silly")
    assert g["A"]
    assert g["B"]
    assert g["B"]
    assert g[("silly", "B")]

    with pytest.raises(KeyError):
        g[("silly", "A")]

    assert g._actual_key("RoW") == "RoW"

    g = Geomatcher()
    assert g._actual_key("GLO") == "GLO"


def test_actual_key_coco():
    given = {
        "AT": {1, 2},
    }
    g = Geomatcher(given, "silly")

    assert g["AT"]
    assert g["Austria"]

    g = Geomatcher(given, "silly", use_coco=False)
    assert g["AT"]
    with pytest.raises(KeyError):
        g["Austria"]


def test_finish_filter_include_self():
    g = Geomatcher({"A": {1, 2}})
    given = [("A", 4), ("B", 6), ("C", 3)]
    assert g._finish_filter(deepcopy(given), "A", True, False, True) == ["B", "A", "C"]
    assert g._finish_filter(deepcopy(given), "A", True, False, False) == ["C", "A", "B"]


def test_finish_filter_not_include_self():
    g = Geomatcher({"A": {1, 2}})
    given = [("A", 4), ("B", 6), ("C", 3)]
    assert g._finish_filter(deepcopy(given), "A", False, False, True) == ["B", "C"]
    assert g._finish_filter(deepcopy(given), "A", False, False, False) == ["C", "B"]


def test_finish_filter_exclusive():
    given = {
        "A": {1, 2, 3},
        "B": {2, 3, 4},
        "C": {3, 4, 5},
        "D": {10, 11},
        "E": {5, 6, 10},
    }
    g = Geomatcher(given)
    lst = [("A", 5), ("B", 6), ("C", 7), ("D", 8), ("E", 9)]
    result = g._finish_filter(lst, "A", True, True, True)
    # Start with E (biggest), then B (next possible)
    assert result == ["E", "B"]
    result = g._finish_filter(lst, "A", True, True, False)
    # Start with A (smallest), then D (next possible)
    assert result == ["A", "D"]


def test_finish_filter_row_ordering():
    # Test non-exclusive ordering of RoW; RoW not key
    given = {
        "A": set(range(10)),
        "B": {2, 3, 4},
        "C": {3, 4, 5},
        "D": {10, 11},
        "E": {5, 6, 10},
    }
    g = Geomatcher(given)
    lst = [("B", 6), ("RoW", 7), ("D", 8), ("E", 9)]
    result = g._finish_filter(lst, "A", False, False, True)
    assert result[-1] == "RoW"
    result = g._finish_filter(lst, "A", False, False, False)
    assert result[0] == "RoW"


def test_finish_filter_row_exclusive_row_key():
    g = Geomatcher()
    assert (
        g._finish_filter(
            [("NO", 4), ("LT", 3), ("LV", 2), ("EE", 1)], "RoW", False, True, True
        )
        == []
    )
    assert (
        g._finish_filter(
            [("NO", 4), ("LT", 3), ("LV", 2), ("EE", 1)], "RoW", True, True, True
        )
        == []
    )
    assert (
        g._finish_filter(
            [("NO", 4), ("LT", 3), ("LV", 2), ("EE", 1), ("RoW", 0)],
            "RoW",
            False,
            True,
            True,
        )
        == []
    )
    assert g._finish_filter(
        [("NO", 4), ("LT", 3), ("LV", 2), ("EE", 1), ("RoW", 0)],
        "RoW",
        True,
        True,
        True,
    ) == ["RoW"]
    assert (
        g._finish_filter(
            [("NO", 4), ("LT", 3), ("LV", 2), ("EE", 1)], "RoW", False, True, False
        )
        == []
    )
    assert (
        g._finish_filter(
            [("NO", 4), ("LT", 3), ("LV", 2), ("EE", 1)], "RoW", True, True, False
        )
        == []
    )
    assert (
        g._finish_filter(
            [("NO", 4), ("LT", 3), ("LV", 2), ("EE", 1), ("RoW", 0)],
            "RoW",
            False,
            True,
            False,
        )
        == []
    )
    assert g._finish_filter(
        [("NO", 4), ("LT", 3), ("LV", 2), ("EE", 1), ("RoW", 0)],
        "RoW",
        True,
        True,
        False,
    ) == ["RoW"]


def test_intersects():
    g = Geomatcher()
    expected = [
        "GLO",
        ("ecoinvent", "UN-AMERICAS"),
        ("ecoinvent", "RLA"),
        ("ecoinvent", "UN-CARIBBEAN"),
    ]
    assert g.intersects("CU") == expected
    assert g.intersects("CU", exclusive=True) == ["GLO"]
    expected = [
        ("ecoinvent", "UN-CARIBBEAN"),
        ("ecoinvent", "RLA"),
        ("ecoinvent", "UN-AMERICAS"),
        "GLO",
    ]
    assert g.intersects("CU", biggest_first=False) == expected

    only = [
        ("ecoinvent", "RLA"),
        ("ecoinvent", "UN-AMERICAS"),
    ]
    expected = [
        ("ecoinvent", "UN-AMERICAS"),
        ("ecoinvent", "RLA"),
    ]
    assert g.intersects("CU", only=only) == expected


def test_contained():
    g = Geomatcher()
    expected = [
        "US",
        ("ecoinvent", "US-AK"),
        ("ecoinvent", "US-AL"),
        ("ecoinvent", "US-AR"),
        ("ecoinvent", "US-ASCC"),
        ("ecoinvent", "US-AZ"),
    ]
    _ = lambda x: sorted(x, key=lambda elem: str(elem))
    assert _(g.contained("US"))[:5] == _(expected)[:5]
    expected.pop(0)
    assert _(g.contained("US", include_self=False))[:5] == _(expected[:5])

    exclusive_expected = [
        ("ecoinvent", "US-AK"),
        ("ecoinvent", "US-HI"),
        ("ecoinvent", "US-IA"),
        ("ecoinvent", "US-KS"),
        ("ecoinvent", "US-MN"),
        ("ecoinvent", "US-ND"),
        ("ecoinvent", "US-NPCC"),
        ("ecoinvent", "US-OK"),
        ("ecoinvent", "US-RFC"),
        ("ecoinvent", "US-SERC"),
        ("ecoinvent", "US-WECC"),
    ]
    assert _(g.contained("US", include_self=False, exclusive=True))[:5] == _(
        exclusive_expected[:5]
    )
    assert g.contained("US", biggest_first=False, include_self=False)[-1] in [
        (
            "ecoinvent",
            "US-AK",
        ),
        (
            "ecoinvent",
            "US-ASCC",
        ),
    ]

    expected = [
        "US",
        ("ecoinvent", "US-ASCC"),
        ("ecoinvent", "US-NPCC"),
        ("ecoinvent", "US-HICC"),
        ("ecoinvent", "US-WECC"),
    ]
    only = [
        ("ecoinvent", "US-WECC"),
        "US",
        ("ecoinvent", "US-NPCC"),
        ("ecoinvent", "US-ASCC"),
        ("ecoinvent", "US-HICC"),
    ]
    assert _(g.contained("US", only=only)) == _(expected)


def test_within():
    g = Geomatcher()
    expected = [
        "GLO",
        ("ecoinvent", "UN-EUROPE"),
        ("ecoinvent", "UN-EEUROPE"),
        ("ecoinvent", "FSU"),
        ("ecoinvent", "IAI Area, Russia & RER w/o EU27 & EFTA"),
        "RU",
    ]
    _ = lambda x: sorted(x, key=lambda elem: str(elem))

    assert _(g.within("RU")) == _(expected)
    expected.pop(-1)
    assert g.within("RU", include_self=False) == expected
    assert g.within("RU", exclusive=True) == ["GLO"]
    expected = [
        "RU",
        ("ecoinvent", "IAI Area, Russia & RER w/o EU27 & EFTA"),
        ("ecoinvent", "FSU"),
        ("ecoinvent", "UN-EEUROPE"),
        ("ecoinvent", "UN-EUROPE"),
        "GLO",
    ]
    assert g.within("RU", biggest_first=False) == expected

    expected = [
        ("ecoinvent", "UN-EUROPE"),
        ("ecoinvent", "UN-EEUROPE"),
        ("ecoinvent", "FSU"),
    ]
    only = [
        ("ecoinvent", "UN-EUROPE"),
        ("ecoinvent", "UN-EEUROPE"),
        ("ecoinvent", "FSU"),
    ]
    assert g.within("RU", only=only) == expected


def test_intersects_row():
    g = Geomatcher()
    assert g.intersects("RoW") == []
    assert g.intersects("RoW", include_self=True) == []
    assert g.intersects("RoW", include_self=True, only=["NO", "LT", "RoW"]) == ["RoW"]
    assert g.intersects(("ecoinvent", "NORDEL"), only=["NO", "RoW"]) == ["NO"]
    assert g.intersects(
        "NO", only=["NO", "RoW"], include_self=True, exclusive=True
    ) == ["NO"]
    assert g.intersects(
        "NO", only=["NO", "RoW"], include_self=True, exclusive=False
    ) == ["NO"]
    assert sorted(
        g.intersects(
            ("ecoinvent", "BALTSO"),
            include_self=False,
            exclusive=True,
            only=["RoW", "EE", "LT", "LV"],
        )
    ) == sorted(["EE", "LT", "LV"])
    assert sorted(
        g.intersects(
            ("ecoinvent", "BALTSO"),
            include_self=False,
            exclusive=True,
            only=["RoW", "LT", "LV"],
        )
    ) == sorted(["LT", "LV"])


def test_contained_row():
    g = Geomatcher()
    assert g.contained("RoW") == []
    assert g.contained("RoW", include_self=True, only=["RoW"]) == ["RoW"]
    assert "RoW" not in g.contained("GLO", only=["NO", "RoW"])
    assert "RoW" not in g.contained("GLO")
    assert "RoW" not in g.contained(("ecoinvent", "RAS"), only=["NO", "LT", "RoW"])


def test_within_row():
    g = Geomatcher()
    assert g.within("RoW") == ["GLO"]
    del g["GLO"]
    assert g.within("RoW") == []


def test_row_contextmanager_add_remove_row():
    g_orig = Geomatcher()
    assert "RoW" not in g_orig
    with resolved_row(["NO", "LT", "EE"], g_orig) as g:
        assert "RoW" in g
        assert "RoW" in g_orig
        assert g is g_orig
    assert "RoW" not in g_orig


def test_row_contextmanager_datasets_or_locations():
    g_orig = Geomatcher()
    with resolved_row(["NO", "LT", "EE"], g_orig) as g:
        assert "RoW" in g.intersects(("ecoinvent", "BALTSO"))
    given = [
        {"location": "NO"},
        {"location": "LT"},
        {"location": "EE"},
    ]
    with resolved_row(given, g_orig) as g:
        assert "RoW" in g.intersects(("ecoinvent", "BALTSO"))


def test_row_contextmanager_intersects():
    g_orig = Geomatcher()
    with resolved_row(["NO", "LT", "EE"], g_orig) as g:
        assert "RoW" in g.intersects(("ecoinvent", "BALTSO"))


def test_row_contextmanager_contained():
    g_orig = Geomatcher()
    with resolved_row(["NO", "LT", "EE"], g_orig) as g:
        assert "RoW" not in g.contained(("ecoinvent", "BALTSO"))
        assert "LT" in g.contained(("ecoinvent", "BALTSO"))
        assert "RoW" in g.contained("GLO")


def test_row_contextmanager_within():
    g_orig = Geomatcher()
    with resolved_row(["NO", "LT", "EE"], g_orig) as g:
        assert g.within("RoW") == ["GLO", "RoW"]
        assert g.within("RoW", biggest_first=False) == ["RoW", "GLO"]


def test_backwards_compatibility():
    cg = ConstructiveGeometries()
    assert "SPP" not in cg.locations
    assert "SPP" not in cg.data

    assert "Europe, without Russia and Turkey" not in cg.locations
    assert "Europe, without Russia and Turkey" not in cg.data
    assert "Europe, without Russia and Türkiye" in cg.locations
    assert "Europe, without Russia and Türkiye" in cg.data

    cg = ConstructiveGeometries(backwards_compatible=True)
    assert "SPP" in cg.locations
    assert "SPP" in cg.data
    assert cg.data["SERC"] == cg.data["US-SERC"]

    assert "Europe, without Russia and Turkey" in cg.locations
    assert "Europe, without Russia and Turkey" in cg.data
    assert "Europe, without Russia and Türkiye" in cg.locations
    assert "Europe, without Russia and Türkiye" in cg.data

    g = Geomatcher()
    assert ("ecoinvent", "SPP") not in g

    g = Geomatcher(backwards_compatible=True)
    assert ("ecoinvent", "SPP") in g
