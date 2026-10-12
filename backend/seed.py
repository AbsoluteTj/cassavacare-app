from app.database import SessionLocal, engine
from app.models import Base, Disease

# Buat tabel di database jika belum ada
Base.metadata.create_all(bind=engine)


def seed_diseases():
    db = SessionLocal()
    try:
        # Cek jika data di dalam tabel sudah ada untuk menghindari duplikasi
        if db.query(Disease).count() > 0:
            print("Data katalog penyakit sudah ada di database.")
            return

        # Daftar data awal penyakit dan kondisi sehat
        diseases = [
            Disease(
                code="CBB",
                name="Cassava Bacterial Blight",
                category="Bacterial",
                description="Bakteri Xanthomonas axonopodis yang menyebabkan bercak bersudut basah dan layu pada daun.",
                treatment_recommendation="Gunakan bibit bebas penyakit, pangkas bagian terinfeksi, dan lakukan rotasi tanaman."
            ),
            Disease(
                code="CBSD",
                name="Cassava Brown Streak Disease",
                category="Viral",
                description="Virus yang menyebabkan klorosis pada tulang daun dan pembusukan cokelat pada umbi.",
                treatment_recommendation="Gunakan varietas tahan virus dan musnahkan tanaman terinfeksi segera."
            ),
            Disease(
                code="CGM",
                name="Cassava Green Mite",
                category="Pest",
                description="Hama tungau hijau yang mengisap cairan daun muda hingga daun bercak kuning dan kerdil.",
                treatment_recommendation="Gunakan musuh alami (tungau pemangsa) atau semprotkan akarisida hayati."
            ),
            Disease(
                code="CMD",
                name="Cassava Mosaic Disease",
                category="Viral",
                description="Virus mosaik yang disebarkan lalat putih (Bemisia tabaci), menyebabkan daun belang kekuningan dan keriting.",
                treatment_recommendation="Gunakan stek sehat, kendalikan populasi lalat putih, dan tanam varietas resisten."
            ),
            Disease(
                code="HEALTHY",
                name="Daun Singkong Sehat",
                category="Healthy",
                description="Daun singkong tampak hijau segar, simetris, dan bebas dari gejala penyakit atau hama.",
                treatment_recommendation="Lanjutkan pemeliharaan rutin, pemupukan berimbang, dan pengairan yang cukup."
            )
        ]

        # Simpan seluruh data ke database
        db.add_all(diseases)
        db.commit()
        print("Berhasil mengimpor 5 data penyakit awal ke MySQL XAMPP!")

    except Exception as e:
        db.rollback()
        print(f"Terjadi kesalahan saat seeding data: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_diseases()