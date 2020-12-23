#!/usr/bin/env bash

# chirps dataset is updated 3rd week of every month when data from previous month is made available

# based on curent date, this script determines latest month of available data and download them

current_date=`date -I`;# -d $1`;
current_month=`date -d $current_date +"%Y-%m"`;
current_day=`date -d $current_date +"%d"`;

# determine begining of latest month of data
if [[ $current_day > 21 ]]; then
    start_date=`date -d "$current_month-01 - 1 month" +"%Y-%m-%d"`;
else
    start_date=`date -d "$current_month-01 - 2 month" +"%Y-%m-%d"`;
fi

end_date=`date -d "$start_date + 1 month" +"%Y-%m-%d"`;

#echo $start_date, $end_date;

# loop through each date in the month
loop_date=$start_date;
while [[ $loop_date < $end_date ]]; do
    date -d $loop_date +"%Y %m %d" |xargs -n 3 bash chirps_download_and_cog.sh;
    loop_date=`date -d "$loop_date + 1 day" +"%Y-%m-%d"`;
done
