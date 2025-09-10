from typing import Any, Dict, List, Optional,Annotated
from kirara_ai.workflow.core.block import Block, Input, Output, ParamMeta

from kirara_ai.im.message import IMMessage, TextMessage, ImageMessage
from kirara_ai.im.sender import ChatSender, ChatType
from .image_generator import WebImageGenerator
import asyncio
from kirara_ai.logger import get_logger
from kirara_ai.ioc.container import DependencyContainer
import os
import yaml
from kirara_ai.llm.format.response import LLMChatResponse
from kirara_ai.media import MediaManager
import re
from kirara_ai.im.message import ImageMessage
from kirara_ai.media.types.media_type import MediaType

logger = get_logger("ImageGenerator")
def get_image_platform_options_provider(container: DependencyContainer, block: Block) -> List[str]:
    return ["modelscope", "shakker"]
def get_options_provider(container: DependencyContainer, block: Block) -> List[str]:
    return ["flux", "ketu", "NoobXl","anime", "photo"]

def get_voice_provider(container: DependencyContainer, block: Block) -> List[str]:
    return ["周杰伦", "可莉", "可莉2", "提莫", "阿珂", "爱莉希雅"]
class WebImageGenerateBlock(Block):
    """图片生成Block"""
    name = "text_to_image"
    description = "文生图，通过英文提示词生成图片"
    # 平台和对应的模型配置
    PLATFORM_MODELS = {
        "modelscope": ["flux", "ketu","NoobXl"],
        "shakker": ["anime", "photo"]
    }

    inputs = {
        "prompt": Input(name="prompt", label="提示词", data_type=str, description="文生图的英文提示词"),
        "width": Input(name="width", label="宽度", data_type=int, description="图片宽度", nullable=True, default=1024),
        "height": Input(name="height", label="高度", data_type=int, description="图片高度", nullable=True, default=1024),
        "cookie": Input(name="cookie", label="cookie", data_type=str, description="生图需要的cookie", nullable=True)
    }

    outputs = {
        "media_id": Output(name="media_id", label="图片id", data_type=str, description="生成的图片id")
    }

    def __init__(
            self,
            name: str = None,
            platform: Annotated[Optional[str],ParamMeta(label="平台", description="要使用的画图平台", options_provider=get_image_platform_options_provider),] = "modelscope",
            model: Annotated[Optional[str],ParamMeta(label="平台", description="要使用的画图平台", options_provider=get_options_provider),] = "flux",
            cookie: str = ""
    ):
        super().__init__(name)

        # 验证平台和模型的合法性
        if platform not in self.PLATFORM_MODELS:
            supported_platforms = ", ".join(self.PLATFORM_MODELS.keys())
            logger.error(f"不支持的平台 '{platform}'。支持的平台有: {supported_platforms}")
            raise ValueError(f"不支持的平台 '{platform}'。支持的平台有: {supported_platforms}")

        if model not in self.PLATFORM_MODELS[platform]:
            supported_models = ", ".join(self.PLATFORM_MODELS[platform])
            logger.error(f"平台 '{platform}' 不支持模型 '{model}'。支持的模型有: {supported_models}")
            raise ValueError(f"平台 '{platform}' 不支持模型 '{model}'。支持的模型有: {supported_models}")

        self.platform = platform
        self.model = model
        self.cookie = cookie
        self.generator = WebImageGenerator()
        self.config_path = os.path.join(os.path.dirname(__file__), "config.yaml")

    def _load_config(self):
        """从配置文件加载cookie"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
                    return config.get('cookies', {})
            return {}
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            return {}

    def _save_config(self, cookies):
        """保存cookie到配置文件"""
        try:
            config = {'cookies': cookies}
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True)
        except Exception as e:
            logger.error(f"保存配置文件失败: {str(e)}")

    def execute(self, **kwargs) -> Dict[str, Any]:
        prompt = kwargs.get("prompt", "")
        width = int(kwargs.get("width") or 1024)
        height = int(kwargs.get("height") or 1024)
        cookie_input = kwargs.get("cookie", "")

        # 如果传入了cookie，优先使用传入的cookie
        if cookie_input:
            self.cookie = cookie_input

        # 如果cookie为空，从配置文件加载
        if not self.cookie:
            cookies = self._load_config()
            self.cookie = cookies.get(self.platform, "")

        # 如果cookie仍然为空，返回平台特定的提示信息
        if not self.cookie:
            if self.platform == "modelscope":
                return {"image_url": "生成图片失败，请提醒用户前往https://modelscope.cn/登录后获取token并发送(按F12-应用-cookie中的m_session_id)"}
            elif self.platform == "shakker":
                return {"image_url": "生成图片失败，请提醒用户前往https://www.shakker.ai/登录后获取token并发送(按F12-应用-cookie中的usertoken)"}

        # 根据平台格式化cookie
        if self.platform == "modelscope" and not self.cookie.startswith("m_session_id="):
            self.cookie = "m_session_id=" + self.cookie

        try:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            self.generator.cookie = self.cookie
            image_url = loop.run_until_complete(
                self.generator.generate_image(
                    platform=self.platform,
                    model=self.model,
                    prompt=prompt,
                    width=width,
                    height=height
                )
            )

            # 生成成功后，保存cookie到配置文件
            if image_url:
                cookies = self._load_config()
                cookies[self.platform] = self.cookie
                self._save_config(cookies)

            return {"media_id": image_url}
        except Exception as e:
            return {"image_url": f"生成失败: {str(e)}"}

def image_reference_type_options_provider(container: DependencyContainer, block: Block) -> List[str]:
    return ["ip","id","style"]
class DreamoImageGenerateBlock(Block):
    """Dreamo图片生成Block，支持文生图和图生图"""
    name = "dreamo_image_generate"
    description = "文生图，图生图，根据提示词和图片生成图片"
    container: DependencyContainer

    inputs = {
        "prompt": Input(name="prompt", label="提示词", data_type=str, description="图片的英文提示词"),
        "media1_id": Input(name="media1_id", label="图片1的media_id", data_type=str, description="可选的第一张参考图片的media_id", nullable=True),
        "media2_id": Input(name="media2_id", label="图片2的media_id", data_type=str, description="可选的第二张参考图片的media_id", nullable=True),
        "image1_reference_type": Input(name="image1_reference_type", label="图片1参考类型", data_type=str, description="图片1的参考类型(ip/id/style),对于一般物体、人物或服装或移除背景，请选择ip;如果从输入图像中提取人脸区域，请选择id;如果保留背景，请选择style", nullable=True, default="ip"),
        "image2_reference_type": Input(name="image2_reference_type", label="图片2参考类型", data_type=str, description="图片2的参考类型(ip/id/style)", nullable=True, default="ip"),
        "width": Input(name="width", label="宽度", data_type=int, description="图片宽度", nullable=True, default=768),
        "height": Input(name="height", label="高度", data_type=int, description="图片高度", nullable=True, default=1024),
        "cookie": Input(name="cookie", label="cookie", data_type=str, description="生图需要的cookie", nullable=True)
    }

    outputs = {
        "media_id": Output(name="media_id", label="图片id", data_type=str, description="生成的图片id")
    }

    def __init__(
            self,
            name: str = None,
            cookie: str = "",
            image1_reference_type: Annotated[
                Optional[str],
                ParamMeta(label="图片1参考类型", description="图片1的参考类型(ip/id/style),对于一般物体、人物或服装或移除背景，请选择ip。如果从输入图像中提取人脸区域，请选择id。如果保留背景，请选择style", options_provider=image_reference_type_options_provider),
            ] = None,
            image2_reference_type: Annotated[
                Optional[str],
                ParamMeta(label="图片2参考类型", description="图片1的参考类型(ip/id/style),对于一般物体、人物或服装或移除背景，请选择ip。如果从输入图像中提取人脸区域，请选择id。如果保留背景，请选择style", options_provider=image_reference_type_options_provider),
            ] = None
    ):
        super().__init__(name)
        self.cookie = cookie
        self.image1_reference_type = image1_reference_type
        self.image2_reference_type = image2_reference_type
        self.generator = WebImageGenerator()
        self.config_path = os.path.join(os.path.dirname(__file__), "config.yaml")

    def _load_config(self):
        """从配置文件加载cookie"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
                    return config.get('cookies', {})
            return {}
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            return {}

    def _save_config(self, cookies):
        """保存cookie到配置文件"""
        try:
            config = {'cookies': cookies}
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True)
        except Exception as e:
            logger.error(f"保存配置文件失败: {str(e)}")

    def execute(self, **kwargs) -> Dict[str, Any]:
        self.generator.container = self.container
        prompt = kwargs.get("prompt", "")

        image1_url = kwargs.get("media1_id", None)
        image2_url = kwargs.get("media2_id", None)
        image1_reference_type = self.image1_reference_type or kwargs.get("image1_reference_type", "ip").lower()
        image2_reference_type = self.image2_reference_type or kwargs.get("image2_reference_type", "ip").lower()
        if image1_reference_type == "style" or image2_reference_type == "style":
            prompt = "generate a same style image, " + prompt
        width = int(kwargs.get("width") or 768)
        height = int(kwargs.get("height") or 1024)
        cookie_input = kwargs.get("cookie", "")

        # 验证参考类型是否有效
        valid_reference_types = ["ip", "id", "style"]
        if image1_reference_type not in valid_reference_types:
            image1_reference_type = "ip"
        if image2_reference_type not in valid_reference_types:
            image2_reference_type = "ip"

        # 如果选择了Style类型，且提示词中没有包含必要的指令，自动添加
        if (image1_reference_type == "style" or image2_reference_type == "style") and "generate a same style image" not in prompt.lower():
            prompt = "generate a same style image " + prompt

        # 如果传入了cookie，优先使用传入的cookie
        if cookie_input:
            self.cookie = cookie_input

        # 如果cookie为空，从配置文件加载
        if not self.cookie:
            cookies = self._load_config()
            self.cookie = cookies.get("modelscope", "")

        # 如果cookie仍然为空，返回提示信息
        if not self.cookie:
            return {"image_url": "生成图片失败，请提醒用户前往https://bytedance-dreamo.ms.show/登录后获取token并发送(按F12-应用-cookie中的studio_token)"}

        try:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            self.generator.cookie = self.cookie
            image_url = loop.run_until_complete(
                self.generator.generate_image(
                    platform="dreamo",
                    model="dreamo",  # 使用默认模型名称
                    prompt=prompt,
                    width=width,
                    height=height,
                    image1_url=image1_url,
                    image2_url=image2_url,
                    image1_reference_type=image1_reference_type,
                    image2_reference_type=image2_reference_type
                )
            )

            # 生成成功后，保存cookie到配置文件
            if image_url and not image_url.startswith("生成失败") and not image_url.startswith("请前往"):
                cookies = self._load_config()
                cookies["modelscope"] = self.cookie
                self._save_config(cookies)

            return {"media_id": image_url}
        except Exception as e:
            return {"image_url": f"生成失败: {str(e)}"}

