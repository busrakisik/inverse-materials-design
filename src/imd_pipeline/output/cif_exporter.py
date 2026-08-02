from pymatgen.core import Structure
from pymatgen.io.cif import CifWriter
import os

class CIFExporter:
    """
    Kristal yapılarını (pymatgen Structure) standart CIF formatına dönüştüren 
    ve metadata ekleyen dışa aktarım modülü.
    """
    
    @staticmethod
    def structure_to_cif_string(structure: Structure, symprec: float = 0.1) -> str:
        """
        Structure nesnesini simetri analizi yaparak CIF metni formatına çevirir.
        """
        if not isinstance(structure, Structure):
            raise ValueError("Geçerli bir pymatgen Structure nesnesi sağlanmalıdır.")
            
        # Simetri belirleme hassasiyetiyle CIF yazıcı oluştur
        writer = CifWriter(structure, symprec=symprec)
        return str(writer)

    @staticmethod
    def save_cif_file(structure: Structure, filename: str, output_dir: str = "outputs") -> str:
        """
        Kristal yapısını belirtilen dizine .cif dosyası olarak kaydeder.
        """
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename if filename.endswith('.cif') else f"{filename}.cif")
        
        writer = CifWriter(structure, symprec=0.1)
        writer.write_file(filepath)
        return filepath 