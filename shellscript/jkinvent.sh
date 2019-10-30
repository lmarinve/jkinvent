case "$1" in
	AMBA|ameroc|AVA|ATL|BEL|BOCCHI|BOSC|DEV|FOR|FRE|HAF|HMW|HUD|JAM|KRS|NAT|STOCK|stu|tdp|TRY)
		if /usr/bin/python3 /opt/jkinvent/jkinvent.py $1; then
			echo "success"
		else
			echo "fails"
			/usr/bin/python3 /opt/jkinvent/shellscript/mailalert.py $1
		fi
		;;
	*)
		echo "unknow arg: $1"
		/usr/bin/python3 /opt/jkinvent/shellscript/mailalert.py $1
		;;
esac