class TextToAmineImageBlock(Block):
    """Dreamo图片生成Block，支持文生图和图生图"""
    name = "text_to_anime_image"
    description = "文生图，根据提示词生成动漫风格的图片"
    container: DependencyContainer

    inputs = {
        "prompt": Input(name="prompt", label="提示词", data_type=str, description="图片的英文提示词"),
        "width": Input(name="width", label="宽度", data_type=int, description="图片宽度", nullable=True, default=768),
        "height": Input(name="height", label="高度", data_type=int, description="图片高度", nullable=True, default=1024),
        "cookie": Input(name="cookie", label="cookie", data_type=str, description="生图需要的cookie", nullable=True)
    }

    outputs = {
        "media_id": Output(name="media_id", label="图片id", data_type=str, description="生成的图片id")
    }

    def __init__(
            self,
            name: str = None,
            cookie: str = "",
    ):
        super().__init__(name)
        self.cookie = cookie
        self.generator = WebImageGenerator()
        self.config_path = os.path.join(os.path.dirname(__file__), "config.yaml")

    def _load_config(self):
        """从配置文件加载cookie"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
                    return config.get('cookies', {})
            return {}
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            return {}

    def _save_config(self, cookies):
        """保存cookie到配置文件"""
        try:
            config = {'cookies': cookies}
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True)
        except Exception as e:
            logger.error(f"保存配置文件失败: {str(e)}")

    def execute(self, **kwargs) -> Dict[str, Any]:
        self.generator.container = self.container
        prompt = kwargs.get("prompt", "")

        width = int(kwargs.get("width") or 768)
        height = int(kwargs.get("height") or 1024)
        cookie_input = kwargs.get("cookie", "")

        # 如果传入了cookie，优先使用传入的cookie
        if cookie_input:
            self.cookie = cookie_input

        # 如果cookie为空，从配置文件加载
        if not self.cookie:
            cookies = self._load_config()
            self.cookie = cookies.get("modelscope", "")

        # 如果cookie仍然为空，返回提示信息
        if not self.cookie:
            return {"image_url": "生成图片失败，请提醒用户前往https://bytedance-dreamo.ms.show/登录后获取token并发送(按F12-应用-cookie中的studio_token)"}

        try:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            self.generator.cookie = self.cookie
            image_url = loop.run_until_complete(
                self.generator.generate_image(
                    platform="NoobXl",
                    model="NoobXl",  # 使用默认模型名称
                    prompt=prompt,
                    width=width,
                    height=height,
                )
            )

            # 生成成功后，保存cookie到配置文件
            if image_url and not image_url.startswith("生成失败") and not image_url.startswith("请前往"):
                cookies = self._load_config()
                cookies["modelscope"] = self.cookie
                self._save_config(cookies)
            return {"media_id": image_url}
        except Exception as e:
            return {"image_url": f"生成失败: {str(e)}"}

class TextToImageByQwenBlock(Block):
    """文生图"""
    name = "text_to_image_by_qwen"
    description = "文生图，使用千问图片模型根据提示词生成图片"
    container: DependencyContainer

    inputs = {
        "prompt": Input(name="prompt", label="提示词", data_type=str, description="图片的提示词"),
        "width": Input(name="width", label="宽度", data_type=int, description="图片宽度", nullable=True, default=768),
        "height": Input(name="height", label="高度", data_type=int, description="图片高度", nullable=True, default=768),
    }

    outputs = {
        "media_id": Output(name="media_id", label="图片id", data_type=str, description="生成的图片id")
    }

    def __init__(
            self,
            name: str = None,
            cookie: str = "",
    ):
        super().__init__(name)
        self.generator = WebImageGenerator()

    def execute(self, **kwargs) -> Dict[str, Any]:
        self.generator.container = self.container
        prompt = kwargs.get("prompt", "")

        width = int(kwargs.get("width") or 768)
        height = int(kwargs.get("height") or 1024)


        try:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            media_id = loop.run_until_complete(
                self.generator.generate_image(
                    platform="qwen_image",
                    model="qwen_image",  # 使用默认模型名称
                    prompt=prompt,
                    width=width,
                    height=height,
                )
            )

            return {"media_id": media_id}
        except Exception as e:
            return {"media_id": f"生成失败: {str(e)}"}
class FluxKontextImageGenerateBlock(Block):
    """Dreamo图片生成Block，支持文生图和图生图"""
    name = "flux_kontext_image_generate"
    description = "图生图（编辑图片，包括单张图片的修改和多图参考生成新的图片）"
    container: DependencyContainer

    inputs = {
        "english_prompt": Input(name="english_prompt", label="英文提示词", data_type=str, description="图片编辑的英文提示词"),
        "media1_id": Input(name="media1_id", label="图片1的media_id", data_type=str, description="参考图片1的media_id", nullable=True),
        "media2_id": Input(name="media2_id", label="图片2的media_id", data_type=str, description="参考图片2的media_id", nullable=True),
        "width": Input(name="width", label="宽度", data_type=int, description="图片宽度", nullable=True, default=768),
        "height": Input(name="height", label="高度", data_type=int, description="图片高度", nullable=True, default=1024),
        "cookie": Input(name="cookie", label="cookie", data_type=str, description="生图需要的cookie", nullable=True)
    }

    outputs = {
        "media_id": Output(name="media_id", label="图片id", data_type=str, description="生成的图片id")
    }

    def __init__(
            self,
            name: str = None,
            cookie: str = "",
            image1_reference_type: Annotated[
                Optional[str],
                ParamMeta(label="图片1参考类型", description="图片1的参考类型(ip/id/style),对于一般物体、人物或服装或移除背景，请选择ip。如果从输入图像中提取人脸区域，请选择id。如果保留背景，请选择style", options_provider=image_reference_type_options_provider),
            ] = None,
            image2_reference_type: Annotated[
                Optional[str],
                ParamMeta(label="图片2参考类型", description="图片1的参考类型(ip/id/style),对于一般物体、人物或服装或移除背景，请选择ip。如果从输入图像中提取人脸区域，请选择id。如果保留背景，请选择style", options_provider=image_reference_type_options_provider),
            ] = None
    ):
        super().__init__(name)
        self.cookie = cookie
        self.generator = WebImageGenerator()
        self.config_path = os.path.join(os.path.dirname(__file__), "config.yaml")

    def _load_config(self):
        """从配置文件加载cookie"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
                    return config.get('cookies', {})
            return {}
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            return {}

    def _save_config(self, cookies):
        """保存cookie到配置文件"""
        try:
            config = {'cookies': cookies}
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True)
        except Exception as e:
            logger.error(f"保存配置文件失败: {str(e)}")

    def execute(self, **kwargs) -> Dict[str, Any]:
        self.generator.container = self.container
        prompt = kwargs.get("english_prompt", "")

        image1_url = kwargs.get("media1_id", None)
        image2_url = kwargs.get("media2_id", None)
        width = int(kwargs.get("width") or 768)
        height = int(kwargs.get("height") or 1024)
        cookie_input = kwargs.get("cookie", "")

        # 如果传入了cookie，优先使用传入的cookie
        if cookie_input:
            self.cookie = cookie_input

        # 如果cookie为空，从配置文件加载
        if not self.cookie:
            cookies = self._load_config()
            self.cookie = cookies.get("modelscope", "")

        # 如果cookie仍然为空，返回提示信息
        if not self.cookie:
            return {"image_url": "生成图片失败，请提醒用户前往https://bytedance-dreamo.ms.show/登录后获取token并发送(按F12-应用-cookie中的studio_token)"}

        try:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            self.generator.cookie = self.cookie
            image_url = loop.run_until_complete(
                self.generator.generate_image(
                    platform="flux_kontext",
                    model="flux_kontext",  # 使用默认模型名称
                    prompt=prompt,
                    width=width,
                    height=height,
                    image1_url=image1_url,
                    image2_url =image2_url,
                )
            )

            # 生成成功后，保存cookie到配置文件
            if image_url and not image_url.startswith("生成失败") and not image_url.startswith("请前往"):
                cookies = self._load_config()
                cookies["modelscope"] = self.cookie
                self._save_config(cookies)

            return {"media_id": image_url}
        except Exception as e:
            return {"image_url": f"生成失败: {str(e)}"}



