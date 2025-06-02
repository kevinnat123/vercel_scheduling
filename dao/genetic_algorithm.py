import random, copy

class JadwalKuliah:
    def __init__(
            self, 
            kode_matkul, kode_dosen, sks_akademik, kode_ruangan, kapasitas, 
            hari, jam_mulai, jam_selesai, 
            tipe_kelas, program_studi):
        self.kode_matkul = kode_matkul
        self.kode_dosen = kode_dosen
        self.sks_akademik = sks_akademik
        self.kode_ruangan = kode_ruangan
        self.kapasitas = kapasitas
        self.hari = hari
        self.jam_mulai = jam_mulai
        self.jam_selesai = jam_selesai
        self.tipe_kelas = tipe_kelas  # 'TEORI' atau 'PRAKTIKUM'
        self.program_studi = program_studi

# TO BE CHECKED:
# (15)  Jadwal Ruangan Bertabrakan                                  >> ruangan_bentrok           (DONE)
# (15)  Jadwal Dosen Bertabrakan                                    >> dosen_bentrok             (DONE)
# (15)  Jadwal Dosen dan Asisten Berjalan Bersamaan                 >> asdos_nabrak_dosen        (DONE)
# (15)  Kelas Dosen atau Asisten Hilang atau Tidak Lengkap          >> kelas_gaib                (DONE)
# (10)  Beban SKS Dosen melebihi 12 sks                             >> dosen_overdosis           (DONE)
# (10)  Matkul berlangsung sebelum pukul 7 atau sesudah pukul 19    >> diluar_jam_kerja          (DONE)
# (10)  Cek Total Kelas Bisa Cangkup Semua Mahasiswa                >> kapasitas_kelas_terbatas  (DONE)
# (5)   Tidak Sesuai dengan permintaan / request dosen              >> melanggar_preferensi      (DONE)
BOBOT_PENALTI = {
    "ruangan_bentrok": 15,
    "dosen_bentrok": 15,
    "asdos_nabrak_dosen": 15,
    "dosen_overdosis": 10,
    "diluar_jam_kerja": 10,
    "melanggar_preferensi": 5,
    "kelas_gaib": 15,
    "kapasitas_kelas_terbatas": 10,

    "weekend_class": 10,
    "istirahat": 5,
    "salah_tipe_ruangan": 3,
}

def convertOutputToDict(jadwal_list):
    """
    Menkonversi object jadwal menjadi dictionary.

    Returns:
        dict: Jadwal dalam bentuk dictionary.
    """

    jadwal = []

    for sesi in jadwal_list:
        s = {}
        s['kode_matkul'] = sesi.kode_matkul
        s['kode_dosen'] = sesi.kode_dosen
        s['sks_akademik'] = sesi.sks_akademik
        s['kode_ruangan'] = sesi.kode_ruangan
        s['kapasitas'] = sesi.kapasitas
        s['hari'] = sesi.hari
        s['jam_mulai'] = sesi.jam_mulai
        s['jam_selesai'] = sesi.jam_selesai
        s['tipe_kelas'] = sesi.tipe_kelas  # 'TEORI' atau 'PRAKTIKUM'
        s['program_studi'] = sesi.program_studi
        jadwal.append(s)

    return jadwal

def find_available_schedule(jadwal:list, kode:str, hari:str):
    """
    Mencari waktu yang tersedia dari jadwal yang sudah ada berdasarkan hari yang dipilih.

    Args:
        jadwal (list): List jadwal yang sudah ada.
        kode (str): Kode yang akan diperiksa (kode ruangan / nip).
        hari (str): Hari yang akan diperiksa jadwalnya.

    Returns:
        list: List jadwal yang bisa digunakan (jam).
    """
    
    pilihan_jam = list(range(7, 19)) if hari != "SABTU" else list(range(7, 13))
    
    jadwal_sesuai_hari = [sesi for sesi in jadwal[kode] if sesi['hari'] == hari] if jadwal[kode] else []
    used_jam = []
    for sesi in jadwal_sesuai_hari:
        used_jam.extend(range(sesi['jam_mulai'], sesi['jam_selesai'] + 1))

    return [h for h in pilihan_jam if h not in used_jam]

def angka_ke_huruf(n: int):
    """
    Generate alphabet (A-Z) dari angka (n) yang diberikan.

    Args:
        n (int): Angka yang ingin diparsing ke alphabet.

    Returns:
        chr|None: Alphabet yang sesuai dengan angka yang diberikan.
    """

    if 1 <= int(n) <= 26:
        return chr(64 + n)  # Karena ord('A') = 65
    else:
        return None  # Diluar jangkauan 1-26
    
def find_missing_course(jadwal, matakuliah_list):
    kode_matkul = []
    for matkul in matakuliah_list:
        kode_matkul.append(matkul['kode'])

    sesi_matkul = []
    for sesi in jadwal:
        if sesi.kode_dosen != "AS" and sesi.kode_matkul[:-1] not in sesi_matkul:
            sesi_matkul.append(sesi.kode_matkul[:-1])

    missing = []
    for kode in kode_matkul:
        if kode not in sesi_matkul:
            missing.append(kode)

    return missing

