from prompt_templates import ALPHA_PROMPT, BETA_PROMPT, GAMA_DONGU_PROMPT, GAMA_RAPOR_PROMPT
from llm_client import generate_response
import json
import asyncio

async def run_debate(user_idea: str, model_name: str, max_loops: int = 5):
    """
    Asenkron generator. Her ajan cevabında UI'a gitmesi için mesaj yield eder.
    Yield formati: {"agent": "Alpha", "message": "..."}
    """
    
    yield {"agent": "System", "message": "Gama başlangıç çerçevesini oluşturuyor..."}
    # 1. Gama başlangıç promptunu oluşturur
    gama_init_system = "Sen Gama'sın. Kullanıcının kısa fikrini alıp, tartışmanın başlayabilmesi için teknik ve detaylı bir başlangıç konseptine çevir. Kısa ve öz bir metin olsun."
    initial_prompt = await generate_response(gama_init_system, user_idea, model_name)
    await asyncio.sleep(3)
    
    yield {"agent": "Gama", "message": initial_prompt}
    
    alpha_input = initial_prompt
    history = f"Gama'nın Başlangıç Konsepti: {initial_prompt}\n"
    
    # 2. Döngü
    for i in range(max_loops):
        yield {"agent": "System", "message": f"Döngü {i+1} başlıyor..."}
        
        # ALPHA
        yield {"agent": "System_Status", "message": "Alpha düşünüyor..."}
        alpha_req = f"TÜM YAZIŞMA GEÇMİŞİ:\n{history}\n\n---\nSIRA SENDE ALPHA!\nGörevin: Yukarıdaki geçmişi göz önünde bulundurarak aşağıdaki son girdideki (Beta'dan gelen) sorunları çözmek.\nŞU ANKİ GİRDİ (SADECE BUNA CEVAP VER VE KENDİNİ TEKRAR ETME):\n{alpha_input}"
        alpha_res = await generate_response(ALPHA_PROMPT, alpha_req, model_name)
        await asyncio.sleep(3)
        yield {"agent": "Alpha", "message": alpha_res}
        
        history += f"\nAlpha: {alpha_res}\n"
        
        # BETA
        yield {"agent": "System_Status", "message": "Beta eleştiriyor..."}
        beta_req = f"TÜM YAZIŞMA GEÇMİŞİ:\n{history}\n\n---\nSIRA SENDE BETA!\nGörevin: Alpha'nın EN SON sunduğu çözümü eleştirmektir. Geçmişte söylediğin eleştirileri tekrar etme.\nŞU ANKİ ALPHA ÇÖZÜMÜ:\n{alpha_res}"
        beta_res = await generate_response(BETA_PROMPT, beta_req, model_name)
        await asyncio.sleep(3)
        yield {"agent": "Beta", "message": beta_res}
        
        history += f"\nBeta: {beta_res}\n"
        
        # GAMA KONTROL
        yield {"agent": "System_Status", "message": "Gama durumu değerlendiriyor..."}
        gama_check_req = f"Şu ana kadarki tartışma:\n{history}\n\nLütfen uzlaşı durumunu kontrol et."
        gama_check_res = await generate_response(GAMA_DONGU_PROMPT, gama_check_req, model_name)
        await asyncio.sleep(3)
        
        if "[DURUM: ROTAYI DÜZELT]" in gama_check_res.upper() or "ROTAYI DÜZELT" in gama_check_res.upper():
            yield {"agent": "Gama", "message": f"🚩 {gama_check_res}"}
            alpha_input = f"Beta'nın Eleştirisi:\n{beta_res}\n\nGama'nın Yönlendirmesi:\n{gama_check_res}"
            history += f"\nGama (Yönlendirme): {gama_check_res}\n"
            
        elif "[DURUM: TAMAMLANDI]" in gama_check_res.upper() or "TAMAMLANDI" in gama_check_res.upper():
            yield {"agent": "System", "message": "Gama uzlaşı sağlandığını tespit etti. Döngü kırılıyor."}
            break
            
        else:
            # Devam
            alpha_input = f"Beta'nın Eleştirisi:\n{beta_res}"

    # Nihai Çıktı
    yield {"agent": "System", "message": "Gama Nihai Raporu hazırlıyor..."}
    gama_report_req = f"İşte tüm tartışmanın transkripti:\n{history}\n\nLütfen Nihai Teknik Spesifikasyon Raporunu oluştur."
    final_report = await generate_response(GAMA_RAPOR_PROMPT, gama_report_req, model_name)
    yield {"agent": "Gama (Nihai Rapor)", "message": final_report}
    yield {"agent": "System", "message": "Süreç Tamamlandı!"}
