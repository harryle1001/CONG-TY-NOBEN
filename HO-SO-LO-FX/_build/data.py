# Du lieu 7 san pham F.X - tinh tu TCCS x 100 lit/lo
BL = "……"          # o de trong ghi tay
DATE = "……/……/………"

def spec(form):
    return ("TCCS nhà cung cấp, " + form + ", sản phẩm còn nguyên vẹn trong bao/phuy, "
            "còn hạn sử dụng, bao bì nguyên vẹn không bong tróc; có phiếu kiểm nghiệm (COA) của lô nguyên liệu.")

WATER_SPEC = "Trong suốt, không màu, không mùi, đảm bảo đạt yêu cầu các chỉ tiêu an toàn."
WATER = ("Nước lọc (RO) vừa đủ", "100 lít", WATER_SPEC, "Nước lọc (RO)")

KL_LIVER = "As vô cơ ≤ 10 mg/l; Cd ≤ 3 mg/l; Pb ≤ 5 mg/l; Hg ≤ 0,1 mg/l"
VS_10 = "Salmonella spp.: Không phát hiện/25 ml; E. coli ≤ 10 CFU/ml"

LIVER_NL = [
    ("Sorbitol", "1,000 kg", spec("dạng bột/hạt màu trắng (nếu dùng dung dịch sorbitol phải quy đổi theo hàm lượng)"), "Sorbitol"),
    ("DL-Methionine", "0,150 kg", spec("dạng bột màu trắng, mùi đặc trưng"), "DL-Methionine"),
    ("Betain", "0,300 kg", spec("dạng bột/tinh thể màu trắng"), "Betain"),
    WATER,
]
LIVER_DL = "Sorbitol ≥ 10.000 mg/l; Methionine ≥ 1.500 mg/l; Betain ≥ 3.000 mg/l"
LIVER_NOTE = ("Ghi chú công thức: tính từ TCCS × 100 lít (Sorbitol 10.000 mg/l; Methionine 1.500 mg/l; Betain 3.000 mg/l), "
              "quy về nguyên liệu tinh khiết 100%. Nếu nguyên liệu có độ tinh khiết/dạng khác (vd sorbitol lỏng 70%, betain HCl) "
              "phải quy đổi lại – chờ Phòng Kỹ thuật xác nhận.")