def repair_jadwal(jadwal, matakuliah_list, dosen_list, ruang_list):
    pilihan_hari_dosen = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT"]
    pilihan_hari_asisten = copy.deepcopy(pilihan_hari_dosen)
    pilihan_hari_asisten.append("SABTU")

    max_attempt = 10

    jadwal_dosen = {} # Cek Jadwal Dosen {'kode': [{'hari': '', 'jam_mulai': 0, 'jam_selesai': 0}]}
    jadwal_ruangan = {} # Cek Jadwal Ruangan {'kode': [{'hari': '', 'jam_mulai': 0, 'jam_selesai': 0}]}
    beban_dosen = {} # Cek SKS Dosen {'kode': 0}

    # AMBIL INITIAL
    for ruang in ruang_list:
        if ruang['kode'] not in jadwal_ruangan: jadwal_ruangan[ruang['kode']] = []
    for dosen in dosen_list:
        if dosen['nip'] not in jadwal_dosen: jadwal_dosen[dosen['nip']] = []
        if dosen['nip'] not in beban_dosen: beban_dosen[dosen['nip']] = 0

    # HAPUS DATA MATKUL DUPLIKAT
    seen_kode_matkul = set()
    filtered_jadwal = []

    for sesi in jadwal:
        if sesi.kode_matkul not in seen_kode_matkul:
            seen_kode_matkul.add(sesi.kode_matkul)
            filtered_jadwal.append(sesi)
        # else:
        #     print(sesi.kode_matkul)

    jadwal = filtered_jadwal

    # LOOP PERTAMA:
    # - REPAIR DOSEN DENGAN SKS BERLEBIH (DONE)
    # - REPAIR JADWAL DOSEN BENTROK (DONE)
    # - PENUHI KAPASITAS KELAS KALAU BERKURANG
    for sesi_dosen in jadwal:
        if sesi_dosen.kode_dosen != "AS":
            matkul = next((m for m in matakuliah_list if m['kode'] == sesi_dosen.kode_matkul[:-1]), None)
            dosen = next((d for d in dosen_list if d['nip'] == sesi_dosen.kode_dosen), None)
            preferensi_hari_dosen = [d for d in pilihan_hari_dosen if d not in dosen['preferensi']['hindari_hari']]

            if matkul:
                conflict = False

                # Repair Dosen dg SKS Berlebih
                if beban_dosen[dosen['nip']] > (12 - sesi_dosen.sks_akademik):
                    dosen_pakar = [
                        d for d in dosen_list 
                            if (d["prodi"] == matkul['prodi'] or d['status'] == "DOSEN TIDAK TETAP") and 
                                len(set(d['kepakaran']) & set(matkul['bidang'])) > 0
                    ]
                    if len(dosen_pakar) > 1:
                        calon_dosen_pengganti = [d for d in dosen_pakar if beban_dosen[d['nip']] + sesi_dosen.sks_akademik <= 12]
                        if not calon_dosen_pengganti:
                            sks_dosen_pakar = [value for key, value in beban_dosen.items() if key in [d['nip'] for d in dosen_pakar]]
                            calon_dosen_pengganti = [
                                d for d in dosen_pakar
                                    if (
                                        beban_dosen[d['nip']] < max(sks_dosen_pakar) 
                                        if any(sks < max(sks_dosen_pakar) for sks in sks_dosen_pakar) 
                                        else beban_dosen[d['nip']] <= max(sks_dosen_pakar))
                            ]
                        bobot_calon_dosen_pengganti = [
                            len(set(d['kepakaran']) & set(matkul['bidang'])) > 0
                            for d in calon_dosen_pengganti
                        ]
                        dosen = random.choices(
                            population=calon_dosen_pengganti, 
                            weights=bobot_calon_dosen_pengganti, 
                            k=1)[0]
                        sesi_dosen.kode_dosen = dosen['nip']

                for sesi_lain in jadwal_ruangan[sesi_dosen.kode_ruangan]:
                    if sesi_dosen.hari == sesi_lain['hari']:
                        if sesi_dosen.jam_mulai < sesi_lain['jam_selesai'] and sesi_dosen.jam_selesai > sesi_lain['jam_mulai']:
                            conflict = True
                            break

                for sesi_lain in jadwal_dosen[sesi_dosen.kode_dosen]:
                    if sesi_dosen.hari == sesi_lain['hari']:
                        if sesi_dosen.jam_mulai < sesi_lain['jam_selesai'] and sesi_dosen.jam_selesai > sesi_lain['jam_mulai']:
                            conflict = True
                            break

                attempt = 1
                excluded_day = []
                excluded_room = []
                # Repair Jadwal Dosen Bentrok
                while conflict and attempt <= max_attempt:
                    # print(sesi_dosen.kode_matkul, sesi_dosen.kode_dosen, sesi_dosen.sks_akademik, sesi_dosen.hari)
                    available_room_schedule = find_available_schedule(jadwal_ruangan, sesi_dosen.kode_ruangan, sesi_dosen.hari)
                    available_lecturer_schedule = find_available_schedule(jadwal_dosen, sesi_dosen.kode_dosen, sesi_dosen.hari)
                    # print('room     ', available_room_schedule)
                    # print('lecture  ', available_lecturer_schedule)
                    
                    available_schedule = list(set(available_room_schedule) & set(available_lecturer_schedule))
                    
                    status = False
                    for jam in available_schedule:
                        rentang_waktu = list(range(jam, jam + matkul['sks_akademik'] + 1))
                        if all(r in available_schedule for r in rentang_waktu) and jam != 12:
                            status = True
                            conflict = False
                            sesi_dosen.jam_mulai = jam
                            sesi_dosen.jam_selesai = jam + matkul['sks_akademik']
                            break
                        else:
                            status = False

                    if not status:
                        excluded_day.append(sesi_dosen.hari)
                        # print('DOSEN pil ', pilihan_hari_dosen)
                        # print('DOSEN exc ', excluded_day)
                        # print('DOSEN     ', [d for d in pilihan_hari_dosen if d not in excluded_day])
                        # print('      ', available_schedule)
                        if all(d in excluded_day for d in preferensi_hari_dosen):
                            excluded_day = []
                            excluded_room.append(sesi_dosen.kode_ruangan)
                            calon_ruang_pengganti = [
                                r for r in ruang_list if 
                                    (matkul['prodi'] in r['plot'] or 'GENERAL' in r['plot']) and
                                    r['kapasitas'] >= 35 and # REMINDER: PENENTUAN KAPASITAS PERLU DIPERTIMBANGKAN
                                    (r['tipe_ruangan'] == matkul['tipe_kelas'] if matkul.get('asistensi') else r['tipe_ruangan'] in [matkul['tipe_kelas'], 'RAPAT']) and 
                                    r['kode'] not in excluded_room
                            ]
                            bobot_calon_ruang_pengganti = [
                                (len(set(r['plot']) & set(matkul['bidang']))*10 or 1) * (10 if matkul['prodi'] in r['plot'] else 1)
                                for r in calon_ruang_pengganti
                            ]
                            ruang_pengganti = random.choices(
                                population=calon_ruang_pengganti, 
                                weights=bobot_calon_ruang_pengganti, 
                                k=1)[0]
                            sesi_dosen.kode_ruangan = ruang_pengganti['kode']
                            sesi_dosen.kapasitas = ruang_pengganti['kapasitas']
                            sesi_dosen.tipe_kelas = ruang_pengganti['tipe_ruangan']
                        else:
                            sesi_dosen.hari = random.choice([d for d in preferensi_hari_dosen if d not in excluded_day])

                    attempt += 1
                
                beban_dosen[dosen['nip']] += sesi_dosen.sks_akademik
                jadwal_ruangan[sesi_dosen.kode_ruangan].append({'hari': sesi_dosen.hari, 'jam_mulai': sesi_dosen.jam_mulai, 'jam_selesai': sesi_dosen.jam_selesai})
                jadwal_dosen[sesi_dosen.kode_dosen].append({'hari': sesi_dosen.hari, 'jam_mulai': sesi_dosen.jam_mulai, 'jam_selesai': sesi_dosen.jam_selesai})
    
    # LOOP KEDUA:
    # 2. REPAIR JADWAL ASISTEN KALAU BENTRO K DENGAN KELAS LAIN (DONE)
    for sesi_asisten in jadwal:
        if sesi_asisten.kode_dosen == "AS": # KODE ASISTEN
            matkul = next((m for m in matakuliah_list if m['kode'] == sesi_asisten.kode_matkul[:-4]), None)

            if matkul:
                conflict = False

                sesi_dosen = next((sesi_dosen for sesi_dosen in jadwal if sesi_dosen.kode_matkul == sesi_asisten.kode_matkul[:-3]), None)
                suggested_hari_asisten = pilihan_hari_asisten[pilihan_hari_dosen.index(sesi_dosen.hari):]
                for sesi_lain in jadwal_ruangan[sesi_asisten.kode_ruangan]:
                    if sesi_asisten.hari == sesi_lain['hari']:
                        if sesi_asisten.jam_mulai < sesi_lain['jam_selesai'] and sesi_asisten.jam_selesai > sesi_lain['jam_mulai']:
                            conflict = True
                            break

                attempt = 1
                excluded_day = []
                excluded_room = []
                # 2. Repair Jadwal Asisten
                while conflict and attempt <= max_attempt:
                    # print(sesi_asisten.kode_matkul, sesi_asisten.kode_dosen, sesi_asisten.sks_akademik, sesi_asisten.hari)
                    available_room_schedule = find_available_schedule(jadwal_ruangan, sesi_asisten.kode_ruangan, sesi_asisten.hari)

                    status = False
                    for jam in available_room_schedule:
                        rentang_waktu = list(range(jam, jam + matkul['sks_akademik'] + 1))
                        if all(r in available_room_schedule for r in rentang_waktu) and jam != 12 and not (sesi_asisten.hari == sesi_dosen.hari and jam < sesi_dosen.jam_selesai and (jam + matkul['sks_akademik']) > sesi_dosen.jam_mulai):
                            status = True
                            conflict = False
                            sesi_asisten.jam_mulai = jam
                            sesi_asisten.jam_selesai = jam + matkul['sks_akademik']
                            break
                        else:
                            status = False

                    if not status:
                        excluded_day.append(sesi_asisten.hari)
                        # print('ASISTEN pil ', suggested_hari_asisten)
                        # print('ASISTEN exc ', excluded_day)
                        # print('ASISTEN     ', [d for d in suggested_hari_asisten if d not in excluded_day])
                        # print('      ', available_room_schedule)
                        if all(d in excluded_day for d in suggested_hari_asisten):
                            excluded_day = []
                            excluded_room.append(sesi_asisten.kode_ruangan)
                            calon_ruang_pengganti = [
                                r for r in ruang_list if 
                                    (matkul['prodi'] in r['plot'] or 'GENERAL' in r['plot']) and
                                    r['kapasitas'] >= sesi_dosen.kapasitas and
                                    r['tipe_ruangan'] == matkul['tipe_kelas_asistensi'] and
                                    r['kode'] not in excluded_room
                            ]
                            if calon_ruang_pengganti:
                                bobot_calon_ruang_pengganti = [
                                    (len(set(r['plot']) & set(matkul['bidang']))*10 or 1) * (10 if matkul['prodi'] in r['plot'] else 1)
                                    for r in calon_ruang_pengganti
                                ]
                                ruang_pengganti = random.choices(
                                    population=calon_ruang_pengganti, 
                                    weights=bobot_calon_ruang_pengganti, 
                                    k=1)[0]
                                sesi_asisten.kode_ruangan = ruang_pengganti['kode']
                                sesi_asisten.kapasitas = ruang_pengganti['kapasitas']
                                sesi_asisten.tipe_kelas = ruang_pengganti['tipe_ruangan']
                            else:
                                suggested_hari_asisten = pilihan_hari_asisten
                        else:
                            sesi_asisten.hari = random.choice([d for d in suggested_hari_asisten if d not in excluded_day])

                    attempt += 1
                
                jadwal_ruangan[sesi_asisten.kode_ruangan].append({'hari': sesi_asisten.hari, 'jam_mulai': sesi_asisten.jam_mulai, 'jam_selesai': sesi_asisten.jam_selesai})
    
    # # SWITCH SCHEDULE DOSEN x ASISTEN
    # for sesi_asisten in jadwal:
    #     if sesi_asisten.kode_matkul.endswith("-AS"):
    #         sesi_dosen = next((sd for sd in jadwal if sd.kode_matkul == sesi_asisten.kode_matkul[:-3]), None)
            
    #         tipe_ruang_dosen = next((r['tipe_ruangan'] for r in ruang_list if r['kode'] == sesi_dosen.kode_ruangan), None)
    #         tipe_ruang_asisten = next((r['tipe_ruangan'] for r in ruang_list if r['kode'] == sesi_asisten.kode_ruangan), None)

    #         if tipe_ruang_dosen == tipe_ruang_asisten:
    #             if pilihan_hari_dosen.index(sesi_dosen.hari) >= pilihan_hari_asisten.index(sesi_asisten.hari):
    #                 if sesi_dosen.jam_mulai > sesi_asisten.jam_selesai:
    #                     sesi_dosen.kode_ruangan, sesi_asisten.kode_ruangan = sesi_asisten.kode_ruangan, sesi_dosen.kode_ruangan
    #                     sesi_dosen.hari, sesi_asisten.hari = sesi_asisten.hari, sesi_dosen.hari
    #                     sesi_dosen.jam_mulai, sesi_asisten.jam_mulai = sesi_asisten.jam_mulai, sesi_dosen.jam_mulai
    #                     sesi_dosen.jam_selesai, sesi_asisten.jam_selesai = sesi_asisten.jam_selesai, sesi_dosen.jam_selesai
    #                     # print(f"{'':<3}Switched {sesi_dosen.kode_matkul} <--> {sesi_asisten.kode_matkul}")
        
    return jadwal

