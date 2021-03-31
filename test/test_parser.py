import textwrap

import pytest

from armaclass import parse, ParseError


# We're not really deleting anything, just acknowledging the command to delete an object
def test_delete():
    expected = {'Foo': {}}
    result = parse(
        'class Foo {\r\ndelete Moo; };')
    assert result == expected


# We're not really importing anything, just acknowledging the command to delete an object
def test_import():
    expected = {'Foo': {}}
    result = parse(
        'import bar;\n'
        'class Foo {\r\nimport Moo; //Not sure if valid here but whatever\n };')
    assert result == expected


def test_ignore_newlines():
    expected = {
        'value1': 1,
        'value2': 2,
        'value3': 3,
        'value4': 4,
    }
    result = parse('value1 = 1;\r\nvalue2 = 2;\rvalue3 = 3;\nvalue4 = 4;')
    assert result == expected


def test_integer_property():
    expected = {
        'Moo': {
            'value': 1
        }
    }
    result = parse('''
        class Moo {
            value=1;
        };
    ''')
    assert result == expected


def test_more_than_one_value_in_file():
    expected = {
        'version': 12,
        'Moo': {
            'value': 1
        }
    }
    result = parse('''
        version=12;

        class Moo  {
            value = 1;
        };
    ''')
    assert result == expected


def test_nested_arrays():
    expected = {
        'Moo': {
            'foo': [[], ['foo'], [1, 2]]
        }
    }
    result = parse('''
        class Moo {
            foo[]={{}, {"foo"}, {1, 2}};
        };
    ''')
    assert result == expected


def test_array_of_scalars():
    expected = {
        'Moo': {
            'foo': ['bar', 'baz', 1.5e2]
        }
    }
    result = parse('''
        class Moo {
            foo[]={"bar", "baz",1.5e2};
        };
    ''')
    assert result == expected


def test_scientific_notation_negative_exponent():
    assert parse('x=-1.5e2;') == {'x': -1.5e2}


def test_scientific_notation_positive_exponent():
    assert parse('x=1.5e2;') == {'x': 1.5e2}


def test_scientific_explicitly_positive_exponent():
    assert parse('x=+1.5e2;') == {'x': 1.5e2}


def test_scientific_notation_negative_exponent_with_zeroes():
    assert parse('x=-1.9073486e-006;') == {'x': -1.9073486e-6}


def test_plus_array():
    expected = {'Moo': {
        'foo': [1, 2, 3]
    }}
    result = parse('''
        class Moo {
            foo[] += {1,2,3};
        };
    ''')
    assert result == expected


def test_hanging_quote():
    with pytest.raises(ParseError, match=r'Got EOF'):
        parse('v="')


def test_ignore_inheritance():
    parsed_string = 'class Moo : foo {};'
    assert parse(parsed_string) == {'Moo': {}}


def test_line_comments():
    assert parse('// foo comment') == {}
    assert parse('// foo comment\nx=2;') == {'x': 2}
    assert parse('x=2;// foo comment') == {'x': 2}
    assert parse('class Moo { // foo comment\n};') == {'Moo': {}}


def test_slash_asterisk_comments():
    assert parse('/* foo comment*/') == {}
    assert parse('/* foo comment\nsomething */x=2;') == {'x': 2}
    assert parse('x=2;/* foo comment*/') == {'x': 2}
    assert parse('x/*asd*/=/**/2;/* foo comment*/') == {'x': 2}
    assert parse('class Moo { /* foo comment*/};') == {'Moo': {}}


def test_multiline_comments():
    expected = {
        'testClass': {'values': [0, 1]}
    }
    to_parse = textwrap.dedent('''
        /*
        multiline
        comment
        */
        class testClass {
            values[] = {0,1};
        };
    ''')
    assert parse(to_parse) == expected


def test_quote_escaping_by_double_quote():
    assert parse('foo="bar ""haha"";";') == {'foo': 'bar "haha";'}


