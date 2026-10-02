/*
 * rp11-launch/1: the LB-2S static first image (proposal §5).
 *
 * rp11_main is the only C function in the image (§5.1, RI-1). It is entered
 * only by _start's jmp, is noreturn, and contains no call and no ret: every
 * exit is the inline exit_group wrapper followed by __builtin_trap() (SR-4).
 * Every other function here and in select.h is static inline
 * __attribute__((always_inline)).
 *
 * The steps S-1 ... S-9 of §5.7 run in order. A refusal or failure writes one
 * fixed line to descriptor 2 and calls exit_group with the step's status
 * (§5.9); the write's result is ignored. No system call other than the nine of
 * the §5.4 inventory is made, and no output pointer is ever passed (SR-6).
 *
 * Locals are set only by scalar assignments at constant indices (SR-3, SR-5):
 * no aggregate initialiser, no loop that writes memory, no variable-length
 * array. The 32 INVOCATION_ID bytes are copied by 32 written-out assignments,
 * after validation has succeeded.
 */
#include "select.h"

enum {
	RP11_SYS_WRITE = 1,
	RP11_SYS_RT_SIGACTION = 13,
	RP11_SYS_RT_SIGPROCMASK = 14,
	RP11_SYS_EXECVE = 59,
	RP11_SYS_FCNTL = 72,
	RP11_SYS_CHDIR = 80,
	RP11_SYS_UMASK = 95,
	RP11_SYS_EXIT_GROUP = 231,
	RP11_SYS_CLOSE_RANGE = 436
};

enum {
	RP11_F_GETFD = 1,
	RP11_SIG_SETMASK = 2,
	RP11_SIGSET_BYTES = 8,
	RP11_SIGKILL = 9,
	RP11_SIGSTOP = 19,
	RP11_SIGNAL_MAX = 64
};

__attribute__((noreturn, used)) void rp11_main(long argc, char *const *argv,
					       char *const *envp);

static inline __attribute__((always_inline)) long
rp11_syscall1(long number, long a1)
{
	long ret;

	__asm__ volatile ("syscall"
			  : "=a" (ret)
			  : "a" (number), "D" (a1)
			  : "rcx", "r11", "memory");
	return ret;
}

static inline __attribute__((always_inline)) long
rp11_syscall3(long number, long a1, long a2, long a3)
{
	long ret;

	__asm__ volatile ("syscall"
			  : "=a" (ret)
			  : "a" (number), "D" (a1), "S" (a2), "d" (a3)
			  : "rcx", "r11", "memory");
	return ret;
}

static inline __attribute__((always_inline)) long
rp11_syscall4(long number, long a1, long a2, long a3, long a4)
{
	long ret;
	register long r10 __asm__ ("r10") = a4;

	__asm__ volatile ("syscall"
			  : "=a" (ret)
			  : "a" (number), "D" (a1), "S" (a2), "d" (a3), "r" (r10)
			  : "rcx", "r11", "memory");
	return ret;
}

/* A return value in [-4095, -1] is a kernel error (§5.4). */
static inline __attribute__((always_inline)) int
rp11_is_error(long ret)
{
	return (unsigned long)ret >= (unsigned long)-4095L;
}

/* §5.9: exactly one write(2, line, length) is attempted, then exit_group. */
static inline __attribute__((always_inline, noreturn)) void
rp11_fail(const char *line, long length, long status)
{
	rp11_syscall3(RP11_SYS_WRITE, 2, (long)line, length);
	rp11_syscall1(RP11_SYS_EXIT_GROUP, status);
	__builtin_trap();
}

