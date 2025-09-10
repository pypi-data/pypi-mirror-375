import pytest

from int3 import Architectures, Int3CodeGenerationError, MemoryOperand, Platform, Triple


def test_triple_insn_factory():
    x86_64 = Architectures.x86_64.value
    Mips = Architectures.Mips.value

    linux_x86_64 = Triple(x86_64, Platform.Linux)
    linux_mips = Triple(Mips, Platform.Linux)

    # x86_64 tests
    # ~~~~~~~~~~~~
    insns = linux_x86_64.insns(
        "\n".join(
            [
                "pop rdx",
                "syscall",
                "add rax, r15",
                "lea rdi, [rip+0x100]",
                "mov byte ptr [rax], 0x1",
                "call qword ptr [rsp-0x10]",
            ]
        )
    )
    assert len(insns) == 6

    # pop rdx
    assert insns[0].mnemonic == "pop"
    assert insns[0].is_pop()
    assert insns[0].op_str == "rdx"
    assert len(insns[0].operands) == 1
    assert insns[0].operands.is_reg(0)
    assert not insns[0].operands.is_imm(0)
    assert insns[0].operands.reg(0) == x86_64.reg("rdx")
    assert insns[0].operands.token(0) == "rdx"

    # syscall
    assert insns[1].mnemonic == "syscall"
    assert insns[1].is_syscall()
    assert insns[1].op_str == ""
    assert len(insns[1].operands) == 0

    # add rax, r15
    assert insns[2].mnemonic == "add"
    assert insns[2].is_add()
    assert insns[2].op_str == "rax, r15"
    assert len(insns[2].operands) == 2
    assert insns[2].operands.is_reg(0)
    assert insns[2].operands.is_reg(1)
    assert insns[2].operands.reg(0) == x86_64.reg("rax")
    assert insns[2].operands.reg(1) == x86_64.reg("r15")
    assert insns[2].operands.token(0) == "rax"
    assert insns[2].operands.token(1) == "r15"

    # lea rdi, [rip+0x100]
    assert insns[3].mnemonic == "lea"
    assert insns[3].is_mov()
    assert insns[3].op_str == "rdi, [rip + 0x100]"
    assert len(insns[3].operands) == 2
    assert insns[3].operands.is_reg(0)
    assert insns[3].operands.reg(0) == x86_64.reg("rdi")
    assert insns[3].operands.is_mem(1)
    assert insns[3].operands.mem(1) == MemoryOperand(x86_64.reg("rip"), 0x100)
    assert insns[3].operands.token(0) == "rdi"
    assert insns[3].operands.token(1) == "[rip + 0x100]"

    # mov byte ptr [rax], 0x1
    assert insns[4].mnemonic == "mov"
    assert insns[4].is_mov()
    assert len(insns[4].operands) == 2
    assert insns[4].operands.mem(0) == MemoryOperand(x86_64.reg("rax"), 0, "byte ptr")
    assert insns[4].operands.imm(1) == 1
    assert insns[4].operands.token(0) == "byte ptr [rax]"
    assert insns[4].operands.token(1) == "1"

    # call qword ptr [rsp-0x10]
    assert insns[5].mnemonic == "call"
    assert insns[5].is_call()
    assert len(insns[5].operands) == 1
    assert insns[5].operands.is_mem(0)
    assert insns[5].operands.mem(0) == MemoryOperand(
        x86_64.reg("rsp"), -0x10, "qword ptr"
    )
    assert insns[5].operands.token(0) == "qword ptr [rsp - 0x10]"

    # Mips tests
    # ~~~~~~~~~~
    insns = linux_mips.insns(
        "\n".join(
            [
                "lui $v0, 0xcafe",
                "ori $v0, $v0, 0xbeef",
                "add $a0, $zero, $v1",
                "syscall",
            ]
        )
    )
    assert len(insns) == 4

    # lui $v0, 0xcafe
    assert insns[0].mnemonic == "lui"
    assert insns[0].is_mov()
    assert len(insns[0].operands) == 2
    assert insns[0].operands.reg(0) == Mips.reg("v0")
    assert insns[0].operands.imm(1) == 0xCAFE

    # ori $v0, $v0, 0xbeef
    assert insns[1].mnemonic == "ori"
    assert insns[1].is_or()
    assert len(insns[1].operands) == 3
    assert insns[1].operands.reg(0) == Mips.reg("v0")
    assert insns[1].operands.reg(1) == Mips.reg("v0")
    assert insns[1].operands.imm(2) == 0xBEEF

    # add $a0, $zero, $v1
    assert insns[2].mnemonic == "add"
    assert insns[2].is_add()
    assert len(insns[2].operands) == 3
    assert insns[2].operands.reg(0) == Mips.reg("a0")
    assert insns[2].operands.reg(1) == Mips.reg("zero")
    assert insns[2].operands.reg(2) == Mips.reg("v1")

    # syscall
    assert insns[3].mnemonic == "syscall"
    assert insns[3].is_syscall()
    assert insns[3].op_str == ""
    assert len(insns[3].operands) == 0