def generate_jadwal(matakuliah_list, dosen_list, ruang_list):
    jadwal = []
    pilihan_hari_dosen = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT"]
    pilihan_hari_asisten: list[str] = copy.deepcopy(pilihan_hari_dosen)
    pilihan_hari_asisten.append("SABTU")

    jadwal_dosen = {}    # {nip: [ {hari, jam_mulai, jam_selesai}, ... ]}
    jadwal_ruangan = {}  # {kode_ruangan: [ {hari, jam_mulai, jam_selesai}, ... ]}
    beban_dosen = {} # {nip: beban_sks}

    for dt in dosen_list:
        beban_dosen[dt['nip']] = 0

    max_attempt = 10

    for matkul in matakuliah_list:
        dosen_pakar = [
            d for d in dosen_list 
                if (d["prodi"] == matkul['prodi'] or d['status'] == "DOSEN TIDAK TETAP") and 
                    len(set(d['kepakaran']) & set(matkul['bidang'])) > 0
        ]
        
        # RUANGAN
        ruangan_prodi = [r for r in ruang_list if (matkul['prodi'] in r['plot'] or 'GENERAL' in r['plot'])]
        ruangan_prodi_prioritas = [r for r in ruangan_prodi if r['kapasitas'] > 35 and (r['tipe_ruangan'] != 'RAPAT' if matkul.get('asistensi') else True)]
        bobot_ruangan_prodi = [(len(set(r['plot']) & set(matkul['bidang']))*10 or 1) + int(r['kapasitas']) + (100 if r['tipe_ruangan'] == matkul['tipe_kelas'] else 1) for r in ruangan_prodi_prioritas or ruangan_prodi]
        
        ruangan_prodi_prioritas_praktikum = [r for r in ruangan_prodi if not (r['kapasitas'] > max([r['kapasitas'] for r in ruangan_prodi if r['tipe_ruangan'] == "PRAKTIKUM"])) and r['tipe_ruangan'] != 'RAPAT']
        bobot_ruangan_prodi_prioritas_praktikum = [((len(set(r['plot']) & set(matkul['bidang']))*10 or 1) + int(r['kapasitas'])) * (100 if r['tipe_ruangan'] == matkul['tipe_kelas'] else 1) for r in ruangan_prodi_prioritas_praktikum if r['tipe_ruangan'] != 'RAPAT']
        
        jumlah_mahasiswa = matkul['jumlah_mahasiswa']
        index_kelas = 1
        
        while jumlah_mahasiswa > 0:
            if matkul.get('asistensi') and not matkul.get('integrated_class') and matkul.get('tipe_kelas_asistensi') == "PRAKTIKUM":
                ruang_dosen = random.choices(
                    population=ruangan_prodi_prioritas_praktikum, 
                    weights=bobot_ruangan_prodi_prioritas_praktikum, 
                    k=1)[0]
            else:
                ruang_dosen = random.choices(
                    population=ruangan_prodi_prioritas or ruangan_prodi, 
                    weights=bobot_ruangan_prodi, 
                    k=1)[0]
            
            # PEMILIHAN DOSEN
            if len(dosen_pakar) > 1:
                calon_dosen = [d for d in dosen_pakar if beban_dosen[d['nip']] + matkul['sks_akademik'] <= 12]
                if not calon_dosen:
                    sks_dosen_pakar = [value for key, value in beban_dosen.items() if key in [d['nip'] for d in dosen_pakar]]
                    calon_dosen = [
                        d for d in dosen_pakar
                            if (
                                beban_dosen[d['nip']] < max(sks_dosen_pakar) 
                                if any(sks < max(sks_dosen_pakar) for sks in sks_dosen_pakar) 
                                else beban_dosen[d['nip']] <= max(sks_dosen_pakar))
                    ]
                bobot_calon_dosen = [
                    len(set(d['kepakaran']) & set(matkul['bidang'])) > 0
                    for d in calon_dosen
                ]
                dosen = random.choices(
                    population=calon_dosen, 
                    weights=bobot_calon_dosen, 
                    k=1)[0]
            else:
                dosen = dosen_pakar[0]

            if dosen['nip'] not in jadwal_dosen: jadwal_dosen[dosen['nip']] = []
            preferensi_hari = [hari for hari in pilihan_hari_dosen if hari not in dosen['preferensi']['hindari_hari']]
            hari_dosen = random.choice(preferensi_hari)

            sukses = False
            attempt = 0
            while not sukses and max_attempt >= attempt:
                if ruang_dosen['kode'] not in jadwal_ruangan: jadwal_ruangan[ruang_dosen['kode']] = []

                jadwal_dosen_sesuai_hari = [d for d in jadwal_dosen[dosen['nip']] if d['hari'] == hari_dosen] if jadwal_dosen[dosen['nip']] else []
                jadwal_ruangan_sesuai_hari = [d for d in jadwal_ruangan[ruang_dosen['kode']] if d['hari'] == hari_dosen] if jadwal_ruangan[ruang_dosen['kode']] else []

                if jadwal_ruangan_sesuai_hari:
                    list_jam_selesai_ruangan = [r['jam_selesai'] for r in jadwal_ruangan_sesuai_hari]
                    jam_terakhir_ruangan = max(list_jam_selesai_ruangan)
                    jam_mulai_dosen = jam_terakhir_ruangan if jam_terakhir_ruangan <= (18 - matkul['sks_akademik']) else 0
                else:
                    jam_mulai_dosen = 7

                if jam_mulai_dosen != 0:
                    jam_selesai_dosen = jam_mulai_dosen + matkul['sks_akademik']
                    sukses = True
                else:
                    hari_dosen = random.choice(preferensi_hari)

                # kalo jadwal dosen ganda, ubah hari
                for jd in jadwal_dosen_sesuai_hari:
                    if jd['hari'] == hari_dosen and (jd['jam_mulai'] < jam_mulai_dosen < jd['jam_selesai'] or jd['jam_mulai'] == jam_mulai_dosen):
                        hari_dosen = random.choice(preferensi_hari) if matkul['kode'][-3:] != '-AS' else random.choice(pilihan_hari_asisten)
                        sukses = False

                attempt += 1

            sesi_dosen = JadwalKuliah(
                kapasitas       = ruang_dosen['kapasitas'],
                kode_matkul     = f"{matkul['kode']}{angka_ke_huruf(index_kelas)}",
                kode_dosen      = dosen['nip'],
                sks_akademik    = matkul['sks_akademik'],
                kode_ruangan    = ruang_dosen['kode'],
                hari            = hari_dosen,
                jam_mulai       = jam_mulai_dosen,
                jam_selesai     = jam_selesai_dosen,
                tipe_kelas      = matkul['tipe_kelas'],
                program_studi   = matkul['prodi']
            )
            jadwal.append(sesi_dosen)

            beban_dosen[dosen['nip']] += matkul['sks_akademik']
            jadwal_dosen[dosen['nip']].append({'hari': hari_dosen, 'jam_mulai': jam_mulai_dosen, 'jam_selesai': jam_selesai_dosen})
            jadwal_ruangan[ruang_dosen['kode']].append({'hari': hari_dosen, 'jam_mulai': jam_mulai_dosen, 'jam_selesai': jam_selesai_dosen})
            jumlah_mahasiswa -= ruang_dosen['kapasitas']

            # Penentuan kelas asistensi yang tidak terintegrasi dengan kelas dosen
            if matkul.get('asistensi') and not matkul.get('integrated_class'):
                # print(f"{matkul['nama']:<50} praktikum: {matkul.get('asistensi'):<10} integrated: {matkul.get('integrated_class')}")
                # print(f"kapasitas ruangan dosen {ruang_dosen['kapasitas']}; {min(40, max(40, ruang_dosen['kapasitas']))}")
                ruang_prodi_asistensi = [r for r in ruangan_prodi_prioritas or ruangan_prodi if r['tipe_ruangan'] == matkul.get('tipe_kelas_asistensi') and r['kapasitas'] >= ruang_dosen['kapasitas'] and r['tipe_ruangan'] != "RAPAT"]
                bobot_ruang_asisten = [(len(set(r['plot']) & set(matkul['bidang']))*10 or 1) for r in ruang_prodi_asistensi]

                # print(f"{ruang_dosen['kapasitas']} available asistance {ruang_prodi_asistensi}")
                ruang_asisten = random.choices(
                    population=ruang_prodi_asistensi, 
                    weights=bobot_ruang_asisten, 
                    k=1)[0]
                
                hari_asisten = random.choice(pilihan_hari_asisten[pilihan_hari_dosen.index(hari_dosen):])
                sukses = False
                attempt = 0
                isolated_day = []
                # print(matkul['kode'], hari_dosen, jam_mulai_dosen, jam_selesai_dosen)
                while not sukses and max_attempt >= attempt:
                    if ruang_asisten['kode'] not in jadwal_ruangan: jadwal_ruangan[ruang_asisten['kode']] = []

                    jadwal_ruangan_sesuai_hari = [d for d in jadwal_ruangan[ruang_asisten['kode']] if d['hari'] == hari_asisten] if jadwal_ruangan[ruang_asisten['kode']] else []

                    if jadwal_ruangan_sesuai_hari:
                        list_jam_selesai_ruangan = [r['jam_selesai'] for r in jadwal_ruangan_sesuai_hari]
                        jam_terakhir_ruangan = max(list_jam_selesai_ruangan)
                        jam_mulai_asisten = jam_terakhir_ruangan if jam_terakhir_ruangan <= (18 - matkul['sks_akademik']) else 0
                    else:
                        jam_mulai_asisten = 7

                    # print(f"  {matkul['kode']}-AS {hari_asisten} {jam_mulai_asisten}")
                    if jam_mulai_asisten != 0 and not (
                        hari_asisten == hari_dosen and 
                        not (
                            jam_mulai_asisten >= jam_selesai_dosen and 
                            (jam_mulai_asisten + matkul['sks_akademik']) <= jam_mulai_dosen
                        )
                    ): # Kalau jam asisten sesuai + Tidak bertabrakan dgn kelas dosen
                        jam_selesai_asisten = jam_mulai_asisten + matkul['sks_akademik']
                        sukses = True
                    else:
                        if hari_asisten == hari_dosen and not (
                            jam_mulai_asisten >= jam_selesai_dosen and 
                            (jam_mulai_asisten + matkul['sks_akademik']) <= jam_mulai_dosen
                        ):
                            isolated_day.append(hari_asisten)
                        dosen_exclude_current_day = [day for day in pilihan_hari_asisten[pilihan_hari_dosen.index(hari_dosen):] if day not in isolated_day]
                        hari_exclude_current_day = [day for day in pilihan_hari_asisten if day not in isolated_day]
                        hari_asisten = random.choice(dosen_exclude_current_day or hari_exclude_current_day)

                    attempt += 1
                
                sesi_asisten = JadwalKuliah(
                    kapasitas    = ruang_asisten['kapasitas'],
                    kode_matkul  = f"{matkul['kode']}{angka_ke_huruf(index_kelas)}-AS",
                    kode_dosen   = "AS",
                    sks_akademik = matkul['sks_akademik'],
                    kode_ruangan = ruang_asisten['kode'],
                    hari         = hari_asisten,
                    jam_mulai    = jam_mulai_asisten,
                    jam_selesai  = jam_selesai_asisten,
                    tipe_kelas   = matkul['tipe_kelas_asistensi'],
                    program_studi= matkul['prodi']
                )
                jadwal.append(sesi_asisten)
                jadwal_ruangan[ruang_asisten['kode']].append({'hari': hari_asisten, 'jam_mulai': jam_mulai_asisten, 'jam_selesai': jam_selesai_asisten})
            
            index_kelas += 1

    # print(f"{beban_dosen}")
    # 🛠️ REPAIR sebelum return
    # jadwal = repair_jadwal(jadwal, matakuliah_list, dosen_list, ruang_list)
    return jadwal

