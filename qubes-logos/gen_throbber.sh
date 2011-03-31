#/bin/bash
FIRST=00
LAST=15
IMAGE=plymouth/charge/throbber-
FORMAT=png

cd `dirname $0`

convert $IMAGE$FIRST.$FORMAT $IMAGE$LAST.$FORMAT -morph $(( 10#$LAST - 1 )) __throbber.png

COUNT=0
for i in `seq -w $FIRST $LAST`; do
    mv __throbber-$((COUNT++)).$FORMAT $IMAGE$i.$FORMAT
done
