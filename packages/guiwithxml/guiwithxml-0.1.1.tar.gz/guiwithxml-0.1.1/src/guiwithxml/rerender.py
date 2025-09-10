import tkinter as tk
from pathlib import Path
import ctypes  # Windows'ta dosya gizlemek için
import os

from .parser import parse_xml_file

class Renderer:
    def __init__(self, root_window: tk.Tk, ui_directory: str = 'ui', create_dir: bool = True, hidden_dir: bool = False, scale: float = 1.0):
        """
        PyRenderGUI'nin ana render motoru.

        :param root_window: Ana Tkinter penceresi (Tk() objesi).
        :param ui_directory: XML dosyalarının bulunacağı klasörün adı/yolu.
        :param create_dir: Eğer ui_directory yoksa oluşturulsun mu?
        :param hidden_dir: ui_directory oluşturulurken gizli klasör olarak mı ayarlansın?
        :param scale: Tüm UI elementlerinin çizileceği ölçek faktörü (örn: 2.0 = %200 zoom).
        """
        self.root = root_window
        self.scale = scale
        self.ui_path = Path(ui_directory)

        if create_dir:
            self._create_ui_directory(hidden_dir)

        # Ana canvas'ı oluştur ve pencereyi kaplamasını sağla
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

    def _create_ui_directory(self, make_hidden: bool):
        """UI klasörünü oluşturur ve istenirse gizler."""
        if not self.ui_path.exists():
            print(f"'{self.ui_path}' oluşturuluyor...")
            self.ui_path.mkdir(parents=True, exist_ok=True)
            if make_hidden:
                try:
                    # Windows için
                    if os.name == 'nt':
                        ctypes.windll.kernel32.SetFileAttributesW(str(self.ui_path), 2) # 2 = FILE_ATTRIBUTE_HIDDEN
                    # Linux ve macOS için (başına . koymak yeterli ama klasör oluşturulduktan sonra yeniden adlandırmak gerekir)
                    # Bu kısmı şimdilik basit tutuyoruz.
                    else:
                        print("Uyarı: Gizli klasör özelliği şimdilik sadece Windows'ta desteklenmektedir.")
                except Exception as e:
                    print(f"Klasör gizlenirken hata oluştu: {e}")

    def render(self, xml_file_name: str):
        """
        Belirtilen XML dosyasını canvas üzerine çizer (render eder).
        """
        full_path = self.ui_path / xml_file_name
        
        if not full_path.exists():
            raise FileNotFoundError(f"XML dosyası bulunamadı: {full_path}")

        # Parser'dan çizilecek elementlerin listesini al
        elements_to_draw, screen_config = parse_xml_file(full_path)
        
        # Ekran arka planını ayarla
        self.canvas.config(bg=screen_config.get("background", "#ffffff"))

        # Her bir elementi ölçeği dikkate alarak çiz
        for element in elements_to_draw:
            element.draw(self.canvas, self.scale) # Her elementin kendi draw metodu olacak