import contextlib
import io
import logging
import os
import tempfile

import pytest

import csa_lab3.machine
import csa_lab3.translator


@pytest.mark.golden_test("golden/*.yml")
def test_translator_asm_and_machine(golden, caplog):
    caplog.set_level(logging.DEBUG)

    with tempfile.TemporaryDirectory() as tmpdir:
        source_file = os.path.join(tmpdir, "source.masm")
        input_stream = os.path.join(tmpdir, "input.txt")
        target_file = os.path.join(tmpdir, "source.json")

        with open(source_file, "w", encoding="utf-8") as file:
            file.write(golden["in_source"])

        with open(input_stream, "w", encoding="utf-8") as file:
            file.write(golden["in_stdin"])

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            csa_lab3.translator.main(source_file, target_file)
            csa_lab3.machine.main(target_file, input_stream)

        with open(target_file, encoding="utf-8") as file:
            code = file.read()

        assert code == golden.out["out_code"]
        assert stdout.getvalue() == golden.out["out_stdout"]
        assert caplog.text == golden.out["out_log"]
