import sys
import csv
import os
from PyQt5 import QtWidgets
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtGui import QTextDocument
from girisekrani import Ui_MainWindow as Ui_GirisEkrani
from secmeekrani import Ui_MainWindow as Ui_SecmeEkrani
from soruekleme import Ui_MainWindow as Ui_SoruEkleme


class UygulamaVerisi:
    def __init__(self, dosya_adi="sorubankasikayit.csv"):
        self.sorular = []
        self.dosya_adi = dosya_adi
        self.sorulari_yukle()

    def sorulari_yukle(self):
        if os.path.exists(self.dosya_adi):
            with open(self.dosya_adi, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)  # Başlığı atla
                self.sorular = [row for row in reader if len(row) == 7]
        else:
            self.sorular = []

    def sorulari_kaydet(self):
        with open(self.dosya_adi, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Soru", "A", "B", "C", "D", "E", "Doğru"])
            writer.writerows(self.sorular)


class GirisEkrani(QtWidgets.QMainWindow):
    def __init__(self, veri):
        super().__init__()
        self.ui = Ui_GirisEkrani()
        self.ui.setupUi(self)
        self.veri = veri
        self.ui.pushButton.clicked.connect(self.ac_soru_ekleme)
        self.ui.pushButton_2.clicked.connect(self.ac_soru_secme)

    def ac_soru_ekleme(self):
        self.pencere = SoruEklemeEkrani(self.veri)
        self.pencere.show()
        self.close()

    def ac_soru_secme(self):
        self.pencere = SecmeEkrani(self.veri)
        self.pencere.show()
        self.close()


class SoruEklemeEkrani(QtWidgets.QMainWindow):
    def __init__(self, veri):
        super().__init__()
        self.ui = Ui_SoruEkleme()
        self.ui.setupUi(self)
        self.veri = veri

        self.ui.pushButton_ekle.clicked.connect(self.soru_ekle)
        self.ui.pushButton_2.clicked.connect(self.sorulari_kaydet)

    def soru_ekle(self):
        soru = self.ui.textEdit_soru.toPlainText()
        secenekler = [
            self.ui.lineEdit_a.text(),
            self.ui.lineEdit_b.text(),
            self.ui.lineEdit_c.text(),
            self.ui.lineEdit_d.text(),
            self.ui.lineEdit_e.text()
        ]

        dogru = ""
        if self.ui.radio_a.isChecked():
            dogru = "A"
        elif self.ui.radio_b.isChecked():
            dogru = "B"
        elif self.ui.radio_c.isChecked():
            dogru = "C"
        elif self.ui.radio_d.isChecked():
            dogru = "D"
        elif self.ui.radio_e.isChecked():
            dogru = "E"

        if not soru.strip() or not dogru:
            QtWidgets.QMessageBox.warning(self, "Hata", "Tüm alanları doldurun ve doğru seçeneği seçin.")
            return

        kayit = [soru] + secenekler + [dogru]
        self.veri.sorular.append(kayit)

        gosterilecek = f"Soru: {soru[:40]}... | Doğru: {dogru}"
        self.ui.listWidget_sorular.addItem(gosterilecek)

        self.ui.textEdit_soru.clear()
        self.ui.lineEdit_a.clear()
        self.ui.lineEdit_b.clear()
        self.ui.lineEdit_c.clear()
        self.ui.lineEdit_d.clear()
        self.ui.lineEdit_e.clear()
        for rb in [self.ui.radio_a, self.ui.radio_b, self.ui.radio_c, self.ui.radio_d, self.ui.radio_e]:
            rb.setChecked(False)

    def sorulari_kaydet(self):
        if not self.veri.sorular:
            QtWidgets.QMessageBox.information(self, "Bilgi", "Kaydedilecek soru yok.")
            return

        self.veri.sorulari_kaydet()
        QtWidgets.QMessageBox.information(self, "Başarılı", f"Sorular kaydedildi: {self.veri.dosya_adi}")


class SecmeEkrani(QtWidgets.QMainWindow):
    def __init__(self, veri):
        super().__init__()
        self.ui = Ui_SecmeEkrani()
        self.ui.setupUi(self)
        self.veri = veri

        self.ui.pushButton.clicked.connect(self.secilen_dosyayi_yukle)
        self.ui.pushButton_2.clicked.connect(self.tabloyu_pdf_yazdir)

    def showEvent(self, event):
        super().showEvent(event)
        self.sorulari_yukle()

    def sorulari_yukle(self):
        self.ui.tableWidget.setRowCount(len(self.veri.sorular))
        for i, satir in enumerate(self.veri.sorular):
            for j, hucre in enumerate(satir):
                self.ui.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(hucre))

    def secilen_dosyayi_yukle(self):
        dosya_adi, _ = QtWidgets.QFileDialog.getOpenFileName(self, "CSV Dosyası Seç", "", "CSV Dosyası (*.csv)")
        if not dosya_adi:
            return

        with open(dosya_adi, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader, None)
            veriler = [row for row in reader if len(row) == 7]

        self.ui.tableWidget.setRowCount(len(veriler))
        for i, satir in enumerate(veriler):
            for j, hucre in enumerate(satir):
                self.ui.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(hucre))

    def tabloyu_pdf_yazdir(self):
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)

        dosya_adi, _ = QtWidgets.QFileDialog.getSaveFileName(self, "PDF Olarak Kaydet", "", "PDF Dosyası (*.pdf)")
        if not dosya_adi:
            return
        if not dosya_adi.endswith(".pdf"):
            dosya_adi += ".pdf"

        printer.setOutputFileName(dosya_adi)

        satir_sayisi = self.ui.tableWidget.rowCount()
        sutun_sayisi = self.ui.tableWidget.columnCount()

        html = "<h2>Soru Tablosu</h2><table border='1' cellspacing='0' cellpadding='4'>"
        html += "<tr>"
        for j in range(sutun_sayisi):
            baslik = self.ui.tableWidget.horizontalHeaderItem(j)
            html += f"<th>{baslik.text() if baslik else ''}</th>"
        html += "</tr>"

        for i in range(satir_sayisi):
            html += "<tr>"
            for j in range(sutun_sayisi):
                item = self.ui.tableWidget.item(i, j)
                html += f"<td>{item.text() if item else ''}</td>"
            html += "</tr>"
        html += "</table>"

        belge = QTextDocument()
        belge.setHtml(html)
        belge.print_(printer)

        QtWidgets.QMessageBox.information(self, "Başarılı", f"PDF oluşturuldu:\n{dosya_adi}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    uygulama_verisi = UygulamaVerisi()
    window = GirisEkrani(uygulama_verisi)
    window.show()
    sys.exit(app.exec_())
