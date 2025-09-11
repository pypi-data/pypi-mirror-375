import pytest
from pymultimap.multimap import (
    MultiMap,
)


class TestMultiMap:
    def create_multi_map(self, sorted, reverse):
        # A fixture that creates and returns a sample MultiMap object
        md = MultiMap(sorted=sorted, reverse=reverse)
        md["a"] = 1
        md["a"] = 2
        md["b"] = 3
        return md

    @pytest.mark.parametrize("sorted", [True, False])
    @pytest.mark.parametrize("reverse", [True, False])
    def test_getitem(self, sorted, reverse):
        # A function that tests the __getitem__ method of the MultiMap class
        md = self.create_multi_map(sorted, reverse)
        assert md["a"] == [1, 2]  # Check if the key "a" returns the list [1, 2]
        assert md["b"] == [3]  # Check if the key "b" returns the list [3]
        with pytest.raises(KeyError):  # Check if a non-existent key raises a KeyError
            md["c"]

    @pytest.mark.parametrize("sorted", [True, False])
    @pytest.mark.parametrize("reverse", [True, False])
    def test_setitem(self, sorted, reverse):
        # A function that tests the __setitem__ method of the MultiMap class
        md = self.create_multi_map(sorted, reverse)
        md["c"] = 4  # Add a new key-value pair to the MultiMap object
        assert md["c"] == [4]  # Check if the key "c" returns the list [4]
        md["a"] = 5  # Add another value to the existing key "a"
        assert md["a"] == [1, 2, 5]  # Check if the key "a" returns the list [1, 2, 5]


class TestMultiMapSorted:
    def create_sorted_multi_map(self, reverse):
        # A fixture that creates and returns a sample MultiMap object
        md = MultiMap(sorted=True, reverse=reverse)
        md[1] = "a"
        md[3] = "c"
        md[2] = "b"
        return md

    @pytest.mark.parametrize("reverse", [True, False])
    def test_getitem(self, reverse):
        # A function that tests the __getitem__ method of the MultiMap class
        md = self.create_sorted_multi_map(reverse)
        keys = list(md.keys())
        assert keys == [3, 2, 1] if reverse else [1, 2, 3]

        values = list(md.values())
        assert values == [["c"], ["b"], ["a"]] if reverse else [["a"], ["b"], ["c"]]

    @pytest.mark.parametrize("reverse", [True, False])
    def test_setitem(self, reverse):
        # A function that tests the __setitem__ method of the MultiMap class
        md = self.create_sorted_multi_map(reverse)
        md[5] = "e"
        md[4] = "d"
        assert md[3] == ["c"]
        md[1] = "aa"
        assert md[1] == ["a", "aa"]
        keys = list(md.keys())
        assert keys == [5, 4, 3, 2, 1] if reverse else [1, 2, 3, 4, 5]
