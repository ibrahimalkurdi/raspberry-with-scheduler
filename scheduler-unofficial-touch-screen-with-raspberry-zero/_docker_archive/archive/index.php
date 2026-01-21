<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<title>عداد الأذان</title>

<!-- Load Lateef Arabic font -->
<link href="https://fonts.googleapis.com/css2?family=Lateef&display=swap" rel="stylesheet">

<style>
@import url('https://fonts.googleapis.com/css2?family=Lateef&display=swap');

html, body {
    height: 100%;
    margin: 0;
    font-family: 'Lateef', 'Tahoma', sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: white;
    text-align: center;
}

#countdown-container {
    background-color: #808080;
    color: white;
    width: 100vw;
    height: 100vh;
    margin: 0;
    padding: 3vh 3vw;
    border-radius: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    box-sizing: border-box;
}

#title-text {
    font-size: 6vw;
    margin-bottom: 4vh;
    font-weight: normal;
}

#prayerName {
    font-size: 12vw;
    font-weight: bold;
    margin-bottom: 2vh;
    line-height: 1.1;
}

#countdown {
    font-size: 40vw;
    font-weight: bold;
    line-height: 1;
    margin: 0;
    padding: 0;
}

@media (max-width: 480px) {
    #title-text {
        font-size: 8vw;
    }
    #prayerName {
        font-size: 15vw;
    }
    #countdown {
        font-size: 30vw;
    }
}
</style>

</head>
<body>
<div id="countdown-container">
    <h3 id="title-text">الوقت المتبقي لأذان</h3>
    <div id="prayerName">الفجر (غداً)</div>
    <div id="countdown"></div>
</div>

<?php
// Read the entire CSV into a date-keyed associative array
// Each entry: "M-D" => ["الفجر"=>"HH:MM", "الشروق"=>"HH:MM", ...]
$prayers_by_date = [];
if (($handle = fopen("berlin_prayer_times.csv", "r")) !== false) {
    $header = fgetcsv($handle); // Skip header
    while (($data = fgetcsv($handle)) !== false) {
        $month = intval($data[0]);
        $day = intval($data[1]);
        $key = "{$month}-{$day}";
        $prayers_by_date[$key] = [
            "الفجر"   => $data[2],
            "الشروق"  => $data[3],
            "الظهر"   => $data[4],
            "العصر"   => $data[5],
            "المغرب"  => $data[6],
            "العشاء"  => $data[7]
        ];
    }
    fclose($handle);
}
?>

<script>
// Full year map injected from PHP
const prayersByDate = <?php echo json_encode($prayers_by_date, JSON_UNESCAPED_UNICODE); ?>;

// Ordered prayer names (matching CSV order)
const prayerOrder = ["الفجر","الشروق","الظهر","العصر","المغرب","العشاء"];

function parseHM(timeStr) {
    if (!timeStr) return null;
    const parts = timeStr.split(':').map(Number);
    return { h: parts[0], m: parts[1] };
}

function keyForDate(d) {
    return `${d.getMonth()+1}-${d.getDate()}`;
}

// Return time string "HH:MM" for given date and prayer name, or null if not available
function getTimeStringForDate(d, prayerName) {
    const key = keyForDate(d);
    const row = prayersByDate[key];
    if (!row) return null;
    return row[prayerName] || null;
}

// Build a Date object that represents that prayer occurrence on that date
function buildPrayerDateFromString(dateObj, timeStr) {
    const parts = parseHM(timeStr);
    if (!parts) return null;
    const dt = new Date(dateObj);
    dt.setHours(parts.h, parts.m, 0, 0);
    return dt;
}

// Next occurrence: prefer same-day time if it's in the future, otherwise use next day's CSV time
function nextOccurrence(prayerName, refNow) {
    // try same-day
    const tToday = getTimeStringForDate(refNow, prayerName);
    if (tToday) {
        let dt = buildPrayerDateFromString(refNow, tToday);
        if (dt > refNow) return dt;
    }

    // fallback: use tomorrow's CSV time (if available)
    const tomorrow = new Date(refNow);
    tomorrow.setDate(tomorrow.getDate() + 1);
    const tTomorrow = getTimeStringForDate(tomorrow, prayerName);
    if (tTomorrow) {
        return buildPrayerDateFromString(tomorrow, tTomorrow);
    }

    // last resort (shouldn't happen with a full-year CSV): take today's time but force it to tomorrow
    if (tToday) {
        const dtForced = buildPrayerDateFromString(refNow, tToday);
        dtForced.setDate(dtForced.getDate() + 1);
        return dtForced;
    }

    return null;
}

