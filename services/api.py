from django.conf import settings
from django.views import View
from django.http import JsonResponse
from apps.models import Visitor, ClientInbox, Article, OwnerProfile, Testimonials, Product
from django.utils import timezone
from datetime import timedelta
from services.utils import is_valid_name, is_valid_phone_number, generate_visit_id
from services.firebase import firebase_delete, firebase_upload
from services.owner_profile_service import update_owner_profile
from services.media_service import upload_media, delete_media
from django.contrib.auth import get_user_model
from services.utils import role_required
from django.utils.decorators import method_decorator
import datetime

# Logger information object
import logging
logger = logging.getLogger('yummypiv')

@method_decorator(role_required(['root', 'admin', 'staff']), name='dispatch')
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
                    visit_id = request.POST['visit_id']
                    if (visit_id == ''):
                        logger.info(f'Client has no `visit_id`, visit record blocked.')
                        return JsonResponse({'status': False, 'data': {'msg': '`visit_id` is empty!'}})     
                    else:
                        try:
                            recorded = Visitor.objects.get(visit_id=visit_id)
                            logger.info(f'Client already recorded, skiiping record visitor - {visit_id}')                        
                            return JsonResponse({'status': True, 'data': {'msg': 'Client already recorded, skiiping record visitor.'}})     
                        except Exception as didnt_match:                            
                            logger.info(f'`visit_id` didnt match on Query! blocked!')                        
                            return JsonResponse({'status': True, 'data': {'msg': 'Succes without record, cause not match query.'}})                                 
                            
                except Exception as error_report_visitor:
                    logger.error(f'report visitor {error_report_visitor}')
                    return JsonResponse({'status': False, 'data': {'msg': 'Fail report'}})     
            else:
                logger.info(f'Record skipped, because doesnot user public.')
                return JsonResponse({'status': False, 'data': {'msg': 'Youre not visitor!'}})     
            
        if (self.context == 'api-visitor-request'):            
            if (str(request.user) == 'AnonymousUser'):
                try:
                    ip_address = request.META.get('REMOTE_ADDR')                        
                    user_agent = request.META.get('HTTP_USER_AGENT')            
                    path = request.POST['path']                    
                    visit_id = generate_visit_id(ip_address, user_agent, path)
                    new_report = Visitor(ip_address=ip_address, user_agent=user_agent, path=path, visit_id=visit_id)   
                    new_report.save()
                    logger.info(f'Generate for new visitor ({visit_id})')
                    return JsonResponse({'status': True, 'data': {'msg': 'Successfully generate visit id', 'visit_id': visit_id}})     
                except Exception as error_generate:
                    logger.error(f'report visitor {error_generate}')
                    return JsonResponse({'status': False, 'data': {'msg': f'Failed to generate visit id ({error_generate})'}})     
            else:
                logger.info(f'Generate blocked cause request not public!')
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
                 obj = Article.objects.get(id=int(article_id))
                 delete_media(obj.img_link)
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
                    logger.error(f'Form data yang di input tiak valid! - {error}')
                    return JsonResponse({'status': False, 'data':{'msg': f'{error}'}})

            except Exception as error:
                logger.error(f'Form data yang di input tiak valid! - {error}')
                return JsonResponse({'status': False, 'data':{'msg': f'{error}'}})
                
                    
        if (self.context == 'api-update-homepage-upper'):
             try:
                 update_owner_profile(request.POST)
                 logger.info(f'Data upper homepage has been updated.')
                 return JsonResponse({'status': True, 'data':{'msg': 'Perubahan data berhasil'}})
             except Exception as error:
                 logger.error(f'Error when update data homepage upper! - {error}')
                 return JsonResponse({'status': False, 'data':{'msg': f'{error}'}})
        
        if (self.context == 'api-update-about'):
             try:
                 update_owner_profile(request.POST)
                 logger.info(f'Data about has been updated.')
                 return JsonResponse({'status': True, 'data':{'msg': 'Perubahan data berhasil'}})
             except Exception as error:
                 logger.error(f'Error when update data about! - {error}')
                 return JsonResponse({'status': False, 'data':{'msg': f'{error}'}})
            
        if (self.context == 'api-add-testimonial'):
             try:
                 testimonial = Testimonials()
                 testimonial.customer_name = request.POST.get('testimonial-customer')
                 testimonial.content = request.POST.get('testimonial-content')

                 image_profile = request.FILES.get('testimonial-image')
                 if image_profile:
                     upload_media('media/testimonial', image_profile, testimonial, 'img_link', convert_webp=True)
                 else:
                     testimonial.img_link = "https://storage.googleapis.com/yummypiv-app.appspot.com/media/testimonial/avatar.png"

                 image_banner = request.FILES.get('testimonial-banner-image')
                 if image_banner:
                     upload_media('media/testimonial', image_banner, testimonial, 'img_banner', convert_webp=True)
                 else:
                     testimonial.img_banner = "https://storage.googleapis.com/yummypiv-app.appspot.com/media/testimonial/default-banner.webp"

                 testimonial.save()
                 logger.info(f'Success uploaded testimonial')
                 return JsonResponse({
                     'success': True,
                     'message': 'Testimoni berhasil ditambah.',
                     'data': {
                         'testimonial_id': testimonial.id,
                         'customer_name': testimonial.customer_name,
                         'img_link': testimonial.img_link,
                         'img_banner': testimonial.img_banner
                     }
                 })
             except Exception as error:
                 logger.error(f'Error when data testimonial! - {error}')
                 return JsonResponse({'status': False, 'data':{'msg': f'{error}'}})
                
        if (self.context == 'api-delete-testimonial'):
            try:                                
                selected_product_id = request.POST.get('testimonial-id')
                selected_product = Testimonials.objects.get(id=selected_product_id)
                selected_product.delete()
                logger.info(f'Testimonial has been deleted.')
                return JsonResponse({'status': True, 'data':{'msg': 'Testimonial deleted!'}})
            except Exception as error:
                logger.error(f'Error when delete testimonial! - {error}')
                return JsonResponse({'status': False, 'data':{'msg': f'{error}'}})

        if (self.context == 'api-add-product'):
             try:
                 product = Product()
                 product.product_name = request.POST.get('product-name')
                 product.price = request.POST.get('product-price')
                 product.description = request.POST.get('product-description')

                 image = request.FILES.get('product-image')
                 if image:
                     success, msg = upload_media('media/product', image, product, 'img_link', convert_webp=True)
                     if not success:
                         product.img_link = "https://storage.googleapis.com/yummypiv-app.appspot.com/media/testimonial/avatar.png"
                         product.save()
                         logger.info(f'Success uploaded product with default image!')
                         return JsonResponse({'status': True, 'data':{'msg': 'Product berhasil ditambah. (default avatar)'}})
                 else:
                     product.img_link = "https://storage.googleapis.com/yummypiv-app.appspot.com/media/testimonial/avatar.png"

                 product.save()
                 logger.info(f'Success uploaded Product')
                 return JsonResponse({
                     'success': True,
                     'message': 'Product berhasil ditambah.',
                     'data': {
                         'product_id': product.id,
                         'product_name': product.product_name,
                         'img_link': product.img_link,
                         'price': product.price
                     }
                 })
             except Exception as error:
                 logger.error(f'Error when data Product! - {error}')
                 return JsonResponse({'status': False, 'data':{'msg': f'{error}'}})
            
        if (self.context == 'api-delete-product'):
            try:                
                logger.info(f'Start deleting product')
                selected_product_id = request.POST.get('product-id')
                selected_product = Product.objects.get(id=selected_product_id)
                selected_product.delete()
                return JsonResponse({'status': True, 'data':{'msg': 'Product deleted!'}})
            except Exception as error:
                logger.error(f'Error when delete data product! - {error}')
                return JsonResponse({'status': False, 'data':{'msg': f'{error}'}})