from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from django.shortcuts import render, redirect
from services.news import most_viewed_article
from services.utils import role_required
from services.firebase import firebase_upload, firebase_delete
from services.addons import analyze_storage
from services.notification import system_notification
from apps.models import Partner, Article, Visitor
from django.utils import timezone
from datetime import timedelta


# Logger information object
from services.logger import logger




@method_decorator(role_required(['root', 'admin', 'staff']), name='dispatch')
class Dashboard(View):
    context = ''

    def get(self, request, *args, **kwargs):

        if (self.context == 'main-dashboard'):
            total_ , used_, free_ = analyze_storage()
            ctx = {}
            now = timezone.now()
            # Pengunjung harian
            start_of_today = now.replace(hour=0, minute=0, second=0)
            daily_visitors = Visitor.objects.filter(visited_at__gte=start_of_today).count()
            
            start_of_week = now - timedelta(days=7)
            weekly_visitors = Visitor.objects.filter(visited_at__gte=start_of_week)
            weekly_visitors_count = weekly_visitors.count()
            
            start_of_month = now - timedelta(days=30)
            monthly_visitors = Visitor.objects.filter(visited_at__gte=start_of_month)
            monthly_visitors_count = monthly_visitors.count()

            visitor_weekly_graph = []

            for day in range(7):
                date = now + timedelta(days=day)
                visitor_count = Visitor.objects.filter(visited_at__date=date).count()  # Hitung pengunjung per hari
                visitor_weekly_graph.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'count': visitor_count
                })            
            
            most_viewed = most_viewed_article()
            ctx['articles'] = most_viewed
            ctx['daily_visit'] = daily_visitors
            ctx['weekly_visit'] = weekly_visitors_count
            ctx['monthly_visit'] = monthly_visitors_count
            ctx['total'] = total_
            ctx['system'] = used_
            ctx['free'] = free_
            ctx['notifications'] = system_notification()
            # Konversi GB ke MB
            total_size_mb = float(total_) * 1024
            # Hitung persentase
            percentage = (float(used_) / total_size_mb) * 100
            ctx['system_percent'] = percentage
            
            return render(request, 'main_dashboard.html', context=ctx)
        
        if (self.context == 'partner-dashboard'):
            partner_list = Partner.objects.all()
            ctx = {'partner_list': partner_list}
            return render(request, 'partner_dashboard.html', context=ctx)
        
        if (self.context == 'news-dashboard'):
            news_list = Article.objects.all()
            ctx = {'news_list': news_list}
            return render(request, 'news_dashboard.html', context=ctx)
        
        if (self.context == 'create-news-dashboard'):            
            return render(request, 'upload_news_dashboard.html')
        
        if (self.context == 'edit-news-dashboard'):
            ctx = {}
            try:
                news = Article.objects.get(id=int(self.kwargs.get('article_id')))
                ctx['article'] = news
                return render(request, 'edit_news_dashboard.html', context=ctx)
            except Exception as no_data:
                logger.error(f'{no_data} - Artikel objek tidak ada')
                return redirect('create-news-dashboard')


    def post(self, request, *args, **kwargs):
        
        if (self.context == 'new-partner'):
            try:
                partner_name = request.POST.get('partner-name')
                partner_image = request.FILES.get('image')
                if (partner_image.name).endswith('.png'):
                    sts, msg = firebase_upload('partner', partner_image, partner_name, ct='png')                    
                if (partner_image.name).endswith('.jpg'):
                    sts, msg = firebase_upload('partner', partner_image, partner_name, ct='jpg')                    
                if (partner_image.name).endswith('.jpeg'):
                    sts, msg = firebase_upload('partner', partner_image, partner_name, ct='jpeg')                    
                if (partner_image.name).endswith('.webp'):
                    sts, msg = firebase_upload('partner', partner_image, partner_name, ct='webp')               

                new_partner = Partner(name=partner_name, img_link=msg)
                new_partner.save()

                return JsonResponse({'status': 'true', 'data':{'msg': 'Partner berhasil ditambahkan.'}})     
            except Exception as firebase_error:
                logger.error(f'{firebase_error} - Gagal upload ke firebase cek services/firebase.py')
                return JsonResponse({'status': 'false', 'data':{'msg': 'Gagal saat menambahkan partner.'}})    
        
        if (self.context == 'delete-partner'):
            try:
                partner_id = request.POST.get('partner-id')            

                new_partner = Partner.objects.get(id=partner_id)
                sts = firebase_delete(new_partner.img_link)
                
                if (sts):
                    new_partner.delete()
                    return JsonResponse({'status': True, 'data':{'msg': 'Partner berhasil dihapus.'}})     
                else:
                    return JsonResponse({'status': False, 'data':{'msg': 'Gagal menghapus dari firebase..'}})                                             
    
            except Exception as firebase_error:
                logger.error(f'{firebase_error} - Gagal menghapus data firebase cek services/firebase.py')
                return JsonResponse({'status': 'false', 'data':{'msg': 'Gagal saat menghapus partner.'}})    

        if (self.context == 'create-news-dashboard'):
            try:
                title = request.POST.get('title')
                content = request.POST.get('content')
                image = request.FILES.get('image')
                sts = False
                if (image.name).endswith('.png'):
                    sts, msg = firebase_upload('news', image, title, ct='png')                    
                if (image.name).endswith('.jpg'):
                    sts, msg = firebase_upload('news', image, title, ct='jpg')                    
                if (image.name).endswith('.jpeg'):
                    sts, msg = firebase_upload('news', image, title, ct='jpeg')                    
                if (image.name).endswith('.webp'):
                    sts, msg = firebase_upload('news', image, title, ct='webp')   

                if (sts):
                    new_article = Article()
                    new_article.title = title
                    new_article.content = content
                    new_article.img_link = msg
                    new_article.save()
                    return JsonResponse({'status': 'true', 'data':{'msg': 'Artikel telah diterbitkan.'}})     
                else:
                    return JsonResponse({'status': 'false', 'data':{'msg': 'Gagal saat menambahkan artikel.'}})         
                             
            except Exception as firebase_error:
                logger.error(f'{firebase_error} - Gagal upload ke firebase cek services/firebase.py')
                return JsonResponse({'status': 'false', 'data':{'msg': 'Gagal saat menambahkan artikel.'}})     


        if (self.context == 'edit-news-dashboard'):
            try:
                title = request.POST.get('title')
                content = request.POST.get('content')
                new_article = Article.objects.get(id=self.kwargs.get('article_id'))
                new_article.title = title
                new_article.content = content

                try:
                    image = request.FILES.get('image')
                
                    if (image):
                        sts = False
                        ext_to_ct = {
                            '.png': 'png',
                            '.jpg': 'jpg',
                            '.jpeg': 'jpeg',
                            '.webp': 'webp'
                        }
                        for ext, ct in ext_to_ct.items():
                            if image.name.endswith(ext):
                                sts, msg = firebase_upload('news', image, title, ct=ct)
                                break                    

                    if (sts):
                        new_article.img_link = msg
                        new_article.save()
                        return JsonResponse({'status': True, 'data':{'msg': 'Artikel berhasil di edit.'}})     
                    else:
                        logger.error(f'{title} - Gagal simpan artikel, ada masalah pada gambar upload firebase.')
                        return JsonResponse({'status': False, 'data':{'msg': 'Gagal saat mengedit artikel.'}})         
                
                except:
                    new_article.save()
                    return JsonResponse({'status': True, 'data':{'msg': 'Artikel berhasil di edit.'}})     
                
                             
            except Exception as err:
                logger.error(f'{err} - Gagal simpan artikel.')                
                return JsonResponse({'status': True, 'data':{'msg': 'Gagal saat mengedit artikel.'}})  
