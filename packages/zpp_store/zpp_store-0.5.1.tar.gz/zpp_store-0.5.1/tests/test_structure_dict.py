import pytest
import zpp_store

@pytest.fixture
def sample_data_store():
    data = {"a": {"b": 2, "c": {"d": 44}}, "e": [1, {"f": 5}, 3]}
    return zpp_store.structure(data)

def test_get_method(sample_data_store):
    # Test basic get
    assert sample_data_store.get('a.b') == 2
    # Test nested get
    assert sample_data_store.get('a.c.d') == 44
    # Test list access
    assert sample_data_store.get('e.0') == 1
    assert sample_data_store.get('e.1.f') == 5
    # Test non-existent path
    assert sample_data_store.get('x.y.z') is None
    # Test non-existent path with default
    assert sample_data_store.get('x.y.z', default='not_found') == 'not_found'
    # Test intermediate non-existent path
    assert sample_data_store.get('a.x.y', default='not_found') == 'not_found'

def test_set_method(sample_data_store):
    # Test basic set
    sample_data_store.set('a.b', 20)
    assert sample_data_store.a.b == 20
    # Test nested set (creating new intermediate DataStore objects)
    sample_data_store.set('new.path.value', 100)
    assert sample_data_store.new.path.value == 100
    # Test overwriting existing value
    sample_data_store.set('a.c.d', 50)
    assert sample_data_store.a.c.d == 50
    # Test setting in a list
    sample_data_store.set('e.0', 10)
    assert sample_data_store.e[0] == 10
    sample_data_store.set('e.1.f', 50)
    assert sample_data_store.e[1].f == 50
    # Test setting a new list item (requires existing list)
    sample_data_store.e.append(99)
    sample_data_store.set('e.3', 999)
    assert sample_data_store.e[3] == 999

def test_pop_method(sample_data_store):
    # Test basic pop
    assert sample_data_store.pop('a.b') == 2
    assert sample_data_store.get('a.b', None)==None
    # Test nested pop
    assert sample_data_store.pop('a.c.d') == 44
    assert sample_data_store.get('a.c.d', None)==None

def test_delete_method(sample_data_store):
    # Test basic delete (attribute)
    sample_data_store.delete('a.b')
    assert sample_data_store.get('a.b', None)==None
    # Test nested delete (attribute)
    sample_data_store.delete('a.c.d')
    assert sample_data_store.get('a.c.d', None)==None

def test_clear_method(sample_data_store):
    sample_data_store.clear()
    assert sample_data_store.__dict__ == {}
    assert sample_data_store.get('a.b') is None

def test_del_operator(sample_data_store):
    # Test del with attribute access
    del sample_data_store.a.b
    assert sample_data_store.get('a.b', None)==None
    # Test del with item access
    del sample_data_store['a']['c']['d']
    assert sample_data_store.get('a.c.d', None)==None


def test_dict_like_access(sample_data_store):
    # Test __getitem__
    assert sample_data_store['a']['b'] == 2
    assert sample_data_store['a']['c']['d'] == 44
    assert sample_data_store['e'][0] == 1
    assert sample_data_store['e'][1]['f'] == 5
    with pytest.raises(KeyError):
        _ = sample_data_store['non_existent']
    # Test __setitem__
    sample_data_store['a']['b'] = 200
    assert sample_data_store.a.b == 200
    sample_data_store['new_key'] = 'new_value'
    assert sample_data_store.new_key == 'new_value'
    # Test __delitem__
    del sample_data_store['a']['b']
    assert "b" in sample_data_store['a']
