#!/bin/sh

set -e

REALBIN=$(readlink -f $0)
HOMEDIR=$(dirname "$REALBIN")
BINNAME="gotchibot.py"
LOGNAME="gotchis.log"
USER="nobody"

BINPATH="${HOMEDIR}${BINNAME}"
LOGPATH="${HOMEDIR}${LOGNAME}"
CMDLINE="--euid $USER --full $BINPATH"

function do_start {
    if [ pgrep "$CMDLINE" >/dev/null  = "1" ]; then
	su -c "$BINPATH" "$USER" > "$LOGPATH"
    else
	echo "Daemon already running. Not doing anything."
    fi
}

function do_stop {
    if ! pkill "$CMDLINE" >/dev/null; then
	echo "Daemon not running. Not doing anything."
    fi
}

if [ "$#" = 0 ]; then
    command="start"
elif [ "$#" -gt 1 ]; then
    echo "Too many arguments. Exiting."
    exit 1
else
    command="$1"
    shift
fi

case "$command" in
    'start' )
	do_start
	;;
    
    'stop' )
	do_stop
	;;
    
    'restart' )
	do_stop && do_start
	;;
esac