class MediaIdToIMMessage(Block):
    """纯文本转 IMMessage"""
    media_manager: MediaManager
    name = "media_id_to_im_message"
    container: DependencyContainer
    inputs = {"media_id": Input("media_id", "媒体id", str, "媒体id")}
    outputs = {"msg": Output("msg", "IM 消息", IMMessage, "IM 消息")}

    def __init__(self):
        self.logger = get_logger("ImageUrlToIMMessage")


    def execute(self, media_id: str) -> Dict[str, Any]:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        self.media_manager = self.container.resolve(MediaManager)
        message = loop.run_until_complete(self.media_manager.create_media_message(media_id))
        return {"msg": IMMessage(sender=ChatSender.get_bot_sender(), message_elements=[message])}

class TextToMusicGenerateBlock(Block):
    """文生音乐生成Block"""
    name = "text_to_music"
    description = "生成音乐（生成歌曲）"

    inputs = {
        "lyrics": Input(name="lyrics", label="歌词", data_type=str, description="歌词内容,示例如下:[verse]\nNeon lights they flicker bright\nCity hums in dead of night\nRhythms pulse through concrete veins\nLost in echoes of refrains\n[verse]\nBassline groovin' in my chest\nHeartbeats match the city's zest\nElectric whispers fill the air\nSynthesized dreams everywhere\n[chorus]\nTurn it up and let it flow\nFeel the fire let it grow\nIn this rhythm we belong\nHear the night sing out our song\n[verse]\nGuitar strings they start to weep\nWake the soul from silent sleep\nEvery note a story told\nIn this night we're bold and gold[bridge]\nVoices blend in harmony\nLost in pure cacophony\nTimeless echoes timeless cries\nSoulful shouts beneath the skies\n[verse]\nKeyboard dances on the keys\nMelodies on evening breeze\nCatch the tune and hold it tight\nIn this moment we take flight"),
        "style": Input(name="style", label="风格", data_type=str, description="音乐风格，示例如下:rock, hip - hop, orchestral, bass, drums, electric guitar, piano, synthesizer, violin, viola, cello, fast, energetic, motivational, inspirational, empowering", nullable=True,default="rock, hip - hop, orchestral, bass, drums, electric guitar, piano, synthesizer, violin, viola, cello, fast, energetic, motivational, inspirational, empowering"),
    }

    outputs = {
        "media_id": Output(name="media_id", label="音乐id", data_type=str, description="生成的音乐id")
    }

    def __init__(self, name: str = None, cookie: str = ""):
        super().__init__(name)
        self.cookie = cookie
        self.generator = WebImageGenerator()
        self.config_path = os.path.join(os.path.dirname(__file__), "config.yaml")

    def _load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
                    return config.get('cookies', {})
            return {}
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            return {}

    def _save_config(self, cookies):
        try:
            config = {'cookies': cookies}
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True)
        except Exception as e:
            logger.error(f"保存配置文件失败: {str(e)}")

    def execute(self, **kwargs) -> Dict[str, Any]:
        import asyncio
        duration = -1
        lyrics = kwargs.get("lyrics", "")
        style = kwargs.get("style", "")
        cookie_input = kwargs.get("cookie", "")

        # 如果传入了cookie，优先使用传入的cookie
        if cookie_input:
            self.cookie = cookie_input

        # 如果cookie为空，从配置文件加载
        if not self.cookie:
            cookies = self._load_config()
            self.cookie = cookies.get("modelscope", "")

        # 如果cookie仍然为空，返回平台特定的提示信息
        if not self.cookie:
            return {"music_url": "生成音乐失败，请提醒用户前往https://modelscope.cn/登录后获取token并发送(按F12-应用-cookie中的m_session_id)"}

        # 根据平台格式化cookie
        if not self.cookie.startswith("m_session_id="):
            self.cookie = "m_session_id=" + self.cookie

        self.generator.cookie = self.cookie
        try:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            url = loop.run_until_complete(self.generator.generate_music(duration, lyrics, style))
            # 生成成功后，保存cookie到配置文件
            if url and url.startswith("http"):
                cookies = self._load_config()
                cookies["modelscope"] = self.cookie
                self._save_config(cookies)
            if url:
                return {"media_id": url,"lyrics":lyrics}
            else:
                return {"music_url": "生成失败，未获取到音乐URL"}
        except Exception as e:
            return {"music_url": f"生成失败: {str(e)}"}
