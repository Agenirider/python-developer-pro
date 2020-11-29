REPORT_TEMPLATE = '''<!doctype html>

<html lang="en">
<head>
  <meta charset="utf-8">
  <title>rbui log analysis report</title>
  <meta name="description" content="rbui log analysis report">
  <style type="text/css">
    html, body {
      background-color: black;
    }
    th {
      text-align: center;
      color: silver;
      font-style: bold;
      padding: 5px;
      cursor: pointer;
    }
    table {
      width: auto;
      border-collapse: collapse;
      margin: 1%;
      color: silver;
    }
    td {
      text-align: right;
      font-size: 1.1em;
      padding: 5px;
    }
    .report-table-body-cell-url {
      text-align: left;
      width: 20%;
    }
    .clipped {
      white-space: nowrap;
      text-overflow: ellipsis;
      overflow:hidden !important;
      max-width: 700px;
      word-wrap: break-word;
      display:inline-block;
    }
    .url {
      cursor: pointer;
      color: #729FCF;
    }
    .alert {
      color: red;
    }
  </style>
</head>

<body>
  <table border="1" class="report-table">
  <thead>
    <tr class="report-table-header-row">
    </tr>
  </thead>
  <tbody class="report-table-body">
  </tbody>

  <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
  <script type="text/javascript" src="/Users/s.stupnikov/Dev/hive7/home/s.stupnikov/custom/analyzer/jquery.tablesorter.min.js"></script> 
  <script type="text/javascript">
  !function($) {
    var table = {%table%};
    var reportDates;
    var columns = new Array();
    var lastRow = 150;
    var $table = $(".report-table-body");
    var $header = $(".report-table-header-row");
    var $selector = $(".report-date-selector");

    $(document).ready(function() {
      $(window).bind("scroll", bindScroll);
        var row = table[0];
        for (k in row) {
          columns.push(k);
        }
        columns = columns.sort();
        columns = columns.slice(columns.length -1, columns.length).concat(columns.slice(0, columns.length -1));
        drawColumns();
        drawRows(table.slice(0, lastRow));
        $(".report-table").tablesorter(); 
    });

    function drawColumns() {
      for (var i = 0; i < columns.length; i++) {
        var $th = $("<th></th>").text(columns[i])
                                .addClass("report-table-header-cell")
        $header.append($th);
      }
    }

    function drawRows(rows) {
      for (var i = 0; i < rows.length; i++) {
        var row = rows[i];
        var $row = $("<tr></tr>").addClass("report-table-body-row");
        for (var j = 0; j < columns.length; j++) {
          var columnName = columns[j];
          var $cell = $("<td></td>").addClass("report-table-body-cell");
          if (columnName == "url") {
            var url = "https://rb.mail.ru" + row[columnName];
            var $link = $("<a></a>").attr("href", url)
                                    .attr("title", url)
                                    .attr("target", "_blank")
                                    .addClass("clipped")
                                    .addClass("url")
                                    .text(row[columnName]);
            $cell.addClass("report-table-body-cell-url");
            $cell.append($link);
          }
          else {
            $cell.text(row[columnName]);
            if (columnName == "time_avg" && row[columnName] > 0.9) {
              $cell.addClass("alert");
            }
          }
          $row.append($cell);
        }
        $table.append($row);
      }
      $(".report-table").trigger("update"); 
    }

    function bindScroll() {
      if($(window).scrollTop() == $(document).height() - $(window).height()) {
        if (lastRow < 1000) {
          drawRows(table.slice(lastRow, lastRow + 50));
          lastRow += 50;
        }
      }
    }

  }(window.jQuery)
  </script>
</body>
</html>
 '''