"""Build invented demo fixtures in data/demo/. Fixed seed -> identical graph every run.
Everything here is fictional: safe to screen-record."""
import json, random, shutil
from pathlib import Path

SEED = 1618
OUT = Path(__file__).resolve().parent / "demo"
rnd = random.Random(SEED)

PRODUCTS = ["Lumen Oxy", "Delta Yucca", "Aqua Probio", "Clear Tide", "Vita Shell", "Liver Guard",
            "Zeo Bind", "Mineral Plus", "Algae Stop", "Gut Max", "Iodine Shield", "Calci Milk"]
CLIENTS = ["Đại lý Minh Phát", "Trại tôm Ba Lan", "HTX Rạch Gốc", "Đại lý Cửu Long", "Trại cá Tân Hưng",
           "Đại lý Bến Tre Xanh", "Trại tôm Sao Biển", "Công ty Mekong Seed"]
WEB = ["Website Hải Đăng Resort", "Website Lotus Spa", "Landing Nova Coffee", "Studio Portfolio"]
GAME = ["Đảo Phân Số", "Rừng Hình Học", "Thành Phố Từ Vựng", "Hang Động Vật Lý", "Cảng Lịch Sử"]
AI = ["Khung chuẩn hóa AI", "Gói AI cho SME", "Checklist dữ liệu AI", "Đề xuất AI ngành thủy sản"]
TOPICS = ["Mưa lớn và pH", "Khí độc NH3", "Tảo tàn", "Phân trắng", "Đốm trắng", "Thay vỏ chậm"]


def w(rel, body):
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, "utf-8")


def links(pool, k):
    return " ".join(f"[[{x}]]" for x in rnd.sample(pool, k))


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    for p in PRODUCTS:
        price = rnd.randrange(85, 420) * 1000
        w(f"Noben/San-pham/{p}.md", f"# {p}\nGiá đại lý: {price:,} đ/kg (demo).\nDùng cho: {links(TOPICS, 2)}\n")
    for c in CLIENTS:
        orders = "\n".join(f"- {rnd.choice(['2026-09','2026-10','2026-11'])}-{rnd.randint(1,28):02d}: "
                           f"{rnd.randint(10,200)} kg [[{rnd.choice(PRODUCTS)}]]" for _ in range(rnd.randint(2, 5)))
        paid = rnd.choice(["đã thanh toán đủ", "thanh toán 50%, phần còn lại khi giao đợt 2", "còn nợ 30 ngày"])
        w(f"Noben/Khach-hang/{c}.md", f"# {c}\nCông nợ: {paid}.\n## Đơn hàng\n{orders}\n")
    for t in TOPICS:
        w(f"Noben/Ky-thuat/{t}.md", f"# {t}\nHướng xử lý: {links(PRODUCTS, 3)}. Gặp ở {links(CLIENTS, 2)}.\n")
    for s in WEB:
        w(f"Web/{s}.md", f"# {s}\nGiá: {rnd.randrange(30, 180)} triệu đ (demo). Tỷ lệ φ bố cục 61.8/38.2.\nLiên quan: [[Studio Portfolio]]\n")
    for g in GAME:
        w(f"Game/{g}.md", f"# {g}\nMàn chơi lớp {rnd.randint(4, 9)}. XP nhân φ mỗi cấp.\nNối với {links(GAME, 2)}\n")
    for a in AI:
        w(f"AI/{a}.md", f"# {a}\nChuẩn hóa AI cho doanh nghiệp. Áp dụng thử: {links(CLIENTS + WEB, 2)}\n")
    for i in range(40):
        d = f"2026-{rnd.randint(9, 11):02d}-{rnd.randint(1, 28):02d}"
        pool = PRODUCTS + CLIENTS + TOPICS + WEB + GAME + AI
        w(f"Ghi-chu/{d}-ghi-chu-{i:02d}.md", f"# Ghi chú {d}\n{links(pool, rnd.randint(2, 4))}\n")
    senders = CLIENTS[:5] + ["Lan (khách lạ)", "Supplier Bio-Chem Ltd"]
    subj = ["Hỏi giá {p}", "Xác nhận đơn {p}", "Ao bị {t}, cần tư vấn", "Đề nghị gia hạn công nợ", "Báo giá nguyên liệu tháng 12"]
    inbox = []
    for i in range(9):
        p, t = rnd.choice(PRODUCTS), rnd.choice(TOPICS)
        inbox.append({"id": f"m{i}", "from": rnd.choice(senders), "date": f"2026-11-{rnd.randint(10, 17):02d}",
                      "subject": rnd.choice(subj).format(p=p, t=t), "unread": rnd.random() < 0.6,
                      "body": f"Chào anh, về {p}: cần trả lời trước cuối tuần. (demo)"})
    cal = [{"date": "2026-11-18", "time": f"{h:02d}:00", "title": rnd.choice(["Gọi đại lý ", "Giao hàng ", "Họp web ", "Test game "]) + rnd.choice(CLIENTS + WEB + GAME)}
           for h in sorted(rnd.sample(range(8, 18), 4))]
    cal.append({"date": "2026-11-14", "time": "09:00", "title": "Gửi báo giá Đại lý Cửu Long", "done": False})
    (OUT / "_inbox.json").write_text(json.dumps(inbox, ensure_ascii=False, indent=1), "utf-8")
    (OUT / "_calendar.json").write_text(json.dumps(cal, ensure_ascii=False, indent=1), "utf-8")
    print(f"demo written to {OUT}")


if __name__ == "__main__":
    main()
