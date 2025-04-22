from flask import session
import random

class JadwalKuliah:
    def __init__(self, id_mk, id_dosen, ruang, hari, jam, tipe_kelas):
        self.id_mk = id_mk
        self.id_dosen = id_dosen
        self.ruang = ruang
        self.hari = hari
        self.jam = jam
        self.tipe_kelas = tipe_kelas  # 'teori' atau 'praktikum'

BOBOT_PENALTI = {
    "konflik_dosen": 15,
    "ruang_salah": 6,
    "jam_berlebih": 4,
    "hindari_sabtu": 10,
    "preferensi_dosen": 3,
}

# if sesi1.id_dosen == sesi2.id_dosen and sesi1.waktu == sesi2.waktu:
#     penalti += BOBOT_PENALTI["dosen_bentrok"]

def repair_jadwal(jadwal, dosen_list, ruang_list, hari_list, jam_list):
    # 1. Perbaiki bentrok dosen
    for i, sesi1 in enumerate(jadwal):
        for j, sesi2 in enumerate(jadwal):
            if i != j and sesi1.hari == sesi2.hari and sesi1.jam == sesi2.jam:
                if sesi1.id_dosen == sesi2.id_dosen:
                    sesi2.jam = random.choice([j for j in jam_list if j != sesi1.jam])

    # 2. Pindahkan sesi dari hari Sabtu jika dosen mengajar
    for sesi in jadwal:
        if sesi.hari == "Sabtu" and sesi.tipe_kelas == "teori":
            sesi.hari = random.choice([h for h in hari_list if h != "Sabtu"])

    # 3. Pindahkan praktikum dari ruang teori jika memungkinkan
    for sesi in jadwal:
        if sesi.tipe_kelas == "praktikum" and sesi.ruang.startswith("T"):
            ruang_praktikum = [r['id'] for r in ruang_list if r['id'].startswith("P")]
            if ruang_praktikum:
                sesi.ruang = random.choice(ruang_praktikum)

    # 4. Perbaiki beban SKS dosen
    sks_dosen = {}
    for sesi in jadwal:
        sks_dosen[sesi.id_dosen] = sks_dosen.get(sesi.id_dosen, 0) + 1

    for sesi in jadwal:
        if sks_dosen[sesi.id_dosen] > 12:
            dosen_tersedia = [d['id'] for d in dosen_list if d['id'] != sesi.id_dosen and sks_dosen.get(d['id'], 0) < 12]
            if dosen_tersedia:
                sesi.id_dosen = random.choice(dosen_tersedia)

    return jadwal

def generate_jadwal(dosen_list, matkul_list, ruang_list, hari_list, jam_list):
    jadwal = []

    for matkul in matkul_list:
        dosen = random.choice(dosen_list)
        ruang = random.choice(ruang_list)
        hari = random.choice(hari_list)
        jam = random.choice(jam_list)

        sesi = JadwalKuliah(
            id_matkul=matkul['id'],
            id_dosen=dosen['id'],
            ruang=ruang['id'],
            hari=hari,
            jam=jam,
            tipe_kelas=matkul['tipe']
        )
        jadwal.append(sesi)

    # 🛠️ REPAIR sebelum return
    jadwal = repair_jadwal(jadwal, dosen_list, ruang_list, hari_list, jam_list)
    return jadwal

def generate_populasi(matakuliah_list, dosen_list, ruang_list, slot_waktu, ukuran_populasi):
    return [generate_jadwal(matakuliah_list, dosen_list, ruang_list, slot_waktu) for _ in range(ukuran_populasi)]

def hitung_fitness(jadwal):
    penalti = 0
    dosen_jadwal = {}
    dosen_jam_total = {}
    ruang_jadwal = {}

    for sesi in jadwal:
        key_waktu = (sesi.hari, sesi.jam)

        # Data dosen saat ini
        dosen_info = next(d for d in dosen_list if d["id"] == sesi.id_dosen)
        preferensi = dosen_info.get("preferensi", {})

        # 1. Total jam mengajar dosen
        dosen_jam_total[sesi.id_dosen] = dosen_jam_total.get(sesi.id_dosen, 0) + 1
        if dosen_jam_total[sesi.id_dosen] > 12:
            penalti += (dosen_jam_total[sesi.id_dosen] - 12) * 5

        # 2. Dosen tidak boleh ganda
        if (sesi.id_dosen, key_waktu) in dosen_jadwal:
            penalti += 10
        else:
            dosen_jadwal[(sesi.id_dosen, key_waktu)] = sesi

        # 3. Praktikum di ruang teori
        if sesi.tipe_kelas == "praktikum" and sesi.ruang.startswith("T"):
            penalti += 5

        # 4. Dosen tidak boleh Sabtu
        if sesi.hari == "Sabtu":
            penalti += 10

        # 5. Praktikum dianjurkan Sabtu (pagi)
        if sesi.tipe_kelas == "praktikum":
            if sesi.hari != "Sabtu":
                penalti += 2
            elif int(sesi.jam.split(":")[0]) > 13:
                penalti += 2

        # 6. Preferensi dosen
        if sesi.hari in preferensi.get("hindari_hari", []):
            penalti += 5

        if sesi.jam in preferensi.get("hindari_jam", []):
            penalti += 3

    return max(0, 100 - penalti)

