function testing() {
  $.ajax({
    type: "GET",
    url: "/get_dosen",
    cache: false,
    beforeSend: () => {
      showLoading();
    },
    complete: () => {
      hideLoading();
    },
    success: async function (res) {
      console.log("res ajax", res);
      asd = res;
    },
  });
}

window.showLoading = function () {
  document.getElementById("loadingModal").style.display = "flex";
};

window.hideLoading = function () {
  document.getElementById("loadingModal").style.display = "none";
};

/**
 * @param {string} [icon] - The icon type (e.g., "success", "error", "warning", "info"). Leave as `undefined` to skip.
 * @param {string} [title] - The title text. Leave as `undefined` to skip.
 * @param {string} [text] - The message text. Leave as `undefined` to skip.
 * @param {number} [timer] - The duration in milliseconds before closing. Leave as `undefined` for default behavior.
 */
window.popUpTimer = async function (icon, title, text = null, timer = 1000) {
  await Swal.fire({
    position: "center",
    icon: icon ?? "error",
    title: title ?? "Terjadi kesalahan pada sistem.",
    text: text ?? null,
    showConfirmButton: false,
    timer: timer ?? 1000,
  });
};

/**
 * Creating empty row contains of empty columns data of the specified datatable.
 */
window.createEmptyRow = function (dataTable) {
  let emptyRow = {};
  dataTable.columns().every(function (index) {
    let columnData = this.dataSrc();
    if (columnData !== null) emptyRow[columnData] = "";
  });
  return emptyRow;
};

/**
 * Adding a new row to the specified datatable.
 */
window.addRow = function (dataTable) {
  if (dataTable.rows().count() > 0) {
    // cek apakah datatable punya baris ?
    let tableId = dataTable.table().node().id; // ambil id table yang digunakan pada datatable
    let lastRow = $("#" + tableId + " tbody tr:last td:first input")
      .val()
      .trim();
    if (!lastRow) return false;
  }

  let emptyRow = createEmptyRow(dataTable);

  dataTable.row.add(emptyRow).draw(false);

  return true;
};

window.addRowButton = function (dataTable) {
  let tableId = dataTable.table().node().id; // ambil id table yang digunakan pada datatable

  addRow(dataTable);

  $("#" + tableId + " tbody tr:last td:first input")
    .click()
    .focus();

  return true;
};
