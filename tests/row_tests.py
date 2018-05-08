from constructive_geometries import distinguish_RoWs
from brightway2 import Database, projects, get_activity
import os
import pytest

@pytest.fixture(scope='function') # Tear down database after every test
def animals_db(tmpdir):
    #Setup
    animal_data = {
        ('animals', 'food'): {
            'name': 'food',
            'exchanges': [
                {
                    'amount': 1.0,
                    'input': ('animals', 'food'),
                    'type': 'production'
                }
            ],
            'unit': 'kilogram',
            'location': 'GLO',
        },
        ('animals', 'german_shepherd'): {
            'name': 'dogs',
            'exchanges': [
                {
                    'amount': 1.0,
                    'input': ('animals', 'food'),
                    'type': 'technosphere'
                },
                {
                    'amount': 1.0,
                    'input': ('animals', 'german_shepherd'),
                    'type': 'production'
                },
            ],
            'unit': 'kilogram',
            'location': 'DE',
        },
        ('animals', 'pug'): {
            'name': 'dogs',
            'exchanges': [
                {
                    'amount': 1.0,
                    'input': ('animals', 'food'),
                    'type': 'technosphere'
                },
                {
                    'amount': 1.0,
                    'input': ('animals', 'pug'),
                    'type': 'production'
                },
            ],
            'unit': 'kilogram',
            'location': 'CN',
        },
        ('animals', 'mutt'): {
            'name': 'dogs',
            'exchanges': [
                {
                    'amount': 1.0,
                    'input': ('db', 'food'),
                    'type': 'technosphere'
                },
                {
                    'amount': 1.0,
                    'input': ('animals', 'mutt'),
                    'type': 'production'
                },
            ],
            'unit': 'kilogram',
            'location': 'ROW',
        },
        ('animals', 'persian'): {
            'name': 'cats',
            'exchanges': [
                {
                    'amount': 1.0,
                    'input': ('animals', 'food'),
                    'type': 'technosphere'
                },
                {
                    'amount': 1.0,
                    'input': ('animals', 'persian'),
                    'type': 'production'
                },
            ],
            'unit': 'kilogram',
            'location': 'IR',
        },
        ('animals', 'moggy'): {
            'name': 'cats',
            'exchanges': [
                {
                    'amount': 1.0,
                    'input': ('animals', 'food'),
                    'type': 'technosphere'
                },
                {
                    'amount': 1.0,
                    'input': ('animals', 'moggy'),
                    'type': 'production'
                },
            ],
            'unit': 'kilogram',
            'location': 'ROW',
        },
    }
    dirpath = str(tmpdir)
    os.environ["BRIGHTWAY2_DIR"] = dirpath

    projects.set_current('test')
    db = Database('animals')
    db.write(animal_data)

    yield

    #teardown
    #db.delete()
    #db.deregister()
    #projects.delete_project(delete_dir=True)
    del os.environ["BRIGHTWAY2_DIR"]
    return None

def test_RoW_db_has_same_structure(animals_db):
    db = Database('animals')
    original_length = len(db)
    original_loaded_db = db.load()

    _, _ = distinguish_RoWs('animals', modify_db_in_place=True)

    # Modification of database hasn't changed its size
    assert len(db) == original_length

    loaded_db = db.load()
    # The keys of the datasets have not changed
    assert set([*original_loaded_db]) == set([*loaded_db])

def test_RoW_dict(animals_db):
    RoW_dict, RoW_act_mapping = distinguish_RoWs('animals', modify_db_in_place=True)
    mutt_act = get_activity(('animals', 'mutt'))
    moggy_act = get_activity(('animals', 'moggy'))
    mutt_location = mutt_act['location']
    moggy_location = moggy_act['location']

    assert mutt_location[0:3] == 'ROW'
    assert moggy_location[0:3] == 'ROW'
    assert len(mutt_location) == 5
    assert len(moggy_location) == 5
    assert mutt_location in RoW_dict.keys()
    assert moggy_location in RoW_dict.keys()
    assert sorted(RoW_dict[mutt_location]) == ['CN', 'DE']
    assert RoW_dict[moggy_location] == ['IR']
    assert RoW_act_mapping[mutt_act.key] == mutt_location
    assert RoW_act_mapping[moggy_act.key] == moggy_location