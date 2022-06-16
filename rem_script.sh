fw_type=$(cat /etc/version | cut -d'.' -f1)
if [ "$fw_type" == "XC" ] || [ "$fw_type" == "WA" ] 
then
	desired_priority=$(mca-status | grep wlanDesiredPriority -i | cut -d'=' -f2)
	actual_priority=$(mca-status | grep wlanActualPriority -i | cut -d'=' -f2)
elif [ "$fw_type" == "XM" ] || [ "$fw_type" == "XW" ] 
then
	signal=$(mca-status | grep signal | cut -d'=' -f2 )
	noise=$(mca-status | grep noise | cut -d'=' -f2)
	conf_priority=$(grep radio.1.pollingpri /tmp/system.cfg | cut -d'=' -f2)
	case $conf_priority in
		0) actual_priority="High" ;;
		1) actual_priority="Medium" ;;
		2) actual_priority="Base" ;;
		3) actual_priority="Low" ;;
		*) actual_priority="Err" ;;
	esac
	if [ $signal -ge -55 ]
	then
		desired_priority="High"	
	elif [ $signal -lt -55 ] && [ $signal -ge -62 ]
	then
		desired_priority="Medium"
	elif [ $signal -lt -62 ] && [ $signal -ge -71 ]
	then
		desired_priority="Base"
	elif [ $signal -lt -71 ]
	then
		desired_priority="Low"
	else
		echo "Error."
	fi
else
	echo "Firmware not supported."
fi
echo $desired_priority
echo $actual_priority
