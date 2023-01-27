from django.db import models
from django.utils.text import slugify 
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw
from math import floor
from django.urls import reverse
from django.utils.timezone import localdate

STATUS = (
    (1, 'Sedang di parkiran'),
    (2, 'Dibayar'),
)

class TipeKendaraan(models.Model):
    id_tipe = models.AutoField(primary_key=True)
    nama_tipe = models.CharField(max_length=10)
    harga_awal = models.IntegerField()
    harga_perjam = models.IntegerField()
    slug = models.SlugField(unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nama_tipe)
        super(TipeKendaraan, self).save(*args, **kwargs)

    def __str__(self):
        return self.nama_tipe

    def get_absolute_url(self):
        return reverse("ambiltiket1", kwargs={"pk": self.pk})

    def get_tiket_url(self):
        return reverse("ambiltiket2", kwargs={"pk": self.pk})
    

class Struk(models.Model):
    id_struk = models.AutoField(primary_key=True)
    plat_nomor = models.CharField(max_length=20)
    tipekendaraan = models.ForeignKey(TipeKendaraan, on_delete=models.CASCADE)
    tanggaljam_masuk = models.DateTimeField(null=True, blank=True)
    jam_masuk = models.TimeField(null=True, blank=True)
    tanggaljam_keluar = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField(choices=STATUS, default=1)
    total = models.CharField(max_length=30, blank=True, null=True)  
    qr_code = models.ImageField(upload_to='images/', blank=True, null=True)
    slug = models.SlugField(null=True, blank=True)
    
    def __str__(self):
        return self.slug

    def save(self, *args, **kwargs):
        self.slug = slugify(f'{self.id_struk}{self.tipekendaraan.id_tipe}{self.jam_masuk}')
        qrcode_img = qrcode.make(self.slug)
        canvas = Image.new('RGB', (290, 290), 'white')
        draw = ImageDraw.Draw(canvas)
        canvas.paste(qrcode_img)
        fname = f'qr_code-{self.slug}'+'.png'
        buffer = BytesIO()
        canvas.save(buffer, 'PNG')
        self.qr_code.save(fname, File(buffer), save=False)
        canvas.close()
        super().save(*args, **kwargs)

    @property
    def date_diff(self):
        if self.tanggaljam_keluar is None:
            return ("Belum Keluar")
        return floor((self.tanggaljam_keluar - self.tanggaljam_masuk).total_seconds() / 3600)


