# Hack Computer Capstone — K = 93

**Project:** Make the Computer Draw a Box  
**Course:** Computer Architecture / Nand2Tetris  
**Personal number:** `K = 93`

This repository contains the three assignment parts: Hack HDL computer chips, a Python two-pass assembler, and the K-specific keyboard-controlled box program.

## K-specific requirements

| Requirement | Calculation | Value |
|---|---:|---:|
| Extra assembler feature | `93 mod 3 = 1` | Invalid instruction reports its physical source line and exits cleanly |
| Box starting row | `K` | 93 |
| Box height | Fixed by assignment | 20 rows |
| Box width | `16 × ((K mod 4) + 1)` | 64 pixels |
| Horizontal start | Left edge (assignment wording) | 0 pixels from left |

The box occupies screen row 93 through row 110. It spans x=0 through x=63 (inclusive). On each row, the four affected screen words are all `0xFFFF`.

## Folder structure

```text
Hack-Computer-Capstone-K93/
├── Part-A-Computer/
│   ├── CPU.hdl
│   ├── Memory.hdl
│   └── Computer.hdl
├── Part-B-Assembler/
│   ├── assembler.py
│   ├── symbols.json
│   └── programs/
│       ├── Add.asm / Add.hack
│       ├── Max.asm / Max.hack
│       ├── Rect.asm / Rect.hack
│       └── Pong.asm / Pong.hack
├── Part-C-Box-Program/
│   ├── generate_box.py
│   ├── Box.asm
│   ├── Box.hack
│   └── emulator.py
├── tests/test_project.py
└── Documentation/
    ├── Project-Report.docx
    └── Viva-Quick-Notes.md
```

## Requirements

- Python 3.10 or newer
- Nand2Tetris Software Suite (Hardware Simulator and CPU Emulator) for Part A validation and the official screenshot workflow
- Tkinter for the optional Python emulator window (usually included with standard desktop Python installations)

No third-party Python packages are required for the assembler, generator, emulator, or tests.

## Run Part B — Python assembler

From the project root:

```bash
python Part-B-Assembler/assembler.py Part-B-Assembler/programs/Add.asm --k 93
python Part-B-Assembler/assembler.py Part-B-Assembler/programs/Max.asm --k 93
python Part-B-Assembler/assembler.py Part-B-Assembler/programs/Rect.asm --k 93
python Part-B-Assembler/assembler.py Part-B-Assembler/programs/Pong.asm --k 93
```

The assembler writes a `.hack` file beside each `.asm` file. To choose an output path and save a symbol table:

```bash
python Part-B-Assembler/assembler.py Part-C-Box-Program/Box.asm \
  -o Part-C-Box-Program/Box.hack --k 93 \
  --symbols Part-B-Assembler/symbols.json
```

### Assembler design

1. **Preprocessing:** strips `//` comments and blank lines while preserving physical line numbers.
2. **Pass 1:** records labels and their ROM addresses; duplicate/reserved labels are rejected.
3. **Pass 2:** converts A- and C-instructions into 16-bit binary. New variables receive RAM addresses starting at 16.
4. **K=93 feature:** invalid instructions print a readable message containing the original source line number instead of an uncaught exception.

## Run Part C — generate and execute the box

Regenerate the program for K=93:

```bash
python Part-C-Box-Program/generate_box.py --k 93
python Part-B-Assembler/assembler.py Part-C-Box-Program/Box.asm \
  -o Part-C-Box-Program/Box.hack --k 93
```

Open the interactive Python emulator:

```bash
python Part-C-Box-Program/emulator.py Part-C-Box-Program/Box.hack --gui
```

Hold any key in the emulator window to draw the black box; release it to erase the box. The emulator displays the 512×256 Hack screen.

Headless smoke test (simulates a held key):

```bash
python Part-C-Box-Program/emulator.py Part-C-Box-Program/Box.hack --key --steps 5000
```

## Run automated tests

```bash
python -m unittest discover -s tests -v
```

The included tests cover A-instruction encoding, labels and variables, duplicate labels, line-numbered invalid-instruction errors, and drawing/erasing the K=93 box in the emulator.

## Part A — HDL validation

Open `Part-A-Computer/` in the Nand2Tetris Hardware Simulator. Run the course-provided official tests for `CPU.hdl`, `Memory.hdl`, and `Computer.hdl` (CPU.tst, Memory.tst, ComputerAdd.tst, ComputerMax.tst, ComputerRect.tst, and ComputerPong.tst, as applicable to the lab package). Capture the simulator output for the report. The official `.tst` and `.cmp` files are course-provided test assets and are intentionally not fabricated or substituted here.

The HDL uses standard Nand2Tetris built-in chips such as `ALU`, `ARegister`, `DRegister`, `PC`, `RAM16K`, `Screen`, `Keyboard`, and `ROM32K`.

## Report and screenshots

`Documentation/Project-Report.docx` contains the written report and clearly marked spaces for:

- CPU / Memory / Computer official Hardware Simulator test results
- Python assembler output
- Box program running in the CPU Emulator
- One short paragraph describing a mistake fixed during development

Insert your own screenshots from the actual simulator/emulator session before submission. Do not present the screenshot placeholders as test evidence.

## Important submission checklist

- [ ] Replace the cover-page student name and roll number with your details.
- [ ] Run the official Part A test files provided by the course and capture the results.
- [ ] Run all four assembler examples and keep their `.hack` outputs.
- [ ] Run the Box program in the CPU Emulator and capture the visible box.
- [ ] Add one paragraph about a real mistake you fixed.
- [ ] Upload the complete folder to the required GitHub capstone folder.
- [ ] Submit the short report on ZOSIMA.

---

**Testing note:** The included Python test suite was run successfully while packaging this project. The HDL files are supplied for validation in the official Nand2Tetris Hardware Simulator; that external simulator was not available in this packaging environment, so no claim is made that its official HDL tests have already passed.