def generate_populasi(matakuliah_list, dosen_list, ruang_list, ukuran_populasi):
    return [generate_jadwal(matakuliah_list, dosen_list, ruang_list) for _ in range(ukuran_populasi)]

def hitung_fitness(jadwal, matakuliah_list, dosen_list, ruang_list, detail=False):
    penalti = 0
    jadwal_dosen = {}
    jadwal_ruangan = {}
    beban_dosen = {}

    # COUNTER
    hitung_ruangan_bentrok = 0
    hitung_dosen_bentrok = 0
    hitung_asdos_nabrak_dosen = 0
    hitung_kelas_dosen_missing = 0
    hitung_kelas_asisten_missing = 0
    hitung_diluar_jam_kerja = 0
    mata_kuliah_minus = {}

    kapasitas_mata_kuliah = {}

    # TO BE CHECKED:
    # (15)  Jadwal Ruangan Bertabrakan                                  >> ruangan_bentrok           (DONE)
    # (15)  Jadwal Dosen Bertabrakan                                    >> dosen_bentrok             (DONE)
    # (15)  Jadwal Dosen dan Asisten Berjalan Bersamaan                 >> asdos_nabrak_dosen        (DONE)
    # (15)  Kelas Dosen atau Asisten Hilang atau Tidak Lengkap          >> kelas_gaib                (DONE)
    # (10)  Beban SKS Dosen melebihi 12 sks                             >> dosen_overdosis           (DONE)
    # (10)  Matkul berlangsung sebelum pukul 7 atau sesudah pukul 19    >> diluar_jam_kerja          (DONE)
    # (10)  Cek Total Kelas Bisa Cangkup Semua Mahasiswa                >> kapasitas_kelas_terbatas  (DONE)
    # (5)   Tidak Sesuai dengan permintaan / request dosen              >> melanggar_preferensi      (DONE)

    for sesi in jadwal:
        kode_matkul = sesi.kode_matkul[:-1] if sesi.kode_dosen != "AS" else sesi.kode_dosen[:-4]
        info_matkul = next((m for m in matakuliah_list if m['kode'] == kode_matkul), None)
        info_ruangan = next((r for r in ruang_list if r["kode"] == sesi.kode_ruangan), None)
        info_dosen = next((d for d in dosen_list if d['nip'] == sesi.kode_dosen), None)
        
        if sesi.kode_ruangan not in jadwal_ruangan: jadwal_ruangan[sesi.kode_ruangan] = []

        # CEK BENTROK JADWAL RUANGAN
        for sesi_lain in jadwal_ruangan[sesi.kode_ruangan]:
            if sesi.hari == sesi_lain['hari']:
                if sesi.jam_mulai < sesi_lain['jam_selesai'] and sesi.jam_selesai > sesi_lain['jam_mulai']:
                    penalti += BOBOT_PENALTI['ruangan_bentrok']
                    hitung_ruangan_bentrok += 1
        jadwal_ruangan[sesi.kode_ruangan].append({'hari': sesi.hari, 'jam_mulai': sesi.jam_mulai, 'jam_selesai': sesi.jam_selesai})

        if sesi.kode_dosen != "AS":
            if sesi.kode_dosen not in jadwal_dosen: jadwal_dosen[sesi.kode_dosen] = []
            if sesi.kode_dosen not in beban_dosen: beban_dosen[sesi.kode_dosen] = 0
            # CEK BENTROK JADWAL DOSEN
            for sesi_lain in jadwal_dosen[sesi.kode_dosen]:
                if sesi.hari == sesi_lain['hari']:
                    if sesi.jam_mulai < sesi_lain['jam_selesai'] and sesi.jam_selesai > sesi_lain['jam_mulai']:
                        penalti += BOBOT_PENALTI['dosen_bentrok']
                        hitung_dosen_bentrok += 1
            jadwal_dosen[sesi.kode_dosen].append({'hari': sesi.hari, 'jam_mulai': sesi.jam_mulai, 'jam_selesai': sesi.jam_selesai})

            # CEK EKSISTENSI KELAS ASISTEN
            if info_matkul.get('asistensi') and not info_matkul.get('integrated_class'):
                sesi_asisten = next((sa for sa in jadwal if sa.kode_matkul == sesi.kode_matkul+"-AS"), None)
                if sesi_asisten:
                    # CEK BENTROK JADWAL DOSEN X ASISTEN NGGA BENER INI ANJENG. CEK ULANG SU
                    if sesi.hari == sesi_asisten.hari:
                        if sesi.jam_mulai < sesi_asisten.jam_selesai and sesi.jam_selesai > sesi_asisten.jam_mulai:
                            penalti += BOBOT_PENALTI['asdos_nabrak_dosen']
                            hitung_asdos_nabrak_dosen += 1
                else:
                    penalti += BOBOT_PENALTI['kelas_gaib']
                    hitung_kelas_asisten_missing += 1

            # CEK PELANGGARAN BEBAN SKS DOSEN
            beban_dosen[sesi.kode_dosen] += sesi.sks_akademik
            if beban_dosen[sesi.kode_dosen] > 12:
                penalti += BOBOT_PENALTI['dosen_overdosis']

            # CEK PELANGGARAN PREFERENSI DOSEN
            preferensi_dosen = info_dosen.get("preferensi_dosen", None)
            if preferensi_dosen:
                hindari_hari = preferensi_dosen.get("hindari_hari", None)
                hindari_jam = preferensi_dosen.get("hindari_jam", None)
                if (hindari_hari and sesi.hari in hindari_hari) or (hindari_jam and any(jam in hindari_jam for jam in range(sesi.jam_mulai, sesi.jam_selesai + 1))):
                    penalti += BOBOT_PENALTI['melanggar_preferensi']

            # HITUNG TOTAL KAPASITAS
            if kode_matkul not in kapasitas_mata_kuliah: kapasitas_mata_kuliah[kode_matkul] = 0
            kapasitas_mata_kuliah[kode_matkul] += sesi.kapasitas
        else:
            sesi_dosen = next((sd for sd in jadwal if sd.kode_matkul == sesi.kode_matkul[:-3]), None)
            # CEK EKSISTENSI KELAS DOSEN
            if not sesi_dosen:
                penalti += BOBOT_PENALTI['kelas_gaib']
                hitung_kelas_dosen_missing += 1

        # CEK JAM MULAI DAN JAM SELESAI MASIH DI JAM KERJA ATAU TIDAK
        if sesi.jam_mulai < 7 or sesi.jam_selesai > 19:
            penalti += BOBOT_PENALTI['diluar_jam_kerja']
            hitung_diluar_jam_kerja += 1

    # CEK TOTAL KAPASITAS TIAP MATKUL
    for kode_matkul, kapasitas in kapasitas_mata_kuliah.items():
        matkul_detail = next((matkul for matkul in matakuliah_list if matkul['kode'] == kode_matkul), None)
        if matkul_detail:
            if kapasitas < matkul_detail['jumlah_mahasiswa']:
                kekurangan_kapasitas = matkul_detail['jumlah_mahasiswa'] - kapasitas
                penalti += (BOBOT_PENALTI['kapasitas_kelas_terbatas'] * (kekurangan_kapasitas/10))
                mata_kuliah_minus[kode_matkul] = kekurangan_kapasitas

    if detail:
        if beban_dosen: print(f"{'':<10}{'beban dosen':<40}: {beban_dosen}")
        if hitung_dosen_bentrok: print(f"{'':<10}{'Bentrok Dosen':<40} : {hitung_dosen_bentrok}")
        if hitung_ruangan_bentrok: print(f"{'':<10}{'Bentrok Ruangan':<40} : {hitung_ruangan_bentrok}")
        if hitung_asdos_nabrak_dosen: print(f"{'':<10}{'Bentrok Dosen-Asdos':<40} : {hitung_asdos_nabrak_dosen}")
        if hitung_diluar_jam_kerja: print(f"{'':<10}{'Kelas Diluar Jam Kerja':<40} : {hitung_diluar_jam_kerja}")
        if hitung_kelas_dosen_missing: print(f"{'':<10}{'Kelas Dosen Missing':<40} : {hitung_kelas_dosen_missing}")
        if hitung_kelas_asisten_missing: print(f"{'':<10}{'Kelas Asisten Missing':<40} : {hitung_kelas_asisten_missing}")
        if mata_kuliah_minus: print(f"{'':<10}{'Kapasitas kelas kurang x':<40} : {mata_kuliah_minus}")

    # print(f"{'final fitness':<50} : {max(0, 1000 - penalti)}")
    # return max(0, 1000 - penalti)
    return 1000-penalti

