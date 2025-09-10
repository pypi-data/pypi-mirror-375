# src/pyrendergui/exceptions.py

class PyRenderGUIError(Exception):
    """Kütüphanemizdeki tüm özel hatalar için temel sınıf.
    Kullanıcılar sadece bu hatayı yakalayarak tüm PyRenderGUI hatalarını yönetebilir."""
    pass


class XMLFileNotFoundError(PyRenderGUIError, FileNotFoundError):
    """Belirtilen XML dosyası bulunamadığında ortaya çıkar.
    Aynı zamanda standart FileNotFoundError gibi de davranır."""
    pass


class XMLParsingError(PyRenderGUIError):
    """XML dosyası bozuk veya hatalı biçimlendirilmiş olduğunda ortaya çıkar."""
    pass


class UnknownElementError(PyRenderGUIError):
    """XML içinde <Rect> veya <Text> gibi tanınmayan bir etiketle
    karşılaşıldığında ortaya çıkar."""
    pass


class MissingAttributeError(PyRenderGUIError):
    """Bir elementte 'width' veya 'color' gibi zorunlu bir öznitelik
    eksik olduğunda ortaya çıkar."""
    pass