def test_sample():
    expected = {
        'Session': {
            'Player1': {
                'customScore': 0,
                'killed': 0,
                'killsAir': 0,
                'killsArmor': 0,
                'killsInfantry': 4,
                'killsPlayers': 0,
                'killsSoft': 0,
                'killsTotal': 4,
                'name': 'Lord DK'
            },
            'Player2': {
                'customScore': 0,
                'killed': 0,
                'killsAir': 0,
                'killsArmor': 0,
                'killsInfantry': 3,
                'killsPlayers': 0,
                'killsSoft': 0,
                'killsTotal': 3,
                'name': 'XiviD'
            },
            'Player3': {
                'customScore': 0,
                'killed': 0,
                'killsAir': 0,
                'killsArmor': 0,
                'killsInfantry': 2,
                'killsPlayers': 0,
                'killsSoft': 0,
                'killsTotal': 2,
                'name': '40mm2Die'
            },
            'Player4': {
                'customScore': 0,
                'killed': 0,
                'killsAir': 0,
                'killsArmor': 0,
                'killsInfantry': 4,
                'killsPlayers': 0,
                'killsSoft': 0,
                'killsTotal': 4,
                'name': 'WickerMan'
            },
            'Player5': {
                'customScore': 0,
                'killed': 1,
                'killsAir': 0,
                'killsArmor': 0,
                'killsInfantry': 3,
                'killsPlayers': 0,
                'killsSoft': -1,
                'killsTotal': 1,
                'name': 'Fusselwurm'
            },
            'Player6': {
                'customScore': 0,
                'killed': 0,
                'killsAir': 0,
                'killsArmor': 0,
                'killsInfantry': 0,
                'killsPlayers': 0,
                'killsSoft': 0,
                'killsTotal': 0,
                'name': 'Simmax'
            },
            'Player7': {
                'customScore': 0,
                'killed': 2,
                'killsAir': 0,
                'killsArmor': 0,
                'killsInfantry': 0,
                'killsPlayers': 0,
                'killsSoft': 0,
                'killsTotal': 0,
                'name': 'Andre'
            },
            'duration': 5821.1724,
            'gameType': 'Coop',
            'island': 'Altis',
            'mission': 'W-CO@10 StealBoot v03'
        }
    }
    result = parse('''
    class Session
    {
        mission="W-CO@10 StealBoot v03";
        island="Altis";
        gameType="Coop";
        duration=5821.1724;

        class Player1
        {
            name="Lord DK";
            killsInfantry=4;
            killsSoft=0;
            killsArmor=0;
            killsAir=0;
            killsPlayers=0;
            customScore=0;
            killsTotal=4;
            killed=0;
        };
        class Player2
        {
            name="XiviD";
            killsInfantry=3;
            killsSoft=0;
            killsArmor=0;
            killsAir=0;
            killsPlayers=0;
            customScore=0;
            killsTotal=3;
            killed=0;
        };
        class Player3
        {
            name="40mm2Die";
            killsInfantry=2;
            killsSoft=0;
            killsArmor=0;
            killsAir=0;
            killsPlayers=0;
            customScore=0;
            killsTotal=2;
            killed=0;
        };
        class Player4
        {
            name="WickerMan";
            killsInfantry=4;
            killsSoft=0;
            killsArmor=0;
            killsAir=0;
            killsPlayers=0;
            customScore=0;
            killsTotal=4;
            killed=0;
        };
        class Player5
        {
            name="Fusselwurm";
            killsInfantry=3;
            killsSoft=-1;
            killsArmor=0;
            killsAir=0;
            killsPlayers=0;
            customScore=0;
            killsTotal=1;
            killed=1;
        };
        class Player6
        {
            name="Simmax";
            killsInfantry=0;
            killsSoft=0;
            killsArmor=0;
            killsAir=0;
            killsPlayers=0;
            customScore=0;
            killsTotal=0;
            killed=0;
        };
        class Player7
        {
            name="Andre";
            killsInfantry=0;
            killsSoft=0;
            killsArmor=0;
            killsAir=0;
            killsPlayers=0;
            customScore=0;
            killsTotal=0;
            killed=2;
        };
    };
    ''')
    assert result == expected


def test_multiline_init():
    source = (
        r'class Item0 {'
        r'    position[]={1954.6425,5.9796591,5538.1045};'
        r'    id=0;'
        r'    init="[this, ""Platoon""] call FP_fnc_setVehicleName;" \n "if (isServer) then {" \n "  [this] call '
        r'FP_fnc_clearVehicle; this addWeaponCargoGlobal [""CUP_launch_M136"", 1];" \n "  this '
        r'addMagazineCargoGlobal [""1Rnd_HE_Grenade_shell"", 10];" \n "  this addMagazineCargoGlobal '
        r'[""ATMine_Range_Mag"", 6];" \n "};";'
        r'};'
    )

    result = parse(source)
    expected = {
        'Item0': {
            'position': [1954.6425, 5.9796591, 5538.1045],
            'id': 0,
            'init': textwrap.dedent('''\
                [this, "Platoon"] call FP_fnc_setVehicleName;
                if (isServer) then {
                  [this] call FP_fnc_clearVehicle; this addWeaponCargoGlobal ["CUP_launch_M136", 1];
                  this addMagazineCargoGlobal ["1Rnd_HE_Grenade_shell", 10];
                  this addMagazineCargoGlobal ["ATMine_Range_Mag", 6];
                };''')
        }
    }
    assert result == expected