// Previous occurrence: prefer same-day time if it's <= now, otherwise use yesterday's CSV time
function prevOccurrence(prayerName, refNow) {
    // try same-day
    const tToday = getTimeStringForDate(refNow, prayerName);
    if (tToday) {
        let dt = buildPrayerDateFromString(refNow, tToday);
        if (dt <= refNow) return dt;
    }

    // fallback: use yesterday's CSV time (if available)
    const yesterday = new Date(refNow);
    yesterday.setDate(yesterday.getDate() - 1);
    const tYesterday = getTimeStringForDate(yesterday, prayerName);
    if (tYesterday) {
        return buildPrayerDateFromString(yesterday, tYesterday);
    }

    // last resort: take today's time but force it to yesterday
    if (tToday) {
        const dtForced = buildPrayerDateFromString(refNow, tToday);
        dtForced.setDate(dtForced.getDate() - 1);
        return dtForced;
    }

    return null;
}

function getPrevNextPrayer(now) {
    let prevPrayer = null, nextPrayer = null;
    let prevTime = null, nextTime = null;

    for (let i = 0; i < prayerOrder.length; i++) {
        const name = prayerOrder[i];

        const nTime = nextOccurrence(name, now);
        if (nTime && nTime > now && (!nextTime || nTime < nextTime)) {
            nextPrayer = name;
            nextTime = nTime;
        }

        const pTime = prevOccurrence(name, now);
        if (pTime && pTime <= now && (!prevTime || pTime > prevTime)) {
            prevPrayer = name;
            prevTime = pTime;
        }
    }

    // Safety: if still missing nextPrayer (very unlikely), try tomorrow's Fajr explicitly
    if (!nextPrayer) {
        const tomorrow = new Date(now);
        tomorrow.setDate(tomorrow.getDate() + 1);
        const fajrStr = getTimeStringForDate(tomorrow, "الفجر");
        if (fajrStr) {
            nextPrayer = "الفجر";
            nextTime = buildPrayerDateFromString(tomorrow, fajrStr);
        }
    }

    return { prevPrayer, nextPrayer, prevTime, nextTime };
}

function updateCountdown() {
    const container = document.getElementById("countdown-container");
    const div = document.getElementById("countdown");
    const nameEl = document.getElementById("prayerName");
    const now = new Date();

    const { prevPrayer, nextPrayer, prevTime, nextTime } = getPrevNextPrayer(now);

    if (!prevPrayer || !nextPrayer || !prevTime || !nextTime) {
        div.textContent = "--:--";
        container.style.backgroundColor = "#808080";
        nameEl.textContent = "";
        return;
    }

    const timeSincePrev = (now - prevTime) / 1000; // seconds
    const timeUntilNext = (nextTime - now) / 1000; // seconds

    // Format countdown as HH:MM (hours may be > 24 in edge case; but should be small)
    const hours = Math.floor(timeUntilNext / 3600);
    const minutes = Math.floor((timeUntilNext % 3600) / 60);
    div.textContent = String(hours).padStart(2, '0') + ':' + String(minutes).padStart(2, '0');

    // Show next prayer name and if it's tomorrow (when nextTime is on a different date)
    let label = nextPrayer;
    const nowKey = `${now.getFullYear()}-${now.getMonth()+1}-${now.getDate()}`;
    const nextKey = `${nextTime.getFullYear()}-${nextTime.getMonth()+1}-${nextTime.getDate()}`;
    if (nowKey !== nextKey) label += " (غداً)";
    nameEl.textContent = label;

    // Background color logic
    if (timeSincePrev >= 0 && timeSincePrev <= 1200) {
        container.style.backgroundColor = "#00cc00"; // within 20 minutes after previous prayer
    } else if (timeUntilNext > 0 && timeUntilNext <= 1200) {
        container.style.backgroundColor = "#ff0000"; // within 20 minutes before next prayer
    } else {
        container.style.backgroundColor = "#808080";
    }
}

// Initialize and update every second
updateCountdown();
setInterval(updateCountdown, 1000);
</script>

</body>
</html>

