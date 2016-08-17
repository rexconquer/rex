#!/bin/bash
TMP=/root/tmps

rm -f $TMP
####################################
hard_info ()
{
 Ser_tmp=`/usr/sbin/dmidecode -t 1`
 Ser_uuid=`echo $Ser_tmp |awk -F'UUID: ' '{print $2}' |awk -F'Wake-up' '{print $1}'`
# Ser_fact=`echo $Ser_tmp |awk -F'Manufacturer: ' '{print $2}' |awk -F'Product' '{print $1}'`
 Ser_fact=`/usr/sbin/dmidecode -t 1 |grep "Manufacturer:" |awk '{print $2}'`
 Ser_type=`echo $Ser_tmp |awk -F'Product Name: ' '{print $2}' |awk -F'Version' '{print $1}'`
 SN=`/usr/sbin/dmidecode -t 1 | grep "Serial Number:" |awk '{print $3}'`
}
###################################
sys_info()
{
 OS_Releases=`cat /etc/issue |sed -n '1p'`
 Kernel_ver=`uname -r`
 Hostname=`hostname`
}
##################################
cpu_info()
{
 LG_core=`cat /proc/cpuinfo | grep "processor" | wc -l`
 PHY_core=`cat /proc/cpuinfo | grep "cpu cores" | uniq | awk -F: '{print $2}'`
 PHY_id=`cat /proc/cpuinfo | grep "physical id" | sort -u | wc -l`
 Mode_name=`cat /proc/cpuinfo  |grep "model name"  |sort -u |awk -F':' '{print $2}'`
 HT_num=`expr $LG_core \/ $PHY_core \/ $PHY_id`

 if [ $HT_num -eq 2 ]; then
      HT_ctl="enable"
 else
      HT_ctl="disable"
 fi
}
vmcpu_info()
{
 LG_core=`cat /proc/cpuinfo | grep "processor" | wc -l`
 Mode_name=`cat /proc/cpuinfo  |grep "model name"  |sort -u |awk -F':' '{print $2}'`
}
##################################
memory_info()
{
Ser_meminfo=`/usr/sbin/dmidecode -t 17 |grep -E 'Size: ' |grep -v "No Module Installed" |sort -nr |uniq -c |awk '{print $3$4"*"$1}'`
}
#################################
netadpter()
{
Net_info=`lspci |grep -i ether| cut -d: -f 3 |awk '{print $1"-"$2"-"$3"-"$4"-"$5}'|sort -nr|uniq -c |awk '{print $2"/"$1}'`
Net_mac=`ifconfig -a |grep eth |awk '{print $1,$NF}'`
ethlist=`echo $Net_mac |sed 's/\//\n/g' |awk '{print $1}'`
Net_ip=`ifconfig|grep "inet addr:" |sed 's/:/ /g' |awk '{print $3}'|grep -E -v "127.0.0.1|192.168.122.1"|tr '\n' '/'|sed 's/\/$//g'`

for y in `echo $ethlist |sed 's/ /\n/g'`
    do
     dev_stat=`ethtool $y |awk '/Speed|Duplex/ {if($2 != "Unknown!") print $2}'|tr '\n' ' '`
     echo "$y:$dev_stat" >> $TMP
    done

Net_stat=`cat $TMP|tr '\n' '/' |sed 's/\/$//g'`
rm -f $TMP

}

vm_netadpter()
{
Net_info=`cat /var/log/dmesg |grep eth |awk '{print $1}'|sed 's/://g'`
Net_mac=`ifconfig -a |grep eth |awk '{print $1,$NF}'`
Net_ip=`ifconfig|grep "inet addr:" |sed 's/:/ /g' |awk '{print $3}'|grep -E -v "127.0.0.1|192.168.122.1"|tr '\n' '/'|sed 's/\/$//g'`
ethlist=`ifconfig -a |grep eth |awk '{print $1}'`

for y in `echo $ethlist`
    do
     dev_stat=`ethtool $y |awk '/Speed|Duplex/ {if($2 != "Unknown!") print $2}'|tr '\n' ' '`
     echo "$y:$dev_stat" >> $TMP
    done

Net_stat=`cat $TMP|tr '\n' '/' |sed 's/\/$//g'`
rm -f $TMP
}
#################################
hardisk()
{
cat /var/log/dmesg |grep "LOGICAL VOLUME" > /dev/null 2>&1
rd=$?
fdisk -l |grep -E "Disk /dev/cciss|/dev/mapper|/dev/df" > /dev/null2>&1
fd=$?

if [ $rd -eq 0 -o $fd -eq 0 ]; then
   raid_info
else
   hba_info
fi
}

