### chuc nang gui Emali ### ###Them sua xoa danh sach###
from django.shortcuts import render,HttpResponse,redirect
from myapp import models
from django.db.models import Q
from django.contrib.sites.shortcuts import get_current_site  #lay trang hien tai
from django.utils.encoding import force_bytes,force_text   #ma hoa
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode  #giai ma
from django.core.mail import EmailMessage  #truyen gui email
from django.template.loader import render_to_string
from django.contrib.auth import login
from myapp.tokens import tuan
from datetime import datetime
from django.contrib.auth import login, authenticate

def signUp(request):
    error={}
    if(request.method =="POST"):
        email=request.POST.get('email')
        user=request.POST.get('user')
        password=request.POST.get('password')
        count = models.AuthUser.objects.filter(Q(email=email)|Q(username=user)).count()
        if count > 0:
            error['error']='trung email hoac username'
        else:
            s=models.AuthUser(email=email, username=user, password=password)
            print(s.email)
            print(s.username)
            s.save()
            #tao cau truc email
            current_site=get_current_site(request)
            email_subject='xac thuc thong tin '
            massge = render_to_string('activateemail.html', {
                'user':user,
                'domain':current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(s.pk)).decode(),  #mahoa
                'token':tuan.make_token(s)
            }) #chuy noi dung himl vao email
            to_email=email
            Email = EmailMessage(email_subject,massge,to=[to_email]) #gui den email
            Email.send()
            return HttpResponse('vao email xac thuc')
    return render(request,'sign up.html', {'error':error})

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64)) #giai ma uidb64
        user= models.AuthUser.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, models.AuthUser.DoesNotExist):
        user= None
    if user is not None and tuan.check_token(user,token):
        user.is_active=True
        user.save()
        login(request, user)
        return HttpResponse("Xac nhan thanh cong ")
    else:
        return  HttpResponse("Xac Nhan khong thanh Cong ")


def home(request):
    models.DjangoSession.objects.filter(expire_date__lt=datetime.utcnow()).delete()    #neu thoi gian lam viec nho hon thoi gan hien tai thi xoa sess
    if not request.session.has_key('username'):
        return redirect('login')
    else:
        username = request.session['username']
    return render(request,'home.html',)

def Mylogin(request):
    error={}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        exist_user = models.AuthUser.objects.filter(Q(is_active=1), Q(username=username) | Q(email=username))
        if exist_user.exists() and exist_user[0].password == password:
            login(request, exist_user[0])
            request.session['username'] = username  # ki login thi tao phien lam viec
            request.session.set_expiry(0)  # khoang thoi gian lam viec cua phien
            return redirect('home')
        else:
            error['uname'] = 'sai toan khoan hoawc mk'
    return render(request, 'login.html', {'error': error})


###Them sua xoa##
def Hienthi(request):
    data = models.SanPham.objects.all()
    if( 'add' in request.POST):
        return redirect('add')
    if('edit' in request.POST):
        for a in data:
            if(request.POST.get('%d' %a.id)):      #kiem tra so gui len co trong id khong
                return redirect('edit', id=a.id)
    if ('delete' in request.POST):
        for a in data:
            if(request.POST.get('%d' %a.id)):
                a.delete()
                return redirect('data')
    return render(request, 'hienthi.html', {'data':data})

def edit(request,id):
    data = models.SanPham.objects.get(id=id)
    if (request.method == 'POST'):
        data.masp=request.POST.get('masp')
        data.tensp=request.POST.get('tensp')
        data.gia=request.POST.get('gia')
        data.save()
        return redirect('data')
    return render(request,'edit.html',{'data1':data})

def add(request):
    if(request.method == 'POST'):
        masp = request.POST.get('masp')
        tensp = request.POST.get('tensp')
        gia = request.POST.get('gia')
        data = models.SanPham(masp=masp,tensp=tensp,gia=gia)
        data.save()
        return redirect('data')
    return render(request,'addsanpham.html')


###ICON_EMAIL###
def IconEmail(request):
    return render(request,'IconEmail.html')

# def base_manager(request):
#     ######In so tin nhan#####
#     List = {}
#     # user = request.session.has_key('username')
#     data = models.AuthUser.objects.filter(username='tt')
#     for da in data:
#     #     data1={}
#         print(da.id)
#     #     data1['a']=da.id
#         count = models.EmailMassage.objects.filter(Emailsent=11).count()
#         print(count)
#     # data1['count'] =count
#     ######################

    # if request.method == 'POST':
    #     data = {}
    #     data['emailsent'] = request.POST.get('emailsent')
    #     data['emailto'] = request.POST.get('emailto')
    #     data['content'] = request.POST.get('conttent')
    #     a=models.PeopleSent(Emailsent_id=models.AuthUser.objects.filter(email=data['emailsent'])[0].id)
    #     a.save()
    #     b=models.PeopleTo(Emailto_id=models.AuthUser.objects.filter(email=data['emailto'])[0].id)
    #     b.save()
    #     # c=models.EmailMassage(content=data['content'],Is_seen=0,Emailsent_id=models.PeopleSent.objects.filter(Emailsent=models.AuthUser.objects.filter(email=data['emailsent'])[0].id),
    #     #                       Emailto_id=models.PeopleTo.objects.filter(Emailto=models.AuthUser.objects.filter(email=data['emailto'])[0].id))
    #     # c.save()
    #     #     peoplesent1=models.PeopleSent(Email=peoplesent.id)
    #     #     for people1 in peoplesent1:
    #     #         b=models.EmailMassage(content=content,IS_see=0,Emailsent=people1.id)
    #     #         print(peoplesent1.id)
    #     # peopleto = models.AuthUser.objects.get(email=emailto)
    #     # for peoplet in peopleto:
    #     #     b=models.PeopleTo(Email=peoplet.id)
    #     #     b.save()
    #     #     peopleto1 = models.PeopleTo(Email=peoplesent.id)
    #     #     for peoplet1 in peoplet1:
    #     #         print(peopleto1.id)
    # return render(request, 'test.html',{'count':count})

# def Email(request):
#     if request.method == 'POST':
#         data = {}
#         data['emailsent'] = 'doanhtuan14111997@gmail.com'
#         data['emailto'] = request.POST.get('sentto')
#         data['content'] = request.POST.get('comment')
#         a=models.EmailMassage(content=data['content'],Is_see=0,Emailsent=data['emailsent'],Emailto=data['emailto'])
#         a.save()
#     return render(request,'test.html')

def ShowEmail(request):
    data=models.EmailMassage.objects.all()
    if request.method=='POST':
        for a in data:
            if request.POST.get('%d' %a.id):
                print(a.id)
                email = models.EmailMassage.objects.get(id=a.id)
                email.Is_see = 1
                email.save()
    return render(request,'Show_Email.html',{'data':data})

def Email(request):
    if request.method == 'POST':
        data = {}
        data['emailsent'] = 'doanhtuan14111997@gmail.com'
        data['emailto'] = request.POST.get('sentto')
        data['content'] = request.POST.get('comment')
        a=models.Emailsent(content=data['content'],Email=data['emailsent'])
        a.save()
        b=models.Emailto(content=data['content'],Email=data['emailto'],Is_see=0)
        b.save()
    return render(request,'test.html')

def LinkFile(request):
    return render(request,'link_File.html')









# Create your views here.