def roulette_selection(populasi, fitness_scores):
    """
    Memilih satu individu dari populasi menggunakan metode seleksi berdasarkan fitness.

    Individu dipilih secara acak menggunakan nilai acak antara 0 hingga total fitness 
    (populasi), di mana individu dengan fitness lebih tinggi memiliki peluang lebih besar terpilih.

    Args:
        populasi (list): Daftar individu (jadwal) yang tersedia.
        fitness_scores (list): Daftar nilai fitness yang sesuai dengan setiap individu dalam populasi.

    Returns:
        object: Individu yang terpilih dari populasi.
    """
    
    total_fitness = sum(fitness_scores)
    pick = random.uniform(0, total_fitness)
    current = 0
    for individu, score in zip(populasi, fitness_scores):
        current += score
        if current > pick:
            return individu
    return random.choice(populasi)  # fallback, jika tidak ketemu

def crossover(parent1: object, parent2: object):
    """
    Melakukan crossover antara parent1 dan parent2 berdasarkan blok kode_matkul (tanpa suffix paralel).

    Titik acak diambil dari parent1, lalu blok matkul utamanya diidentifikasi
    (misal TC502 dari TC502A/TC502C/TC502-AS). Crossover dilakukan dari titik
    awal blok tersebut pada kedua parent.

    Args:
        parent1 (list): Individu pertama berupa list sesi.
        parent2 (list): Individu kedua berupa list sesi.

    Returns:
        tuple: Dua individu hasil crossover (child1, child2).
    """
    
    titik = random.randint(1, len(parent1)-1)
    sesi_target = parent1[titik]
    kode_matkul = sesi_target.kode_matkul
    is_asisten = sesi_target.kode_dosen == "AS"
    matkul_code_base = kode_matkul[:-4] if is_asisten else kode_matkul[:-1]

    titik1 = next((index for index, sesi in enumerate(parent1) if sesi.kode_matkul == matkul_code_base + 'A'), 0)
    titik2 = next((index for index, sesi in enumerate(parent2) if sesi.kode_matkul == matkul_code_base + 'A'), 0)

    child1 = parent1[:titik1] + parent2[titik2:]
    child2 = parent2[:titik2] + parent1[titik1:]
    return child1, child2

