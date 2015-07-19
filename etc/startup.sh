RIAK_BIN=$HOME/app/riak/bin/riak
KASSIS_NUMBERING=$HOME/IdeaProjects/kassis_numbering

echo "riak start"
$RIAK_BIN start

echo "kassis numbering start"
cd $KASSIS_NUMBERING
forever start app.js