def test_access_operand_out_of_bounds():
    linux_x86_64 = Triple(Architectures.x86_64.value, Platform.Linux)

    insn = linux_x86_64.one_insn_or_raise("mov eax, 123")
    with pytest.raises(Int3CodeGenerationError):
        insn.operands.replace(2, 0xBEEF)

    insn = linux_x86_64.one_insn_or_raise("syscall")
    with pytest.raises(Int3CodeGenerationError):
        insn.operands.reg(0)
    with pytest.raises(Int3CodeGenerationError):
        insn.operands.imm(-1)


def test_access_operand_via_negative_index():
    x86_64 = Architectures.x86_64.value
    linux_x86_64 = Triple(x86_64, Platform.Linux)

    insn = linux_x86_64.one_insn_or_raise("xor rax, rbx")
    assert insn.operands.reg(-1) == x86_64.reg("rbx")
    assert insn.operands.reg(-2) == x86_64.reg("rax")

    with pytest.raises(Int3CodeGenerationError):
        insn.operands.token(-3)


def test_patch_immediates_and_registers():
    x86_64 = Architectures.x86_64.value
    Mips = Architectures.Mips.value

    linux_x86_64 = Triple(x86_64, Platform.Linux)
    linux_mips = Triple(Mips, Platform.Linux)

    insn = linux_x86_64.one_insn_or_raise("add rax, rcx")
    insn = insn.operands.replace(-1, 0xBEEF)
    assert str(insn).startswith("add rax, 0xbeef")

    insn = linux_mips.one_insn_or_raise("xor $a0, $v0, $zero")
    insn = insn.operands.replace(1, "t9")
    assert str(insn).startswith("xor $a0, $t9, $zero")


def test_patch_memory_operand():
    x86_64 = Architectures.x86_64.value
    linux_x86_64 = Triple(x86_64, Platform.Linux)

    insn = linux_x86_64.one_insn_or_raise("mov dword ptr [ebx], 0xbeef")
    insn = insn.operands.replace(0, MemoryOperand(x86_64.reg("rax"), 0x64, "qword ptr"))
    insn = insn.operands.replace(-1, 0xDEAD)
    assert str(insn).startswith("mov qword ptr [rax + 0x64], 0xdead")


def test_memory_operand_str():
    x86_64 = Architectures.x86_64.value
    rax = x86_64.reg("rax")

    assert str(MemoryOperand(rax, 100)) == "[rax + 100]"
    assert str(MemoryOperand(rax, 0)) == "[rax]"
    assert str(MemoryOperand(rax, -200)) == "[rax - 200]"
    assert str(MemoryOperand(rax, 1, "byte ptr")) == "byte ptr [rax + 1]"