def roulette_selection(populasi, fitness_scores):
    total_fitness = sum(fitness_scores)
    pick = random.uniform(0, total_fitness)
    current = 0
    for i, score in enumerate(fitness_scores):
        current += score
        if current > pick:
            return populasi[i]
        
def crossover(parent1, parent2):
    titik = random.randint(1, len(parent1) - 2)
    child1 = parent1[:titik] + parent2[titik:]
    child2 = parent2[:titik] + parent1[titik:]
    return child1, child2

def mutasi(jadwal, ruang_list, slot_waktu, peluang=0.05):
    for sesi in jadwal:
        if random.random() < peluang:
            sesi.hari, sesi.jam = random.choice(slot_waktu)
            sesi.ruang = random.choice([r['id'] for r in ruang_list if r['tipe'] == sesi.tipe_kelas])
    return jadwal

def debug_penalti(jadwal):
    # Hitung jumlah penalti spesifik
    count_bentrok_dosen = 0
    count_ruang_bentrok = 0
    count_beban_sks = {}
    
    for i, sesi1 in enumerate(jadwal):
        for j, sesi2 in enumerate(jadwal):
            if i != j and sesi1.hari == sesi2.hari and sesi1.jam == sesi2.jam:
                if sesi1.id_dosen == sesi2.id_dosen:
                    count_bentrok_dosen += 1
                if sesi1.ruang == sesi2.ruang:
                    count_ruang_bentrok += 1
        
        count_beban_sks[sesi1.id_dosen] = count_beban_sks.get(sesi1.id_dosen, 0) + 1

    over_sks = sum(1 for sks in count_beban_sks.values() if sks > 12)

    print(f"  - Bentrok Dosen: {count_bentrok_dosen}")
    print(f"  - Bentrok Ruang: {count_ruang_bentrok}")
    print(f"  - Dosen SKS Berlebih: {over_sks}")

def genetic_algorithm(matakuliah_list, dosen_list, ruang_list, slot_waktu, ukuran_populasi=50, generasi=100):
    populasi = generate_populasi(matakuliah_list, dosen_list, ruang_list, slot_waktu, ukuran_populasi)

    for gen in range(generasi):
        fitness_scores = [hitung_fitness(j) for j in populasi]
        next_gen = []

        while len(next_gen) < ukuran_populasi:
            parent1 = roulette_selection(populasi, fitness_scores)
            parent2 = roulette_selection(populasi, fitness_scores)
            child1, child2 = crossover(parent1, parent2)
            child1 = mutasi(child1, ruang_list, slot_waktu)
            child2 = mutasi(child2, ruang_list, slot_waktu)
            next_gen.extend([child1, child2])

        populasi = next_gen[:ukuran_populasi]
        best = max(fitness_scores)
        print(f"Generasi {gen}: Fitness terbaik = {best}")
        debug_penalti(populasi)

    # Ambil hasil terbaik
    fitness_scores = [hitung_fitness(j) for j in populasi]
    best_jadwal = populasi[fitness_scores.index(max(fitness_scores))]
    return best_jadwal

# Cetak ke Console
def tampilkan_jadwal(jadwal):
    print("\n📅 Jadwal Mata Kuliah Terbaik:\n")
    print(f"{'MK':<8}{'Dosen':<15}{'Ruang':<8}{'Hari':<10}{'Jam':<6}{'Tipe'}")
    print("-" * 60)
    for sesi in sorted(jadwal, key=lambda x: (x.hari, x.jam)):
        print(f"{sesi.id_mk:<8}{sesi.id_dosen:<15}{sesi.ruang:<8}{sesi.hari:<10}{sesi.jam:<6}{sesi.tipe_kelas}")