def mutasi(individu, dosen_list, matakuliah_list, ruang_list, peluang_mutasi=0.1):
    """
    Melakukan mutasi pada individu (jadwal) secara acak berdasarkan peluang yang ditentukan.

    Setiap sesi dalam individu memiliki kemungkinan untuk dimodifikasi secara acak 
    pada atribut `hari`, `jam_mulai` + `jam_selesai`, atau `kode_ruangan`.

    Args:
        individu (list): Daftar sesi jadwal dalam satu individu.
        dosen_list (list): Daftar dosen yang tersedia.
        ruang_list (list): Daftar ruangan yang tersedia, masing-masing berupa dict dengan key 'kode'.
        peluang_mutasi (float, optional): Peluang untuk setiap sesi dimutasi. Default 0.1.

    Returns:
        list: Individu yang telah mengalami mutasi (bisa sama atau berbeda).
    """

    
    pilihan_hari_dosen = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT"]
    pilihan_hari_asisten = copy.deepcopy(pilihan_hari_dosen)
    pilihan_hari_asisten.append("SABTU")
    pilihan_waktu = list(range(7, 20))

    for sesi in individu:
        if random.random() < peluang_mutasi:
            # Randomly mutate hari, jam, atau ruangan
            attr = random.choice(['hari', 'jam', 'ruang'])

            if attr == 'hari':
                sesi.hari = random.choice(pilihan_hari_dosen) if sesi.kode_dosen != "AS" else random.choice(pilihan_hari_asisten)
            elif attr == 'jam':
                jam_mulai = random.choice(pilihan_waktu)
                sesi.jam_mulai = (
                    jam_mulai 
                    if jam_mulai + sesi.sks_akademik <= max(pilihan_waktu) 
                    else max(pilihan_waktu) - sesi.sks_akademik)
                sesi.jam_selesai = sesi.jam_mulai + sesi.sks_akademik
            elif attr == 'ruang':
                kode_matkul = sesi.kode_matkul[:-1] if sesi.kode_dosen != "AS" else sesi.kode_matkul[:-4]
                matkul = next((matkul for matkul in matakuliah_list if matkul['kode'] == kode_matkul), None)
                if sesi.kode_dosen != "AS":
                    calon_ruang_pengganti = [
                        r for r in ruang_list if 
                            (matkul['prodi'] in r['plot'] or 'GENERAL' in r['plot']) and
                            r['kapasitas'] >= 35 and
                            (
                                r['tipe_ruangan'] == sesi.tipe_kelas or 
                                (r['tipe_ruangan'] == "RAPAT" if not matkul.get('asistensi') else False)
                            )
                    ]
                else:
                    calon_ruang_pengganti = [
                        r for r in ruang_list if 
                            (matkul['prodi'] in r['plot'] or 'GENERAL' in r['plot']) and
                            r['kapasitas'] >= sesi.kapasitas and
                            r['tipe_ruangan'] == matkul['tipe_kelas_asistensi']
                    ]
                bobot_calon_ruang_pengganti = [
                    (len(set(r['plot']) & set(matkul['bidang']))*10 or 1)
                    for r in calon_ruang_pengganti
                ]
                ruang_pengganti = random.choices(
                    population=calon_ruang_pengganti, 
                    weights=bobot_calon_ruang_pengganti, 
                    k=1)[0]
                sesi.kode_ruangan = ruang_pengganti['kode']
    return individu

