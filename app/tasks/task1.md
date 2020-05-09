Task python/django istifadə edilərək yazılmalı olan mini bir app-dır.

Fayl paylaşım (file sharing) app-ı yazmaq lazımdır. 
Yalnız qeydiyyatlı istifadəçilərin file yükləyə bildiyi bir sistemdir. 
Yüklənən hər file-ın adı və açıqlaması var.
Yükənən fayla həmçinin “expiration date” təyin etmək olur. Həmin tarixdə fayl avtomatik olaraq silinməlidir. 
File-ların silinməsini asinxron etmək üçün celery task istifadə etməyiniz məsləhətdir. 
Celery broker olaraq rabbitmq və ya redis-i istifadə etməkdə sərbəstsiniz.

By default olaraq file-lar ancaq onu yükləyən istifadəçiyə görünür, digər istifadəçilər tərəfindən görünmür. Lakin istifadəçi digər istifadəçi ilə file-ı, onun username və ya email ünvanını yazaraq paylaşa bilir. Bu zaman 2 formatda paylaşma mümkündür: yalnız file görmək, və ya həm görmək həm də şərh yazmaq imkanı. File-ın details səhifəsində şərhlər realtime olaraq socket ilə yazılır, yəni yazılan şərhlər anlıq olaraq qarşı tərəfdə görünməlidir (django channels istifadə etməyi məsləhət görərdim).

Database olaraq postgresql seçin. Application-u docker (docker-compose) ilə serve edin.

    Əgər mümkün olsa user sistemə login olarkən, browser, OS, İP kimi məlumatlarını log olaraq əsas DB-də yox ayrıca bir DB-də store etməyə çalışın. (django multi-database feature)
    Mümkün olsa file-ın müəllifi file-a yazılan şərhləri silə bilməlidir.
    Mümkün olsa şərhin müəllifi öz şərhini həm silə bilməli, həm də edit edə bilməlidir.


Tapşırıq ilə tanış olun, nə sualınız yaranarsa soruşun. Əgər aydındırsa xahiş edirəm deadline özünüz təyin edin. Yazışmaya bizim CTO - Sadigi də əlavə etdim.  Cavablayanda zəhmət olmasa reply to all edərsiniz.