raid_info()
{
if [ ! -f /usr/sbin/hpacucli ]; then
    wget -O /root/hpacucli.rpm  http://10.1.1.123/mirrors/hpconf/hpacucli-9.40-12.0.x86_64.rpm > /dev/null 2>&1
    rpm -ivh /root/hpacucli.rpm > /dev/null 2>&1
elif [ `hpacucli version |grep CLI|awk -F: '{print $2}' |sed 's/ //g'` != "9.40.12.0" ]; then
    wget -O /root/hpacucli.rpm  http://10.1.1.123/mirrors/hpconf/hpacucli-9.40-12.0.x86_64.rpm > /dev/null 2>&1
    rpm -Uvh /root/hpacucli.rpm > /dev/null 2>&1
fi

rm -f /root/hpacucli.rpm
slotid=`hpacucli ctrl all show status | grep 'Smart Array'|awk '{ print $6 }'`
Raid_info=`hpacucli ctrl slot=$slotid ld all show  |grep "logicaldrive" |sed -e 's/(/ /g' -e 's/,//g' |awk '{print $3$4"/"$5$6}'`
HD_info=` hpacucli ctrl slot=$slotid pd all show detail |grep -E "Interface Type:|Size:|Serial Number:|PHY Transfer Rate:|Model:"|sed -e 's/ //g' -e 's/,Unknown//g' |awk -F: '{print $2}'|awk -v n=5 '{if (NR%n==0){print $0} else {printf"%s ",$0}}'|awk '{print $3,$1,$2,$4,$5}' |tr '\n' '/' |sed 's/\/$//g'`

}

hba_info()
{
if [ ! -f /usr/sbin/smartctl ]; then
    yum install -y smartmontools > /dev/null 2>&1
elif [ `smartctl -V |sed -n '1p' |awk '{print $2}'` != "5.43" ]; then
    yum install -y smartmontools > /dev/null 2>&1
fi

Raid_info="No RAID"

for i in `fdisk -l |grep "Disk /dev" |awk '{print $2","$3}' |sed 's/://g'`
 do
   disk=`echo $i|awk -F, '{print $1}'`
   size=`echo $i|awk -F, '{print $2}' |cut -d . -f 1`
   if [ $size -gt 601 ]; then
        smartctl -i $disk |grep -i -E "Vendor:|Product:|Serial number:|Transport protocol:|User Capacity:|Device Model:|ATA Standard is:"| awk -F: '{print $2}' |sed -e 's/ //g' -e 's/^[0-9]*\(,[0-9]\{3\}\)*bytes\[//g' -e 's/\]//g' -e 's/ATA/SATA/g'|awk -F- '{print $1}' |tr '\n' ' ' |awk '{print $2,$4,$3,"HP"$1,"unkown"}' >> $TMP
    else
        smartctl -i $disk |grep -E "Vendor:|Product:|Serial number:|Transport protocol:|User Capacity:|Device Model:|ATA Standard is:" |awk -F: '{print $2}' |sed -e 's/ //g' -e 's/^[0-9]*\(,[0-9]\{3\}\)*bytes\[//g' -e 's/\]//g' |tr '\n' ' ' |awk '{print $4,$5,$3,$1$2,"unkown"}' >>$TMP
    fi
 done

HD_info=`cat $TMP|tr '\n' '/' |sed 's/\/$//g'`
rm -f $TMP
}

HW_hardisk()
{
 lspci |grep -i raid  > /dev/null 2>&1
 rd=$?
 if [ $rd -eq 0 ]; then
   hwraid_info
  else
   hba_info
 fi
}