class TextToVoiceGenerateBlock(Block):
    """文生音乐生成Block"""
    name = "text_to_voice"
    description = "语音合成"
    container: DependencyContainer

    inputs = {
        "text": Input(name="text", label="文本", data_type=str, description="需要语音合成的文本"),
        "speaker_id": Input(name="speaker_id", label="说话人id", data_type=str, description="说话人id(周杰伦/可莉2/提莫/阿珂/爱莉希雅)", nullable=True, default="可莉2"),
    }

    outputs = {
        "media_id": Output(name="media_id", label="语音id", data_type=str, description="生成的语音id")
    }

    def __init__(self, name: str = None,
                 speaker_id: Annotated[
                     Optional[str],
                     ParamMeta(label="", description="说话人id(周杰伦/可莉/可莉2/提莫/阿珂/爱莉希雅)", options_provider=get_voice_provider),
                 ] = "爱莉希雅"):
        super().__init__(name)
        self.generator = WebImageGenerator()
        self.speaker_id =speaker_id
        self.config_path = os.path.join(os.path.dirname(__file__), "config.yaml")

    def execute(self, **kwargs) -> Dict[str, Any]:
        import asyncio
        text = kwargs.get("text", "")
        speaker_id = kwargs.get("speaker_id", self.speaker_id)

        try:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            url = loop.run_until_complete(self.generator.generate_voice(text, speaker_id))
            if url:
                return {"media_id": url}
            else:
                return {"voice_url": "生成失败，未获取到音乐URL"}
        except Exception as e:
            return {"voice_url": f"生成失败: {str(e)}"}

