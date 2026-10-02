# rp11-launch/1 entry stub (proposal §5.1; SR-7).
#
# The kernel enters here with %rsp 16-byte aligned and pointing at argc,
# followed by argv[0 .. argc-1], a null pointer, envp[...], a null pointer and
# the auxiliary vector (AD-6). _start reads argc only; it computes argv and
# envp by address arithmetic and reads nothing else, in particular not the
# auxiliary vector (HR-6). It contains no call and no ret: it aligns the
# stack, pushes a zero word where a return address would lie, and enters
# rp11_main by one direct jmp, its last instruction (CT-4). Nothing reads the
# pushed word as an address, because the image contains no ret (LD-7).

	.text
	.globl	_start
	.type	_start, @function
_start:
	xorl	%ebp, %ebp
	movq	(%rsp), %rdi
	leaq	8(%rsp), %rsi
	leaq	16(%rsp,%rdi,8), %rdx
	andq	$-16, %rsp
	pushq	$0
	jmp	rp11_main
	.size	_start, .-_start
