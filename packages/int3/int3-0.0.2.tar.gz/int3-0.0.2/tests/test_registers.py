from int3.architecture import Architecture, Architectures, Registers
from int3.codegen import CodeGenerator, CodeSegment
from int3.platform import Platform, Triple

from .qemu import parametrize_qemu_arch


def test_register_expansion():
    x86_64 = Architectures.x86_64.value
    rax = x86_64.reg("rax")
    expanded_regs = x86_64.expand_regs(rax)
    expected_regs = (
        Registers.x86_64.rax,
        Registers.x86_64.eax,
        Registers.x86_64.al,
        Registers.x86_64.ax,
    )
    assert len(expanded_regs) == len(expected_regs)
    assert set(expanded_regs) == set(expected_regs)

    mips = Architectures.Mips.value
    a0 = mips.reg("a0")
    assert mips.expand_regs(a0) == (a0,)


def test_arithmetic_tainted_register_resolution():
    x86_64 = Architectures.x86_64.value
    linux_x86_64 = Triple(x86_64, Platform.Linux)
    segment = CodeSegment.from_asm(
        triple=linux_x86_64,
        asm="""
        mov rax, 0xdead
        inc bx
        add r15, r10
        jne label
    label:
    """,
    )
    assert len(segment.instructions) == 4
    all_tainted_regs = set()
    assert segment.instructions[0].tainted_regs == set(x86_64.expand_regs("rax"))
    all_tainted_regs |= set(x86_64.expand_regs("rax"))
    assert segment.instructions[1].tainted_regs == set(x86_64.expand_regs("bx"))
    all_tainted_regs |= set(x86_64.expand_regs("bx"))
    assert segment.instructions[2].tainted_regs == set(x86_64.expand_regs("r15"))
    all_tainted_regs |= set(x86_64.expand_regs("r15"))
    assert segment.instructions[3].tainted_regs == set()
    assert segment.tainted_regs == all_tainted_regs

    mips = Architectures.Mips.value
    linux_mips = Triple(mips, Platform.Linux)
    segment = CodeSegment.from_asm(
        triple=linux_mips,
        asm="""
        ori $at, $zero, 0xbeef
        addu $a0, $at, $v0
        addiu $v0, $zero, 0xfa1
        jr $ra
    """,
    )
    # There is an extra instruction for the implicit NOP that Keystone adds
    # after the jr instruction.
    assert len(segment.instructions) == 5
    all_tainted_regs = set()
    assert segment.instructions[0].tainted_regs == {mips.reg("at")}
    all_tainted_regs.add(mips.reg("at"))
    assert segment.instructions[1].tainted_regs == {mips.reg("a0")}
    all_tainted_regs.add(mips.reg("a0"))
    assert segment.instructions[2].tainted_regs == {mips.reg("v0")}
    all_tainted_regs.add(mips.reg("v0"))
    assert segment.instructions[3].tainted_regs == set()
    assert segment.tainted_regs == all_tainted_regs


@parametrize_qemu_arch
def test_linux_syscall_tainted_register_resolution(arch: Architecture):
    triple = Triple(arch, Platform.Linux)
    codegen = CodeGenerator(arch)
    segment = CodeSegment(triple=triple, raw_asm=codegen.syscall().bytes, bad_bytes=b"")
    assert segment.tainted_regs == set(
        arch.expand_regs(triple.syscall_convention.result)
    )
