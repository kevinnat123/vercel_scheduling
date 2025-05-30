from io import BytesIO
from flask import render_template, Blueprint, request, jsonify, session, redirect, url_for, send_file
from dao.admin.generateJadwalDao import generateJadwalDao
from dao import genetic_algorithm as ga
from flask_login import login_required
from datetime import datetime
import xlsxwriter
from collections import defaultdict

generateJadwal = Blueprint('generateJadwal', __name__)
dao = generateJadwalDao()

@generateJadwal.route("/generate_jadwal")
@login_required
def generateJadwal_index():
    print(f"{'[ RENDER ]':<15} Generate Jadwal (Role: {session['user']['role']})")
    if session['user']['role'] != 'ADMIN':
        return redirect(url_for('signin.error403'))
    else:
        return render_template(
            '/admin/generate_jadwal/index.html', 
            menu = 'Generate Jadwal', 
            title = 'Generate Jadwal', 
        )
    
@generateJadwal.route("/generate_jadwal/generate", methods=['GET'])
@login_required
def generate_jadwal():
    print(f"{'[ CONTROLLER ]':<15} Generate Jadwal")

    try:
        data_dosen = dao.get_dosen()
        data_matkul = dao.get_matkul()
        data_ruang = dao.get_kelas()

        best_schedule = ga.genetic_algorithm(
            data_matkul, data_dosen, data_ruang, 
            ukuran_populasi=75, jumlah_generasi=1, peluang_mutasi=0.05
        )

        filename = "Jadwal_Kuliah_Semester-" + session['academic_details']['semester_depan'] + "_" + session['academic_details']['tahun_ajaran_berikutnya'].replace("/", "-")

        dao.upload_jadwal(best_schedule)
    except Exception as e:
        print(f"{'[ CONTRO ERROR ]':<15} Error: {e}")
        return jsonify({ 'status': False, 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })

    return jsonify({ 'status': True, 'data': best_schedule, 'filename': filename })

@generateJadwal.route("/generate_jadwal/upload_jadwal", methods=['POST'])
@login_required
def upload_jadwal():
    print(f"{'[ CONTROLLER ]':<15} Upload Jadwal")
    if session['user']['role'] == "ADMIN":
        req = request.get_json('data')
        data = dao.upload_jadwal(req['jadwal'])

    return jsonify( data )

@generateJadwal.route("/generate_jadwal/download_excel", methods=['POST'])
@login_required
def inputpricebystore_downloadExcel():
    print(f"{'[ CONTROLLER ]':<15} Download Excel")
    req = request.get_json('data')
    filename = req['filename']
    ga_result = req['jadwal']

    data_dosen = dao.get_dosen()
    data_matkul = dao.get_matkul()

    excel = export_jadwal_to_excel(ga_result, data_matkul, data_dosen)
    return send_file(excel, as_attachment=True, download_name=f"{filename}.xls")

def get_current_datetime():
    # return datetime.now().strftime('%d-%m-%Y %I-%M-%S')  # 12-hour format
    return datetime.now().strftime('%d-%m-%Y %H-%M-%S')  # 24-hour format

def export_jadwal_to_excel(jadwal_list, matakuliah_list, dosen_list):
    print(f"{'[ CONTROLLER ]':<15} Building File Excel")
    output = BytesIO()

    fixed_headers = [
        'kode_matkul', 'nama_matkul',
        'kode_dosen', 'nama_dosen', 'sks_akademik', 
        'kode_ruangan', 'kapasitas', 
        'hari', 'jam_mulai', 'jam_selesai',
        'tipe_kelas'
    ]

    workbook = xlsxwriter.Workbook(output)

    # 🔹 Group berdasarkan program_studi
    grouped = defaultdict(list)
    for jadwal in jadwal_list:
        grouped[jadwal['program_studi']].append(jadwal)

    # Format header
    format_header = workbook.add_format({
        'align': 'center',
        'bg_color': '#99CCFF',
        'valign': 'vcenter',
        'bold': True
    })
    format_as = workbook.add_format({
        'align': 'center',
        'bg_color': '#b9ebc6',
    })

    # Loop setiap group dan tulis ke sheet terpisah
    for program_studi in sorted(grouped.keys()):
        sheet_name = program_studi[:31]  # Sheet name max 31 chars
        worksheet = workbook.add_worksheet(sheet_name)

        row_idx = 0
        col_widths = [len(h) for h in jadwal_list]

        # Tulis header kolom
        for col_idx, header in enumerate(fixed_headers):
            worksheet.write(row_idx, col_idx, header.replace('_', ' '), format_header)
        row_idx += 1

        # Sort dan tulis data
        # sorted_group = sorted(grouped[program_studi], key=lambda x: (x.kode_ruangan, x.hari, x.jam_mulai))
        sorted_group = sorted(grouped[program_studi], key=lambda x: x['kode_matkul'])
        for jadwal in sorted_group:
            for col_idx, attr in enumerate(fixed_headers):
                if attr == "nama_matkul":
                    value = jadwal['kode_matkul']
                    value = next((m['nama'] for m in matakuliah_list if m['kode'] == value[:-1] or m['kode'] == value[:-4]), None)
                elif attr == "nama_dosen":
                    value = jadwal['kode_dosen']
                    value = next((d['nama'] for d in dosen_list if d['nip'] == value), None)
                elif attr == "kapasitas":
                    value = jadwal['kode_matkul']
                    if value[-2:] == "AS":
                        kapasitas_dosen = next((sesi['kapasitas'] for sesi in jadwal_list if sesi['kode_matkul'] == value[:-3]), None)
                        value = kapasitas_dosen
                    else:
                        value = jadwal[attr]
                else:
                    value = jadwal[attr]

                worksheet.write(row_idx, col_idx, value, format_as if jadwal['kode_dosen'] == "AS" else None)

                val_len = len(str(value))
                if val_len > col_widths[col_idx]:
                    col_widths[col_idx] = val_len
            row_idx += 1

        # Set lebar kolom
        for col_idx, width in enumerate(col_widths):
            worksheet.set_column(col_idx, col_idx, width + 2)

        # Data beban dosen
        beban_dosen = {}
        for sesi in sorted_group:
            if sesi['kode_dosen'] != "AS":
                if sesi['kode_dosen'] not in beban_dosen: beban_dosen[sesi['kode_dosen']] = 0
                beban_dosen[sesi['kode_dosen']] += sesi['sks_akademik']
        # Tulis data beban dosen
        start_col = len(fixed_headers) + 2
        row_idx = 0
        worksheet.write(row_idx, start_col, "NIP", format_header)
        worksheet.write(row_idx, start_col + 1, "Nama", format_header)
        worksheet.write(row_idx, start_col + 2, "Beban SKS", format_header)
        row_idx += 1
        
        for nip, sks in dict(sorted(beban_dosen.items())).items():
            nama_dosen = next((d['nama'] for d in dosen_list if d['nip'] == nip), None)
            worksheet.write(row_idx, start_col, nip)
            worksheet.write(row_idx, start_col + 1, nama_dosen)
            worksheet.write(row_idx, start_col + 2, sks)
            row_idx += 1

    # Simpan workbook
    workbook.close()
    output.seek(0)
    return output