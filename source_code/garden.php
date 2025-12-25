<!DOCTYPE HTML>
<html>
<style>
table {
    font-family: arial, sans-serif;
    border-collapse: collapse;
}

td, th {
    border: 2px solid black;
    text-align: left;
    padding: 8px;
    width: 150px;
}

tr:nth-child(even) {
    background-color: #dddddd;
}
</style>
 <head>
  <title>Garden water</title>
 </head>
 <body>

<?php
 exec('gpio mode 4 output');
 exec('gpio mode 5 output');
 exec('gpio mode 6 output');

 if (isset($_POST['valve_1_on'])) { exec('gpio write 4 1'); }
 if (isset($_POST['valve_1_off'])) { exec('gpio write 4 0'); }
 if (isset($_POST['valve_2_on'])) { exec('gpio write 5 1'); }
 if (isset($_POST['valve_2_off'])) { exec('gpio write 5 0'); }
 if (isset($_POST['valve_3_on'])) { exec('gpio write 6 1'); }
 if (isset($_POST['valve_3_off'])) { exec('gpio write 6 0'); }

    $countertxt1 = "Counter 1"; /* Counter 1 */
    $countertxt2 = "Counter 2"; /* Counter 2 */
    $countertxt3 = "Counter 3"; /* Counter 3 */

    $wlcntr1 = 0.0;
    $wlcntr2 = 0.0;
    $wlcntr3 = 0.0;

    $db = new SQLite3('/var/db/watermon.db');
    if (!$db)
    {
        exit($error);
    }

    $db->busyTimeout(1000);

    $statement = $db->prepare('SELECT * FROM Wcounters ORDER BY ROWID DESC LIMIT 1');
    if (!$statement)
    {
        exit("Cannot prepare SELECT statement.");
    }
    $results = $statement->execute();
    if (!$results)
    {
        exit("Cannot execute SELECT statement.");
    }

    if ($row = $results->fetchArray())
    {
        $wlcntr1 = $row[4];
        $wlcntr2 = $row[5];
        $wlcntr3 = $row[6];
    }

    header("refresh: 10;");

    echo sprintf("<H2>Water measurement</H2>\n");

    echo "<table>";
    echo "<tr>";
    echo sprintf("<th>%s</th>", $countertxt1);
    echo sprintf("<th>%s</th>", $countertxt2);
    echo sprintf("<th>%s</th>", $countertxt3);
    echo  "</tr>";
    echo  "<tr>";
    echo sprintf("<td>%01.2f</td>", $wlcntr1);
    echo sprintf("<td>%01.2f</td>", $wlcntr2);
    echo sprintf("<td>%01.2f</td>", $wlcntr3);
    echo "</tr>";
    echo "</table>";

?>

<h2>Valves on-off</h2>

<?php
  echo "Valve 1 (Dimkylning växthus): ";
  exec("gpio read 4", $output1, $result1);
  if ($output1[0] == "1") {
      echo "On";
  } else {
      echo "Off";
  }
?>
<form method="post">
      <button span style="font-size:20px;" name="valve_1_on">turn on</button>
      <button span style="font-size:20px;" name="valve_1_off">turn off</button>
</form>

<br>
<?php
  echo "Valve 2 (Bevattning odlingskragar): ";
  exec("gpio read 5", $output2, $result2);
  if ($output2[0] == "1") {
      echo "On";
  } else {
      echo "Off";
  }
?>
<form method="post">
      <button span style="font-size:20px;" name="valve_2_on">turn on</button>
      <button span style="font-size:20px;" name="valve_2_off">turn off</button>
</form>

<br>
<?php
  echo "Valve 3 (Bevattning växthus): ";
  exec("gpio read 6", $output3, $result3);
  if ($output3[0] == "1") {
      echo "On";
  } else {
      echo "Off";
  }
?>
<form method="post">
      <button span style="font-size:20px;" name="valve_3_on">turn on</button>
      <button span style="font-size:20px;" name="valve_3_off">turn off</button>
</form>

<H2>Administration</H2>
<li>
   <a href="phpliteadmin.php">Database administration</a>
</li>

 </body>
</html>
