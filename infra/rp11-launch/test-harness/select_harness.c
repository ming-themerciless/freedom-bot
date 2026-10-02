/*
 * T-L8 harness (proposal §5.12.1). Test only; never part of the image.
 *
 * A hosted program linked with select_shim.o. It reads cases from standard
 * input, one per line, as whitespace-separated fields:
 *
 *   A <hex string> ...   rp11_check_argv over these argv strings
 *   E <hex string> ...   rp11_select_invocation_id over these envp strings
 *
 * Each string is given in hexadecimal (an empty string as "-"). For each case
 * it prints one line: for A, the integer result; for E, "null", or the index
 * of the selected entry, the selected pointer's offset into it, and the 32
 * selected bytes in hexadecimal. The Python reference model computes the same
 * line, and T-L8 compares them.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int rp11_shim_check_argv(long argc, char *const *argv);
const char *rp11_shim_select_invocation_id(char *const *envp);

static char *
unhex(const char *field)
{
	size_t n = strlen(field), i;
	char *out;

	if (strcmp(field, "-") == 0)
		n = 0;
	out = malloc(n / 2 + 1);
	if (out == NULL)
		exit(2);
	for (i = 0; i + 1 < n; i += 2) {
		unsigned int byte;

		if (sscanf(field + i, "%2x", &byte) != 1)
			exit(2);
		out[i / 2] = (char)byte;
	}
	out[n / 2] = '\0';
	return out;
}

int
main(void)
{
	static char line[1 << 22];

	while (fgets(line, sizeof line, stdin) != NULL) {
		char *fields[20001];
		long count = 0, k;
		char *tok, *save = NULL;
		char kind;

		line[strcspn(line, "\n")] = '\0';
		tok = strtok_r(line, " ", &save);
		if (tok == NULL)
			continue;
		kind = tok[0];
		while ((tok = strtok_r(NULL, " ", &save)) != NULL && count < 20000)
			fields[count++] = unhex(tok);
		fields[count] = NULL;
		if (kind == 'A') {
			printf("%d\n", rp11_shim_check_argv(count, fields));
		} else {
			const char *sel = rp11_shim_select_invocation_id(fields);

			if (sel == NULL) {
				printf("null\n");
			} else {
				for (k = 0; k < count; k++)
					if (sel >= fields[k] && sel <= fields[k] + strlen(fields[k]))
						break;
				printf("%ld %ld ", k, (long)(sel - fields[k]));
				for (k = 0; k < 32; k++)
					printf("%02x", (unsigned char)sel[k]);
				printf("\n");
			}
		}
		for (k = 0; k < count; k++)
			free(fields[k]);
		fflush(stdout);
	}
	return 0;
}
