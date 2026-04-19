import os
import google.generativeai as genai
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# API Key Check
gemini_api_key = os.getenv("GEMINI_API_KEY")
glm_api_key = os.getenv("GLM_API_KEY")

if gemini_api_key and gemini_api_key != "your_api_key_here":
    genai.configure(api_key=gemini_api_key)
else:
    print("WARNING: GEMINI_API_KEY is not set properly in .env file.")

async def generate_response(system_prompt: str, user_prompt: str, model_name: str = "gemini-2.5-pro") -> str:
    """
    Calls the Gemini or GLM API with a system prompt and a user prompt.
    """
    try:
        if "glm" in model_name.lower():
            if not glm_api_key or glm_api_key == "your_glm_api_key_here":
                return "[HATA] GLM_API_KEY .env dosyasında bulunamadı!"
            client = AsyncOpenAI(api_key=glm_api_key, base_url="https://open.bigmodel.cn/api/paas/v4/")
            response = await client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        else:
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                )
            )
            response = await model.generate_content_async(user_prompt)
            return response.text
    except Exception as e:
        return f"[HATA] API Çağrısında hata oluştu: {str(e)}"
