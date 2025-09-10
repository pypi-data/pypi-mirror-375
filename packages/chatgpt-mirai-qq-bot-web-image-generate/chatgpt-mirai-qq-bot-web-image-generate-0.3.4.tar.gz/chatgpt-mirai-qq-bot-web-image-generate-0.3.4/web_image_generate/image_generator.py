import aiohttp
import random
import json
import time
import asyncio
from typing import Dict, Any, Optional, Tuple, List, Union
from kirara_ai.logger import get_logger
from gradio_client import Client, handle_file
import tempfile
import os
import io
from curl_cffi import AsyncSession, Response
import mimetypes
import random
from kirara_ai.ioc.container import DependencyContainer
from kirara_ai.media.manager import MediaManager
from kirara_ai.im.message import  ImageMessage,VoiceMessage,VideoMessage
logger = get_logger("ImageGenerator")

class WebImageGenerator:
    MODELSCOPE_MODELS = {
        "flux": {
            "path": "ByteDance/Hyper-FLUX-8Steps-LoRA",
            "fn_index": 0,
            "trigger_id": 18,
            "data_builder": lambda height, width, prompt: [height, width, 8, 3.5, prompt, random.randint(0, 9999999999999999)],
            "data_types": ["slider", "slider", "slider", "slider", "textbox", "number"],
            "url_processor": lambda url: url.replace("leofen/flux_dev_gradio", "muse/flux_dev"),
            "output_parser": lambda data: data["output"]["data"][0]["url"]
        },
        "ketu": {
            "path": "AI-ModelScope/Kolors",
            "fn_index": 0,
            "trigger_id": 23,
            "data_builder": lambda height, width, prompt: [prompt, "", height, width, 20, 5, 1, True, random.randint(0, 9999999999999999)],
            "data_types": ["textbox", "textbox", "slider", "slider", "slider", "slider", "slider", "checkbox", "number"],
            "url_processor": lambda url: url,
            "output_parser": lambda data: data.get("output")['data'][0][0]["image"]["url"]
        }
    }

    def __init__(self, cookie: str = "",container: DependencyContainer = None):
        self.cookie = cookie
        self.container = container
        self.api_base = "https://s5k.cn"  # ModelScope API base URL

    async def _get_modelscope_token(self, session: aiohttp.ClientSession, headers: Dict[str, str]) -> str:
        """获取ModelScope token"""
        async with session.get(
                f"https://modelscope.cn/api/v1/studios/token",
                headers=headers
        ) as response:
            response.raise_for_status()
            token_data = await response.json()
            return token_data["Data"]["Token"]

    async def generate_modelscope(self, model: str, prompt: str, width: int, height: int) -> str:
        aspect_ratio = width / height
        # 确保宽度和高度的最小值至少是1024
        if min(height, width) < 1024:
            if height < width:
                height = 1024
                width = (int(height * aspect_ratio/64))*64
            else:
                width = 1024
                height = (int(width / aspect_ratio/64))*64

        """使用ModelScope模型生成图片"""
        if model not in self.MODELSCOPE_MODELS:
            raise ValueError(f"Unsupported ModelScope model: {model}")

        model_config = self.MODELSCOPE_MODELS[model]
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Cookie": self.cookie
        }

        async with aiohttp.ClientSession() as session:
            # 获取 token
            studio_token = await self._get_modelscope_token(session, headers)
            headers["X-Studio-Token"] = studio_token
            session_hash = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=7))

            # 调用模型生成图片
            model_url = f"https://bytedance-hyper-flux-8steps-lora.ms.show/queue/join"
            params = {
                "backend_url": f"/api/v1/studio/{model_config['path']}/gradio/",
                "sdk_version": "4.31.3",
                "studio_token": studio_token
            }
            logger.debug("图片生成prompt:"+prompt)
            json_data = {
                "data": model_config["data_builder"](height, width, prompt),
                "fn_index": model_config["fn_index"],
                "trigger_id": model_config["trigger_id"],
                "dataType": model_config["data_types"],
                "session_hash": session_hash
            }

            async with session.post(
                    model_url,
                    headers=headers,
                    params=params,
                    json=json_data
            ) as response:
                response.raise_for_status()
                data = await response.json()
                logger.debug(data)
                event_id = data["event_id"]

            # 获取结果
            result_url = f"https://bytedance-hyper-flux-8steps-lora.ms.show/queue/data"
            params = {
                "session_hash": session_hash,
                "studio_token": studio_token
            }

            async with session.get(result_url, headers=headers, params=params) as response:
                response.raise_for_status()
                async for line in response.content:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        logger.debug(line)
                        event_data = json.loads(line[6:])
                        if event_data["event_id"] == event_id and event_data["msg"] == "process_completed":
                            try:
                                url = model_config["output_parser"](event_data)
                                if url:
                                    url = model_config["url_processor"](url).replace(
                                        "https://s5k.cn/api/v1/studio/ByteDance/Hyper-FLUX-8Steps-LoRA/gradio/file=",
                                        "https://bytedance-hyper-flux-8steps-lora.ms.show/file=")
                                    async with session.get(
                                            url,
                                            headers=headers,
                                    ) as response:
                                        image_bytes = await response.read()
                                        imageMessage = ImageMessage(data=image_bytes)
                                        return imageMessage.media_id
                            except Exception as e:
                                logger.error(f"Failed to parse output for model {model}: {e}")
            return ""

    async def generate_noobxl(self, prompt: str, width: int, height: int) -> str:

        aspect_ratio = width / height
        # 确保宽度和高度的最小值至少是1024
        if min(height, width) < 1024:
            if height < width:
                height = 1024
                width = (int(height * aspect_ratio/64))*64
            else:
                width = 1024
                height = (int(  width / aspect_ratio/64))*64



        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Cookie": self.cookie
        }

        async with aiohttp.ClientSession() as session:
            # 获取 token
            studio_token = await self._get_modelscope_token(session, headers)
            headers["X-Studio-Token"] = studio_token
            session_hash = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=7))

            # 调用模型生成图片
            model_url = f"https://chuansir-sdxl-anime-epsilon.ms.show/queue/join"
            params = {
                "sdk_version": "4.31.3",
                "studio_token": studio_token
            }
            logger.debug("图片生成prompt:"+prompt)
            json_data = {"data":["masterpiece, best quality, ultra-detailed, high resolution, 8K, sharp focus, professional photography, intricate details,"+prompt,"low quality, worst quality, bad anatomy, bad proportions, blurry, distorted, poorly drawn, extra limbs, missing limbs, deformed hands, deformed fingers, deformed feet, deformed toes, fused fingers, missing fingers, extra fingers, malformed hands, malformed feet, long neck, unnatural body, disfigured, mutated, ugly,text, watermark, signature, username, error, cropped, jpeg artifacts, out of focus, duplicate, morbid, mutilated,cloned face, asymmetrical eyes, unnatural pose, twisted body, extra arms, extra legs, poorly detailed face, unnatural skin tone","Anime",height,width,5,20,"epsilon1.1",0,False],"event_data":None,"fn_index":0,"trigger_id":18,"dataType":["textbox","textbox","dropdown","slider","slider","slider","slider","dropdown","slider","checkbox"],"session_hash":session_hash}

            async with session.post(
                    model_url,
                    headers=headers,
                    params=params,
                    json=json_data
            ) as response:
                response.raise_for_status()
                data = await response.json()
                logger.debug(data)
                event_id = data["event_id"]

            # 获取结果
            result_url = f"https://chuansir-sdxl-anime-epsilon.ms.show/queue/data"
            params = {
                "session_hash": session_hash,
                "studio_token": studio_token
            }

            async with session.get(result_url, headers=headers, params=params) as response:
                response.raise_for_status()
                async for line in response.content:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        logger.debug(line)
                        event_data = json.loads(line[6:])
                        if event_data["event_id"] == event_id and event_data["msg"] == "process_completed":
                            try:
                                url = event_data["output"]["data"][0]["url"]
                                if url:
                                    url = event_data["output"]["data"][0]["url"]
                                    async with session.get(
                                            url,
                                            headers=headers,
                                    ) as response:
                                        image_bytes = await response.read()
                                        imageMessage = ImageMessage(data=image_bytes)
                                        return imageMessage.media_id
                            except Exception as e:
                                logger.error(f"Failed to parse output for model : {e}")
            return ""

    async def generate_qwen_image(self, prompt: str, width: int, height: int) -> str:

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Cookie": self.cookie
        }

        async with aiohttp.ClientSession() as session:
            # 获取 token
            model_url = f"https://chuansir-qwen-image.ms.show/image?prompt={prompt}&width={width}&height={height}"
            async with session.post(
                    model_url,
                    json={"prompt":prompt,"width":width,"height":height},
                    headers=headers,
            ) as response:
                response.raise_for_status()
                image_bytes = await response.read()
                imageMessage = ImageMessage(data=image_bytes)

            return imageMessage.media_id


    async def generate_shakker(self, model: str, prompt: str, width: int, height: int) -> str:
        """使用Shakker平台生成图片"""
        # Model mapping for Shakker platform
        MODEL_MAPPING = {
            "anime": 1489127,
            "photo": 1489700
        }

        if model not in MODEL_MAPPING:
            raise ValueError(f"Unsupported Shakker model: {model}")

        # Adjust dimensions if they exceed 1024
        if width >= height and width > 1024:
            height = int(1024 * height / width)
            width = 1024
        elif height > width and height > 1024:
            width = int(1024 * width / height)
            height = 1024

        # Prepare request payload
        json_data = {
            "source": 3,
            "adetailerEnable": 0,
            "mode": 1,
            "projectData": {
                "style": "",
                "baseType": 3,
                "presetBaseModelId": "photography",
                "baseModel": None,
                "loraModels": [],
                "width": int(width * 1.5),
                "height": int(height * 1.5),
                "isFixedRatio": True,
                "hires": True,
                "count": 1,
                "prompt": prompt,
                "negativePrompt": "",
                "presetNegativePrompts": ["common", "bad_hand"],
                "samplerMethod": "29",
                "samplingSteps": 20,
                "seedType": "0",
                "seedNumber": -1,
                "vae": "-1",
                "cfgScale": 7,
                "clipSkip": 2,
                "controlnets": [],
                "checkpoint": None,
                "hiresOptions": {
                    "enabled": True,
                    "scale": 1.5,
                    "upscaler": "11",
                    "strength": 0.5,
                    "steps": 20,
                    "width": width,
                    "height": height
                },
                "modelCfgScale": 7,
                "changed": True,
                "modelGroupCoverUrl": None,
                "addOns": [],
                "mode": 1,
                "isSimpleMode": False,
                "generateType": "normal",
                "renderWidth": int(width * 1.5),
                "renderHeight": int(height * 1.5),
                "samplerMethodName": "Restart"
            },
            "vae": "",
            "checkpointId": MODEL_MAPPING[model],
            "additionalNetwork": [],
            "generateType": 1,
            "text2img": {
                "width": width,
                "height": height,
                "prompt": prompt,
                "negativePrompt": ",lowres, normal quality, worst quality, cropped, blurry, drawing, painting, glowing",
                "samplingMethod": "29",
                "samplingStep": 20,
                "batchSize": 1,
                "batchCount": 1,
                "cfgScale": 7,
                "clipSkip": 2,
                "seed": -1,
                "tiling": 0,
                "seedExtra": 0,
                "restoreFaces": 0,
                "hiResFix": 1,
                "extraNetwork": [],
                "promptRecommend": True,
                "hiResFixInfo": {
                    "upscaler": 11,
                    "upscaleBy": 1.5,
                    "resizeWidth": int(width * 1.5),
                    "resizeHeight": int(height * 1.5)
                },
                "hiresSteps": 20,
                "denoisingStrength": 0.5
            },
            "cid": f"{int(time.time() * 1000)}woivhqlb"
        }

        headers = {"Token": self.cookie}  # Using cookie as token

        async with aiohttp.ClientSession() as session:
            # Submit generation request
            async with session.post(
                    "https://www.shakker.ai/gateway/sd-api/gen/tool/shake",
                    json=json_data,
                    headers=headers
            ) as response:
                response.raise_for_status()
                data = await response.json()
                task_id = data["data"]

            # Wait for initial processing
            await asyncio.sleep(10)

            # Poll for results
            for _ in range(60):
                async with session.post(
                        f"https://www.shakker.ai/gateway/sd-api/generate/progress/msg/v1/{task_id}",
                        json={"flag": 3},
                        headers=headers
                ) as response:
                    response.raise_for_status()
                    result = await response.json()

                    if result["data"]["percentCompleted"] == 100:
                        url = result["data"]["images"][0]["previewPath"]
                        async with session.get(
                                url,
                                headers=headers,
                        ) as response:
                            image_bytes = await response.read()
                            imageMessage = ImageMessage(data=image_bytes)
                            return imageMessage.media_id

                await asyncio.sleep(1)

            return ""

    async def generate_image(self, platform: str, model: str, prompt: str, width: int, height: int, image1_url: Optional[str] = None, image2_url: Optional[str] = None, image1_reference_type: str = "ip", image2_reference_type: str = "ip") -> str:
        """统一的图片生成入口"""
        if "-ketu" in prompt and platform == "modelscope":
            prompt = prompt.replace("-ketu","")
            model = "ketu"
        elif "-flux" in prompt  and platform == "modelscope":
            prompt = prompt.replace("-flux","")
            model = "flux"
        elif "-anime" in prompt and platform == "shakker":
            prompt = prompt.replace("-anime","")
            model = "anime"
        elif "-photo" in prompt and platform == "shakker":
            prompt = prompt.replace("-photo","")
            model = "photo"
        elif "-dreamo" in prompt and platform == "dreamo":
            prompt = prompt.replace("-dreamo","")

        if platform == "modelscope":
            if not self.cookie:
                return "请前往https://modelscope.cn/登录后获取token(按F12-应用-cookie中的m_session_id)";
            if not self.cookie.startswith("m_session_id="):
                self.cookie = "m_session_id=" + self.cookie
            return await self.generate_modelscope(model, prompt, width, height)
        elif platform == "shakker":
            if not self.cookie:
                return "请前往https://www.shakker.ai/登录后获取token(按F12-应用-cookie中的usertoken)";
            return await self.generate_shakker(model, prompt, width, height)
        elif platform == "dreamo":
            if not self.cookie:
                return "请前往https://modelscope.cn/登录后获取token(按F12-应用-cookie中的m_session_id)";
            return await self.generate_dreamo(prompt, image1_url, image2_url, width, height, image1_reference_type, image2_reference_type)
        elif platform == "flux_kontext":
            if not self.cookie:
                return "请前往https://modelscope.cn/登录后获取token(按F12-应用-cookie中的m_session_id)";
            return await self.generate_flux_kontext(prompt, image1_url,image2_url, width, height)
        elif platform == "NoobXl":
            if not self.cookie:
                return "请前往https://modelscope.cn/登录后获取token(按F12-应用-cookie中的m_session_id)";
            return await self.generate_noobxl(prompt, width, height)
        elif platform == "qwen_image":
            return await self.generate_qwen_image(prompt, width, height)

        raise ValueError(f"Unsupported platform ({platform}) or model ({model})")




    async def _upload_image(self, image_path: str, headers: dict,space_name :str = "chuansir-framepack") -> str:
        """Upload image and return the file path"""
        # Generate upload ID
        upload_id = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=10))

        # Create form data without specifying boundary
        form = aiohttp.FormData()
        form.add_field('files',
                       open(image_path, 'rb'),
                       filename=os.path.basename(image_path),
                       content_type=mimetypes.guess_type(image_path)[0] or 'application/octet-stream')

        # Copy headers for upload
        upload_headers = headers.copy()
        # Let aiohttp handle the content-type header for the form data

        # Upload file
        upload_url = f"https://{space_name}.ms.show/gradio_api/upload?upload_id={upload_id}"
        async with aiohttp.ClientSession() as session:
            async with session.post(upload_url, data=form, headers=upload_headers) as response:
                response.raise_for_status()
                file_paths = await response.json()
            logger.debug(file_paths)
            # Wait for upload to complete
            progress_url = f"https://{space_name}.ms.show/gradio_api/upload_progress?upload_id={upload_id}"
            while True:
                async with session.get(progress_url, headers=headers) as response:
                    # Handle event-stream format
                    progress_text = await response.text()
                    print(progress_text)
                    if "done" in progress_text:
                        break
                    await asyncio.sleep(0.5)
            while True:
                image_url = f"https://{space_name}.ms.show/gradio_api/file={file_paths[0]}"
                try:
                    async with session.get(image_url, headers=headers,timeout=1) as response:
                        response.raise_for_status()
                        break
                except asyncio.TimeoutError:
                    await asyncio.sleep(0.5)
        # await asyncio.sleep(10)
        return file_paths[0]



    async def generate_music(self, duration: int, lyrics: str, style: str) -> str:
        """文生音乐生成，流程与generate_imageToVideo一致，返回音乐url"""
        if not self.cookie:
            return "请前往https://modelscope.cn/登录后获取token(按F12-应用-cookie中的m_session_id)"
        if not self.cookie.startswith("m_session_id="):
            self.cookie = "m_session_id=" + self.cookie

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Cookie": self.cookie
        }
        async with aiohttp.ClientSession() as session:
            studio_token = await self._get_modelscope_token(session, headers)
            # 构造headers
            headers = {
                "Cookie": f"studio_token={studio_token}",
                "x-studio-token": studio_token
            }
            join_url = "https://ace-step-ace-step.ms.show/gradio_api/queue/join"
            data_url = "https://ace-step-ace-step.ms.show/gradio_api/queue/data"
            session_hash = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=10))
            # 构造data参数
            data = [duration, style, lyrics, 27, 15, "euler", "apg", 10, "", 0.5, 0, 3, True, True, True, "", 0, 0]
            payload = {
                "data": data,
                "event_data": None,
                "fn_index": 9,
                "trigger_id": 30,
                "dataType": [
                    "slider", "textbox", "textbox", "slider", "slider", "radio", "radio", "slider", "textbox", "slider", "slider", "slider", "checkbox", "checkbox", "checkbox", "textbox", "slider", "slider"
                ],
                "session_hash": session_hash
            }
            logger.debug(payload)
            # join queue
            async with session.post(join_url, json=payload, headers=headers) as resp:
                resp.raise_for_status()
                join_data = await resp.json()
                event_id = join_data.get("event_id")
            # poll data
            params = {"session_hash": payload["session_hash"], "studio_token": studio_token}
            async with session.get(data_url, params=params, headers=headers) as resp:
                async for line in resp.content:
                    line = line.decode("utf-8").strip()
                    if line.startswith("data:"):
                        try:
                            data_str = line[5:].strip()
                            if data_str:
                                data = json.loads(data_str)
                                if data.get("msg") == "process_completed" and "output" in data and "data" in data["output"] and data.get("event_id") == event_id:
                                    # 提取url
                                    url = data["output"]["data"][0]["url"]
                                    async with session.get(
                                            url,
                                            headers=headers,
                                    ) as response:
                                        image_bytes = await response.read()
                                        imageMessage = VoiceMessage(data=image_bytes)
                                        return imageMessage.media_id
                        except Exception:
                            continue
        return None

    async def generate_voice(self,  text: str, speaker_id: str) -> str:
        """文生音乐生成，流程与generate_imageToVideo一致，返回音乐url"""

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        }
        speaker = {"周杰伦":"jay.wav","可莉":"vo_card_klee_endOfGame_fail_01.wav","可莉2":"vo_card_klee_endOfGame_fail_02.mp3","提莫":"提莫.mp3","阿珂":"暗夜猫娘阿珂 .mp3","爱莉希雅":"爱莉希雅.mp3"}
        voice_model = speaker[speaker_id] if speaker_id in speaker else "vo_card_klee_endOfGame_fail_02.mp3"
        url = f"https://chuansir-index-tts-vllm.ms.show/tts?audio_paths=assets/{speaker[speaker_id]}&text={text}"
        # 统计GET请求时间
        get_start_time = time.time()
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    url,
                    headers=headers,
            ) as response:
                get_end_time = time.time()
                get_duration = get_end_time - get_start_time
                logger.debug(f"GET请求耗时: {get_duration} 秒")

                image_bytes = await response.read()
                read_end_time = time.time()
                read_duration = read_end_time - get_end_time
                logger.debug(f"读取image_bytes耗时: {read_duration} 秒")

                imageMessage = VoiceMessage(data=image_bytes)
                voice_message_duration = time.time() - read_end_time
                logger.debug(f"创建VoiceMessage耗时: {voice_message_duration} 秒")

                return imageMessage.media_id
        return None

    async def generate_dreamo(self, prompt: str, image1_url: Optional[str] = None, image2_url: Optional[str] = None, width: int = 768, height: int = 1024, image1_reference_type: str = "ip", image2_reference_type: str = "ip") -> str:
        """使用Bytedance Dreamo模型生成图片，支持文生图和图生图"""
        aspect_ratio = width / height
        # 确保宽度和高度的最小值至少是1024
        if min(height, width) < 768:
            if height < width:
                height = 768
                width = (int(height * aspect_ratio/64))*64
            else:
                width = 768
                height = (int(width / aspect_ratio/64))*64
            if max(height, width) > 1024:
                return "请保持生成的图片宽高在768到1024之间"
        if max(height, width) > 1024:
            if height < width:
                width = 1024
                height = (int(width / aspect_ratio/64))*64
            else:
                height = 1024
                width = (int(height * aspect_ratio/64))*64
            if min(height, width) < 768:
                return "请保持生成的图片宽高在768到1024之间"

        # 验证cookie
        if not self.cookie:
            return "请前往https://modelscope.cn/登录后获取token(按F12-应用-cookie中的m_session_id)"



        # 生成会话哈希
        session_hash = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10))

        if not self.cookie:
            return "请前往https://modelscope.cn/登录后获取token(按F12-应用-cookie中的m_session_id)"
        if not self.cookie.startswith("m_session_id="):
            self.cookie = "m_session_id=" + self.cookie

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Cookie": self.cookie
        }

        # 需要上传的图片列表
        image_data_list = []
        media_manager = self.container.resolve(MediaManager)
        # 处理图片上传
        async with aiohttp.ClientSession() as session:
            studio_token = await self._get_modelscope_token(session, headers)
            headers["X-Studio-Token"] = studio_token
            # 上传第一张图片（如果有）
            if image1_url:
                try:
                    # 下载图片
                    image1_bytes = await media_manager.get_data(image1_url)

                    # 保存到临时文件
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                        temp_file.write(image1_bytes)
                        temp_path1 = temp_file.name

                    # 上传图片
                    file_path1 = await self._upload_image(temp_path1, headers, "bytedance-dreamo")

                    # 添加到图片数据列表
                    image_data_list.append({
                        "is_stream": False,
                        "meta": {"_type": "gradio.FileData"},
                        "mime_type": None,
                        "orig_name": f"image1.png",
                        "path": file_path1,
                        "size": None,
                        "url": f"https://bytedance-dreamo.ms.show/gradio_api/file={file_path1}"
                    })

                    # 删除临时文件
                    os.remove(temp_path1)
                except Exception as e:
                    logger.error(f"上传第一张图片失败: {str(e)}")
                    return f"上传第一张图片失败: {str(e)}"
            else:
                # 如果没有第一张图片，添加空数据
                image_data_list.append(None)

            # 上传第二张图片（如果有）
            if image2_url:
                try:
                    image2_bytes = await media_manager.get_data(image2_url)

                    # 保存到临时文件
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                        temp_file.write(image2_bytes)
                        temp_path2 = temp_file.name

                    # 上传图片
                    file_path2 = await self._upload_image(temp_path2, headers, "bytedance-dreamo")

                    # 添加到图片数据列表
                    image_data_list.append({
                        "is_stream": False,
                        "meta": {"_type": "gradio.FileData"},
                        "mime_type": None,
                        "orig_name": f"image2.png",
                        "path": file_path2,
                        "size": None,
                        "url": f"https://bytedance-dreamo.ms.show/gradio_api/file={file_path2}"
                    })

                    # 删除临时文件
                    os.remove(temp_path2)
                except Exception as e:
                    logger.error(f"上传第二张图片失败: {str(e)}")
                    return f"上传第二张图片失败: {str(e)}"
            else:
                # 如果没有第二张图片，添加空数据
                image_data_list.append(None)

            # 如果没有提供任何图片，则将两个图片数据项都设为None
            if not image1_url and not image2_url:
                image_data_list = [None, None]


            # 构建请求数据
            data_list: List[Any] = []

            # 添加图片数据（如果有）
            data_list.extend(image_data_list)

            # 添加其他必要参数
            data_list.extend([
                image1_reference_type.lower(),  # 第一张图片的参考类型
                image2_reference_type.lower(),  # 第二张图片的参考类型
                prompt,  # 提示词
                str(random.randint(0, 9999999999999999)),  # 随机数
                width,  # 宽度
                height,  # 高度
                512,  # 其他参数
                12,   # 其他参数
                3.5,  # 其他参数
                1,    # 其他参数
                0,    # 其他参数
                0,    # 其他参数
                "",   # 其他参数
                3.5,  # 其他参数
                0     # 其他参数
            ])

            # 构建完整的请求payload
            payload = {
                "data": data_list,
                "event_data": None,
                "fn_index": 2,
                "trigger_id": 26,
                "dataType": [],  # 将在下面填充
                "session_hash": session_hash
            }

            # 填充dataType
            for i in range(len(image_data_list)):
                payload["dataType"].append("image")

            # 添加其他dataType
            payload["dataType"].extend([
                "dropdown", "dropdown", "textbox", "textbox",
                "slider", "slider", "slider", "slider",
                "slider", "slider", "slider", "slider",
                "textbox", "slider", "slider"
            ])

            # 发送生成请求
            logger.debug(f"Dreamo request payload: {json.dumps(payload)}")
            queue_url = f"https://bytedance-dreamo.ms.show/gradio_api/queue/join?t={int(time.time()*1000)}&__theme=light&studio_token={studio_token}"

            try:
                async with session.post(queue_url, json=payload, headers=headers) as response:
                    response.raise_for_status()
                    queue_data = await response.json()
                    logger.debug(f"Queue response: {queue_data}")

                    if "event_id" not in queue_data:
                        return f"请求失败，未能获取event_id: {queue_data}"

                    event_id = queue_data["event_id"]
            except Exception as e:
                logger.error(f"请求生成队列失败: {str(e)}")
                return f"请求生成队列失败: {str(e)}"

            # 获取生成结果
            status_url = f"https://bytedance-dreamo.ms.show/gradio_api/queue/data?session_hash={session_hash}&studio_token={studio_token}"

            try:
                async with session.get(status_url, headers=headers, timeout=aiohttp.ClientTimeout(total=300)) as response:
                    response.raise_for_status()

                    # 使用流式读取处理事件流
                    async for line in response.content:
                        line = line.decode('utf-8').strip()

                        if line.startswith('data:'):
                            try:
                                data_str = line[5:].strip()
                                if data_str:
                                    data = json.loads(data_str)
                                    logger.debug(f"Received data: {data_str}...")

                                    if data.get("msg") == "process_completed" and data.get("event_id") == event_id:
                                        if "output" in data and "data" in data["output"]:
                                            # 返回生成的图片URL
                                            url = data["output"]["data"][0]["url"]
                                            async with session.get(
                                                    url,
                                                    headers=headers,
                                            ) as response:
                                                image_bytes = await response.read()
                                                imageMessage = ImageMessage(data=image_bytes)
                                                return imageMessage.media_id
                            except json.JSONDecodeError:
                                continue
                            except Exception as e:
                                logger.error(f"处理事件流时出错: {str(e)}")
            except Exception as e:
                logger.error(f"获取生成结果失败: {str(e)}")
                return f"获取生成结果失败: {str(e)}"

        return "生成图片失败，未能获取结果"

    async def generate_flux_kontext(self, prompt: str, image1_url: Optional[str] = None, image2_url: Optional[str] = None, width: int = 768, height: int = 1024) -> str:
        """使用Bytedance Dreamo模型生成图片，支持文生图和图生图"""

        # 验证cookie
        if not self.cookie:
            return "请前往https://modelscope.cn/登录后获取token(按F12-应用-cookie中的m_session_id)"



        # 生成会话哈希
        session_hash = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10))

        if not self.cookie:
            return "请前往https://modelscope.cn/登录后获取token(按F12-应用-cookie中的m_session_id)"
        if not self.cookie.startswith("m_session_id="):
            self.cookie = "m_session_id=" + self.cookie

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Cookie": self.cookie
        }

        # 需要上传的图片列表
        image_data_list = []
        media_manager = self.container.resolve(MediaManager)
        # 处理图片上传
        async with aiohttp.ClientSession() as session:
            studio_token = await self._get_modelscope_token(session, headers)
            headers["X-Studio-Token"] = studio_token
            # 上传第一张图片（如果有）
            if image1_url:
                try:
                    # 下载图片
                    image1_bytes = await media_manager.get_data(image1_url)

                    # 保存到临时文件
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                        temp_file.write(image1_bytes)
                        temp_path1 = temp_file.name

                    # 上传图片
                    file_path1 = await self._upload_image(temp_path1, headers, "chuansir-flux-1-kontext-dev")

                    # 添加到图片数据列表
                    image_data_list.append({"image":{
                        "meta": {"_type": "gradio.FileData"},
                        "mime_type": "image/png",
                        "orig_name": f"image1.png",
                        "path": file_path1,
                        "size": None,
                        "url": f"https://chuansir-flux-1-kontext-dev.ms.show/gradio_api/file={file_path1}"
                    }})

                    # 删除临时文件
                    os.remove(temp_path1)
                except Exception as e:
                    logger.error(f"上传第一张图片失败: {str(e)}")
                    return f"上传第一张图片失败: {str(e)}"
            if image2_url:
                try:
                    # 下载图片
                    image1_bytes = await media_manager.get_data(image2_url)

                    # 保存到临时文件
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                        temp_file.write(image1_bytes)
                        temp_path1 = temp_file.name

                    # 上传图片
                    file_path1 = await self._upload_image(temp_path1, headers, "chuansir-flux-1-kontext-dev")

                    # 添加到图片数据列表
                    image_data_list.append({"image":{
                        "meta": {"_type": "gradio.FileData"},
                        "mime_type": "image/png",
                        "orig_name": f"image1.png",
                        "path": file_path1,
                        "size": None,
                        "url": f"https://chuansir-flux-1-kontext-dev.ms.show/gradio_api/file={file_path1}"
                    }})

                    # 删除临时文件
                    os.remove(temp_path1)
                except Exception as e:
                    logger.error(f"上传第二张图片失败: {str(e)}")
                    return f"上传第二张图片失败: {str(e)}"


            # 如果没有提供任何图片，则将两个图片数据项都设为None
            if not image1_url:
                image_data_list = [None]


            # 构建请求数据
            data_list: List[Any] = []

            # 添加图片数据（如果有）
            data_list.extend([image_data_list])

            # 添加其他必要参数
            data_list.extend([
                prompt,  # 提示词
                str(random.randint(0, 999999999)),  # 随机数
                True,
                2.5,
                20,
                height,  # 高度
                width,  # 宽度
            ])

            # 构建完整的请求payload
            payload = {
                "data": data_list,
                "event_data": None,
                "fn_index": 0,
                "trigger_id": 8,
                "dataType": [],  # 将在下面填充
                "session_hash": session_hash
            }


            # 添加其他dataType
            payload["dataType"].extend(["gallery"
                                        "textbox",
                                        "slider", "checkbox", "slider", "slider",
                                        "slider", "slider"
                                        ])

            # 发送生成请求
            logger.debug(f"Dreamo request payload: {json.dumps(payload)}")
            queue_url = f"https://chuansir-flux-1-kontext-dev.ms.show/gradio_api/queue/join?t={int(time.time()*1000)}&__theme=light&studio_token={studio_token}"

            try:
                async with session.post(queue_url, json=payload, headers=headers) as response:
                    response.raise_for_status()
                    queue_data = await response.json()
                    logger.debug(f"Queue response: {queue_data}")

                    if "event_id" not in queue_data:
                        return f"请求失败，未能获取event_id: {queue_data}"

                    event_id = queue_data["event_id"]
            except Exception as e:
                logger.error(f"请求生成队列失败: {str(e)}")
                return f"请求生成队列失败: {str(e)}"

            # 获取生成结果
            status_url = f"https://chuansir-flux-1-kontext-dev.ms.show/gradio_api/queue/data?session_hash={session_hash}&studio_token={studio_token}"

            try:
                async with session.get(status_url, headers=headers, timeout=aiohttp.ClientTimeout(total=300)) as response:
                    response.raise_for_status()

                    # 使用流式读取处理事件流
                    async for line in response.content:
                        line = line.decode('utf-8').strip()

                        if line.startswith('data:'):
                            try:
                                data_str = line[5:].strip()
                                if data_str:
                                    data = json.loads(data_str)
                                    logger.debug(f"Received data: {data_str}...")

                                    if data.get("msg") == "process_completed" and data.get("event_id") == event_id:
                                        if "output" in data and "data" in data["output"]:
                                            # 返回生成的图片URL
                                            url = data["output"]["data"][0]["url"]
                                            async with session.get(
                                                    url,
                                                    headers=headers,
                                            ) as response:
                                                image_bytes = await response.read()
                                                imageMessage = ImageMessage(data=image_bytes)
                                                return imageMessage.media_id
                            except json.JSONDecodeError:
                                continue
                            except Exception as e:
                                logger.error(f"处理事件流时出错: {str(e)}")
            except Exception as e:
                logger.error(f"获取生成结果失败: {str(e)}")
                return f"获取生成结果失败: {str(e)}"

        return "生成图片失败，未能获取结果"