hwraid_info()
{
TMP_RAID=/tmp/tmp_raid
Raid_infos=/tmp/tmp_raids

if [ ! -f /opt/MegaRAID/MegaCli/MegaCli64 ]; then
    wget -O /root/MegaCli.rpm http://10.1.1.123/mirrors/rpm/MegaCli-8.07.14-1.noarch.rpm > /dev/null 2>&1
    rpm -ivh /root/MegaCli.rpm > /dev/null 2>&1
    rm -f /root/MegaCli.rpm
#    export PATH="$PATH:/opt/MegaRAID/MegaCli"
#    echo "export PATH="$PATH:/opt/MegaRAID/MegaCli"" >>/etc/profile
fi

raid1="RAID Level          : Primary-1, Secondary-0, RAID Level Qualifier-0"
raid0="RAID Level          : Primary-0, Secondary-0, RAID Level Qualifier-0"
raid5="RAID Level          : Primary-5, Secondary-0, RAID Level Qualifier-3"

/opt/MegaRAID/MegaCli/MegaCli64  -LDInfo -Lall -aALL |grep -A 8 "RAID Level" >> $TMP_RAID
cat $TMP_RAID|while read rad
  do
    case $rad in
      $raid0)
        cat $TMP_RAID | grep -A 1 "$raid0" |grep Size |awk -F: '{print $2}' |sed 's/ //g' >> $Raid_infos
        echo Raid0   >> $Raid_infos
      ;;
      $raid1)
        cat $TMP_RAID | grep -A 1 "$raid1" |grep Size |awk -F: '{print $2}' |sed 's/ //g' >> $Raid_infos
        cat $TMP_RAID | grep -A 8 "$raid1" |grep "Number Of Drives per span" > /dev/null 2>&1
        if [ $? -eq 0 ];then
            echo Raid10  >> $Raid_infos
        else
            echo Raid1   >> $Raid_infos
        fi
      ;;
      $raid5)
        cat $TMP_RAID | grep -A 1 "$raid5" |grep Size |awk -F: '{print $2}' |sed 's/ //g' >> $Raid_infos
        cat $TMP_RAID | grep -A 8 "$raid5" |grep "Number Of Drives per span" > /dev/null 2>&1
        if [ $? -eq 0 ];then
            echo Raid50  >> $Raid_infos
        else
            echo Raid5   >> $Raid_infos
        fi
      ;;
    esac
 done

Raid_info=`cat $Raid_infos |tr '\n' ':'|sed -e 's/:$//g' -e 's/:R/\/R/g'`
rm -f $TMP_RAID $Raid_infos
HD_info=`/opt/MegaRAID/MegaCli/MegaCli64 -cfgdsply -aALL| grep -E 'PD Type|Raw Size|Link Speed|Inquiry Data'|awk -F: '{print $2}' |sed -e 's/\[.*]//g' -e 's/558.911/600/g' -e 's/Gb\/s/Gbps/g'|awk -v n=4 '{if (NR%n==0){print $0} else {printf"%s ",$0}}' |awk '{print $6,$1,$2$3,$5,$NF}'|tr '\n' '/' |sed 's/\/$//g'`
}

vm_hardisk()
{
HD_info=`fdisk -l|grep "Disk /dev" |awk '{print $2,$3$4}' |sed 's/,/;/g'`
}
#################################
vm_info()
{
if [ -f /usr/bin/virsh ]
  then
    vms=`virsh list --all |grep -E -v "Id|--*|^$"|awk '{print $2}' |tr '\n' '/'|sed 's/\/$//g'`
    for i in `echo $vms|tr '/' '\n'`
      do
       VM_conf=`cat /etc/libvirt/qemu/$i.xml |grep -E "<uuid>|<name>|<graphics type"  | sed -e 's/port='\''/>/g' -e 's/'\'' auto/</g' |awk -F '>' '{print $2}'|awk -F '<' '{print $1 }'|tr '\n' ' ' |sed  -e 's/ $//g'`
      echo "$VM_conf " >> $TMP
    done
    vms_info=`cat $TMP |tr '\n' '/' |sed 's/\/$//g'`
    rm -f $TMP
else
    vms_info=""
fi

}
#################################
ilo_info()
{
if [ ! -f /usr/bin/ipmitool ];then
   yum install -y OpenIPMI ipmitool > /dev/null 2>&1
fi

service ipmi status |grep "/dev/ipmi0 exists." > /dev/null 2>&1
ipmit=$?
if [ $ipmit -ne 0 ]
  then
   /etc/init.d/ipmi restart > /dev/null 2>&1
   chkconfig ipmi on > /dev/null 2>&1
fi

iLO_info=`ipmitool  lan print |grep -E "IP Address|MAC Address" |grep -v Source|awk  '{print $4}'|tr '\n' '/'|sed 's/\/$//g'`
}