PRODUCTS = [
    dict(key="LIVER-SUPPORT", name="F.X LIVER SUPPORT", tccs="12:2026/NOBEN", hsd=12,
         nl=LIVER_NL, camquan="Dạng lỏng, màu nâu, mùi đặc trưng",
         dinhtinh="Sorbitol, Methionine, Betain, Nước lọc (RO)",
         kimloai=KL_LIVER, visinh=VS_10, dinhluong=LIVER_DL, note=LIVER_NOTE),
    dict(key="GARLIC", name="F.X GARLIC", tccs="10:2026/NOBEN", hsd=12,
         nl=LIVER_NL, camquan="Dạng lỏng, màu nâu, mùi đặc trưng",
         dinhtinh="Sorbitol, Methionine, Betain, Nước lọc (RO)",
         kimloai=KL_LIVER, visinh=VS_10, dinhluong=LIVER_DL,
         note=LIVER_NOTE + " LƯU Ý: TCCS 10:2026/NOBEN (F.X GARLIC) và danh mục đều ghi thành phần giống hệt F.X LIVER SUPPORT "
              "(không có tỏi/allicin) – hồ sơ lập theo TCCS hiện hành, cần kiểm tra lại TCCS trước khi sản xuất."),
    dict(key="GROW", name="F.X GROW", tccs="11:2026/NOBEN", hsd=12,
         nl=[("Protein (nguyên liệu đạm, quy về 100% protein)", "25,000 kg",
              spec("dạng bột hoặc dịch đạm thủy phân, màu vàng nâu, mùi đặc trưng; hàm lượng protein theo COA"), "Protein"),
             WATER],
         camquan="Dạng lỏng/sệt, màu nâu, mùi đặc trưng",
         dinhtinh="Protein, Nước lọc (RO)",
         kimloai="As vô cơ ≤ 2 mg/l; Cd ≤ 1 mg/l; Pb ≤ 5 mg/l; Hg ≤ 0,2 mg/l",
         visinh=VS_10, dinhluong="Protein ≥ 25%",
         note=("Ghi chú công thức: Protein min 25% (giả định % khối lượng/thể tích, 25 g/100 ml) × 100 lít = 25,0 kg protein nguyên chất. "
               "Khối lượng nguyên liệu thực = 25,0 kg × 100 / (% protein trong nguyên liệu theo COA), vd nguyên liệu 50% protein → 50,0 kg. "
               "Chờ Phòng Kỹ thuật chọn nguyên liệu và xác nhận.")),
    dict(key="YUCCA-RUS", name="F.X YUCCA RUS", tccs="13:2026/NOBEN", hsd=12,
         nl=[("Dịch chiết Yucca schidigera (saponin 12%)", "30,0 lít",
              spec("dạng lỏng màu nâu, mùi đặc trưng; hàm lượng saponin trong dịch chiết 12% theo COA"), "Dịch chiết Yucca schidigera"),
             WATER],
         camquan="Dạng lỏng (bán lỏng, gel, sệt), màu nâu, mùi đặc trưng sản phẩm",
         dinhtinh="Saponin (dịch chiết Yucca schidigera), Nước lọc (RO)",
         kimloai=None, visinh="Salmonella spp.: Không phát hiện/25 ml; E. coli ≤ 1x10³ CFU/ml",
         dinhluong="Dịch chiết Yucca schidigera ≥ 300 ml/lít (saponin trong dịch chiết 12%)",
         note=("Ghi chú công thức: dịch chiết Yucca schidigera 300 ml/lít × 100 lít = 30,0 lít; nước RO vừa đủ 100 lít. "
               "Nếu cân theo khối lượng cần quy đổi theo tỷ trọng dịch chiết (theo COA).")),
    dict(key="PURE", name="F.X PURE", tccs="14:2026/NOBEN", hsd=24,
         nl=[("Sodium thiosulfate", "0,100 kg", spec("dạng tinh thể/hạt màu trắng"), "Sodium thiosulfate"),
             ("Sodium lauryl sulfate", "0,150 kg", spec("dạng bột/kim màu trắng"), "Sodium lauryl sulfate"),
             ("EDTA", "0,050 kg", spec("dạng bột màu trắng"), "EDTA"),
             WATER],
         camquan="Dạng lỏng/keo/sệt, không màu đến vàng nhạt, mùi đặc trưng, không có mùi lạ khác",
         dinhtinh="Sodium thiosulfate, Sodium lauryl sulfate, EDTA, Nước lọc (RO)",
         kimloai="As ≤ 5 mg/l; Pb ≤ 30 mg/l", visinh=None,
         dinhluong="Sodium thiosulfate ≥ 1.000 mg/l; Sodium lauryl sulfate ≥ 1.500 mg/l; EDTA ≥ 500 mg/l",
         note=("Ghi chú công thức: TCCS × 100 lít (1.000 / 1.500 / 500 mg/l → 0,100 / 0,150 / 0,050 kg), quy về chất tinh khiết khan. "
               "Nếu dùng Na2S2O3.5H2O nhân 1,57 (→ 0,157 kg); EDTA muối 2Na.2H2O quy đổi theo COA. "
               "Tham khảo: lệnh SX NO TOXIN (thành phần tương tự) dùng 1 kg / 1,2 kg / 500 g cho 100,1 lít – Phòng Kỹ thuật xác nhận mức dùng.")),
    dict(key="PREMIX-MILK", name="F.X PREMIX MILK", tccs="15:2026/NOBEN", hsd=12,
         nl=[("Kali clorua (KCl)", "0,953 kg", spec("dạng tinh thể/bột màu trắng"), "Kali (KCl)"),
             ("Magie clorua (MgCl2.6H2O)", "0,836 kg", spec("dạng tinh thể/vảy màu trắng"), "Magie (MgCl2)"),
             WATER],
         camquan="Dạng lỏng, không màu, mùi đặc trưng",
         dinhtinh="Kali (KCl), Magie (MgCl2), Nước lọc (RO)",
         kimloai="As vô cơ ≤ 12 mg/l; Cd ≤ 5 mg/l; Pb ≤ 30 mg/l; Hg ≤ 0,2 mg/l", visinh=None,
         dinhluong="K (dạng KCl) ≥ 5.000 mg/l; Mg (dạng MgCl2) ≥ 1.000 mg/l",
         note=("Ghi chú công thức: K 5.000 mg/l × 100 lít = 500 g K → KCl = 500 / 0,5244 = 0,953 kg; "
               "Mg 1.000 mg/l × 100 lít = 100 g Mg → MgCl2.6H2O = 100 / 0,1196 = 0,836 kg (nếu dùng MgCl2 khan: 0,392 kg). "
               "Quy về nguyên liệu tinh khiết 100%. Chờ Phòng Kỹ thuật xác nhận dạng muối.")),
    dict(key="GLUBENCO", name="F.X-GLUBENCO", tccs="16:2026/NOBEN", hsd=24,
         nl=[("Glutaraldehyde 50% (dung dịch thương mại)", "40,000 kg",
              spec("dạng dung dịch trong suốt, không màu đến vàng nhạt, hàm lượng glutaraldehyde 50% theo COA"), "Glutaraldehyde"),
             WATER],
         camquan="Dạng lỏng, trong suốt, mùi đặc trưng",
         dinhtinh="Glutaraldehyde, Nước lọc (RO)",
         kimloai="As ≤ 5 mg/l; Pb ≤ 30 mg/l", visinh=None,
         dinhluong="Glutaraldehyde ≥ 20%",
         note=("Ghi chú công thức: Glutaraldehyde min 20% (giả định 20 g/100 ml) × 100 lít = 20,0 kg glutaraldehyde nguyên chất; "
               "GIẢ ĐỊNH nguyên liệu thương mại 50% → 40,0 kg (≈ 35,4 lít, tỷ trọng ≈ 1,13). "
               "Nếu 20% hiểu theo khối lượng/khối lượng thì cần tính lại theo tỷ trọng thành phẩm. Chờ Phòng Kỹ thuật xác nhận. "
               "Hóa chất sát trùng: thao tác có găng tay, kính, khẩu trang.")),
]
