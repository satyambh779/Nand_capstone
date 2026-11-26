import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Part-B-Assembler'))
sys.path.insert(0, str(ROOT / 'Part-C-Box-Program'))
from assembler import assemble_text, AssemblyError
from emulator import HackMachine

class AssemblerTests(unittest.TestCase):
    def test_a_instruction(self):
        code, _ = assemble_text('@21\n')
        self.assertEqual(code, [format(21, '016b')])

    def test_label_and_variable(self):
        code, symbols = assemble_text('(START)\n@i\nM=1\n@START\n0;JMP\n')
        self.assertEqual(symbols['START'], 0)
        self.assertEqual(symbols['i'], 16)
        self.assertEqual(len(code), 4)

    def test_invalid_instruction_has_physical_line(self):
        with self.assertRaises(AssemblyError) as ctx:
            assemble_text('// comment\n@0\nD=NOT_A_COMP\n')
        self.assertIn('Line 3:', str(ctx.exception))

    def test_duplicate_label_warning_as_error(self):
        with self.assertRaises(AssemblyError):
            assemble_text('(LOOP)\n@0\n(LOOP)\n')

class BoxExecutionTests(unittest.TestCase):
    def test_k93_box_draws_and_erases(self):
        hack = ROOT / 'Part-C-Box-Program' / 'Box.hack'
        machine = HackMachine(hack.read_text().splitlines())
        machine.keyboard = 1
        machine.run(5000)
        # K=93: screen row 93, from the left edge, 4 full words per row.
        start = 16384 + 32 * 93
        expected = [0xFFFF] * 4
        for row in range(20):
            self.assertEqual(machine.ram[start + row * 32:start + row * 32 + 4], expected)
        machine.keyboard = 0
        machine.run(5000)
        for row in range(20):
            self.assertEqual(machine.ram[start + row * 32:start + row * 32 + 4], [0] * 4)

if __name__ == '__main__':
    unittest.main(verbosity=2)