class VariableAssignBlock(Block):
    """变量赋值Block"""
    name = "variable_assign"
    description = "将一个字符串值赋给变量，并持久化到本地"

    inputs = {
        "value": Input(name="value", label="值", data_type=str, description="要赋给变量的字符串值"),
        "sender": Input(
            name="sender",
            label="发送者",
            data_type=ChatSender,
            description="获取 IM 消息的发送者",
            nullable=True,
        )
    }

    outputs = {}

    def __init__(
            self,
            name: str = None,
            variable_name: str = "default_var",
            validity_seconds: int = -1
    ):
        super().__init__(name)
        self.variable_name = variable_name
        self.validity_seconds = validity_seconds
        self.config_path = os.path.join(os.path.dirname(__file__), "variable.yaml")

    def _load_config(self):
        """从配置文件加载变量"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
                    if 'variables' not in config:
                        config['variables'] = {}
                    return config
            return {'cookies': {}, 'variables': {}}
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            return {'cookies': {}, 'variables': {}}

    def _save_config(self, config):
        """保存变量到配置文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True)
            return True
        except Exception as e:
            logger.error(f"保存配置文件失败: {str(e)}")
            return False

    def execute(self, **kwargs) -> Dict[str, Any]:
        import time
        value = kwargs.get("value", "")
        sender = kwargs.get("sender")

        # 确定租户ID
        tenant_id = "global"
        if sender:
            if sender.chat_type == ChatType.GROUP:
                tenant_id = str(sender.group_id)
            else:
                tenant_id = str(sender.user_id)

        # 加载当前配置
        config = self._load_config()

        # 确保变量部分存在
        if 'variables' not in config:
            config['variables'] = {}

        # 确保租户部分存在
        if tenant_id not in config['variables']:
            config['variables'][tenant_id] = {}

        # 存储变量值和过期时间
        variable_data = {
            "value": value,
            "expires_at": int(time.time()) + self.validity_seconds if self.validity_seconds > 0 else -1
        }

        # 存储变量数据
        config['variables'][tenant_id][self.variable_name] = variable_data

        # 保存配置
        success = self._save_config(config)
        logger.debug(f"保存变量 {self.variable_name} 成功: {success}, tenant: {tenant_id}")


