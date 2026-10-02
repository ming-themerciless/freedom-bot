# rp11-launch/1 build definition (proposal §5.2, §5.3.3, §5.3.5 R-2).
#
# Run from the checkout root, as the first process in the verified build
# root, by exactly:
#   /usr/bin/env -i LC_ALL=C PATH=/usr/bin SOURCE_DATE_EPOCH=0 TZ=UTC0 \
#       /bin/sh infra/rp11-launch/build.sh build-out
# The argument is an existing, empty directory, given as a relative path.
#
# Only shell built-ins and the absolute tool paths named in toolchain.lock are
# used: no glob, no command substitution, no external utility. Every tool
# argument is a relative path. The compiler runs with -S, so the driver starts
# only cc1 and needs neither PATH nor a temporary file; the pinned as and ld
# are run directly. The listing is produced by the pinned readelf and objdump,
# one instruction per line with its complete byte field and no elided zero
# block. Its decoding is not trusted: XD must agree with it (T-L11).
set -eu
umask 022
if [ "$#" -ne 1 ]; then
	exit 2
fi
out=$1

cd infra/rp11-launch
# cc1 looks for a precompiled header beside each input (IC-1). Their absence
# is a checkout property, not a bound-root one, so a present one refuses.
if [ -e launch.c.gch ] || [ -e select.h.gch ]; then
	exit 3
fi
/usr/bin/gcc-15 \
	-S -v -std=c11 -ffreestanding -nostdinc -fno-builtin \
	-fno-pic -fno-pie -fno-stack-protector -fno-stack-clash-protection \
	-fcf-protection=none -mindirect-branch=keep -mfunction-return=keep \
	-fno-asynchronous-unwind-tables -fno-unwind-tables \
	-fno-jump-tables -fno-tree-vectorize -fno-common -fno-ident \
	-fno-optimize-sibling-calls -fno-reorder-blocks-and-partition \
	-fno-partial-inlining -fno-ipa-cp-clone -fno-ipa-sra \
	-fno-tree-loop-distribute-patterns -fomit-frame-pointer \
	-falign-functions=1 -falign-jumps=1 -falign-loops=1 -falign-labels=1 \
	-mgeneral-regs-only -mno-red-zone -march=x86-64 -mtune=generic \
	-frandom-seed=rp11-launch \
	-Os -g0 -U_FORTIFY_SOURCE \
	-Wall -Wextra -Wvla -Werror \
	-o ../../"$out"/launch.s launch.c 2> ../../"$out"/cc1.v
/usr/bin/as --64 --noexecstack -mx86-used-note=no -o ../../"$out"/start.o start.s

cd ../../"$out"
/usr/bin/as --64 --noexecstack -mx86-used-note=no -o launch.o launch.s
/usr/bin/ld.bfd \
	-m elf_x86_64 -static -nostdlib --build-id=none -z noexecstack \
	-z norelro --no-dynamic-linker -T ../infra/rp11-launch/rp11-launch.ld \
	-Map rp11-launch.map -o rp11-launch start.o launch.o

printf '== readelf -W -h -l -S -s rp11-launch\n' > rp11-launch.x86_64.listing
/usr/bin/readelf -W -h -l -S -s rp11-launch >> rp11-launch.x86_64.listing
printf '== objdump -d -w -z rp11-launch\n' >> rp11-launch.x86_64.listing
/usr/bin/objdump -d -w -z rp11-launch >> rp11-launch.x86_64.listing
printf '== objdump -s -j .rodata rp11-launch\n' >> rp11-launch.x86_64.listing
/usr/bin/objdump -s -j .rodata rp11-launch >> rp11-launch.x86_64.listing
