#!/bin/sh

set -e

REALBIN=$(readlink -f $0)
HOMEDIR=$(dirname "$REALBIN")
BINNAME="gotchibot.py"
LOGNAME="gotchis.log"
SAVENAME="gotchis.save"
USER="nobody"

BINPATH="${HOMEDIR}/${BINNAME}"
LOGPATH="${HOMEDIR}/${LOGNAME}"
SAVEPATH="${HOMEDIR}${SAVENAME}"
CMDLINE="--euid $USER --full $BINPATH"

do_start() {
    if ! pgrep $CMDLINE >/dev/null; then
	echo -n "Starting daemon..."
	if ! [ -e "$SAVEPATH" ]; then
	    touch "$SAVEPATH"
	    chown "$USER" "$SAVEPATH"
	fi
	sudo -u "$USER" python3 "$BINPATH" 2>&1 | ts >> "$LOGPATH" &
	echo "done."
    else
	echo "Daemon already running. Not doing anything."
    fi
}

do_stop() {
    if ! pkill $CMDLINE --signal SIGINT >/dev/null; then
	echo "Daemon not running. Not doing anything."
    else
	echo "Daemon stopped."
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
	do_stop && sleep 1 &&  do_start
	;;
esac
