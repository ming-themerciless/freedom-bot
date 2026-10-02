/*
 * T-L8 shim (proposal §5.2, §5.12.1). Test only; never part of the image.
 *
 * It includes the same select.h, unchanged, and defines two non-inline
 * wrappers around the two always_inline selection functions. It is compiled
 * with the image's exact compile vector (taken from build.sh) and assembled
 * with the pinned as. What T-L8 then establishes is narrow: the selection
 * source, as compiled by the pinned compiler under the image's flags in a
 * separate, non-inlined context, returns the reference model's result. It
 * says nothing about the instructions inlined into rp11_main.
 */
#include "../select.h"

int rp11_shim_check_argv(long argc, char *const *argv);
const char *rp11_shim_select_invocation_id(char *const *envp);

int
rp11_shim_check_argv(long argc, char *const *argv)
{
	return rp11_check_argv(argc, argv);
}

const char *
rp11_shim_select_invocation_id(char *const *envp)
{
	return rp11_select_invocation_id(envp);
}
