"""
Task 1 — Thu thập tài liệu chính sách/quy định.

Hướng dẫn:
    1. Chọn chủ đề của nhóm.
    2. Tìm tối thiểu 3 tài liệu PDF/DOCX từ nguồn công khai.
    3. Lưu file gốc vào data/landing/legal/.
    4. Đặt tên không dấu và thể hiện đúng nội dung.

Ví dụ tài liệu: học phí, học bổng, ký túc xá, quy trình đăng ký.
Nếu website chặn crawler, hãy chọn nguồn công khai khác; không vượt WAF.
"""

from pathlib import Path
import requests


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"

LEGAL_SOURCES = {
    "luat_to_tung_hanh_chinh_2015.pdf": "https://wipolex-res.wipo.int/edocs/lexdocs/laws/en/vn/vn082en.pdf?last-modified=1501772629&Expires=1790254186&Signature=R3dbCa7gjH9-1i7MK0jAhINSvqT3u91a3MDKGwewoM~brXgKp0Gll98T3NjznyNC-2keDNioVIy1lWwhDNK0jv~sLHnXBS16YgyCtcS~Rho3ZIYjJ99xEJO7Ss2~3WZI~6wg6cy2pB1OKhIHLr~6HojxTqXUhrU3EsQmI3QaDx6AqDCDBjUQPrFk~B80R68wl6lViZuKNXFm9QrDeO-LRb3ubuG2jDOkVq3bmdVyNvn18pPPQuMXvhqiyrh5FoztiR4X8dtb4XLO1ZPy6hCtuYz9eWauZRcJ029umKszXBohm2C0ltDJswmNb9StIGHA7VGBk5Whe7Z1ll2jDyxfrg__&Key-Pair-Id=K1QGBX7Y6FHYJN",
    "thong_tu_211_2016_quyen_tac_gia.pdf": "https://wipolex-res.wipo.int/edocs/lexdocs/laws/en/vn/vn116en.pdf?last-modified=1503591774&Expires=1790254218&Signature=KGuqPcEZ1QhGxCfrhlicfzusjk6gyze-c3dDR7gusePfvC7GIjAv-ekhz92BxCk2z2H99ZS76QRGIKXBXcRXC8gAldpwAXRcADDasS4yBcRWMnr8TSJpi8~9hFb4O~QL4iDaEtl6u7Ux9RLJQ6D824Z5Pb~bEQHgt83vYnuVXj41yScVBZP4GftiZI6acewrYZIk38z7J2iQB8zllqMrMNq-K-23chVA7kMl1rnmuD59JrfkLUNJlaE0JFfoah0PHG78RHKTbxLv3KtP2eut1TTSXWMx5fn-m9n5WvkvUOngFthTeBeELB7amDGzDmUMSRKSU7t5ZrA19rCtyaxtnQ__&Key-Pair-Id=K1QGBX7Y6FHYJN",
    "luat_khoa_hoc_cong_nghe_2013.pdf": "https://wipolex-res.wipo.int/edocs/lexdocs/laws/en/vn/vn085en.pdf?last-modified=1502123812&Expires=1790254234&Signature=AjQsgvmd7qdc~lk1fL7Rbz20jWB3T0YPgABQkQPEhI1FW76vNEV3ZETGwgaQcSPK17-lgx2bI5Ay6yD2a-hpgA8dlJg8X0zNKPUuKqqhb7QO6VuUZmvuwGvMLRHSpSteY-xojC7cE3Botwd7wNKnnwL~sZuEY8N934gw8ZUPeP5qH-nkpfY6I6dXNQJQCHvXvs4NfTqVBf8rahs45MOKXs8Z3mn7bMVphQ9c6R3HoWzvvRdKw8ZTh1xD4nTwjchhGCpjOPEgQ6pWtVf0KgLyJtrGhmKco8VFZI-y-JCGtHkknipl9Ev6e06Nz831fOLyoIwBSGZuB60I0P3MT2op2g__&Key-Pair-Id=K1QGBX7Y6FHYJN",
}

def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def download_documents() -> None:
    """Tải ít nhất 3 PDF/DOCX từ nguồn công khai."""
    # TODO: Có thể tải thủ công hoặc dùng requests.
    #
    # Ví dụ:
    # import requests
    #
    # sources = {
    #     "policy-a.pdf": "https://example.edu/policy-a.pdf",
    # }
    # for filename, url in sources.items():
    #     response = requests.get(url, timeout=30)
    #     response.raise_for_status()
    #     (DATA_DIR / filename).write_bytes(response.content)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

    for filename, url in LEGAL_SOURCES.items():
        dest = DATA_DIR / filename
        if dest.exists() and dest.stat().st_size > 0:
            print(f"File already exists: {filename} ({dest.stat().st_size:,} bytes)")
            continue

        print(f"Downloading {filename} from {url} ...")
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()

        if len(response.content) == 0:
            raise ValueError(f"Downloaded content is empty for {filename}")

        dest.write_bytes(response.content)
        print(f"-> Successfully saved {filename} ({len(response.content):,} bytes)")


if __name__ == "__main__":
    setup_directory()
    download_documents()
