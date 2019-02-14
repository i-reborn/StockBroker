
function searchItem() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("stockInput");
    filter = input.value.toUpperCase();
    table = document.getElementById("stockTable");
    var counter=0;
    tr = table.getElementsByTagName("tr");
    for (i = 0; i < tr.length; i++) {
      td = tr[i].getElementsByTagName("td")[0];
      if (td) {
        txtValue = td.textContent || td.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1 && counter<10) {
          tr[i].style.display = "";
          counter++;
        } else {
          tr[i].style.display = "none";
        }
      }       
    }
  }
