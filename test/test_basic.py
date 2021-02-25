import textwrap
import unittest

from armaclass import parse


class TestArmaClass(unittest.TestCase):

    def test_empty(self):
        expected = {'Moo': {}}
        result = parse('class Moo {};')
        self.assertEqual(result, expected)

    def test_delete(self):
        expected = {'Moo': {}}
        result = parse(
            'class Moo {\r\ndelete Moo; };')
        self.assertEqual(result, expected)

    def test_integer_property(self):
        expected = {
            'Moo': {
                'value': 1
            }
        }
        result = parse('class Moo {\r\nvalue=1; };')
        self.assertEqual(result, expected)

    def test_more_than_one_value_in_file(self):
        expected = {
            'version': 12,
            'Moo': {
                'value': 1
            }
        }
        result = parse('version=12;\n\nclass Moo  {\r\n value = 1; };')
        self.assertEqual(result, expected)

    def test_array_of_scalars(self):
        expected = {
            'Moo': {
                'foo': ['bar', 'baz', 1.5e2]
            }
        }
        result = parse('class Moo {\r\nfoo[]={"bar", "baz",1.5e2}; };')
        self.assertEqual(result, expected)

    def test_scientific_notation(self):
        self.assertEqual(parse('x=-1.5e2;'), {'x': -1.5e2})

    def test_plus_array(self):
        expected = {'Moo': {
            'foo': [1, 2, 3]
        }}
        result = parse(
            'class Moo {\r\nfoo[] += {1,2,3}; };')
        self.assertEqual(result, expected)

    # def test_simple_arithmetic(self):
    #     self.assertEqual(parse('x=48+0x800;'), {'x': 48 + 0x800})

    def test_ignore_symbols(self):
        testString = ("class Moo {\n"
                      "\tfoo = xxx;\n"
                      "\tclass xxx {};\n"
                      "};"
                      )
        with self.assertRaises(RuntimeError):
            parse(testString)

    def test_ignore_inheritance(self):
        testString = 'class Moo : foo {};'
        self.assertEqual(parse(testString), {'Moo': {}})

    def test_line_comments(self):
        self.assertEqual(parse('// foo comment'), {})
        self.assertEqual(parse('// foo comment\nx=2;'), {'x': 2})
        self.assertEqual(parse('x=2;// foo comment'), {'x': 2})
        self.assertEqual(parse('class Moo { // foo comment\n};'), {'Moo': {}})

    def test_multiline_comments(self):
        self.assertEqual(parse("/* foo comment*/"), {})
        self.assertEqual(parse("/* foo comment\nsomething */x=2;"), {'x': 2})
        self.assertEqual(parse("x=2;/* foo comment*/"), {'x': 2})
        self.assertEqual(parse("x/*asd*/=/**/2;/* foo comment*/"), {'x': 2})
        self.assertEqual(parse("class Moo { /* foo comment*/};"), {'Moo': {}})

    def test_quote_escaping_by_double_quote(self):
        self.assertEqual(parse('foo="bar ""haha"";";\n'),
                         {'foo': 'bar "haha";'})

    def test_sample(self):
        expected = {
            "Session": {
                "Player1": {
                    "customScore": 0,
                    "killed": 0,
                    "killsAir": 0,
                    "killsArmor": 0,
                    "killsInfantry": 4,
                    "killsPlayers": 0,
                    "killsSoft": 0,
                    "killsTotal": 4,
                    "name": "Lord DK"
                },
                "Player2": {
                    "customScore": 0,
                    "killed": 0,
                    "killsAir": 0,
                    "killsArmor": 0,
                    "killsInfantry": 3,
                    "killsPlayers": 0,
                    "killsSoft": 0,
                    "killsTotal": 3,
                    "name": "XiviD"
                },
                "Player3": {
                    "customScore": 0,
                    "killed": 0,
                    "killsAir": 0,
                    "killsArmor": 0,
                    "killsInfantry": 2,
                    "killsPlayers": 0,
                    "killsSoft": 0,
                    "killsTotal": 2,
                    "name": "40mm2Die"
                },
                "Player4": {
                    "customScore": 0,
                    "killed": 0,
                    "killsAir": 0,
                    "killsArmor": 0,
                    "killsInfantry": 4,
                    "killsPlayers": 0,
                    "killsSoft": 0,
                    "killsTotal": 4,
                    "name": "WickerMan"
                },
                "Player5": {
                    "customScore": 0,
                    "killed": 1,
                    "killsAir": 0,
                    "killsArmor": 0,
                    "killsInfantry": 3,
                    "killsPlayers": 0,
                    "killsSoft": -1,
                    "killsTotal": 1,
                    "name": "Fusselwurm"
                },
                "Player6": {
                    "customScore": 0,
                    "killed": 0,
                    "killsAir": 0,
                    "killsArmor": 0,
                    "killsInfantry": 0,
                    "killsPlayers": 0,
                    "killsSoft": 0,
                    "killsTotal": 0,
                    "name": "Simmax"
                },
                "Player7": {
                    "customScore": 0,
                    "killed": 2,
                    "killsAir": 0,
                    "killsArmor": 0,
                    "killsInfantry": 0,
                    "killsPlayers": 0,
                    "killsSoft": 0,
                    "killsTotal": 0,
                    "name": "Andre"
                },
                "duration": 5821.1724,
                "gameType": "Coop",
                "island": "Altis",
                "mission": "W-CO@10 StealBoot v03"
            }
        }
        result = parse("\n\tclass Session\n\t{\n\tmission=\"W-CO@10 StealBoot v03\";\n\tisland=\"Altis\";\n\t" +
                       "gameType=\"Coop\";\n\tduration=5821.1724;\n\tclass Player1\n\t{\n\tname=\"Lord DK\";\n\tkillsInfantry=4;\n\t" +
                       "killsSoft=0;\n\tkillsArmor=0;\n\tkillsAir=0;\n\tkillsPlayers=0;\n\tcustomScore=0;\n\tkillsTotal=4;\n\tkilled=0;" +
                       "\n\t};\n\tclass Player2\n\t{\n\tname=\"XiviD\";\n\tkillsInfantry=3;\n\tkillsSoft=0;\n\tkillsArmor=0;\n\tkillsAir=0;" +
                       "\n\tkillsPlayers=0;\n\tcustomScore=0;\n\tkillsTotal=3;\n\tkilled=0;\n\t};\n\t" +
                       "class Player3\n\t{\n\tname=\"40mm2Die\";\n\tkillsInfantry=2;\n\tkillsSoft=0;\n\tkillsArmor=0;\n\tkillsAir=0;" +
                       "\n\tkillsPlayers=0;\n\tcustomScore=0;\n\tkillsTotal=2;\n\tkilled=0;\n\t};\n\t" +
                       "class Player4\n\t{\n\tname=\"WickerMan\";\n\tkillsInfantry=4;\n\tkillsSoft=0;\n\tkillsArmor=0;\n\tkillsAir=0;" +
                       "\n\tkillsPlayers=0;\n\tcustomScore=0;\n\tkillsTotal=4;\n\tkilled=0;\n\t};\n\t" +
                       "class Player5\n\t{\n\tname=\"Fusselwurm\";\n\tkillsInfantry=3;\n\tkillsSoft=-1;\n\tkillsArmor=0;\n\tkillsAir=0;" +
                       "\n\tkillsPlayers=0;\n\tcustomScore=0;\n\tkillsTotal=1;\n\tkilled=1;\n\t};\n\t" +
                       "class Player6\n\t{\n\tname=\"Simmax\";\n\tkillsInfantry=0;\n\tkillsSoft=0;\n\tkillsArmor=0;\n\tkillsAir=0;" +
                       "\n\tkillsPlayers=0;\n\tcustomScore=0;\n\tkillsTotal=0;\n\tkilled=0;\n\t};\n\t" +
                       "class Player7\n\t{\n\tname=\"Andre\";\n\tkillsInfantry=0;\n\tkillsSoft=0;\n\tkillsArmor=0;\n\tkillsAir=0;" +
                       "\n\tkillsPlayers=0;\n\tcustomScore=0;\n\tkillsTotal=0;\n\tkilled=2;\n\t};\n\t};\n\n\t")
        self.assertEqual(result, expected)

    def test_multiline_init(self):
        source = textwrap.dedent(r'''
            class Item0 {
                position[]={1954.6425,5.9796591,5538.1045};
                id=0;
                init="[this, ""Platoon""] call FP_fnc_setVehicleName;" \n "if (isServer) then {" \n "  [this] call FP_fnc_clearVehicle; this addWeaponCargoGlobal [""CUP_launch_M136"", 1];" \n "  this addMagazineCargoGlobal [""1Rnd_HE_Grenade_shell"", 10];" \n "  this addMagazineCargoGlobal [""ATMine_Range_Mag"", 6];" \n "};";
            };
        ''')

        result = parse(source)
        expected = {
            'Item0': {
                'position': [1954.6425, 5.9796591, 5538.1045],
                'id': 0,
                'init': '[this, "Platoon"] call FP_fnc_setVehicleName;\nif (isServer) then {\n  [this] call FP_fnc_clearVehicle; this addWeaponCargoGlobal ["CUP_launch_M136", 1];\n  this addMagazineCargoGlobal ["1Rnd_HE_Grenade_shell", 10];\n  this addMagazineCargoGlobal ["ATMine_Range_Mag", 6];\n};'
            }
        }
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
