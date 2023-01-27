from django.shortcuts import render, get_object_or_404, redirect
from .models import Struk, TipeKendaraan 
from .forms import StrukForm, SearchForm, TiketForm
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.views import View
from django.views.generic import DetailView
from escpos.printer import Usb
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from thermalprinter import thermalprinter
from math import floor
from escpos import printer
from escpos.printer import Serial
from time import gmtime, strftime

@login_required
def Dashboard(request):
    context = {
        'navbar': 'dashboard'
    }
    return render(request, 'home/dashboard.html', context)

@login_required
def Kelola(request):
    paginate = Paginator(Struk.objects.all().order_by('status', '-tanggaljam_masuk'), 10)
    page = request.GET.get('page')
    struk = paginate.get_page(page)

    form_class = StrukForm()

    if request.method == "POST":
        form_class = StrukForm(request.POST)
        if form_class.is_valid():
            plat_nomor = form_class.cleaned_data.get('plat_nomor')
            tipekendaraan = form_class.cleaned_data.get('tipekendaraan')
            tanggaljam_masuk = datetime.now()
            Struk.objects.create(
                plat_nomor = plat_nomor,
                tipekendaraan = tipekendaraan,
                tanggaljam_masuk = tanggaljam_masuk
            )
            
        messages.success(request, "Struk berhasil ditambahkan")
        return redirect('kelola')

    context = {
        'navbar': 'kelola',
        'struk': struk,
        'form': form_class,
    }
    return render(request, 'home/kelola.html', context)

@login_required
def Keluar(request, pk):
    struk_qs = Struk.objects.filter(pk=pk)
    struk_qs.update(tanggaljam_keluar=datetime.now())

    messages.success(request, "Struk berhasil diklaim")
    return redirect('kelola')
        
@login_required
def Dibayar(request, pk):
    struk_qs = Struk.objects.filter(pk=pk)
    struk_qs.update(status=2)

    messages.success(request, "Struk berhasil dibayar")
    return redirect('kelola')

@login_required
def Search(request):
    if request.method == "POST":
        searched = request.POST['searched']
        struk = Struk.objects.filter(slug__contains=searched).order_by('status', '-tanggaljam_masuk')

        context = {
            'searched': searched,
            'struk': struk,
            'navbar': 'telusuri'
        }
    else:
        return redirect(request, 'kelola')

    return render(request, 'home/search.html', context)

@login_required
def struk_render_to_pdf_view(request, *args, **kwargs):
    pk = kwargs.get('pk')
    struk = get_object_or_404(Struk, pk=pk)


    template_path = 'home/struk.html'

    context = {
        'struk': struk
    }

    response = HttpResponse(content_type='application/pdf')

    response['Content-Disposition'] = 'filename="struk.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error' + html + '</pre>')
    return response

@login_required
def render_to_pdf(request):
    template_path = 'home/struk.html'

    context = {
        'test': 'test'
    }

    response = HttpResponse(content_type='application/pdf')

    response['Content-Disposition'] = 'filename="struk.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error' + html + '</pre>')
    return response

@login_required
def Tiket(request):
    if request.method == 'POST':
        searched = request.POST.get('searched')
        struk = Struk.objects.get(slug=searched)
        tanggaljam_keluar = timezone.now()
        date_diff = floor((tanggaljam_keluar - struk.tanggaljam_masuk).total_seconds() / 3600)
        if date_diff > 10:
            date_diff = 10
            total_harga = struk.tipekendaraan.harga_awal + struk.tipekendaraan.harga_perjam * date_diff
            struk.tanggaljam_keluar = datetime.now()
            struk.total = total_harga
            context = {
                'searched': searched,
                'struk': struk,
                'tanggaljam_keluar': tanggaljam_keluar,
                'date_diff': date_diff,
                'total_harga': total_harga,
                'navbar': 'tiket'
            }
            return render(request, 'home/tiket.html', context)
        # total_harga = struk.tipekendaraan.harga_awal + struk.tipekendaraan.harga_perjam * date_diff
        # context = {
        #     'searched': searched,
        #     'struk': struk,
        #     'tanggaljam_keluar': tanggaljam_keluar,
        #     'date_diff': date_diff,
        #     'total_harga': total_harga,
        #     'navbar': 'tiket'
        # }
        if struk == None:
            return render(request, 'home/tiket.html', {'navbar': 'tiket'})

        else:
            total_harga = struk.tipekendaraan.harga_awal + struk.tipekendaraan.harga_perjam * date_diff
            struk.tanggaljam_keluar = datetime.now()
            struk.total = total_harga
            context = {
                'searched': searched,
                'struk': struk,
                'tanggaljam_keluar': tanggaljam_keluar,
                'date_diff': date_diff,
                'total_harga': total_harga,
                'navbar': 'tiket'
            }
            return render(request, 'home/tiket.html', context)
    else:
        return render(request, 'home/tiket.html', {'navbar': 'tiket'})