def genetic_algorithm(matakuliah_list, dosen_list, ruang_list, ukuran_populasi=75, jumlah_generasi=100, peluang_mutasi=0.1, proporsi_elite=0.05):
    """
    Melakukan mutasi pada individu (jadwal) secara acak berdasarkan peluang yang ditentukan.

    Setiap sesi dalam individu memiliki kemungkinan untuk dimodifikasi secara acak 
    pada atribut `hari`, `jam_mulai` + `jam_selesai`, atau `kode_ruangan`.

    Args:
        matakuliah_list (list): Daftar matakuliah yang dibuka pada semester berikutnya.
        dosen_list (list): Daftar dosen yang tersedia.
        ruang_list (list): Daftar ruangan yang tersedia, masing-masing berupa dict dengan key 'kode'.
        ukuran_populasi (int, optional): Jumlah populasi dalam setiap generasi. Default 75.
        jumlah_generasi (int, optional): Jumlah algoritma menghasilkan penerus. Default 100.
        peluang_mutasi (float, optional): Peluang untuk setiap sesi dimutasi. Default 0.1.

    Returns:
        dict: Jadwal hasil algoritma genetika dalam bentuk dictionary.
    """

    populasi = generate_populasi(matakuliah_list, dosen_list, ruang_list, ukuran_populasi)
    populasi = [repair_jadwal(j, matakuliah_list, dosen_list, ruang_list) for j in populasi]
    
    best_fitness_global = float('-inf')
    best_individual_global = None

    jumlah_elite = max(1, int(ukuran_populasi * proporsi_elite))

    for gen in range(jumlah_generasi):
        fitness_scores = [hitung_fitness(individu, matakuliah_list, dosen_list, ruang_list) for individu in populasi]
        next_gen = []

        # Simpan individu terbaik
        individu_elite = [individu for _, individu in sorted(zip(fitness_scores, populasi), key=lambda x: x[0], reverse=True)][:jumlah_elite]
        next_gen = individu_elite.copy()

        # Generate anak baru
        while len(next_gen) < ukuran_populasi:
            parent1 = roulette_selection(populasi, fitness_scores)
            parent2 = roulette_selection(populasi, fitness_scores)

            child1, child2 = crossover(parent1, parent2)

            child1 = mutasi(child1, dosen_list, matakuliah_list, ruang_list, peluang_mutasi)
            child2 = mutasi(child2, dosen_list, matakuliah_list, ruang_list, peluang_mutasi)

            child1 = repair_jadwal(child1, matakuliah_list, dosen_list, ruang_list)
            child2 = repair_jadwal(child2, matakuliah_list, dosen_list, ruang_list)

            next_gen.append(child1)
            if len(next_gen) < ukuran_populasi:
                next_gen.append(child2)
            
        populasi = next_gen

        fitness_scores = [hitung_fitness(individu, matakuliah_list, dosen_list, ruang_list) for individu in populasi]
        gen_best_fitness = max(fitness_scores)
        gen_best_individual = populasi[fitness_scores.index(gen_best_fitness)]

        if gen_best_fitness > best_fitness_global:
            best_fitness_global = gen_best_fitness
            best_individual_global = copy.deepcopy(gen_best_individual)

        avg = sum(fitness_scores) / len(fitness_scores)
        print(f"[Gen {gen}] [({len(populasi)} population)] AVG : {round(avg, 2):<10} BEST ALLTIME: {best_fitness_global}")
        print(f"{'':<5}Min: {min(fitness_scores):<5}Max: {max(fitness_scores):<5}Best Gen: {gen_best_fitness}")
        print(f"gen best fitness {gen_best_fitness} {hitung_fitness(gen_best_individual, matakuliah_list, dosen_list, ruang_list, True)}")
        # hitung_fitness(gen_best_individual, matakuliah_list, dosen_list, ruang_list, True)
        print(f"{'':<5}Missing: {find_missing_course(best_individual_global, matakuliah_list)}\n") if find_missing_course(best_individual_global, matakuliah_list) else print("\n")

    print(f"GLOBAL BEST FITNESS {best_fitness_global}")
    hitung_fitness(best_individual_global, matakuliah_list, dosen_list, ruang_list, True)
    return convertOutputToDict(best_individual_global)