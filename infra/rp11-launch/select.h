/*
 * rp11-launch/1 selection functions (proposal §5.5, §5.6; SR-2, SR-8).
 *
 * These are the only source that reads argv or envp strings. Both functions
 * are pure: no system call, no global or static object, no store through a
 * pointer and no out-parameter. They return their result only as a return
 * value. Each is static inline __attribute__((always_inline)), so in the image
 * they exist only inlined into rp11_main; a failure to inline is a compile
 * error, not a silent call. The test shim includes this file unchanged (T-L8).
 *
 * Bounds (§5.6): an envp entry is read only up to its first mismatch with
 * "INVOCATION_ID" and never past byte 13 unless all thirteen bytes match; a
 * matching entry is read for at most 47 bytes. Every comparison is
 * short-circuited, so no byte after a string's NUL is read.
 */

enum {
	RP11_ARGV_OK = 0,
	RP11_ARGV_REFUSED = 1
};

static inline __attribute__((always_inline)) int
rp11_check_argv(long argc, char *const *argv)
{
	const char *pass;
	const char *value;

	if (argc != 3)
		return RP11_ARGV_REFUSED;
	pass = argv[1];
	value = argv[2];
	if (pass[0] != '-' || pass[1] != '-' || pass[2] != 'p' || pass[3] != 'a'
	    || pass[4] != 's' || pass[5] != 's' || pass[6] != '\0')
		return RP11_ARGV_REFUSED;
	if (value[0] != 'A' || value[1] != '\0')
		return RP11_ARGV_REFUSED;
	return RP11_ARGV_OK;
}

static inline __attribute__((always_inline)) const char *
rp11_select_invocation_id(char *const *envp)
{
	const char *candidate = 0;
	long count = 0;
	long i;
	char *const *p;

	for (p = envp; *p != 0; p++) {
		const char *e = *p;

		if (e[0] != 'I' || e[1] != 'N' || e[2] != 'V' || e[3] != 'O'
		    || e[4] != 'C' || e[5] != 'A' || e[6] != 'T' || e[7] != 'I'
		    || e[8] != 'O' || e[9] != 'N' || e[10] != '_' || e[11] != 'I'
		    || e[12] != 'D')
			continue;
		if (e[13] == '=') {
			count++;
			candidate = e + 14;
		} else if (e[13] == '\0') {
			count++;
			candidate = 0;
		}
	}
	if (count != 1 || candidate == 0)
		return 0;
	for (i = 0; i < 32; i++) {
		char c = candidate[i];

		if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f')))
			return 0;
	}
	if (candidate[32] != '\0')
		return 0;
	return candidate;
}
