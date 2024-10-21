from django.conf import settings
from django.views import View
from django.http import JsonResponse
from apps.models import Visitor, ClientInbox, Article, OwnerProfile, Testimonials, Product
from django.utils import timezone
from datetime import timedelta
from services.utils import is_valid_name, is_valid_phone_number
from services.firebase import firebase_delete, firebase_upload
from django.contrib.auth import get_user_model
import datetime

# Logger information object
import logging
logger = logging.getLogger('yummypiv')

class API(View):
    
    context = ''

    def get(self, request, *args, **kwargs):
        resp = JsonResponse({'status': False, 'data':{'msg': '403 Forbidden'}})     
        resp.status_code = 403
        return resp
        
    def post(self, request, *args, **kwargs):
        
        if (self.context == 'api-reporter'):            
            if (str(request.user) == 'AnonymousUser'):
                try:
                    ip_address = request.META.get('REMOTE_ADDR')                        
                    user_agent = request.META.get('HTTP_USER_AGENT')            
                    path = request.POST['path']                    
                    new_report = Visitor(ip_address=ip_address, user_agent=user_agent, path=path)   
                    new_report.save()
                    logger.info(f'{path} from {ip_address} saved to visitor')
                    return JsonResponse({'status': True, 'data': {'msg': 'Successfully report'}})     
                except Exception as error_report_visitor:
                    logger.error(f'report visitor {error_report_visitor}')
                    return JsonResponse({'status': False, 'data': {'msg': 'Fail report'}})     
            else:
                logger.info(f'Record skipped, because doesnot user public.')
                return JsonResponse({'status': False, 'data': {'msg': 'Youre not visitor!'}})     
            
        
        if (self.context == 'api-client-inbox'):
            try:
                ip_address = request.META.get('REMOTE_ADDR')                        
                user_agent = request.META.get('HTTP_USER_AGENT')    
                subject = request.POST['name']                    
                phone_input = request.POST['phone']                    
                desc = request.POST['message']                                            
                try:
                    valid_name, name_capital = is_valid_name(subject)
                    if (valid_name):
                        _valid, phone = is_valid_phone_number(phone_input) 
                        if (_valid):
                            new_inbox = ClientInbox(ip_address=ip_address, user_agent=user_agent, subject=name_capital, phone_number=phone, message=desc)
                            new_inbox.save()
                            logger.info(f'New inbox client from {ip_address} / name : {name_capital}')
                            return JsonResponse({'status': True, 'data': {'msg': 'Berhasil upload form, tunggu sampai kami menghubungi Anda.'}})  
                        else:
                            logger.error(f'Gagal validasi form field "whatsapp" - {phone_input}')
                            return JsonResponse({'status': False, 'data': {'msg': 'Nomor invalid, pastikan nomor yang di input valid. Ex: 081xxxxxx'}})                                    
                    else:
                        logger.error(f'Gagal validasi form field "subject" - {subject}')
                        return JsonResponse({'status': False, 'data': {'msg': 'Nama invalid, pastikan menggunakan nama yang sesuai.'}})                             
                except Exception as error_models:
                    logger.error(f'Terjadi masalah saat akan menyimpan inbox ke database - {error_models}')
                    return JsonResponse({'status': False, 'data': {'msg': 'Fail report'}})     
            except Exception as error:
                logger.error(f'API Client Inbox bermasalah pada data request - {error}')
                return JsonResponse({'status': False, 'data': {'msg': 'Data invalid, please check your form or reload page.'}})     
            
                
        if (self.context == 'api-news-delete'):
            article_id = request.POST['data-id']
            try:
                ip_address = request.META.get('REMOTE_ADDR')                        
                user_agent = request.META.get('HTTP_USER_AGENT')    
                            
                obj = Article.objects.get(id=int(article_id))
                firebase_delete(obj.img_link)
                obj.delete()
                logger.info(f'Berhasil menghapus artikel ID {article_id}')
                return JsonResponse({'status': True, 'data': {'msg': 'Article berhasil dihapus.'}})
            except Exception as err:
                logger.error(f'Gagal delete artikel ID {article_id}')
                return JsonResponse({'status': False, 'data': {'msg': 'Gagal hapus article, coba lagi beberapa saat.'}})
            
        
        if (self.context == 'api-social-link'):
            
            for sosmed in request.POST.items():                
                key = str(sosmed[0]).replace('-', '_')
                obj, created = OwnerProfile.objects.get_or_create(info=key, defaults={'content': sosmed[1]})
                obj.save()
                
                if (created is False):
                    obj.content = sosmed[1]
                    obj.save()                                
            
            try:
                logger.info(f'Berhasil update tautan sosial media')
                return JsonResponse({'status': True, 'data': {'msg': 'Tautan berhasil di update.'}})
            except Exception as err:
                logger.error(f'Gagal delete artikel ID {article_id}')
                return JsonResponse({'status': False, 'data': {'msg': 'Gagal hapus article, coba lagi beberapa saat.'}})
                

        if (self.context == 'api-visitor'):
            req_range = request.POST.get('data-range')
            now = timezone.now().date()

            visitor_weekly_graph = []

            if (req_range == 'monthly'):
                for day in range(30):
                    date = now - timedelta(days=day)
                    visitor_count = Visitor.objects.filter(visited_at__date=date).count()  # Hitung pengunjung per hari
                    visitor_weekly_graph.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'count': visitor_count
                    })   
                visitor_weekly_graph = sorted(visitor_weekly_graph, key=lambda x: datetime.datetime.strptime(x['date'], '%Y-%m-%d'))
                logger.info(f'Request API pengunjung bulanan')
                
            if (req_range == 'weekly'):
                for day in range(7):
                    date = now - timedelta(days=day)
                    visitor_count = Visitor.objects.filter(visited_at__date=date).count()  # Hitung pengunjung per hari
                    visitor_weekly_graph.append({
                        'date': date.strftime('%d %B'),
                        'count': visitor_count
                    })   
                visitor_weekly_graph = sorted(visitor_weekly_graph, key=lambda x: datetime.datetime.strptime(x['date'], '%d %B'))
                logger.info(f'Request API pengunjung mingguan')
                
            return JsonResponse({'status': True, 'data': visitor_weekly_graph})     
                
        
        if (self.context == 'api-edit-user'):
            
            try:
                username = request.POST.get('username-lock')
                try:
                    logger.info(f'Try to change user credential {username}')
                    user_model = get_user_model()
                    if (len(username) > 7):        
                        try:
                            selected_user = user_model.objects.get(username=username)                            
                            
                            for field, value in request.POST.items():
                                if (value):
                                    if hasattr(selected_user, field):
                                        if field == 'password':
                                            if len(value) > 7:  
                                                selected_user.set_password(value)
                                            else:
                                                logger.info(f'Rejected: Password must be more than 7 characters, continue change next field.')
                                                continue
                                        else:
                                            setattr(selected_user, field, value)       
                            selected_user.save()                                                             
                            logger.info(f'Akun user berhasil diubah {username}')
                            return JsonResponse({'status': True, 'data':{'msg': 'Perubahan data berhasil'}})
                        
                        except Exception as failed_create_user:
                            logger.error(f'Gagal mengubah data user {failed_create_user}')
                            return JsonResponse({'status': False, 'data':{'msg': 'Server maintenance (500 Internal Server)'}})
                    else:
                        logger.error(f'Karakter kurang atau invalid {username}')
                        return JsonResponse({'status': False, 'data':{'msg': 'Username/password terlalu pendek'}})
                    
                except Exception as error:
                    logger.error(f'Form data yang di input tiak valid! - {error_field}')
                    return JsonResponse({'status': False, 'data':{'msg': f'{error_field}'}})                    
                
            except Exception as error_field:
                logger.error(f'Form data yang di input tiak valid! - {error_field}')
                return JsonResponse({'status': False, 'data':{'msg': f'{error_field}'}})
                
                    
        if (self.context == 'api-update-homepage-upper'):
            try:
                for key, value in request.POST.items():
                    key_correction = str(key).replace('-', '_')
                    try: 
                        exist_data = OwnerProfile.objects.get(info=key_correction)
                        exist_data.content = value
                        exist_data.save()
                    except Exception as no_data:
                        new_data = OwnerProfile(info=key_correction, content=value)
                        new_data.save()
            
                logger.info(f'Data upper homepage has been updated.')
                return JsonResponse({'status': True, 'data':{'msg': 'Perubahan data berhasil'}})
            except Exception as error:
                logger.error(f'Error when update data homepage upper! - {error}')
                return JsonResponse({'status': False, 'data':{'msg': f'{error}'}})   
        
        if (self.context == 'api-update-about'):
            try:
                for key, value in request.POST.items():
                    key_correction = str(key).replace('-', '_')
                    try: 
                        exist_data = OwnerProfile.objects.get(info=key_correction)
                        exist_data.content = value
                        exist_data.save()
                    except Exception as no_data:
                        new_data = OwnerProfile(info=key_correction, content=value)
                        new_data.save()
            
                logger.info(f'Data about has been updated.')
                return JsonResponse({'status': True, 'data':{'msg': 'Perubahan data berhasil'}})
            except Exception as error:
                logger.error(f'Error when update data about! - {error}')
                return JsonResponse({'status': False, 'data':{'msg': f'{error}'}})
            
        if (self.context == 'api-add-testimonial'):
            try:                    
                exist_data = Testimonials()
                exist_data.customer_name = request.POST.get('testimonial-customer')
                exist_data.content = request.POST.get('testimonial-content')
                        
                image = request.FILES.get('testimonial-image')
                if (image):
                    sts = False
                    msg = ''
                    if (image.name).endswith('.png'):
                        sts, msg = firebase_upload('media/testimonial', image, image.name, ct='png')
                    if (image.name).endswith('.jpg'):
                        sts, msg = firebase_upload('media/testimonial', image, image.name, ct='jpg')
                    if (image.name).endswith('.webp'):
                        sts, msg = firebase_upload('media/testimonial', image, image.name, ct='webp')
                    else:
                        exist_data.img_link = "https://storage.googleapis.com/yummypiv-app.appspot.com/media/testimonial/avatar.png"
                        logger.info(f'Image not supported, force to default avatar.')
                        exist_data.save()
                        logger.info(f'Success uploaded testimonial')
                        return JsonResponse({'status': True, 'data':{'msg': 'Testimoni berhasil ditambah. (default avatar)'}})
                        
                    if (sts):
                        exist_data.img_link = msg
                        logger.info(f'Testimonial image save to firebase -> {msg}')
                else:
                    exist_data.img_link = "https://storage.googleapis.com/yummypiv-app.appspot.com/media/testimonial/avatar.png"
                    logger.info(f'Image does not exist, force to default avatar.')
                    
                exist_data.save()
                logger.info(f'Success uploaded testimonial')
                return JsonResponse({'status': True, 'data':{'msg': 'Testimoni berhasil ditambah.'}})
            except Exception as error:
                logger.error(f'Error when data testimonial! - {error}')
                return JsonResponse({'status': False, 'data':{'msg': f'{error}'}})                
                
        if (self.context == 'api-delete-testimonial'):
            try:                
                print('Berhasil kok',request.POST.get('testimonial-id'))
                logger.info(f'Data about has been updated.')
                return JsonResponse({'status': True, 'data':{'msg': 'Okay'}})
            except Exception as error:
                logger.error(f'Error when update data about! - {error}')
                return JsonResponse({'status': False, 'data':{'msg': f'{error}'}})

        if (self.context == 'api-add-product'):
            try:                    
                
                new_product = Product()
                new_product.product_name = request.POST.get('product-name')
                new_product.price = request.POST.get('product-price')
                new_product.description = request.POST.get('product-description')
                        
                image = request.FILES.get('product-image')
                if (image):
                    sts = False
                    msg = ''
                    if (image.name).endswith('.png'):
                        sts, msg = firebase_upload('media/product', image, image.name, ct='png')
                    if (image.name).endswith('.jpg'):
                        sts, msg = firebase_upload('media/product', image, image.name, ct='jpg')
                    if (image.name).endswith('.webp'):
                        sts, msg = firebase_upload('media/product', image, image.name, ct='webp')
                        
                    if (sts):
                        new_product.img_link = msg
                        new_product.save()
                        logger.info(f'Product image save to firebase -> {msg}')
                        return JsonResponse({'status': True, 'data':{'msg': 'Product berhasil ditambah.'}})
                    else:
                        new_product.save()                      
                        logger.info(f'Success uploaded product with no image!')
                        return JsonResponse({'status': True, 'data':{'msg': 'Product berhasil ditambah. (default avatar)'}})
                        
                else:
                    new_product.img_link = "https://storage.googleapis.com/yummypiv-app.appspot.com/media/testimonial/avatar.png"
                    logger.info(f'Image does not exist, force to default avatar.')
                    
                new_product.save()
                logger.info(f'Success uploaded Product')
                return JsonResponse({'status': True, 'data':{'msg': 'Product berhasil ditambah.'}})
            except Exception as error:
                logger.error(f'Error when data Product! - {error}')
                return JsonResponse({'status': False, 'data':{'msg': f'{error}'}})   