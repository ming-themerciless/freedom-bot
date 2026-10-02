/*
 * rp11-launch/1 linker script (proposal §5.2, BI-1 ... BI-5).
 *
 * One read-and-execute PT_LOAD holds the headers, .text and .rodata; one
 * read-write PT_GNU_STACK. start.o is linked first, so .text begins with
 * _start (RI-2). Notes, .comment and unwind tables are discarded. Every
 * section that could carry pre-entry code, a dynamic interpreter, relocation,
 * TLS or writable data is declared here only so that it can be asserted
 * empty: an input that fills one fails the link.
 */
ENTRY(_start)

PHDRS
{
	image PT_LOAD FILEHDR PHDRS FLAGS(5);
	stack PT_GNU_STACK FLAGS(6);
}

SECTIONS
{
	. = 0x400000 + SIZEOF_HEADERS;
	.text : { *(.text .text.*) } :image
	.rodata : { *(.rodata .rodata.*) } :image

	/DISCARD/ : { *(.note.*) *(.comment) *(.eh_frame) *(.eh_frame_hdr) *(.eh_frame.*) }

	.interp : { *(.interp) }
	.dynamic : { *(.dynamic) }
	.rela.dyn : { *(.rela.*) }
	.got : { *(.got) }
	.got.plt : { *(.got.plt) }
	.plt : { *(.plt) *(.plt.*) }
	.init_array : { *(.init_array .init_array.*) }
	.fini_array : { *(.fini_array .fini_array.*) }
	.preinit_array : { *(.preinit_array) }
	.ctors : { *(.ctors .ctors.*) }
	.dtors : { *(.dtors .dtors.*) }
	.tdata : { *(.tdata .tdata.*) }
	.tbss : { *(.tbss .tbss.*) }
	.data : { *(.data .data.*) }
	.bss : { *(.bss .bss.*) *(COMMON) }
}

ASSERT(SIZEOF(.interp) == 0, "rp11-launch: .interp must be absent")
ASSERT(SIZEOF(.dynamic) == 0, "rp11-launch: .dynamic must be absent")
ASSERT(SIZEOF(.rela.dyn) == 0, "rp11-launch: .rela.* must be absent")
ASSERT(SIZEOF(.got) == 0, "rp11-launch: .got must be absent")
ASSERT(SIZEOF(.got.plt) == 0, "rp11-launch: .got.plt must be absent")
ASSERT(SIZEOF(.plt) == 0, "rp11-launch: .plt must be absent")
ASSERT(SIZEOF(.init_array) == 0, "rp11-launch: .init_array must be absent")
ASSERT(SIZEOF(.fini_array) == 0, "rp11-launch: .fini_array must be absent")
ASSERT(SIZEOF(.preinit_array) == 0, "rp11-launch: .preinit_array must be absent")
ASSERT(SIZEOF(.ctors) == 0, "rp11-launch: .ctors must be absent")
ASSERT(SIZEOF(.dtors) == 0, "rp11-launch: .dtors must be absent")
ASSERT(SIZEOF(.tdata) == 0, "rp11-launch: .tdata must be absent")
ASSERT(SIZEOF(.tbss) == 0, "rp11-launch: .tbss must be absent")
ASSERT(SIZEOF(.data) == 0, "rp11-launch: .data must be absent")
ASSERT(SIZEOF(.bss) == 0, "rp11-launch: .bss must be absent")