class VariableGetBlock(Block):
    """变量获取Block"""
    name = "variable_get"
    description = "获取先前存储的变量值"

    inputs = {
        "sender": Input(
            name="sender",
            label="发送者",
            data_type=ChatSender,
            description="获取 IM 消息的发送者",
            nullable=True,
        )
    }

    outputs = {
        "value": Output(name="value", label="变量值", data_type=str, description="获取到的变量值")
    }

    def __init__(
            self,
            name: str = None,
            variable_name: str = "default_var",
            default_value: str = ""
    ):
        super().__init__(name)
        self.variable_name = variable_name
        self.default_value = default_value
        self.config_path = os.path.join(os.path.dirname(__file__), "variable.yaml")

    def _load_config(self):
        """从配置文件加载变量"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
                    if 'variables' not in config:
                        config['variables'] = {}
                    return config
            return {'cookies': {}, 'variables': {}}
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            return {'cookies': {}, 'variables': {}}

    def execute(self, **kwargs) -> Dict[str, Any]:
        import time
        sender = kwargs.get("sender")

        # 确定租户ID
        tenant_id = "global"
        if sender:
            if sender.chat_type == ChatType.GROUP:
                tenant_id = str(sender.group_id)
            else:
                tenant_id = str(sender.user_id)

        # 加载当前配置
        config = self._load_config()

        # 确保变量部分存在
        if 'variables' not in config:
            return {"value": self.default_value}

        # 如果找不到该租户的数据，返回默认值
        if tenant_id not in config['variables']:
            return {"value": self.default_value}

        # 获取变量数据
        variable_data = config['variables'][tenant_id].get(self.variable_name)

        # 如果变量不存在，返回默认值
        if not variable_data:
            return {"value": self.default_value}

        # 兼容旧版本数据格式（直接存储字符串值的情况）
        if isinstance(variable_data, str):
            return {"value": variable_data}

        # 检查变量是否过期
        current_time = int(time.time())
        expires_at = variable_data.get("expires_at", -1)

        if expires_at != -1 and current_time > expires_at:
            # 变量已过期，返回默认值
            return {"value": self.default_value}

        # 返回变量值
        return {"value": variable_data.get("value", self.default_value)}

class VariableDeleteBlock(Block):
    """变量删除Block"""
    name = "variable_delete"
    description = "删除先前存储的变量"

    inputs = {
        "sender": Input(
            name="sender",
            label="发送者",
            data_type=ChatSender,
            description="获取 IM 消息的发送者",
            nullable=True,
        )
    }

    outputs = {
    }

    def __init__(
            self,
            name: str = None,
            variable_name: str = "default_var"
    ):
        super().__init__(name)
        self.variable_name = variable_name
        self.config_path = os.path.join(os.path.dirname(__file__), "variable.yaml")

    def _load_config(self):
        """从配置文件加载变量"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
                    if 'variables' not in config:
                        config['variables'] = {}
                    return config
            return {'cookies': {}, 'variables': {}}
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            return {'cookies': {}, 'variables': {}}

    def _save_config(self, config):
        """保存变量到配置文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True)
            return True
        except Exception as e:
            logger.error(f"保存配置文件失败: {str(e)}")
            return False

    def execute(self, **kwargs) -> Dict[str, Any]:
        sender = kwargs.get("sender")

        # 确定租户ID
        tenant_id = "global"
        if sender:
            if sender.chat_type == ChatType.GROUP:
                tenant_id = str(sender.group_id)
            else:
                tenant_id = str(sender.user_id)

        # 加载当前配置
        config = self._load_config()

        # 确保变量部分存在
        if 'variables' not in config:
            return

        # 如果找不到该租户的数据，返回失败
        if tenant_id not in config['variables']:
            return

        # 如果变量不存在，返回失败
        if self.variable_name not in config['variables'][tenant_id]:
            return

        # 删除变量
        del config['variables'][tenant_id][self.variable_name]

        # 如果租户的变量字典为空，也删除租户
        if not config['variables'][tenant_id]:
            del config['variables'][tenant_id]

        # 保存配置
        success = self._save_config(config)
        logger.debug(f"删除变量 {self.variable_name} 成功: {success}, tenant: {tenant_id}")

class LLMResponseReplaceText(Block):
    """LLM 响应替换文本"""

    name = "llm_response_replace_text"
    container: DependencyContainer
    inputs = {"response": Input("response", "LLM 响应", LLMChatResponse, "LLM 响应")}
    outputs = {"response": Output("response", "LLM 响应", LLMChatResponse, "LLM 响应")}
    def __init__(
            self
            , regex: Annotated[str, ParamMeta(label="正则表达式", description="正则表达式")]
            , replace_text: Annotated[str, ParamMeta(label="替换文本", description="替换文本")] = ""
    ):
        self.regex = regex
        self.replace_text = replace_text
    def execute(self, response: LLMChatResponse) -> LLMChatResponse:

        if response.message:
            for part in response.message.content:
                if part.type == "text":
                    text = part.text
                    regex = re.compile(self.regex, re.DOTALL)
                    match = regex.search(text)
                    # 如果匹配到，则替换
                    if match:
                        part.text = re.sub(self.regex, self.replace_text, text, flags=re.DOTALL)

        return {"response": response}
