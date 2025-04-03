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
window.popUpTimer = async function (icon, title, text = null, timer = null) {
  await Swal.fire({
    position: "center",
    icon: icon ?? "error",
    title: title ?? "Terjadi kesalahan pada sistem.",
    text: text ?? null,
    showConfirmButton: false,
    timer: timer ?? Math.max(1000, title.length * 75), // Hitung timer berdasarkan panjang title (75ms per karakter, minimal 1000ms)
    timerProgressBar: true,
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

window.yearInput = function (targetValue) {
  let today = new Date();
  let currentYear = today.getFullYear();
  let maxYear = today.getMonth() >= 7 ? currentYear : currentYear - 1; // Agustus = index 7
  let minYear = maxYear - 7;

  // Hanya angka & maksimal 4 digit
  let sanitizedValue = targetValue.replace(/[^0-9]/g, "").slice(0, 4);

  // Jika sudah 4 digit, cek apakah dalam rentang yang diizinkan
  if (sanitizedValue.length === 4) {
    let year = parseInt(sanitizedValue, 10);
    if (year < minYear) {
      popUpTimer("error", "Angkatan " + year + " terlalu tua!");
      sanitizedValue = minYear; // Ubah ke tahun tertua jika tidak valid
    } else if (year > maxYear) {
      popUpTimer("error", "Angkatan " + year + " belum ada!");
      sanitizedValue = maxYear; // Ubah ke tahun termuda jika tidak valid
    }
  }

  return sanitizedValue;
};