@login_required
def TiketBayar(request, pk):
    if request.method == 'POST':
        struk_qs = Struk.objects.get(pk=pk)
        tanggaljam_keluar = timezone.now()
        date_diff = floor((tanggaljam_keluar - struk_qs.tanggaljam_masuk).total_seconds() / 3600)
        total_harga = struk_qs.tipekendaraan.harga_awal + struk_qs.tipekendaraan.harga_perjam * date_diff
        plat_nomor = request.POST['searched']
        struk_qs.plat_nomor = plat_nomor
        struk_qs.status = 2
        struk_qs.tanggaljam_keluar = datetime.now()
        struk_qs.total = total_harga
        struk_qs.save()

        # p = Usb(0x04B8, 0x0E11)
        # p.set(align='left')
        # p.text("SMK 7 SAMARINDA" + "\n")
        # p.text("Nomor Plat: {}\n".format(struk_qs.plat_nomor))
        # p.text("Tanggal Jam Masuk: {}\n".format(struk_qs.tanggaljam_masuk))
        # p.text("Tanggal Jam Keluar: {}\n".format(struk_qs.tanggaljam_keluar))
        # p.text("Total Harga: {}\n".format(struk_qs.total))
        # p.text("Tipe Kendaraan: {}\n".format(struk_qs.tipekendaraan))
        # p.text("TERIMA KASIH" + "\n")
        # p.cut()

        messages.success(request, "Struk berhasil dibayar & Plat Nomor")
        return redirect('tiket')

def AmbilTiket(request):
    tipekendaraan = TipeKendaraan.objects.all()
    
    context = {
        'tipe': tipekendaraan,
        'navbar': 'ambiltiket'
    }
    return render(request, 'home/ambiltiket.html', context)

class AmbilTiketView(DetailView):
    queryset = TipeKendaraan.objects.all()
    template_name = 'home/ambiltiket1.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

def AmbilTiket2(request, pk):
    tipe = get_object_or_404(TipeKendaraan, pk=pk)
    tanggaljam_masuk = datetime.now()
    jam_masuk = datetime.now().strftime('%H:%M:%S')
    tiket_ambil = Struk.objects.create(tipekendaraan=tipe, status=1, tanggaljam_masuk=tanggaljam_masuk, jam_masuk=jam_masuk)
    tiket_ambil.save()
    primary = tiket_ambil.pk
    print(primary)

    # p = Usb(0x04B8, 0x0E11)
    # p.set(align='left')
    # p.text("SMK 7 SAMARINDA" + "\n")
    # p.text("Tanggal Jam Masuk: {}\n".format(jam_masuk))
    # p.text("Tipe Kendaraan: {}\n".format(tiket_ambil.tipekendaraan))
    # p.image(tiket_ambil.qr_code)
    # p.text("TIKET JANGAN SAMPAI HILANG" + "\n")
    # p.cut()

    # We already have both IDs, the IN_ENDPOINT is usually 0x81 while OUT_ENDPOINT can be found with this command:
    # lsusb -vvv -d VENDOR_ID:DEVICE_ID | grep bEndpointAddress | grep OUT
    #
    # Serial (UART) printers can be initialized by specifying the device name, for example:
    # p = printer.Serial("/dev/ttyUSB0", timeout=6000)
    #
    #   CHAT GPT
    #
    # p = Serial(port='COM3', baudrate=9600, timeout=5) 
    # p.text("Hello, World!")
    # p.cut()
    #
    # Port: To find the correct serial port that the thermal printer is connected to, 
    # you can check the Device Manager in Windows. Open the Device Manager by pressing the Windows key + X, 
    # then selecting Device Manager from the menu. Look for the thermal printer in the list of devices 
    # under the "Ports (COM & LPT)" or "Print queues" category, the port will be listed next to it, for example, 
    # "COM3"
    #
    # Baudrate: Baudrate is the speed at which data is transmitted over a serial connection, 
    # it's measured in bits per second (bps). The baud rate is typically set by the manufacturer 
    # and can be found in the printer's manual or in the technical specifications. 
    # Common baud rates for thermal printers are 9600, 19200, and 38400. If you can't find the baudrate 
    # information in the manual, you can try using different baudrate options and see which one works.
    #
    # Timeout: Timeout value is the amount of time that the printer will wait for a response before timing out. 
    # It's typically set in seconds. The default value is 5 seconds, but it could be different for your printer. 
    # If you are experiencing communication issues, you might want to try increasing the timeout value.

    messages.success(request, "Ahh")
    return redirect('ambiltiket1', pk=pk)