void
rp11_main(long argc, char *const *argv, char *const *envp)
{
	const char *id;
	char idbuf[48];
	const char *argv_out[8];
	const char *envp_out[4];
	unsigned long sa[4];
	unsigned long mask;
	long s;

	/* S-1: argv (§5.5). No system call precedes it. */
	if (rp11_check_argv(argc, argv) != RP11_ARGV_OK)
		rp11_fail("rp11-launch/1: launch-usage\n", 28, 111);

	/* S-2: the one INVOCATION_ID (§5.6). */
	id = rp11_select_invocation_id(envp);
	if (id == 0)
		rp11_fail("rp11-launch/1: launch-invocation-id\n", 36, 112);

	/* S-3: descriptors 0, 1 and 2 must be open (FD-7). */
	if (rp11_is_error(rp11_syscall3(RP11_SYS_FCNTL, 0, RP11_F_GETFD, 0)))
		rp11_fail("rp11-launch/1: launch-stdio\n", 28, 113);
	if (rp11_is_error(rp11_syscall3(RP11_SYS_FCNTL, 1, RP11_F_GETFD, 0)))
		rp11_fail("rp11-launch/1: launch-stdio\n", 28, 113);
	if (rp11_is_error(rp11_syscall3(RP11_SYS_FCNTL, 2, RP11_F_GETFD, 0)))
		rp11_fail("rp11-launch/1: launch-stdio\n", 28, 113);

	/* S-4: close every descriptor from 3 up. */
	if (rp11_syscall3(RP11_SYS_CLOSE_RANGE, 3, 0xFFFFFFFFL, 0) != 0)
		rp11_fail("rp11-launch/1: launch-descriptors\n", 34, 114);

	/* S-5: SIG_DFL for 1 ... 64 except SIGKILL and SIGSTOP; the old-action
	 * pointer is NULL (RI-6). */
	sa[0] = 0;
	sa[1] = 0;
	sa[2] = 0;
	sa[3] = 0;
	for (s = 1; s <= RP11_SIGNAL_MAX; s++) {
		if (s == RP11_SIGKILL || s == RP11_SIGSTOP)
			continue;
		if (rp11_syscall4(RP11_SYS_RT_SIGACTION, s, (long)sa, 0,
				  RP11_SIGSET_BYTES) != 0)
			rp11_fail("rp11-launch/1: launch-signals\n", 30, 115);
	}

	/* S-6: an empty signal mask; the old-set pointer is NULL. */
	mask = 0;
	if (rp11_syscall4(RP11_SYS_RT_SIGPROCMASK, RP11_SIG_SETMASK, (long)&mask,
			  0, RP11_SIGSET_BYTES) != 0)
		rp11_fail("rp11-launch/1: launch-signals\n", 30, 115);

	/* S-7: umask 0077. It cannot fail; its result is ignored. */
	rp11_syscall1(RP11_SYS_UMASK, 0077);

	/* S-8: the working directory is /. */
	if (rp11_syscall1(RP11_SYS_CHDIR, (long)"/") != 0)
		rp11_fail("rp11-launch/1: launch-chdir\n", 28, 116);

	/* S-9: the literal execve of §5.8. */
	idbuf[0] = 'I';
	idbuf[1] = 'N';
	idbuf[2] = 'V';
	idbuf[3] = 'O';
	idbuf[4] = 'C';
	idbuf[5] = 'A';
	idbuf[6] = 'T';
	idbuf[7] = 'I';
	idbuf[8] = 'O';
	idbuf[9] = 'N';
	idbuf[10] = '_';
	idbuf[11] = 'I';
	idbuf[12] = 'D';
	idbuf[13] = '=';
	idbuf[14] = id[0];
	idbuf[15] = id[1];
	idbuf[16] = id[2];
	idbuf[17] = id[3];
	idbuf[18] = id[4];
	idbuf[19] = id[5];
	idbuf[20] = id[6];
	idbuf[21] = id[7];
	idbuf[22] = id[8];
	idbuf[23] = id[9];
	idbuf[24] = id[10];
	idbuf[25] = id[11];
	idbuf[26] = id[12];
	idbuf[27] = id[13];
	idbuf[28] = id[14];
	idbuf[29] = id[15];
	idbuf[30] = id[16];
	idbuf[31] = id[17];
	idbuf[32] = id[18];
	idbuf[33] = id[19];
	idbuf[34] = id[20];
	idbuf[35] = id[21];
	idbuf[36] = id[22];
	idbuf[37] = id[23];
	idbuf[38] = id[24];
	idbuf[39] = id[25];
	idbuf[40] = id[26];
	idbuf[41] = id[27];
	idbuf[42] = id[28];
	idbuf[43] = id[29];
	idbuf[44] = id[30];
	idbuf[45] = id[31];
	idbuf[46] = '\0';

	argv_out[0] = "/usr/bin/python3.12";
	argv_out[1] = "-I";
	argv_out[2] = "-S";
	argv_out[3] = "/usr/local/libexec/freedom-blades-rp11/rp11_entry.py";
	argv_out[4] = "run";
	argv_out[5] = "--pass";
	argv_out[6] = "A";
	argv_out[7] = 0;

	envp_out[0] = "LC_ALL=C";
	envp_out[1] = "PATH=/usr/bin";
	envp_out[2] = idbuf;
	envp_out[3] = 0;

	rp11_syscall3(RP11_SYS_EXECVE, (long)"/usr/bin/python3.12", (long)argv_out,
		      (long)envp_out);
	rp11_fail("rp11-launch/1: launch-exec-failed\n", 34, 117);
}
