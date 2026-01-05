import subprocess
import whisper
import os
from pathlib import Path
from typing import List, Dict, Optional
import logging
from config import config_manager
from pydub import AudioSegment
import re

class VideoProcessor:
    def __init__(self):
        self.config = config_manager.get_video_config()
        self.ai_config = config_manager.get_ai_config()
        self.logger = logging.getLogger(__name__)
        
        # 加载语音识别模型
        self.whisper_model = None
        self.load_whisper_model()
    
    def load_whisper_model(self):
        """加载Whisper模型"""
        try:
            import torch
            
            # 设置默认数据类型为 float32，避免 FP16 警告
            torch.set_default_dtype(torch.float32)
            
            # 根据配置选择模型大小
            model_size = self.ai_config.model.split('-')[-1] if '-' in self.ai_config.model else 'base'
            if model_size not in ['tiny', 'base', 'small', 'medium', 'large']:
                model_size = 'base'  # 默认模型
            
            self.logger.info(f"正在加载Whisper模型 ({model_size})...")
            # 明确指定使用 CPU 设备，避免 FP16 警告
            self.whisper_model = whisper.load_model(model_size, device='cpu')
            self.logger.info("Whisper模型加载完成")
        except Exception as e:
            self.logger.error(f"加载Whisper模型失败: {e}")
    
    def extract_audio(self, video_path: str, audio_path: str) -> bool:
        """从视频中提取音频"""
        try:
            # 确保输出目录存在
            output_dir = Path(audio_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 使用ffmpeg提取音频
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-q:a', '0',
                '-map', 'a',
                audio_path,
                '-y'  # 覆盖输出文件
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"音频提取失败: {result.stderr}")
                return False
            
            self.logger.info(f"音频提取成功: {audio_path}")
            return True
        except Exception as e:
            self.logger.error(f"音频提取异常: {e}")
            return False
    
    def convert_audio_format(self, input_path: str, output_path: str, format: str = 'mp3') -> bool:
        """转换音频格式"""
        try:
            audio = AudioSegment.from_file(input_path)
            audio.export(output_path, format=format)
            return True
        except Exception as e:
            self.logger.error(f"音频格式转换失败: {e}")
            return False
    
    def speech_to_text(self, audio_path: str) -> Optional[str]:
        """语音转文字"""
        if not self.whisper_model:
            self.logger.error("Whisper模型未加载")
            return None
        
        try:
            self.logger.info(f"开始语音转文字: {audio_path}")
            
            # 使用Whisper进行语音识别，明确指定 fp16=False 避免警告
            result = self.whisper_model.transcribe(audio_path, language='zh', fp16=False)
            
            text = result['text'].strip()
            self.logger.info(f"语音转文字完成，文本长度: {len(text)} 字符")
            
            return text
        except Exception as e:
            self.logger.error(f"语音转文字失败: {e}")
            return None
    
    def preprocess_text(self, text: str) -> str:
        """文本预处理"""
        if not text:
            return ""
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除特殊字符，保留中英文、数字、基本标点
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s，。！？；：""''（）【】《》、]', '', text)
        
        # 去除首尾空白
        text = text.strip()
        
        return text
    
    def process_video(self, video_path: str) -> Optional[str]:
        """处理整个视频：提取音频 -> 语音转文字 -> 文本预处理"""
        try:
            # 创建音频文件路径（放在 downloads 目录）
            video_file = Path(video_path)
            audio_path = Path(self.config.download_dir) / f"{video_file.stem}_audio.mp3"
            
            #1. 提取音频
            if not self.extract_audio(video_path, str(audio_path)):
                self.logger.error("音频提取失败")
                return None
            
            #2. 语音转文字
            raw_text = self.speech_to_text(str(audio_path))
            if not raw_text:
                self.logger.error("语音转文字失败")
                return None
            
            #3. 文本预处理
            processed_text = self.preprocess_text(raw_text)
            
            #4. 清理音频文件
            # if audio_path.exists():
            #     audio_path.unlink()
            
            self.logger.info(f"视频处理完成，原始文本长度: {len(raw_text)}, 处理后长度: {len(processed_text)}")
            
            return processed_text
        except Exception as e:
            self.logger.error(f"视频处理异常: {e}")
            return None
    
    def batch_process_videos(self, video_paths: List[str]) -> List[Optional[str]]:
        """批量处理视频"""
        results = []
        
        for video_path in video_paths:
            self.logger.info(f"处理视频: {video_path}")
            result = self.process_video(video_path)
            results.append(result)
        
        return results

class TextProcessor:
    """高级文本处理器"""
    
    @staticmethod
    def segment_text(text: str, max_length: int = 1000) -> List[str]:
        """将长文本分割成段落"""
        if len(text) <= max_length:
            return [text]
        
        segments = []
        current_segment = ""
        
        # 按句子分割
        sentences = re.split(r'([。！？])', text)
        
        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            if i + 1 < len(sentences):
                sentence += sentences[i + 1]  # 添加标点符号
            
            if len(current_segment + sentence) <= max_length:
                current_segment += sentence
            else:
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = sentence
        
        if current_segment:
            segments.append(current_segment.strip())
        
        return segments
    
    @staticmethod
    def extract_key_sentences(text: str, num_sentences: int = 3) -> List[str]:
        """提取关键句子"""
        if not text:
            return []
        
        # 简单的句子分割
        sentences = re.split(r'[。！？.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # 根据长度和关键词简单评分
        scored_sentences = []
        for sentence in sentences:
            score = len(sentence)  # 基础分数为长度
            # 可以添加更多评分规则
            scored_sentences.append((score, sentence))
        
        # 按分数排序，取前几个
        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        top_sentences = [s[1] for s in scored_sentences[:num_sentences]]
        
        return top_sentences
    
    @staticmethod
    def extract_keywords(text: str, num_keywords: int = 5) -> List[str]:
        """提取关键词（简单实现）"""
        import jieba
        
        if not text:
            return []
        
        # 使用jieba进行中文分词
        words = jieba.lcut(text)
        
        # 过滤掉停用词和短词
        filtered_words = [w for w in words if len(w) > 1 and w.strip()]
        
        # 统计词频
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 按频率排序
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # 返回前N个关键词
        return [word for word, freq in sorted_words[:num_keywords]]
    
    @staticmethod
    def summarize_text(text: str, max_length: int = 200) -> str:
        """文本摘要（简单实现）"""
        if len(text) <= max_length:
            return text
        
        # 简单截断摘要
        summary = text[:max_length].rsplit(' ', 1)[0]  # 避免在单词中间截断
        if len(summary) < len(text):
            summary += "..."
        
        return summary

# 使用示例
def main():
    processor = VideoProcessor()
    
    # 示例：处理单个视频
    video_path = "path/to/your/video.mp4"  # 替换为实际视频路径
    text = processor.process_video(video_path)
    
    if text:
        print("提取的文本:")
        print(text[:500] + "..." if len(text) > 500 else text)  # 只打印前500个字符
        
        # 使用高级文本处理器
        text_processor = TextProcessor()
        keywords = text_processor.extract_keywords(text, 5)
        print(f"\n关键词: {keywords}")
        
        summary = text_processor.summarize_text(text)
        print(f"\n摘要: {summary}")
    else:
        print("视频处理失败")

if __name__ == "__main__":
    main()