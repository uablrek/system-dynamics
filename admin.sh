#! /bin/sh
##
## admin.sh --
##   Help script for https://github.com/uablrek/system-dynamics/
##
## Commands;
##

prg=$(basename $0)
dir=$(dirname $0); dir=$(readlink -f $dir)
tmp=/tmp/${prg}_$$

die() {
    echo "ERROR: $*" >&2
    rm -rf $tmp
    exit 1
}
help() {
    grep '^##' $0 | cut -c3-
    rm -rf $tmp
    exit 0
}
test -n "$1" || help
echo "$1" | grep -qi "^help\|-h" && help

log() {
	echo "$*" >&2
}
findf() {
	f=$HOME/Downloads/$1
	test -r $f && return 0
	test -n "$ARCHIVE" && f=$ARCHIVE/$1
	test -r $f
}
findar() {
	findf $1.tar.bz2 || findf $1.tar.gz || findf $1.tar.xz || findf $1.zip
}

##   env
##     Print environment.
cmd_env() {
	test "$envread" = "yes" && return 0
	envread=yes

	eset GITHUBD=$HOME/go/src/github.com
	eset svgasm=$GITHUBD/tomkwok/svgasm/svgasm

	if test "$cmd" = "env"; then
		set | grep -E "^($opts)="
		exit 0
	fi
}
# Set variables unless already defined
eset() {
	local e k
	for e in "$@"; do
		k=$(echo $e | cut -d= -f1)
		opts="$opts|$k"
		test -n "$(eval echo \$$k)" || eval $e
		test "$(eval echo \$$k)" = "?" && eval $e
	done
}
##   animate [--out=-] [--delay=2] files.svg...
##     Create an animated SVG from files. Requires "svgasm" (in $GITHUBD)
##     from: https://github.com/tomkwok/svgasm/
cmd_animate() {
	local cleaner='cat %s'
	if which svgo > /dev/null 2>&1; then
		cleaner='svgo --multipass -o - -i %s'
		log "Cleaner [$cleaner]"
	fi
	eset __out=- __delay=2
	test -x $svgasm || die "Not executable [$svgasm]"
	$svgasm -d $__delay -o $__out -c "$cleaner" $@
}


##
# Get the command
cmd=$1
shift
grep -q "^cmd_$cmd()" $0 $hook || die "Invalid command [$cmd]"

while echo "$1" | grep -q '^--'; do
	if echo $1 | grep -q =; then
		o=$(echo "$1" | cut -d= -f1 | sed -e 's,-,_,g')
		v=$(echo "$1" | cut -d= -f2-)
		eval "$o=\"$v\""
	else
		if test "$1" = "--"; then
			shift
			break
		fi
		o=$(echo "$1" | sed -e 's,-,_,g')
		eval "$o=yes"
	fi
	shift
done
unset o v

# Execute command
trap "die Interrupted" INT TERM
cmd_env
cmd_$cmd "$@"
status=$?
rm -rf $tmp
exit $status
