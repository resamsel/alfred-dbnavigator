#!/bin/bash

TARGET=target
TEST_DIR="src/test/resources"
ACTUAL_DIR="$TARGET/testfiles/actual"
EXPECTED_DIR="$TEST_DIR/expected"
LOGLEVEL=debug
LOGFILE=$TARGET/dbnavigator.log

export DBEXPLORER_CFG="$TARGET/testfiles/resources/dbexplorer.cfg"
export PGPASS_CFG="$TARGET/testfiles/resources/pgpass"

TT=$(ruby -e 'puts "%.3f" % Time.now')
STATUS=0
TOTAL=$#
OK=0
FAILED=0

while (( "$#" )); do
	TESTCASE="$(basename ${1%})"
	ACTUAL="$ACTUAL_DIR/$TESTCASE"
	EXPECTED="$EXPECTED_DIR/$TESTCASE"
	SCRIPT="/usr/bin/python -m main.dbnavigator -l $LOGLEVEL -f $LOGFILE -s $(cat $TEST_DIR/$TESTCASE)"

	echo -n "Testing $TESTCASE... "
	T=$(ruby -e 'puts "%.3f" % Time.now')
	PYTHONPATH=$TARGET/testfiles $SCRIPT > $ACTUAL
	T=$(ruby -e 'puts "%.3f" % (Time.now - '$T')')

	DIFF=$(diff -u $EXPECTED $ACTUAL)

	if [ "$DIFF" != "" ]; then
		FAILED=$((FAILED+1))
		echo "FAILED (took ${T}s)"
		echo $SCRIPT
		if [ "$(which colordiff)" != "" ]; then
			echo colordiff $EXPECTED $ACTUAL
			colordiff $EXPECTED $ACTUAL
		else
			echo diff -u $EXPECTED $ACTUAL
			echo $DIFF
		fi
		STATUS=-1
	else
		OK=$((OK+1))
		echo "OK (took ${T}s)"
	fi

	shift
done

TT=$(ruby -e 'puts "%.3f" % (Time.now - '$TT')')

#echo "Tests run: $TOTAL, failed: $FAILED (took ${TT}s)"
#echo

exit $STATUS
