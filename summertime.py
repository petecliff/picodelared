# Used from https://www.robmiles.com/journal/2020/10/12/maketober-day-12-fun-with-british-summer-time
# Thank you!

def summerTime(time):
    year=time[0]
    month = time[1]
    day = time[2]
    hour = time[3]
    #print("Test: ", year,month,day,hour)
    if month<3 or month>10: return False
    if month>3 and month<10: return True
    if month==3:
        hours_into_March = hour + (24 * day)
        date_of_Sunday = 31 - ((year + int(year/4) + 4) % 7)
        summertime_start = 2 + 24*date_of_Sunday
        #print("   Date of Sunday: ", date_of_Sunday)
        #print("   Hours into March: ", hours_into_March)
        #print("   Summertime start: ", summertime_start)
        if hours_into_March>=summertime_start: return True
    if month==10:
        hours_into_October = hour + (24 * day)
        date_of_Sunday = 31 - ((year + int(year/4) + 1) % 7) 
        summertime_end = 2 + 24*date_of_Sunday
        #print("   Date of Sunday: ", date_of_Sunday)
        #print("   Hours into October: ", hours_into_October)
        #print("   Summertime end: ", summertime_end)
        if hours_into_October<summertime_end: return True
    return False