#############pcie-ssd ############

virident()
{
        /usr/bin/vgc-monitor -d /dev/vgca >> $TMP
        PSN=`cat $TMP| grep "Serial Number" |awk '{print $NF}'`
        size=`cat $TMP | grep "vgca0" |awk '{print $2$3}'`
        speed=`cat $TMP | grep Rev |awk '{print "pcie"$6}'`
        rm -f $TMP
}

shannon()
{
        /usr/bin/shannon-status -a >> $TMP
        PSN=`cat $TMP | grep "Serial Number:" |awk '{print $NF}'`
        size=`cat $TMP | grep "Disk Capacity:" |awk -F: '{print $2}' |sed -e 's/\.00//g' -e 's/ //g'`
        speed=`cat $TMP |grep "PCI Link Speed:" | awk -F: '{print $2}' | sed -e 's/2.0//g' -e 's/ //g'`
        rm -f $TMP
}

pciessd_info()
{
/sbin/lspci -vvv  |grep "Kernel modules: shannon" > /dev/null 2>&1
#shannon_fact=`/sbin/lspci -vvv -s 07:00.0 |grep "Kernel modules:" |awk '{print $NF}'`
shannon_fact=$?
/sbin/lspci -vvv  |grep "Kernel modules: vgc" > /dev/null 2>&1
vgc_fact=$?

   if [ $vgc_fact -eq 0 ];then
   # if [ -f /usr/bin/vgc-monitor ]; then
        fact=Virident
        virident
        pcie_ssd_info="$fact $PSN $size $speed"
   elif [ $shannon_fact -eq 0 ];then
        fact=shannon
        shannon
        pcie_ssd_info="$fact $PSN $size $speed"
   elif [ -f /usr/bin/fio-status ];then
        /usr/bin/fio-status >> $TMP
        PSN=`cat $TMP |grep -A1 "Adapter: ioDrive" |grep SN |awk '{print $NF}' |sed -e 's/SN://g'`
        size=`cat $TMP |grep "device size" |awk '{print $1"GB"}'`
        speed=unknow
        fact=Fusion-io
        rm -f $TMP
        pcie_ssd_info="$fact $PSN $size $speed"
   fi
}

############ main ###############
hard_info
#1if [ "$Ser_fact" = "HP "  -o "$Ser_fact" = "IBM "  -o "$Ser_fact" = "Huawei Technologies Co., Ltd. " ];then
if [ "$Ser_fact" = "HP"  -o "$Ser_fact" = "IBM"  -o "$Ser_fact" = "Huawei" -o "$Ser_fact" = "Inspur" -o "$Ser_fact" = "Dell" ];then
#   if [ "$Ser_fact" = "Huawei Technologies Co., Ltd. " ]; then
    if [ "$Ser_fact" = "Huawei" -o "$Ser_fact" = "Inspur" -o "$Ser_fact" = "Dell" ];then
       HW_hardisk
   else
       hardisk
   fi
   netadpter
   sys_info
   cpu_info
   memory_info
   vm_info
   ilo_info
   pciessd_info
   echo $Hostname,$SN,$Ser_fact,$Ser_type,$Ser_uuid,$iLO_info,$OS_Releases,$Kernel_ver,$Mode_name,$PHY_id,$LG_core,$HT_ctl,$Ser_meminfo,$Net_ip,$Net_stat,$Net_info,$Net_mac,$Raid_info,$HD_info,$vms_info,$pcie_ssd_info
else
   sys_info
   memory_info
   vmcpu_info
   vm_hardisk
   vm_netadpter
   echo $Hostname,$Ser_type,$Ser_uuid,$OS_Releases,$Kernel_ver,$Mode_name,$LG_core,$Ser_meminfo,$Net_ip,$Net_mac,$HD_info
fi
