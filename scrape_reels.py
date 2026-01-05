import instaloader
import pandas as pd
import time
import os

def scrape_reels(username, max_posts=10, scrape_comments=False):
    # Instaloader örneği oluştur
    L = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False, 
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False
    )

    try:
        # Profili yükle
        profile = instaloader.Profile.from_username(L.context, username)
        print(f"Profil bulundu: {profile.username}")
        
        reels_data = []
        count = 0

        # Gönderileri gez
        for post in profile.get_posts():
            if count >= max_posts:
                break
            
            # Sadece videoları/Reels'leri al
            if post.is_video:
                print(f"İşleniyor: {post.shortcode} - {post.date_local}")
                
                data = {
                    'shortcode': post.shortcode,
                    'date': post.date_local,
                    'views': post.video_view_count,
                    'likes': post.likes,
                    'comments_count': post.comments,
                    'caption': post.caption,
                    'url': f"https://www.instagram.com/reel/{post.shortcode}/",
                    'comments': []
                }
                
                # Yorumları çek (Opsiyonel ve yavaş olabilir)
                if scrape_comments:
                    print(f"  > Yorumlar çekiliyor...")
                    comments_list = []
                    try:
                        for comment in post.get_comments():
                            comments_list.append({
                                'owner': comment.owner.username,
                                'text': comment.text,
                                'created_at': comment.created_at_utc
                            })
                            # Çok fazla yorum varsa limit koyabiliriz, şimdilik hepsini alıyoruz ama dikkatli olun.
                            # Rate limit yememek için kısa bir bekleme
                            # time.sleep(0.5) 
                    except Exception as e:
                        print(f"  ! Yorum hatası: {e}")
                    
                    data['comments'] = comments_list

                reels_data.append(data)
                count += 1
                
                # Her gönderi arası bekleme (Anti-ban)
                time.sleep(2) 
                
        # Veriyi kaydet
        if reels_data:
            df = pd.DataFrame(reels_data)
            
            # Yorumları string olarak sakla (CSV için) veya ayrı bir JSON yap
            # CSV'de yorum listesi karmaşık görünebilir, o yüzden JSON daha iyi olabilir ama kullanıcı CSV isteyebilir.
            # Şimdilik ana veriyi CSV'ye, detaylı veriyi JSON'a basalım.
            
            output_csv = f"{username}_reels.csv"
            output_json = f"{username}_reels.json"
            
            # Basit CSV (Yorum içeriği hariç, sadece sayı)
            df_simple = df.drop(columns=['comments'])
            df_simple.to_csv(output_csv, index=False)
            
            # Detaylı JSON
            df.to_json(output_json, orient='records', force_ascii=False, indent=4)
            
            print(f"İşlem tamamlandı! {count} reels çekildi.")
            print(f"Dosyalar: {output_csv}, {output_json}")
        else:
            print("Hiç reels bulunamadı veya erişim sorunu var.")

    except instaloader.ProfileNotExistsException:
        print("Profil bulunamadı.")
    except instaloader.ConnectionException as e:
        print(f"Bağlantı hatası (IP ban veya login gerekli olabilir): {e}")
    except Exception as e:
        print(f"Beklenmeyen hata: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Instagram Reels Scraper')
    parser.add_argument('username', nargs='?', help='Target username')
    parser.add_argument('--count', type=int, default=10, help='Number of reels to scrape')
    parser.add_argument('--comments', action='store_true', help='Scrape comments')
    
    args = parser.parse_args()
    
    if args.username:
        target_username = args.username
        limit = args.count
        scrape_comments_choice = args.comments
    else:
        target_username = input("Hedef kullanıcı adı: ")
        scrape_comments_choice = input("Yorumlar çekilsin mi? (e/h): ").lower() == 'e'
        limit = int(input("Kaç reels çekilsin? (Varsayılan 10): ") or 10)
    
    scrape_reels(target_username, max_posts=limit, scrape_comments=scrape_comments_choice)
